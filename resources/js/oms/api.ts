import { useEffect, useRef, useState } from 'react';
import { User } from './types';

export class ApiError extends Error {
  constructor(readonly status: number, readonly code: string, message: string) { super(message); }
}
async function decode<T>(response: Response): Promise<T> {
  if (response.status === 204) return undefined as T;
  if (!response.headers.get('content-type')?.includes('application/json')) {
    if (response.status >= 502 && response.status <= 504) throw new ApiError(response.status, 'service_unavailable', '服务暂时无法连接，请稍后重试。');
    throw new Error('服务返回了无法识别的内容，请重试或反馈。');
  }
  const body: unknown = await response.json();
  if (!response.ok) {
    const problem = (body as { error?: { code: string; message: string } }).error;
    if (problem == null) throw new Error('请求失败，服务器没有返回错误详情。');
    throw new ApiError(response.status, problem.code, problem.message);
  }
  return body as T;
}
async function send<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');
  return decode<T>(await fetch(path, { ...init, headers, credentials: 'same-origin', cache: 'no-store' }));
}
export function write<T>(path: string, body: unknown, signal?: AbortSignal, actorId?: number) {
  return send<T>(path, { method: 'POST', signal, headers: { 'Content-Type': 'application/json', 'X-OMS-IR': '1', ...(actorId == null ? {} : { 'X-OMS-Actor': String(actorId) }) }, body: JSON.stringify(body) });
}
export function message(error: unknown) { return error instanceof Error ? error.message : String(error); }
function authLock<T>(operation: () => Promise<T>) {
  return navigator.locks == null ? operation() : navigator.locks.request('oms-ir-browser-session', operation);
}

class Session {
  user: User | null = null;
  error: string | null = null;
  revision = 0;
  private confirmed = false;
  private reading?: Promise<void>;
  private readonly channel = typeof BroadcastChannel === 'undefined' ? null : new BroadcastChannel('oms-ir-browser-session');

  constructor() {
    this.channel?.addEventListener('message', () => {
      const pending = this.reading;
      this.confirmed = false;
      this.change(null);
      void (pending ?? Promise.resolve()).then(() => this.refresh());
    });
    window.addEventListener('focus', () => { void this.refresh(); });
  }

  change(user: User | null) {
    this.user = user;
    this.revision++;
    document.dispatchEvent(new Event('oms:session'));
  }

  ensure() {
    // Navigation reuses a confirmed identity; focus and cross-tab changes force a read.
    return this.reading ?? (this.confirmed ? Promise.resolve() : this.refresh());
  }

  refresh() {
    if (this.reading != null) return this.reading;
    const revision = this.revision;
    this.reading = authLock(async () => {
      try {
        if (revision !== this.revision) return;
        let result: { user: User };
        try { result = await send('/api/ir/v1/user/me'); }
        catch (error) {
          if (!(error instanceof ApiError) || error.status !== 401) throw error;
          try { await write('/api/ir/v1/auth/refresh', {}); }
          catch (refreshError) {
            if (!(refreshError instanceof ApiError) || refreshError.status !== 401) throw refreshError;
            if (revision === this.revision) {
              const changed = this.error != null || this.user != null;
              this.confirmed = true;
              this.error = null;
              if (changed) this.change(null);
            }
            return;
          }
          result = await send('/api/ir/v1/user/me');
        }
        if (revision !== this.revision) return;
        const changed = this.error != null || this.user == null || this.user.id !== result.user.id || this.user.username !== result.user.username;
        this.confirmed = true;
        this.error = null;
        if (changed) this.change(result.user);
      } catch (error) {
        if (revision !== this.revision) return;
        this.confirmed = false;
        this.error = message(error);
        if (this.user != null) this.change(null);
        document.dispatchEvent(new Event('oms:session'));
      } finally { this.reading = undefined; }
    });
    return this.reading;
  }

  async login(kind: 'login' | 'register', username: string, password: string) {
    this.confirmed = false;
    this.change(null); // cancel any old owner's in-flight view before changing credentials
    const revision = this.revision;
    return authLock(async () => {
      if (revision !== this.revision) throw new Error('账号已改变，请重新确认登录。');
      const result = await write<{ user: User }>(`/api/ir/v1/auth/${kind}`, { username, password, transport: 'browser' });
      if (revision !== this.revision) throw new Error('账号已改变，请重新确认登录。');
      this.confirmed = true;
      this.error = null;
      this.change(result.user);
      Turbo.cache.clear();
      this.channel?.postMessage('changed');
      return this.revision;
    });
  }

  async logout() {
    this.confirmed = false;
    this.change(null);
    const revision = this.revision;
    await authLock(async () => {
      if (revision !== this.revision) throw new Error('账号已改变，请重新确认退出。');
      await write('/api/ir/v1/auth/logout', {});
    });
    if (revision !== this.revision) return;
    this.confirmed = true;
    this.error = null;
    Turbo.cache.clear();
    this.channel?.postMessage('changed');
    document.dispatchEvent(new Event('oms:session'));
  }
}
export const session = new Session();

export async function downloadBms(path: string, signal: AbortSignal) {
  const endpoint = new URL(path, location.origin);
  endpoint.searchParams.set('resolve', '1');
  const result = await request<{ url?: unknown } | null>(endpoint.pathname + endpoint.search, signal);
  const invalidUrl = () => new Error('服务没有返回可用的谱包地址。');
  if (result == null || typeof result !== 'object' || typeof result.url !== 'string'
    || Array.from(result.url).some(character => character.charCodeAt(0) <= 32)) throw invalidUrl();
  let target: URL;
  try { target = new URL(result.url); }
  catch (error) {
    if (!(error instanceof TypeError)) throw error;
    throw invalidUrl();
  }
  if (target.protocol !== 'https:' || !['gingerrush.com', 'pixeldrain.net', 'bms.alvorna.com'].includes(target.hostname)
    || target.port !== '' || target.username !== '' || target.password !== '' || target.hash !== '') throw invalidUrl();
  signal.throwIfAborted();
  window.location.assign(target.href);
}

export async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  try { return await send<T>(path, { signal }); }
  catch (error) {
    if (!(error instanceof ApiError) || error.status !== 401) throw error;
    // A single explicit refresh keeps cookie rotation; failures remain errors.
    await session.refresh();
    return send<T>(path, { signal });
  }
}
export async function ownedWrite<T>(path: string, body: unknown, actorId: number): Promise<T> {
  if (session.user?.id !== actorId) throw new Error('登录账号已切换，请切回原账号后重试。');
  try { return await write<T>(path, body, undefined, actorId); }
  catch (error) {
    if (!(error instanceof ApiError) || error.status !== 401) throw error;
    await session.refresh();
    if (session.user?.id !== actorId) throw new Error('原账号已退出，请重新登录后重试。');
    return write<T>(path, body, undefined, actorId);
  }
}
export function useSession() {
  const [, setRevision] = useState(session.revision);
  useEffect(() => {
    const changed = () => setRevision(value => value + 1);
    document.addEventListener('oms:session', changed);
    return () => document.removeEventListener('oms:session', changed);
  }, []);
  return session;
}
export function useApi<T>(path: string | null, initial?: T, scope: 'account' | 'public' = 'account'): { key: string; data?: T; error?: string } {
  const current = useSession();
  const key = JSON.stringify([path, scope === 'public' ? null : current.revision]);
  const seeded = useRef(initial == null ? null : key);
  const [value, setValue] = useState<{ key: string; data?: T; error?: string }>({ key, data: initial });
  useEffect(() => {
    if (path == null) return;
    // SSR data is used once; path changes and account-bound reads invalidate it.
    if (seeded.current === key) { seeded.current = null; return; }
    const cancel = new AbortController();
    setValue({ key });
    request<T>(path, cancel.signal).then(
      data => { if (!cancel.signal.aborted) setValue({ key, data }); },
      error => { if (!cancel.signal.aborted) setValue({ key, error: message(error) }); },
    );
    return () => cancel.abort();
  }, [key, path]);
  return value.key === key ? value : { key };
}
