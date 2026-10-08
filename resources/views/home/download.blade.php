{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@extends('master')
@section('content')
    @include('home._user_header_default')
    <div class="osu-page osu-page--generic-compact"><div class="download-page">
        <div class="download-page__header"><div class="download-page__banner">
            <div class="download-page__banner-content download-page__banner-content--main">
                <div class="download-page__intro">
                    <h1>下载 OMS</h1>
                    <p class="download-page__tagline">BMS · mania</p>
                    <p>Windows 音乐游戏客户端。离线游玩不需要注册。</p>
                </div>
                <div class="download-page__release">
                    <a class="btn-osu-big btn-osu-big--download" href="{{ $omsData['release_url'] }}">
                    <div class="btn-osu-big__content"><div class="btn-osu-big__left">前往 GitHub 下载
                        <div><div class="btn-osu-big__text-top btn-osu-big__text-top--download">OMS</div>Windows · ZIP</div>
                        <div class="btn-osu-big__text-bottom btn-osu-big__text-bottom--download-version">20260626</div>
                    </div><span class="btn-osu-big__icon"><span class="svg-icon svg-icon--download"></span></span></div>
                    </a>
                    <p>当前公开版为 20260626，尚不包含 IR。<a href="/help#ir">开发版连接说明</a></p>
                </div>
            </div>
        </div></div>
        <div class="download-page__guide"><div class="download-page__guide-content">
            <div class="download-page__steps">
                <div class="download-page__step"><span class="download-page__step-number">1</span>
                    <div class="download-page__text download-page__text--title">解压客户端</div>
                    <div class="download-page__text download-page__text--description">在 GitHub 发行页下载 ZIP，解压到可写目录后运行 OMS。</div>
                </div>
                <div class="download-page__step"><span class="download-page__step-number">2</span>
                    <div class="download-page__text download-page__text--title">放入谱面</div>
                    <div class="download-page__text download-page__text--description">把完整歌曲文件夹放入 <code>chartbms</code>（BMS）或 <code>chartmania</code>（mania）。<a href="/help#library">添加谱面的方法</a></div>
                </div>
                <div class="download-page__step"><span class="download-page__step-number">3</span>
                    <div class="download-page__text download-page__text--title">设置键位，开始游玩</div>
                    <div class="download-page__text download-page__text--description">在设置中确认 BMS 或 mania 的键位，再到选歌页选择谱面。</div>
                </div>
            </div>
        </div></div>
    </div></div>
@endsection
