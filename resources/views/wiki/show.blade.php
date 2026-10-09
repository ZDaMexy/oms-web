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
            <ul class="wiki-toc-list"><li><a href="#start">启动游戏</a></li><li><a href="#library">添加谱面</a></li><li><a href="#ir">连接 IR</a></li><li><a href="#scores">怎么看榜单</a></li><li><a href="#players">其他播放器</a></li><li><a href="#feedback">反馈问题</a></li></ul>
        </div></div>
        <div class="wiki-page__content"><div class="wiki-content">
            <h1>开始使用 OMS</h1>
            <h2 id="start">启动游戏</h2>
            <ol>
                <li>从 <a href="/download">下载页</a> 前往 GitHub，下载 Windows 客户端 ZIP。</li>
                <li>解压到可写目录，运行 OMS。</li>
                <li>在设置中确认 BMS 或 mania 的键位。</li>
            </ol>
            <h2 id="library">添加谱面</h2>
            <p>把完整歌曲文件夹放入对应目录，再到选歌页选择谱面：</p>
            <ul>
                <li>BMS：<code>chartbms</code></li>
                <li>mania：<code>chartmania</code></li>
            </ul>
            <p>保留文件夹内的音频、BGA 和谱面文件，以及它们的相对路径。BMS 可以直接读取原文件，无需转成 <code>.osz</code>。</p>
            <p><a href="/beatmapsets?ruleset=bms">查找 BMS 谱面</a> · <a href="/beatmapsets?ruleset=mania">查找 mania 谱面</a>。谱包由 Ginger Rush、616 或 Sayobot 原站提供，点击下载后会转到原站。</p>
            <h2 id="ir">连接 IR</h2>
            <p>IR 用于提交成绩和查看排行榜，目前仅在开发版试运行。公开下载的 20260626 版尚不支持。</p>
            <ol>
                <li>在游戏内打开账号窗口，启用 IR。</li>
                <li>填写本站地址 <code>{{ config('app.url') }}</code>，保存连接。</li>
                <li>保存连接后再登录 OMS 账号。保存地址不会自动连接。</li>
            </ol>
            <p>成绩先保存在本地，再提交到网站；断网时会保留待交记录。IR 默认关闭，离线游玩无需账号。网页和游戏使用同一套 OMS 账号，但需要分别登录。</p>
            <h2 id="scores">怎么看榜单</h2>
            <p>公开榜展示播放器提交的成绩。在 <a href="/ir">谱面榜</a> 找到一张谱面后，可以选择一个、多个或全部成绩来源。</p>
            <ul>
                <li><strong>排行榜</strong>包含 OMS、其他播放器和已收录的 LR2IR 成绩，按 EX 分排列。播放器规则不同，跨来源排名仅供参考。</li>
                <li><strong>同条件榜</strong>只比较规则和物量相同的 OMS 成绩。</li>
            </ul>
            <p>最佳分和最佳通关灯可能来自不同记录。展开成绩详情可查看各自的来源与条件。旧 LR2IR 账号单独保留，同名也不会合并到 OMS 账号。</p>
            <h2 id="players">其他播放器</h2>
            <p>先在 <a href="/account">账号页</a> 为对应播放器创建密钥，再下载匹配版本的插件。密钥只显示一次，请保存到播放器设置中。</p>
            <div class="wiki-page__table-container"><table>
                <thead><tr><th scope="col">播放器版本</th><th scope="col">插件下载</th></tr></thead>
                <tbody>
                    <tr><td>beatoraja 0.8.8</td><td><a href="/ir/adapters/omsir-beatoraja-0.8.8-0.1.0.jar" data-turbo="false">Java 插件</a></td></tr>
                    <tr><td>LR2oraja build11611350155</td><td><a href="/ir/adapters/omsir-lr2oraja-build11611350155-0.1.0.jar" data-turbo="false">Java 插件</a></td></tr>
                    <tr><td>Endless Dream v0.4.0</td><td><a href="/ir/adapters/omsir-ed-v0.4.0-0.1.0.jar" data-turbo="false">Java 插件</a></td></tr>
                    <tr><td>OpenLR2 v260915</td><td><a href="/ir/adapters/OmsIR-v260915.x64.dll" data-turbo="false">64 位 DLL</a> · <a href="/ir/adapters/OmsIR-v260915.x86.dll" data-turbo="false">32 位 DLL</a></td></tr>
                </tbody>
            </table></div>
            <p>这些插件仍在试运行，只支持表中列出的版本。Java 插件放入播放器的 <code>ir/</code> 目录，并确认启动器加载了该目录；在 IR 设置中选择 OMS，ID 填 <code>OMS</code>，Password 填播放器密钥。</p>
            <p>OpenLR2 的 DLL 必须与播放器的 32 / 64 位版本一致。放入 <code>LR2files/CustomIRs/OmsIR/</code>，在同目录的 <code>omsir.json</code> 中填写 <code>origin</code>（本站地址）与 <code>integration_key</code>（播放器密钥）。换账号或密钥后需要重启播放器。</p>
            <p>每种播放器使用对应的密钥，请勿填入网页密码。不再使用时可以在账号页撤销密钥。</p>
            <p>其他播放器只上传最佳成绩，不提供每次游玩的记录。LR2IR 档案则是历史最佳成绩。来源没有提供的时间、判定或条件会标为未知。</p>
            <details><summary>查看插件版本与校验信息</summary><p><a href="/ir/adapters/versions.json">版本清单</a> · <a href="/ir/adapters/nlohmann-json-LICENSE.MIT.txt">nlohmann/json 许可</a> · <a href="/ir/adapters/zlib-LICENSE.txt">zlib 许可</a></p></details>
            <h2 id="feedback">反馈问题</h2>
            <p>可以在 <a href="/community">社区</a> 求助，或在 <a href="https://github.com/ZDaMexy/oms/issues">GitHub</a> 报告问题。请写清客户端版本、谱面、操作步骤，以及出现的提示。截图和日志中请遮去密码、密钥与私人信息。</p>
        </div></div>
    </div></div>
@endsection
