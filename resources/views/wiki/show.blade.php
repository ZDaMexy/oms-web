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
            <p>OMSIR 汇集各客户端提交的成绩。在 <a href="/ir">谱面榜</a> 选择难度表与等级，再按首字母找到谱面；榜内可按客户端筛选。</p>
            <ul>
                <li><strong>排行榜</strong>按 EX SCORE 排列。BMS 的 ACC 是 EX / 最大 EX；最大连击、判定、Mod / Option 都沿用实际记录。</li>
                <li><strong>同条件榜</strong>只比较规则和物量相同的 OMS 成绩。</li>
            </ul>
            <p>从旧 LR2IR 数据库继承的成绩与新成绩同榜显示，仅附「旧库」标记。旧账号保留原身份，同名不会自动合并到 OMS 账号。旧库的 SBMP 标记尚未确认对应客户端；未确认与未标记记录可在客户端筛选的展开项单独选择。</p>
            <p>PG / GR / GD / BD / PR 分别表示 PGREAT、GREAT、GOOD、BAD、POOR。EP 是单独收录的空 POOR；OpenLR2 的 PR 已包含空 POOR，旧库也不能可靠拆分，EP 显示「—」。未收录的连击或时间同样显示「—」。</p>
            <p>镜像、随机与血条使用一致的短标签和图标。MR 为镜像，RD / R-RD / S-RD 分别为 RANDOM / R-RANDOM / S-RANDOM；DP 的左右侧分别标 1P / 2P，FLIP 表示左右交换。标签统一不代表各客户端判定窗口与血条完全相同，跨客户端排名仍供参考。</p>
            <p>最佳分和最佳通关灯可能来自不同记录；主行展示最高 EX 所在记录的判定与选项，独立最佳灯可在详情查看。</p>
            <h2 id="players">其他播放器</h2>
            <p>目前为下表的四款播放器提供插件，接口与文件已上线，实际播放器游玩联调仍待验收。经典原版 LR2 的实时接入尚未提供；OpenLR2 与 LR2oraja 是独立播放器。</p>
            <p>先在 <a href="/account">账号页</a> 为对应播放器创建专用密钥，再下载匹配版本的插件。密钥只显示一次，填入播放器设置，不要使用网页密码。</p>
            <div class="wiki-page__table-container"><table>
                <thead><tr><th scope="col">播放器版本</th><th scope="col">插件下载</th></tr></thead>
                <tbody>
                    <tr><td>beatoraja 0.8.8</td><td><a href="/ir/adapters/omsir-beatoraja-0.8.8-0.1.0.jar" data-turbo="false">Java 插件</a></td></tr>
                    <tr><td>LR2oraja build11611350155</td><td><a href="/ir/adapters/omsir-lr2oraja-build11611350155-0.1.0.jar" data-turbo="false">Java 插件</a></td></tr>
                    <tr><td>Endless Dream v0.4.0</td><td><a href="/ir/adapters/omsir-ed-v0.4.0-0.1.0.jar" data-turbo="false">Java 插件</a></td></tr>
                    <tr><td>OpenLR2 v260915</td><td><a href="/ir/adapters/OmsIR-v260915.x64.dll" data-turbo="false">64 位 DLL</a> · <a href="/ir/adapters/OmsIR-v260915.x86.dll" data-turbo="false">32 位 DLL</a></td></tr>
                </tbody>
            </table></div>
            <h3 id="java-ir">beatoraja / LR2oraja / Endless Dream</h3>
            <ol>
                <li>确认版本与上表一致，将对应 JAR 放入播放器的 <code>ir/</code> 目录。</li>
                <li>在原启动器的 Java classpath 中加入 <code>ir/*</code>，保留原有项目；然后重启播放器，让插件被加载。</li>
                <li>在播放器的 IR 设置中选择对应的 OMS 插件。ID 填 <code>OMS</code>，Password 填为该播放器创建的专用密钥。</li>
                <li>保存并重启。插件默认连接 <code>https://oms.zdamexy.work</code>；有自建服务时可在原 Java 启动参数加入 <code>-Domsir.origin=https://你的站点</code>。</li>
                <li>检查播放器的 IR 连接提示，再完成一张标准 LN 谱面并在网站核对成绩。当前插件不支持 CN、HCN 或带随机分支的谱面。</li>
            </ol>
            <h3 id="openlr2-ir">OpenLR2 v260915</h3>
            <ol>
                <li>关闭播放器，选择与播放器 EXE 架构一致的 32 / 64 位 DLL，放入 <code>LR2files/CustomIRs/OmsIR/</code>。</li>
                <li>下载 <a href="/ir/omsir-openlr2.example.json" download="omsir.json" data-turbo="false">omsir.json 配置模板</a>，将它以 <code>omsir.json</code> 保存到同一目录。<code>origin</code> 保留本站地址，<code>integration_key</code> 换成 OpenLR2 专用密钥。</li>
                <li>保留原 <code>LR2files/Config/openlr2-config.xml</code> 的备份，在已有 <code>&lt;config&gt;&lt;network&gt;</code> 节点内设置 <code>&lt;display_ir&gt;OMS IR (OpenLR2 v260915)&lt;/display_ir&gt;</code>，用于选择原生榜显示插件。</li>
                <li>重新启动，查看插件目录内的 <code>LastStatus.txt</code>，核对连接结果；完成正常单谱游玩后，再核对网站成绩与播放器榜单。</li>
            </ol>
            <p>OpenLR2 插件已包含所需解压依赖，无需另装 DLL。更换账号或密钥后重启播放器；不再使用时可在账号页撤销密钥。</p>
            <p>每种播放器使用对应的密钥，请勿填入网页密码。不再使用时可以在账号页撤销密钥。</p>
            <p>其他播放器提交最佳状态，不提供每次游玩的记录，也没有可证实的本局时间。旧库记录保留已有判定与原选项；未收录字段不会补成零。</p>
            <details><summary>查看插件版本与校验信息</summary><p><a href="/ir/adapters/versions.json">版本清单</a> · <a href="/ir/adapters/nlohmann-json-LICENSE.MIT.txt">nlohmann/json 许可</a> · <a href="/ir/adapters/zlib-LICENSE.txt">zlib 许可</a></p></details>
            <h2 id="feedback">反馈问题</h2>
            <p>可以在 <a href="/community">社区</a> 求助，或在 <a href="https://github.com/ZDaMexy/oms/issues">GitHub</a> 报告问题。请写清客户端版本、谱面、操作步骤，以及出现的提示。截图和日志中请遮去密码、密钥与私人信息。</p>
        </div></div>
    </div></div>
@endsection
