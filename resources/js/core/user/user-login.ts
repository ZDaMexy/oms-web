// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import { message, session } from 'oms/api';

export default class UserLogin {
  private readonly busy = new WeakSet<HTMLFormElement>();
  constructor() {
    document.addEventListener('submit', this.submit, true);
    document.addEventListener('click', this.click);
    document.addEventListener('turbo:load', this.update);
    document.addEventListener('oms:session', this.update);
  }

  readonly update = () => {
    const user = session.user;
    for (const element of document.querySelectorAll<HTMLElement>('[data-oms-auth]')) element.hidden = (element.dataset.omsAuth === 'user') !== (user != null);
    for (const element of document.querySelectorAll('[data-oms-username]')) element.textContent = user?.username ?? '登录';
    for (const element of document.querySelectorAll<HTMLAnchorElement>('[data-oms-profile-link]')) {
      if (user != null) element.href = `/users/${user.id}`; else element.removeAttribute('href');
    }
    for (const element of document.querySelectorAll<HTMLAnchorElement>('[data-oms-history-link]')) element.href = user == null ? '/account?section=history' : `/users/${user.id}?section=history`;
    for (const element of document.querySelectorAll<HTMLElement>('[data-oms-session-message]')) { element.textContent = session.error ?? ''; element.hidden = session.error == null; }
    if (user == null) for (const element of document.querySelectorAll<HTMLElement>('[data-oms-private]')) element.replaceChildren();
  };

  private readonly submit = async (event: Event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement) || !['oms-login', 'oms-register'].includes(form.id)) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    if (this.busy.has(form)) return;
    const result = form.querySelector('[data-oms-message]');
    const fields = new FormData(form);
    const username = fields.get('username');
    const password = fields.get('password');
    if (typeof username !== 'string' || typeof password !== 'string') throw new Error('登录表单字段不完整。');
    const buttons = form.querySelectorAll<HTMLButtonElement>('button[type=submit]');
    this.busy.add(form);
    buttons.forEach(button => button.disabled = true);
    if (result != null) result.textContent = '正在登录…';
    const operation = session.login(form.id === 'oms-login' ? 'login' : 'register', username, password);
    const revision = session.revision;
    try {
      const completedRevision = await operation;
      if (!form.isConnected || session.revision !== completedRevision) return;
      form.reset();
      if (result != null) result.textContent = '';
      window.osuCore.clickMenu.close();
      this.update();
    } catch (error) { if (result != null && form.isConnected && session.revision === revision) result.textContent = message(error); }
    finally { this.busy.delete(form); buttons.forEach(button => button.disabled = false); }
  };

  private readonly click = async (event: Event) => {
    if (!(event.target instanceof Element) || event.target.closest('[data-oms-logout]') == null) return;
    event.preventDefault();
    try { await session.logout(); }
    catch (error) { session.error = message(error); }
    this.update();
  };
}
