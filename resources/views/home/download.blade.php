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
                <div class="download-page__tagline"><span class="download-page__tagline-1">OMS</span><span class="download-page__tagline-2">BMS · mania</span></div>
                <a class="btn-osu-big btn-osu-big--download" href="{{ $omsData['release_url'] }}">
                    <div class="btn-osu-big__content"><div class="btn-osu-big__left">下载
                        <div><div class="btn-osu-big__text-top btn-osu-big__text-top--download">OMS</div>Windows</div>
                        <div class="btn-osu-big__text-bottom btn-osu-big__text-bottom--download-version">20260626</div>
                    </div><span class="btn-osu-big__icon"><span class="svg-icon svg-icon--download"></span></span></div>
                </a>
                <p>公开版本尚不支持 IR。开发版的 IR 仍在试运行。</p>
            </div>
        </div></div>
        <div class="download-page__guide"><div class="download-page__guide-content">
            <div class="download-page__steps">
                <div class="download-page__step"><span class="download-page__step-number">1</span>
                    <div class="download-page__text download-page__text--title">解压客户端</div>
                    <div class="download-page__text download-page__text--description">在发行页下载 ZIP，解压到可写目录，运行 OMS。首次运行会建立本地资料。</div>
                </div>
                <div class="download-page__step"><span class="download-page__step-number">2</span>
                    <div class="download-page__text download-page__text--title">添加谱面与设置键位</div>
                    <div class="download-page__text download-page__text--description">BMS 放入 chartbms，mania 放入 chartmania。进入设置确认输入键位，再从选歌页开始。<a href="/help#library">谱库说明</a></div>
                </div>
                <div class="download-page__step"><span class="download-page__step-number">3</span>
                    <div class="download-page__text download-page__text--title">选择是否使用 IR</div>
                    <div class="download-page__text download-page__text--description">离线游玩不需要注册。使用支持 IR 的开发版时，主动启用并登录 OMS 账号。<a href="/help#ir">连接说明</a></div>
                </div>
            </div>
        </div></div>
    </div></div>
@endsection