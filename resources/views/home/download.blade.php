{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@extends('master')
@section('content')
    @include('home._user_header_default')
    <div class="osu-page osu-page--generic-compact"><div class="download-page">
        <div class="download-page__header">
            <div class="download-page__banner-content">
                <div class="download-page__intro">
                    <h1>下载 OMS</h1>
                    <p>解压后即可离线游玩 BMS 和 mania。</p>
                </div>
                <div class="download-page__release">
                    <a class="btn-osu-big btn-osu-big--download" href="{{ $omsData['release_url'] }}">
                        <span class="btn-osu-big__content">
                            <span><strong>从 GitHub 下载</strong><small>20260626 · Windows · ZIP</small></span>
                            <i class="fas fa-download" aria-hidden="true"></i>
                        </span>
                    </a>
                    <p>IR 在开发版试运行。<a href="{{ route('help') }}#ir">开发版使用说明</a></p>
                </div>
            </div>
        </div>
        <div class="download-page__guide"><div class="download-page__guide-content">
            <h2>开始游玩</h2>
            <ol class="download-page__steps">
                <li class="download-page__step">
                    <h3>解压并运行</h3>
                    <p>把 ZIP 解压到可写目录，运行 OMS。</p>
                </li>
                <li class="download-page__step">
                    <h3>添加谱面</h3>
                    <p>把整首歌的文件夹放进 <code>chartbms</code> 或 <code>chartmania</code>。</p>
                    <a href="{{ route('help') }}#library">谱面导入指南</a>
                </li>
                <li class="download-page__step">
                    <h3>设置键位</h3>
                    <p>确认当前玩法的键位，然后选一张谱面开始游玩。</p>
                </li>
            </ol>
        </div></div>
        <div class="download-page__guide"><div class="download-page__guide-content">
            <h2>其他播放器</h2>
            <p>beatoraja、LR2oraja、Endless Dream 和 OpenLR2 可下载试运行插件。</p>
            <div class="download-page__links">
                <a href="{{ route('help') }}#players">下载插件与安装指南</a>
                <a href="/omsir-openlr2.example.json" download="omsir.json" data-turbo="false">OpenLR2 配置模板</a>
            </div>
        </div></div>
    </div></div>
@endsection
