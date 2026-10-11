{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@extends('master')
@php
    $sections = $omsData['help'];
@endphp
@section('content')
    @include('layout._page_header_v4', ['params' => ['theme' => 'help']])
    <div class="osu-page osu-page--wiki"><div class="wiki-page">
        <div class="wiki-page__toc"><div class="sidebar">
            <h2 class="sidebar__title">入门帮助</h2>
            <ul class="wiki-toc-list">
                @foreach ($sections as $section)
                    <li><a href="#{{ $section['id'] }}">{{ $section['heading'] }}</a></li>
                @endforeach
            </ul>
        </div></div>
        <div class="wiki-page__content"><div class="wiki-content">
            <h1>开始使用 OMS</h1>
            @foreach ($sections as $section)
                @if (in_array($section['id'], ['java-ir', 'openlr2-ir'], true))
                    <h3 id="{{ $section['id'] }}">{{ $section['heading'] }}</h3>
                @else
                    <h2 id="{{ $section['id'] }}">{{ $section['heading'] }}</h2>
                @endif
                <p style="white-space: pre-line">{{ $section['text'] }}</p>
                @if (!empty($section['links']))
                    <ul>
                        @foreach ($section['links'] as $link)
                            <li><a href="{{ $link['href'] }}"
                                @if (str_starts_with($link['href'], '/ir/adapters/') || $link['href'] === '/omsir-openlr2.example.json') data-turbo="false" @endif
                                @if ($link['href'] === '/omsir-openlr2.example.json') download="omsir.json" @endif
                            >{{ $link['label'] }}</a></li>
                        @endforeach
                    </ul>
                @endif
            @endforeach
        </div></div>
    </div></div>
@endsection
