// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import { message, ownedWrite, request, session } from './api';
import { pageData } from './page';
import { Ranking } from './types';

interface Fields { body: string; title?: string; category?: string }
interface Draft { uuid: string; actorId: number; actorName: string; fields: Fields; signature: string }
interface Key { id: number; source: string; label: string; created_at: string; revoked: boolean | number }
const drafts = new Map<string, Draft>();
const busy = new WeakSet<HTMLFormElement>();
const disabledControls = new WeakMap<HTMLFormElement, Map<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement, boolean>>();
const formKey = (form: HTMLFormElement) => location.pathname + ':' + form.dataset.kind + ':' + (form.dataset.id ?? '');
let keyRevision = -1;
let privateRead = 0;
let lastPage: string | null = null;
function show(form: Element, text: string) {
  const output = form.querySelector('[data-oms-message]');
  if (output != null) output.textContent = text;
}
function setBusy(form: HTMLFormElement, value: boolean) {
  if (value) {
    busy.add(form);
    const controls = new Map<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement, boolean>();
    for (const control of form.elements) {
      if (control instanceof HTMLInputElement || control instanceof HTMLSelectElement || control instanceof HTMLTextAreaElement) {
        controls.set(control, control.disabled);
        control.disabled = true;
      }
    }
    disabledControls.set(form, controls);
  } else {
    busy.delete(form);
    for (const [control, disabled] of disabledControls.get(form) ?? []) control.disabled = disabled;
    disabledControls.delete(form);
  }
  updatePermissions();
}
function fields(form: HTMLFormElement): Fields {
  const body = new FormData(form);
  if (typeof body.get('body') !== 'string') throw new Error('社区表单缺少正文。');
  const result: Fields = { body: body.get('body') as string };
  if (form.dataset.kind === 'post' || form.dataset.kind === 'post-edit') {
    if (typeof body.get('title') !== 'string' || typeof body.get('category') !== 'string') throw new Error('帖子表单缺少标题或分类。');
    result.title = body.get('title') as string;
    result.category = body.get('category') as string;
  }
  return result;
}
function setFields(form: HTMLFormElement, value: Fields) {
  for (const [name, text] of Object.entries(value)) {
    const input = form.elements.namedItem(name);
    if (input instanceof HTMLInputElement || input instanceof HTMLTextAreaElement || input instanceof HTMLSelectElement) input.value = text;
  }
}
function updatePermissions() {
  const user = session.user;
  for (const element of document.querySelectorAll<HTMLElement>('[data-oms-owner-id]')) element.hidden = user == null || String(user.id) !== element.dataset.omsOwnerId;
  for (const form of document.querySelectorAll<HTMLFormElement>('[data-oms-community-form]')) {
    const draft = drafts.get(formKey(form));
    const mismatch = draft != null && user != null && draft.actorId !== user.id;
    const wrongOwner = form.dataset.ownerId != null && form.dataset.ownerId !== '' && String(user?.id) !== form.dataset.ownerId;
    for (const button of form.querySelectorAll<HTMLButtonElement>('button[type=submit]')) button.disabled = busy.has(form) || user == null || mismatch || wrongOwner;
    const rebind = form.querySelector<HTMLButtonElement>('[data-oms-rebind-draft]');
    if (rebind != null) { rebind.hidden = !mismatch || form.dataset.kind?.endsWith('-edit') === true; rebind.disabled = busy.has(form); }
    if (mismatch) show(form, '草稿与提交 ID 属于 ' + draft.actorName + '（OMS #' + draft.actorId + '）。上次提交可能已经发布；先查看原账号帖子，再切回重试或主动用当前账号发布。');
  }
  const keyForm = document.querySelector<HTMLFormElement>('#oms-key-create');
  if (keyForm != null) for (const button of keyForm.querySelectorAll<HTMLButtonElement>('button[type=submit]')) button.disabled = user == null || busy.has(keyForm);
}
function linkText(element: HTMLElement) {
  if (element.dataset.omsLinked === '1') return;
  element.dataset.omsLinked = '1';
  const text = element.textContent ?? '';
  element.replaceChildren();
  let offset = 0;
  for (const match of text.matchAll(/https?:\/\/[^\s<>"']+/g)) {
    const index = match.index!;
    element.append(document.createTextNode(text.slice(offset, index)));
    const value = match[0].replace(/[.,;!?。，；！？]+$/, '');
    let url: URL;
    try { url = new URL(value); }
    catch (error) {
      if (!(error instanceof TypeError)) throw error;
      element.append(document.createTextNode(match[0]));
      offset = index + match[0].length;
      continue;
    }
    const link = document.createElement('a');
    link.href = url.href;
    link.textContent = value;
    link.target = '_blank';
    link.rel = 'nofollow noopener noreferrer';
    element.append(link, document.createTextNode(match[0].slice(value.length)));
    offset = index + match[0].length;
  }
  element.append(document.createTextNode(text.slice(offset)));
}
function clearPrivate() {
  privateRead++;
  document.querySelector('[data-oms-keys]')?.replaceChildren();
  const secret = document.querySelector('[data-oms-key-secret]');
  if (secret != null) secret.textContent = '';
  for (const input of document.querySelectorAll<HTMLInputElement>('input[type=password]')) input.value = '';
  document.querySelector('[data-oms-ranking-me]')?.replaceChildren();
}
async function loadKeys() {
  const target = document.querySelector('[data-oms-keys]');
  if (target == null || session.user == null) return;
  const revision = session.revision;
  const reading = ++privateRead;
  const form = document.querySelector('#oms-key-create');
  try {
    const response = await request<{ items: Key[] }>('/api/ir/v1/integration-keys');
    if (revision !== session.revision || reading !== privateRead || !target.isConnected) return;
    target.replaceChildren();
    for (const key of response.items) {
      const row = document.createElement('tr');
      row.className = 'ranking-page-table__row';
      for (const value of [key.source, key.label, key.revoked ? '已撤销' : '有效']) {
        const cell = document.createElement('td');
        cell.className = 'ranking-page-table__column';
        cell.textContent = value;
        row.append(cell);
      }
      const actions = document.createElement('td');
      actions.className = 'ranking-page-table__column';
      if (!key.revoked) {
        const button = document.createElement('button');
        button.type = 'button'; button.className = 'btn-osu-big btn-osu-big--account-edit';
        button.dataset.omsKeyRevoke = ''; button.dataset.keyId = String(key.id);
        button.textContent = '撤销';
        actions.append(button);
      }
      row.append(actions);
      target.append(row);
    }
  } catch (error) { if (revision === session.revision && reading === privateRead && form?.isConnected) show(form, message(error)); }
}
async function rankingMe() {
  const target = document.querySelector('[data-oms-ranking-me]');
  if (target == null || session.user == null) return;
  const initial = pageData<{ context: Record<string, unknown> }>();
  if (initial.page !== 'rankings') return;
  const parameters = new URLSearchParams();
  for (const name of ['ruleset', 'keymode', 'source', 'metric', 'condition', 'page', 'limit']) {
    const value = initial.data.context[name];
    if (value != null && value !== '') parameters.set(name, String(value));
  }
  const revision = session.revision;
  try {
    const response = await request<Ranking>('/api/ir/v1/rankings/players?' + parameters);
    if (revision !== session.revision || !target.isConnected) return;
    target.replaceChildren();
    if (response.me == null) { target.textContent = '你尚未进入此范围。'; return; }
    const me = response.me;
    const link = document.createElement('a');
    link.href = '/users/' + me.user.id;
    link.textContent = me.user.username;
    target.append(document.createTextNode('你的名次：#' + me.rank + ' · '), link, document.createTextNode(' · ' + me.value));
  } catch (error) { if (revision === session.revision && target.isConnected) { target.setAttribute('role', 'alert'); target.textContent = message(error); } }
}
function sessionChanged() {
  if (keyRevision !== session.revision) {
    keyRevision = session.revision;
    clearPrivate();
    void loadKeys();
    void rankingMe();
  }
  updatePermissions();
}
function pageLoaded() {
  clearPrivate();
  for (const element of document.querySelectorAll<HTMLElement>('[data-oms-plain-text]')) linkText(element);
  for (const form of document.querySelectorAll<HTMLFormElement>('[data-oms-community-form]')) {
    const draft = drafts.get(formKey(form));
    if (draft != null) setFields(form, draft.fields);
  }
  updatePermissions();
  if (redirectLegacyAnchor()) return;
  lastPage = location.pathname;
  void loadKeys();
  void rankingMe();
}
function redirectLegacyAnchor() {
  if (location.pathname==='/'&&location.hash==='#download') { Turbo.visit('/download',{action:'replace'}); return true; }
  if (!/^\/ir\/?$/.test(location.pathname)) return false;
  if (location.hash==='#keys') { Turbo.visit('/account',{action:'replace'}); return true; }
  if (location.hash!=='#history') return false;
  const original = location.href;
  void session.refresh().then(()=>{
    if (location.href!==original) return;
    Turbo.visit(session.user==null?'/account?section=history':`/users/${session.user.id}?section=history`,{action:'replace'});
  });
  return true;
}

document.addEventListener('submit', event => {
  const form = event.target;
  if (!(form instanceof HTMLFormElement)) return;
  if (!form.matches('[data-oms-community-form]') && form.id !== 'oms-key-create') return;
  event.preventDefault();
  event.stopImmediatePropagation();
  if (busy.has(form)) return;
  const user = session.user;
  if (user == null) { show(form, '请先登录 OMS 账号。'); return; }
  const revision = session.revision;
  if (form.id === 'oms-key-create') {
    const values = new FormData(form);
    const source = values.get('source');
    const label = values.get('label');
    if (typeof source !== 'string' || typeof label !== 'string') throw new Error('接入密钥表单缺少来源或名称。');
    setBusy(form, true);
    show(form, '正在创建…');
    document.querySelector('[data-oms-key-secret]')?.replaceChildren();
    void ownedWrite<{ secret: string }>('/api/ir/v1/integration-keys', { source, label }, user.id).then(
      response => {
        if (revision !== session.revision || !form.isConnected) return;
        const output = document.querySelector('[data-oms-key-secret]');
        if (output != null) output.textContent = response.secret;
        show(form, '密钥只显示这一次，请保存到对应播放器。');
        form.reset();
        void loadKeys();
      },
      error => { if (revision === session.revision && form.isConnected) show(form, message(error) + ' 若请求中断，请先查看列表；无法找回已创建的秘密，可撤销后重新创建。'); },
    ).finally(() => { setBusy(form, false); });
    return;
  }
  const kind = form.dataset.kind;
  if (!['post', 'reply', 'post-edit', 'reply-edit'].includes(kind ?? '')) throw new Error('未知社区表单。');
  const value = fields(form);
  const signature = JSON.stringify(value);
  const key = formKey(form);
  const previous = drafts.get(key);
  if (previous != null && previous.actorId !== user.id) { updatePermissions(); return; }
  const draft = previous?.signature === signature ? previous : { uuid: crypto.randomUUID(), actorId: previous?.actorId ?? user.id, actorName: previous?.actorName ?? user.username, fields: value, signature };
  drafts.set(key, draft);
  const creation = kind === 'post' || kind === 'reply';
  const payload = creation ? { submission_id: draft.uuid, ...value } : value;
  const id = form.dataset.id;
  const path = kind === 'post' ? '/posts' : kind === 'reply' ? '/posts/' + id + '/replies' : kind === 'post-edit' ? '/posts/' + id + '/edit' : '/replies/' + id + '/edit';
  setBusy(form, true);
  show(form, '正在提交…');
  void ownedWrite<{ post?: { id: number }; reply?: { id: number; post_id: number } }>('/api/ir/v1/community' + path, payload, draft.actorId).then(
    response => {
      if (revision !== session.revision || !form.isConnected) return;
      drafts.delete(key);
      form.reset();
      Turbo.cache.clear();
      const target = response.post?.id ?? response.reply?.post_id;
      if (target == null) throw new Error('社区返回缺少真实帖子 ID。');
      Turbo.visit('/community/' + target + (response.reply == null ? '' : '#reply-' + response.reply.id), { action: 'replace' });
    },
    error => { if (revision === session.revision && form.isConnected) show(form, message(error) + ' 草稿与提交 ID 已保留，可以重试。'); },
  ).finally(() => { setBusy(form, false); });
}, true);

document.addEventListener('input', event => {
  const input = event.target;
  if (!(input instanceof Element)) return;
  const form = input.closest<HTMLFormElement>('[data-oms-community-form]');
  if (form == null || busy.has(form)) return;
  const draft = drafts.get(formKey(form));
  if (draft == null) return;
  const value = fields(form);
  const signature = JSON.stringify(value);
  if (signature !== draft.signature) drafts.set(formKey(form), { ...draft, fields: value, signature, uuid: crypto.randomUUID() });
});
document.addEventListener('click', event => {
  if (!(event.target instanceof Element)) return;
  const rebind = event.target.closest('[data-oms-rebind-draft]');
  if (rebind != null) {
    event.preventDefault();
    const form = rebind.closest<HTMLFormElement>('[data-oms-community-form]');
    if (form == null || session.user == null || busy.has(form)) return;
    const value = fields(form);
    drafts.set(formKey(form), { uuid: crypto.randomUUID(), actorId: session.user.id, actorName: session.user.username, fields: value, signature: JSON.stringify(value) });
    show(form, '已用当前账号建立新的提交 ID。');
    updatePermissions();
    return;
  }
  const remove = event.target.closest<HTMLButtonElement>('[data-oms-delete], [data-oms-key-revoke]');
  if (remove == null || session.user == null || remove.disabled) return;
  event.preventDefault();
  if (!window.confirm(remove.hasAttribute('data-oms-key-revoke') ? '撤销这个播放器的交分密钥？' : '删除这条内容？')) return;
  const revision = session.revision;
  const path = remove.hasAttribute('data-oms-key-revoke')
    ? '/api/ir/v1/integration-keys/' + remove.dataset.keyId + '/revoke'
    : '/api/ir/v1/community/' + (remove.dataset.kind === 'post' ? 'posts' : 'replies') + '/' + remove.dataset.id + '/delete';
  remove.disabled = true;
  void ownedWrite(path, {}, session.user.id).then(
    () => {
      if (revision !== session.revision) return;
      if (remove.hasAttribute('data-oms-key-revoke')) void loadKeys();
      else { Turbo.cache.clear(); Turbo.visit(location.href, { action: 'replace' }); }
    },
    error => { if (revision === session.revision) window.popup(message(error), 'danger'); },
  ).finally(() => { remove.disabled = false; });
});
document.addEventListener('oms:session', sessionChanged);
document.addEventListener('turbo:load', pageLoaded);
document.addEventListener('turbo:before-cache', clearPrivate);
window.addEventListener('hashchange',()=>{redirectLegacyAnchor();});
window.addEventListener('beforeunload', event => {
  if (lastPage == null || !Array.from(drafts.keys()).some(key => key.startsWith(lastPage + ':'))) return;
  event.preventDefault();
  event.returnValue = '';
});
