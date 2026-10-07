{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
<div class="nav2">
    <div class="nav2__colgroup nav2__colgroup--menu">
        <div class="nav2__col nav2__col--logo">
            <a href="{{ route('home') }}" class="nav2__logo-link"><div class="nav2__logo nav2__logo--bg"></div><div class="nav2__logo"></div></a>
        </div>
        @foreach ($navLinks as $section => $links)
            <div class="nav2__col nav2__col--menu">
                <a class="nav2__menu-link-main js-menu" href="{{ $links['_'] ?? array_values($links)[0] }}"
                    data-menu-target="nav2-menu-popup-{{ $section }}" data-menu-show-delay="0">
                    <span class="u-relative">{{ $navTitles[$section] ?? $section }}
                        @if ($section === $currentSection)<span class="nav2__menu-link-bar u-section--bg-normal"></span>@endif
                    </span>
                </a>
                <div class="nav2__menu-popup">
                    <div class="simple-menu simple-menu--nav2 simple-menu--nav2-left-aligned simple-menu--nav2-transparent js-menu"
                        data-menu-id="nav2-menu-popup-{{ $section }}" data-visibility="hidden">
                        @foreach ($links as $label => $link)
                            @if ($label !== '_')<a class="simple-menu__item u-section-{{ $section }}--before-bg-normal" href="{{ $link }}">{{ $label }}</a>@endif
                        @endforeach
                    </div>
                </div>
            </div>
        @endforeach
    </div>
    <div class="nav2__colgroup nav2__colgroup--icons">
        <div class="nav2__col nav2__col--avatar">
            @include('layout._header_user')
            <div class="nav-click-popup nav-click-popup--user js-user-header-popup">@include('layout._popup_user')</div>
        </div>
    </div>
</div>
