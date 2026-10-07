{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
<div class="{{ class_with_modifiers('login-box', $modifiers ?? []) }}">
    <div class="login-box__content js-click-menu js-nav2--centered-popup js-nav2--login-box"
        data-click-menu-id="nav2-login-box" data-visibility="hidden">
        <form id="oms-login" class="login-box__section login-box__section--login js-nav-popup--submenu"
            action="/api/ir/v1/auth/login" method="POST">
            <h2 class="login-box__row login-box__row--title">登录</h2>
            <div class="login-box__row login-box__row--inputs">
                <input class="login-box__form-input js-nav2--autofocus" name="username" placeholder="用户名" autocomplete="username" required>
                <input class="login-box__form-input" name="password" type="password" placeholder="密码" autocomplete="current-password" required>
            </div>
            <div class="login-box__row login-box__row--error" data-oms-message role="status"></div>
            <div class="login-box__row login-box__row--actions">
                <div class="login-box__action"><button class="btn-osu-big btn-osu-big--nav-popup" type="submit">
                    <div class="btn-osu-big__content"><span class="btn-osu-big__left">登录</span><span class="fas fa-fw fa-sign-in-alt"></span></div>
                </button></div>
            </div>
        </form>
        <form id="oms-register" class="login-box__section login-box__section--register"
            action="/api/ir/v1/auth/register" method="POST">
            <h2 class="login-box__row login-box__row--title">创建 OMS 账号</h2>
            <div class="login-box__row">离线游玩无需账号。账号用于提交成绩和参与社区。</div>
            <div class="login-box__row">用户名为 3–24 位英文字母、数字或下划线；密码为 10–128 个字符。</div>
            <div class="login-box__row login-box__row--inputs">
                <input class="login-box__form-input" name="username" placeholder="用户名" autocomplete="username" required>
                <input class="login-box__form-input" name="password" type="password" placeholder="密码" autocomplete="new-password" required>
            </div>
            <div class="login-box__row login-box__row--error" data-oms-message role="status"></div>
            <div class="login-box__row login-box__row--actions">
                <div class="login-box__action"><button class="btn-osu-big btn-osu-big--nav-popup" type="submit">
                    <div class="btn-osu-big__content"><span class="btn-osu-big__left">注册</span><span class="fas fa-fw fa-user-plus"></span></div>
                </button></div>
            </div>
        </form>
    </div>
</div>
