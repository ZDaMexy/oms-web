// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import 'setup-turbo';
import 'setup-jquery';
import { configure as mobxConfigure } from 'mobx';
import * as moment from 'moment';
import 'moment/locale/zh-cn';
import { popup } from 'utils/popup';
import { reloadPage } from 'utils/turbolinks';

interface QTip2Api {
  destroy(immediate?: boolean): QTip2Api;
  hide(): QTip2Api;
  set(...args: unknown[]): QTip2Api;
  tooltip?: JQuery<HTMLElement>;
}
declare global {
  interface JQuery { qtip: { (method: 'api'): QTip2Api | undefined; (...args: unknown[]): unknown } }
  interface HTMLElement { _tooltip?: string }
  interface Window {
    $: JQueryStatic; jQuery: JQueryStatic; moment: typeof moment;
    _styles: { header: { height: number; heightMobile: number; heightSticky: number } };
    popup: typeof popup; reloadPage: typeof reloadPage;
    currentLocale: string;
  }
}
window.moment = moment;
moment.locale('zh-cn');
window.currentLocale = 'zh-CN';
window.popup = popup;
window.reloadPage = reloadPage;
window._styles = { header: { height: 90, heightMobile: 50, heightSticky: 50 } };
mobxConfigure({ computedRequiresReaction: true });
