{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
<div class="visible-xs no-print js-header--main">
    <div class="navbar-mobile-before"></div>
    <div class="navbar-mobile" role="navigation">
        <div class="navbar-mobile__header-section">
            <a class="navbar-mobile__logo" href="{{ route('home') }}"></a>
            <span class="navbar-mobile__brand u-ellipsis-overflow">{{ page_title() }}</span>
        </div>
        <div class="navbar-mobile__header-section navbar-mobile__header-section--buttons">
            <button type="button" class="navbar-mobile__toggle js-click-menu" data-click-menu-target="mobile-menu">
                <span class="sr-only">打开导航</span><span class="navbar-mobile__toggle-icon"><i class="fas fa-chevron-down"></i></span>
            </button>
        </div>
    </div>
    <div class="mobile-menu js-click-menu u-fancy-scrollbar" data-click-menu-id="mobile-menu">
        <div class="mobile-menu__content">
            <div class="mobile-menu__tabs">
                <button class="mobile-menu-tab mobile-menu-tab--user js-click-menu" data-click-menu-target="nav2-login-box" data-oms-auth="guest">
                    <span class="mobile-menu-tab__avatar"><span class="avatar avatar--full-rounded avatar--guest"></span></span><span>登录</span>
                </button>
                <a class="mobile-menu-tab mobile-menu-tab--user" data-oms-auth="user" data-oms-profile-link href="/account" hidden>
                    <span class="mobile-menu-tab__avatar"><span class="avatar avatar--full-rounded avatar--guest"></span></span><span data-oms-username></span>
                </a>
                <button class="mobile-menu-tab js-click-menu" data-click-menu-target="mobile-nav"><span class="fas fa-sitemap"></span></button>
            </div>
            <div class="mobile-menu__item js-click-menu" data-click-menu-id="mobile-nav">
                @include('layout.header_mobile.nav')
                <div class="navbar-mobile-item" data-oms-auth="user" hidden>
                    <a class="navbar-mobile-item__main" href="/account">账号与播放器密钥</a>
                    <button class="navbar-mobile-item__main" data-oms-logout type="button">退出登录</button>
                </div>
            </div>
        </div>
    </div>
</div>