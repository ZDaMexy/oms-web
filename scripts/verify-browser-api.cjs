// Software regression only: mocked browser and HTTP responses, no live accounts.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');

const source = fs.readFileSync(path.join(__dirname, '../resources/js/oms/api.ts'), 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText;
const alice = { id: 7, username: 'Alice' };
const bob = { id: 8, username: 'Bob' };
const unauthorized = { error: { code: 'not_authenticated', message: '请先登录。' } };
const json = (status, body) => new Response(status === 204 ? null : JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
const turn = () => new Promise(resolve => setImmediate(resolve));
function deferred() {
  let resolve;
  const promise = new Promise(complete => { resolve = complete; });
  return { promise, resolve };
}

function browser({ locks = true } = {}) {
  const steps = [];
  const calls = [];
  const failures = [];
  const assigned = [];
  const channels = [];
  const document = new EventTarget();
  const location = { origin: 'https://oms.test', assign: value => assigned.push(value) };
  const window = Object.assign(new EventTarget(), { location });
  let runningHook;
  let lockTail = Promise.resolve();
  class BroadcastChannel extends EventTarget {
    constructor(name) { super(); this.name = name; channels.push(this); }
    postMessage(value) { this.lastMessage = value; }
    receive() { this.dispatchEvent(new Event('message')); }
  }
  const react = {
    useState(initial) {
      const hook = runningHook;
      const index = hook.cursor++;
      const state = hook.slots[index] ??= { value: initial };
      return [state.value, value => { state.value = typeof value === 'function' ? value(state.value) : value; }];
    },
    useRef(initial) { return runningHook.slots[runningHook.cursor++] ??= { current: initial }; },
    useEffect(operation, dependencies) {
      const hook = runningHook;
      const index = hook.cursor++;
      const prior = hook.slots[index];
      if (prior != null && dependencies.every((value, i) => Object.is(value, prior.dependencies[i]))) return;
      hook.effects.push(() => {
        prior?.cleanup?.();
        hook.slots[index] = { dependencies, cleanup: operation() };
      });
    },
  };
  const module = { exports: {} };
  vm.runInNewContext(compiled, {
    module, exports: module.exports,
    require: name => { assert.equal(name, 'react'); return react; },
    window, document, location, BroadcastChannel,
    navigator: locks ? { locks: { request: (_name, operation) => {
      const pending = lockTail.then(operation);
      lockTail = pending.catch(() => undefined);
      return pending;
    } } } : {},
    Turbo: { cache: { clear() {} } },
    Event, Error, TypeError, URL, URLSearchParams, Headers, AbortController,
    fetch: async (url, init = {}) => {
      const call = { url: String(url), method: init.method ?? 'GET', headers: new Headers(init.headers), signal: init.signal, init };
      calls.push(call);
      const step = steps.shift();
      try {
        assert.ok(step, `Unexpected ${call.method} ${call.url}`);
        assert.equal(call.url, step.url);
        assert.equal(call.method, step.method);
      } catch (error) { failures.push(error); throw error; }
      return typeof step.response === 'function' ? step.response(call) : step.response;
    },
  }, { filename: 'oms/api.ts' });
  return {
    api: module.exports, calls, assigned, window, document, channels,
    expect(url, status, body, method = 'GET') { steps.push({ url, method, response: json(status, body) }); },
    pending(url, response, method = 'GET') { steps.push({ url, method, response }); },
    anonymous() { this.expect('/api/ir/v1/user/me', 401, unauthorized); this.expect('/api/ir/v1/auth/refresh', 401, unauthorized, 'POST'); },
    finish() { assert.equal(steps.length, 0, 'Expected requests were not consumed'); assert.deepEqual(failures, []); },
    hook(operation) {
      const hook = {
        slots: [], cursor: 0, effects: [], output: undefined,
        render() {
          this.cursor = 0;
          this.effects = [];
          runningHook = this;
          try { this.output = operation(); } finally { runningHook = undefined; }
          for (const effect of this.effects) effect();
          return this.output;
        },
        dispose() { for (const slot of this.slots) slot?.cleanup?.(); },
      };
      return hook;
    },
  };
}

async function anonymousNavigationAndFocus(locks) {
  const b = browser({ locks });
  b.anonymous();
  await Promise.all([b.api.session.ensure(), b.api.session.ensure()]);
  for (let i = 0; i < 5; i++) await b.api.session.ensure();
  assert.equal(b.calls.length, 2);
  assert.equal(b.api.session.user, null);
  b.anonymous();
  b.window.dispatchEvent(new Event('focus'));
  await b.api.session.ensure();
  assert.equal(b.calls.length, 4, 'Focus must force a fresh identity check');
  b.anonymous();
  b.channels[0].receive();
  await turn();
  await b.api.session.ensure();
  assert.equal(b.calls.length, 6, 'Cross-tab changes must invalidate an anonymous confirmation');
  b.finish();
}

async function loginLogoutAndFailure() {
  const b = browser();
  b.expect('/api/ir/v1/auth/login', 200, { user: alice }, 'POST');
  await b.api.session.login('login', 'Alice', 'software-test-password');
  await b.api.session.ensure();
  assert.equal(b.api.session.user.id, alice.id);
  assert.equal(b.calls.length, 1, 'Successful login already confirms identity');
  b.expect('/api/ir/v1/auth/logout', 204, null, 'POST');
  await b.api.session.logout();
  await b.api.session.ensure();
  assert.equal(b.calls.length, 2, 'Successful logout already confirms anonymity');
  assert.equal(b.api.session.user, null);
  b.pending('/api/ir/v1/user/me', () => { throw new Error('network unavailable'); });
  await b.api.session.refresh();
  assert.match(b.api.session.error, /network unavailable/);
  b.expect('/api/ir/v1/user/me', 200, { user: bob });
  await b.api.session.ensure();
  assert.equal(b.api.session.user.id, bob.id);
  assert.equal(b.api.session.error, null, 'Failed reads must not suppress later retries');
  b.finish();
}

async function crossTabDiscardsOldIdentity() {
  const b = browser();
  const old = deferred();
  b.pending('/api/ir/v1/user/me', () => old.promise);
  b.expect('/api/ir/v1/user/me', 200, { user: bob });
  const observed = [];
  b.document.addEventListener('oms:session', () => observed.push(b.api.session.user?.id ?? null));
  const reading = b.api.session.ensure();
  await turn();
  b.channels[0].receive();
  assert.equal(b.api.session.user, null);
  assert.equal(b.calls.length, 1, 'Replacement waits for the old read');
  old.resolve(json(200, { user: alice }));
  await reading;
  await turn();
  await b.api.session.ensure();
  assert.equal(b.api.session.user.id, bob.id);
  assert.ok(!observed.includes(alice.id), 'A stale identity must never be restored');
  b.finish();
}

async function expiredCookieAndActorProtection() {
  const b = browser();
  b.expect('/private', 401, unauthorized);
  b.expect('/api/ir/v1/user/me', 401, unauthorized);
  b.expect('/api/ir/v1/auth/refresh', 200, {}, 'POST');
  b.expect('/api/ir/v1/user/me', 200, { user: alice });
  b.expect('/private', 200, { value: 'current-owner' });
  assert.equal((await b.api.request('/private')).value, 'current-owner');
  b.expect('/write', 401, unauthorized, 'POST');
  b.expect('/api/ir/v1/user/me', 200, { user: bob });
  await assert.rejects(b.api.ownedWrite('/write', { body: 'draft' }, alice.id), /原账号已退出/);
  assert.equal(b.calls.filter(call => call.url === '/write').length, 1, 'Changed owners must not replay a write');
  assert.equal(b.calls.find(call => call.url === '/write').headers.get('X-OMS-Actor'), String(alice.id));
  b.finish();
}

async function sameActorCanRetry() {
  const b = browser();
  b.expect('/api/ir/v1/user/me', 200, { user: alice });
  await b.api.session.ensure();
  b.expect('/write', 401, unauthorized, 'POST');
  b.expect('/api/ir/v1/user/me', 401, unauthorized);
  b.expect('/api/ir/v1/auth/refresh', 200, {}, 'POST');
  b.expect('/api/ir/v1/user/me', 200, { user: alice });
  b.expect('/write', 200, { saved: true }, 'POST');
  assert.equal((await b.api.ownedWrite('/write', { body: 'draft' }, alice.id)).saved, true);
  assert.ok(b.calls.filter(call => call.url === '/write').every(call => call.headers.get('X-OMS-Actor') === String(alice.id)));
  b.finish();
}

async function publicReadsSurviveIdentityChanges() {
  const b = browser();
  const response = deferred();
  b.pending('/public', () => response.promise);
  const hook = b.hook(() => b.api.useApi('/public', undefined, 'public'));
  hook.render();
  const signal = b.calls[0].signal;
  b.api.session.change(alice);
  hook.render();
  assert.equal(b.calls.length, 1);
  assert.equal(signal.aborted, false, 'Public reads must not be cancelled by identity changes');
  response.resolve(json(200, { value: 'public-data' }));
  await turn();
  hook.render();
  assert.equal(hook.output.data.value, 'public-data');
  b.api.session.change(null);
  hook.render();
  assert.equal(hook.output.data.value, 'public-data');
  assert.equal(b.calls.length, 1);
  hook.dispose();
  b.finish();
}

async function accountReadsDiscardLateResponses() {
  const b = browser();
  const old = deferred();
  b.pending('/account-bound', () => old.promise);
  b.expect('/account-bound', 200, { value: 'new-owner' });
  const hook = b.hook(() => b.api.useApi('/account-bound'));
  hook.render();
  const oldSignal = b.calls[0].signal;
  b.api.session.change(bob);
  hook.render();
  assert.equal(oldSignal.aborted, true);
  await turn();
  old.resolve(json(200, { value: 'old-owner' }));
  await turn();
  hook.render();
  assert.equal(hook.output.data.value, 'new-owner');
  assert.equal(b.calls.length, 2);
  hook.dispose();
  b.finish();
}

async function publicSsrAndScopeChanges() {
  const b = browser();
  let endpoint = '/table?page=1';
  const hook = b.hook(() => b.api.useApi(endpoint, { value: 'ssr' }, 'public'));
  hook.render();
  b.api.session.change(alice);
  hook.render();
  assert.equal(b.calls.length, 0, 'Public SSR data must survive initial identity confirmation');
  b.expect('/table?page=2', 200, { value: 'second-page' });
  endpoint = '/table?page=2';
  hook.render();
  await turn();
  hook.render();
  assert.equal(hook.output.data.value, 'second-page');
  hook.dispose();
  b.finish();
}

async function singleDownloadResolution() {
  for (const host of ['gingerrush.com', 'pixeldrain.net', 'bms.alvorna.com']) {
    const b = browser();
    const url = `https://${host}/package.zip?download=1`;
    b.expect('/api/ir/v1/catalog/bms/chart/download?sha256=hash&resolve=1', 200, { url });
    await b.api.downloadBms('/api/ir/v1/catalog/bms/chart/download?sha256=hash', new AbortController().signal);
    assert.deepEqual(b.assigned, [url]);
    assert.equal(b.calls.length, 1, 'Download resolution must not probe identity or call the redirect twice');
    assert.equal(b.calls[0].headers.get('Accept'), 'application/json');
    b.finish();
  }
  for (const url of [null, 123, '', '/relative.zip', 'http://gingerrush.com/package.zip', 'https://unapproved.test/file', 'https://user:password@gingerrush.com/file', 'https://gingerrush.com:444/file', 'https://gingerrush.com/file#fragment', 'https://gingerrush.com/white space']) {
    const b = browser();
    b.expect('/download?resolve=1', 200, { url });
    await assert.rejects(b.api.downloadBms('/download', new AbortController().signal), /服务没有返回可用的谱包地址/);
    assert.deepEqual(b.assigned, []);
    b.finish();
  }
  const missing = browser();
  missing.expect('/download?resolve=1', 200, null);
  await assert.rejects(missing.api.downloadBms('/download', new AbortController().signal), /服务没有返回可用的谱包地址/);
  missing.finish();
  const failed = browser();
  failed.expect('/download?resolve=1', 503, { error: { code: 'source_unavailable', message: '原站无法连接。' } });
  await assert.rejects(failed.api.downloadBms('/download', new AbortController().signal), /原站无法连接/);
  assert.deepEqual(failed.assigned, []);
  failed.finish();
  const cancelled = browser();
  cancelled.expect('/download?resolve=1', 200, { url: 'https://gingerrush.com/package.zip' });
  const controller = new AbortController();
  const download = cancelled.api.downloadBms('/download', controller.signal);
  controller.abort();
  await assert.rejects(download, error => error.name === 'AbortError');
  assert.deepEqual(cancelled.assigned, [], 'Late resolution must not start a cancelled download');
  cancelled.finish();
}

(async () => {
  await anonymousNavigationAndFocus(true);
  await anonymousNavigationAndFocus(false);
  await loginLogoutAndFailure();
  await crossTabDiscardsOldIdentity();
  await expiredCookieAndActorProtection();
  await sameActorCanRetry();
  await publicReadsSurviveIdentityChanges();
  await accountReadsDiscardLateResponses();
  await publicSsrAndScopeChanges();
  await singleDownloadResolution();
  console.log('Browser API regressions passed (mocked session, request lifecycle, download resolution).');
})().catch(error => { console.error(error); process.exitCode = 1; });
