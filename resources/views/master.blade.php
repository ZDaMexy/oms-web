{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@php
    $currentRoute = app('route-section')->getCurrent();
    $currentSection = $currentRoute['section'];
    $currentAction = $currentRoute['action'];
    $currentUser = null;
    $title = ($titleOverride ?? $titlePrepend ?? page_title()).' | OMS';
    $defaultHue = section_to_hue_map($currentSection);
    $currentHue ??= $defaultHue;
    $navLinks ??= nav_links();
    $currentLocaleMeta ??= current_locale_meta();
    $navTitles = ['home' => '主页', 'beatmaps' => '谱面', 'rankings' => '排行', 'community' => '社区', 'help' => '帮助'];
@endphp
<!DOCTYPE html>
<html prefix="og: http://ogp.me/ns#" lang="zh-CN">
    <head>
        @include('layout.metadata')
        <title>{{ $title }}</title>
    </head>
    <body class="t-section osu-layout osu-layout--body {{ $bodyAdditionalClasses ?? '' }}"
        style="--base-hue-default: {{ $defaultHue }}; --base-hue-override: {{ $currentHue }}">
        <div id="overlay" class="blackout blackout--overlay" style="display: none;"></div>
        <div class="blackout js-blackout" data-visibility="hidden"></div>
        @if (!isset($blank))
            @include('layout.header')
            <div class="osu-page osu-page--notification-banners js-notification-banners js-sync-height--reference"
                data-sync-height-target="notification-banners"><div class="alert alert-danger" data-oms-session-message role="alert" hidden></div></div>
        @endif
        <div class="osu-layout__section osu-layout__section--full">@yield('content')</div>
        @if (!isset($blank))
            @include('layout.footer')
        @endif
        <div class="fixed-bar js-fixed-element js-fixed-bottom-bar js-sticky-footer--fixed-bar">
            <div class="js-permanent-fixed-footer js-sync-height--reference"
                data-sync-height-target="permanent-fixed-footer">@yield('permanent-fixed-footer')</div>
        </div>
        <div id="estimate-min-lines" class="estimate-min-lines" data-turbo-permanent>
            <div class="estimate-min-lines__content js-estimate-min-lines"></div>
        </div>
        @include('layout._global_variables')
        @include('layout._loading_overlay')
        @include('layout.popup-container')
        <script id="json-route-section" type="application/json">{!! json_encode($currentRoute, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT) !!}</script>
        @yield('script')
    </body>
</html>
