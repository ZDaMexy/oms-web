// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import AnimateNav from 'core/animate-nav';
import ClickMenu from 'core/click-menu';
import Localtime from 'core/localtime';
import MobileToggle from 'core/mobile-toggle';
import ReactTurbolinks from 'core/react-turbolinks';
import Spoilerbox from 'core/spoilerbox';
import StickyFooter from 'core/sticky-footer';
import StickyHeader from 'core/sticky-header';
import SyncHeight from 'core/sync-height';
import Timeago from 'core/timeago';
import TurbolinksReload from 'core/turbolinks-reload';
import UserLogin from 'core/user/user-login';
import WindowSize from 'core/window-size';
import { session } from 'oms/api';

// The original navigation and React lifecycle remain. Unsupported global
// chat/socket/store/account editors have no construction or import path.
export default class OsuCore {
  readonly animateNav = new AnimateNav();
  readonly clickMenu = new ClickMenu();
  readonly localtime = new Localtime();
  readonly mobileToggle = new MobileToggle();
  readonly spoilerbox = new Spoilerbox();
  readonly stickyFooter = new StickyFooter();
  readonly windowSize = new WindowSize();
  readonly stickyHeader = new StickyHeader();
  readonly syncHeight = new SyncHeight();
  readonly timeago = new Timeago();
  readonly turbolinksReload = new TurbolinksReload();
  readonly reactTurbolinks = new ReactTurbolinks(this.turbolinksReload);
  readonly userLogin = new UserLogin();
  get currentUser() { return session.user; }
  readonly updateCurrentUser = () => session.refresh();
}
