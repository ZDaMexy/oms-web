{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
<meta charset="utf-8">
<meta name="description" content="{{ $pageDescription ?? 'OMS：BMS 与 mania。下载客户端、查找谱面和成绩。' }}">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="{{ hsl_to_hex($currentHue, 0.1, 0.4) }}">
<meta name="turbo-cache-control" content="no-cache">
<meta name="turbo-prefetch" content="false">
<meta property="og:site_name" content="OMS">
<meta property="og:type" content="website">
<link rel="icon" href="/images/oms-logo.svg" type="image/svg+xml">
@if (isset($canonicalUrl))
    <link rel="canonical" href="{{ $canonicalUrl }}">
    <meta property="og:url" content="{{ $canonicalUrl }}">
@endif
@if ($noindex ?? false)
    <meta name="robots" content="noindex">
@endif
<link rel="stylesheet" media="all" href="{{ unmix('css/app.css') }}" data-turbo-track="reload">
<script src="{{ unmix('js/runtime.js') }}" data-turbo-eval="false" data-turbo-track="reload"></script>
<script src="{{ unmix('js/vendor.js') }}" data-turbo-eval="false" data-turbo-track="reload"></script>
<script src="{{ unmix('js/commons.js') }}" data-turbo-eval="false" data-turbo-track="reload"></script>
<script src="{{ unmix('js/app.js') }}" data-turbo-eval="false" data-turbo-track="reload"></script>
