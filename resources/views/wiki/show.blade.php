{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@extends('master')
@section('content')
    @include('layout._page_header_v4', ['params' => ['theme' => 'help']])
    <div class="osu-page osu-page--wiki"><div class="wiki-page">
        <div class="wiki-page__toc"><div class="sidebar">
            <h2 class="sidebar__title">入门帮助</h2>
            <ul class="wiki-toc-list"><li><a href="#start">启动</a></li><li><a href="#library">添加谱面</a></li><li><a href="#ir">连接 IR</a></li><li><a href="#players">其他播放器</a></li><li><a href="#feedback">反馈问题</a></li></ul>
        </div></div>
        <div class="wiki-page__content"><div class="wiki-content">
            <h1>开始使用 OMS</h1>
            <h2 id="start">启动</h2>
            <p>在 <a href="/download">下载页</a> 打开发行说明，下载 Windows 客户端 ZIP，解压到可写目录后运行。第一次启动后，在设置中确认 BMS 或 mania 的键位，再开始游玩。</p>
            <h2 id="library">添加谱面</h2>
            <p>BMS 使用 chartbms，mania 使用 chartmania。把完整歌曲目录放入对应目录，保留音频、BGA 与谱面之间的相对路径。BMS 直接读取原文件，不需要转成 .osz。</p>
            <p><a href="/beatmapsets?ruleset=bms">查找 BMS 谱面</a> · <a href="/beatmapsets?ruleset=mania">查找 mania 谱面</a>。下载转到对应的 Ginger Rush、616 或 Sayobot 原站；本站不托管谱包。</p>
            <h2 id="ir">连接 IR</h2>
            <p>公开下载的 20260626 版本尚不包含 IR。使用支持 IR 的开发版时，打开原账号窗口，主动启用 IR，填写本站地址 <code>{{ config('app.url') }}</code>，保存连接后再登录 OMS 账号。保存地址不会自动连接。</p>
            <p>成绩先保存在本地，之后按需提交。断网时保留待交内容。默认不连接，离线游玩无需账号。网页和游戏内使用同一 OMS 身份，旧 LR2IR ID 独立保留。</p>
            <p><a href="/ir">谱面榜</a> 支持按一个、多个或全部来源查看参考成绩。主动选择同条件榜时，只比较有已知依据的同规则记录；不同播放器的灯和判定不强行换算。</p>
            <h2 id="players">其他播放器</h2>
            <p>使用 <a href="/account">账号页</a> 为对应播放器创建独立密钥，再按照插件说明配置。密钥只在创建时显示；不再使用时撤销。请勿在帖子、截图或问题报告中公开密钥。</p>
            <p><a href="/ir/adapters/versions.json">当前适配版本清单与插件校验信息</a></p>
            <p>外部播放器上传的是当前最佳状态。没有稳定局 ID 的播放器不产生逐局历史。LR2IR 档案提供历史最佳摘要，缺字段和未知条件会保留说明。</p>
            <h2 id="feedback">反馈问题</h2>
            <p>可以在 <a href="/community">社区</a> 求助，或在 <a href="https://github.com/ZDaMexy/oms/issues">GitHub</a> 提交问题。附上客户端版本、谱面和操作步骤；密码、会话、密钥与私人数据请先移除。</p>
        </div></div>
    </div></div>
@endsection
