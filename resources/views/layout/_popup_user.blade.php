{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
<div class="simple-menu simple-menu--nav2 js-click-menu js-nav2--centered-popup"
    data-click-menu-id="nav2-user-popup" data-visibility="hidden">
    <a href="/account" data-oms-profile-link class="simple-menu__header simple-menu__header--link">
        <img class="simple-menu__header-icon" src="/images/icons/profile.svg" alt="">
        <div class="u-relative" data-oms-username></div>
    </a>
    <a class="simple-menu__item" href="/account" data-oms-profile-link>个人页</a>
    <a class="simple-menu__item" href="/account?section=history" data-oms-history-link>我的完整记录</a>
    <a class="simple-menu__item" href="/account">账号与播放器密钥</a>
    <button class="simple-menu__item" type="button" data-oms-logout>退出登录</button>
</div>
