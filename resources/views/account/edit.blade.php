{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@extends('master')
@section('content')
    @include('layout._page_header_v4', ['params' => ['theme' => 'settings']])
    <div class="osu-page osu-page--account-edit">
        <div class="account-edit account-edit--first">
            <div class="account-edit__section"><h2 class="account-edit__section-title">账号</h2></div>
            <p data-oms-auth="guest">打开导航中的登录入口，登录或创建 OMS 账号，即可查看自己的记录、管理播放器密钥。离线游玩无需账号。</p>
            <div class="account-edit__input-groups" data-oms-auth="user" hidden>
                <div class="account-edit__input-group"><div class="account-edit-entry account-edit-entry--read-only">
                    <div class="account-edit-entry__label">用户名</div><div class="account-edit-entry__input" data-oms-username></div>
                </div></div>
                <div class="account-edit__input-group"><a class="btn-osu-big btn-osu-big--account-edit" href="/account" data-oms-profile-link><span class="btn-osu-big__content">我的个人页</span></a>
                    <a class="btn-osu-big btn-osu-big--account-edit" href="/account?section=history" data-oms-history-link><span class="btn-osu-big__content">我的完整记录</span></a>
                    <button class="btn-osu-big btn-osu-big--account-edit" type="button" data-oms-logout><span class="btn-osu-big__content">退出登录</span></button>
                </div>
            </div>
        </div>
        <div class="account-edit" data-oms-auth="user" hidden>
            <div class="account-edit__section"><h2 class="account-edit__section-title">播放器密钥</h2><p>为每种播放器创建对应的密钥，用它连接 OMS。密钥只显示一次，请保存到播放器设置中。</p></div>
            <div class="account-edit__input-groups">
                <form id="oms-key-create" class="account-edit__input-group" method="POST" action="/api/ir/v1/integration-keys">
                    <label class="account-edit-entry"><span class="account-edit-entry__label">播放器</span><select class="account-edit-entry__input" name="source"><option value="beatoraja">beatoraja</option><option value="lr2oraja">LR2oraja</option><option value="lr2oraja_ed">Endless Dream</option><option value="openlr2">OpenLR2</option></select></label>
                    <label class="account-edit-entry"><span class="account-edit-entry__label">名称</span><input class="account-edit-entry__input" name="label" maxlength="80" placeholder="例如：家里的 ED" required></label>
                    <button class="btn-osu-big btn-osu-big--account-edit" type="submit"><span class="btn-osu-big__content">创建密钥</span></button>
                    <p data-oms-message role="status"></p>
                    <output data-oms-key-secret style="overflow-wrap: anywhere"></output>
                </form>
                <div class="account-edit__input-group"><table class="ranking-page-table"><thead><tr><th class="ranking-page-table__heading">播放器</th><th class="ranking-page-table__heading">名称</th><th class="ranking-page-table__heading">状态</th><th class="ranking-page-table__heading"></th></tr></thead><tbody data-oms-keys></tbody></table></div>
            </div>
            <p><a href="/help#players">各播放器设置与插件</a></p>
        </div>
    </div>
    @include('oms._page_data')
@endsection
