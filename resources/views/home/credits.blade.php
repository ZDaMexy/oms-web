@extends('master')
@section('content')
    @include('layout._page_header_v4', ['params' => ['theme' => 'help']])
    <div class="osu-page osu-page--wiki"><div class="wiki-page">
        <div class="wiki-page__toc"><p><a href="https://github.com/ZDaMexy/oms-web">OMS Web 源码</a></p><p><a href="https://github.com/ppy/osu-web">osu-web 上游</a></p></div>
        <div class="wiki-page__content"><div class="wiki-content">
            <h1>源码与许可</h1>
            <p>本网站基于 ppy 的 osu-web 原项目，初始来源为 2c596022a1345fbed288978e7fa5304df0359f50，保留上游历史及作者归属。OMS 修改页面可用功能、品牌和数据接入，账号、成绩与社区使用现有 OMS 服务。</p>
            <p>网站源码按 <a href="https://github.com/ZDaMexy/oms-web/blob/main/LICENCE">GNU AGPL v3</a> 发布。页面名称与代码中的 osu 前缀保留原项目结构；本站是 OMS，不属于 ppy 官方服务。</p>
            <p>启用的西文字体为 Inter，遵循 SIL Open Font License 1.1；中文使用系统字体。原商业 Torus 与许可未核对的 Venera 不在本站启用。图标沿原 Font Awesome Free 许可与作者归属。</p>
            <p>客户端：<a href="https://github.com/ZDaMexy/oms">OMS</a>。谱面与音频版权属于对应作者；外部目录仅提供已批准的元数据和原站下载入口。</p>
        </div></div>
    </div></div>
@endsection