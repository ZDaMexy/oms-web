@extends('master')
@section('content')
    @include('layout._page_header_v4', ['params' => ['theme' => 'help']])
    <div class="osu-page osu-page--wiki"><div class="wiki-page">
        <div class="wiki-page__toc"><p><a href="https://github.com/ZDaMexy/oms-web">OMS Web 源码</a></p><p><a href="https://github.com/ppy/osu-web">osu-web 上游</a></p></div>
        <div class="wiki-page__content"><div class="wiki-content">
            <h1>源码与许可</h1>
            <p>OMS Web 基于 ppy 的 <a href="https://github.com/ppy/osu-web">osu-web</a>，沿用其页面结构，并接入 OMS 的账号、成绩和社区服务。感谢原项目作者与贡献者。</p>
            <p>网站源码按 <a href="https://github.com/ZDaMexy/oms-web/blob/main/LICENCE">GNU AGPL v3</a> 发布，保留原作者归属。OMS 与 osu! / ppy 的官方服务无隶属关系。</p>
            <p><a href="/oms-web-source.tar.gz" data-turbo="false">下载当前站点的对应源码</a>，或在 <a href="https://github.com/ZDaMexy/oms-web">GitHub</a> 查看开发记录。</p>
            <h2>字体与图标</h2>
            <ul>
                <li>西文字体：Inter，采用 SIL Open Font License 1.1。中文使用系统字体。</li>
                <li>图标：Font Awesome Free，按其许可保留作者归属。</li>
            </ul>
            <h2>客户端与谱面</h2>
            <p><a href="https://github.com/ZDaMexy/oms">OMS 客户端源码</a>。谱面、音频与 BGA 的版权属于各自作者，谱包由目录来源的原站提供。</p>
            <details><summary>网站修改与依赖说明</summary>
                <p>初始上游提交：<code>2c596022a1345fbed288978e7fa5304df0359f50</code>。OMS 修改了品牌、页面功能和数据接入，保留上游 Git 历史。代码中的 <code>osu</code> 前缀沿用原项目命名。</p>
                <p>本站未启用 Torus 或 Venera。依赖清单见源码中的 <a href="https://github.com/ZDaMexy/oms-web/blob/main/package.json">前端依赖</a> 与 <a href="https://github.com/ZDaMexy/oms-web/blob/main/composer.json">PHP 依赖</a>。</p>
            </details>
        </div></div>
    </div></div>
@endsection
