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
    <div class="osu-page osu-page--wiki"><div class="wiki-page wiki-page--help">
        <nav class="wiki-page__toc" aria-label="帮助目录">
            <ul class="wiki-toc-list">
                @foreach ($sections as $section)
                    <li><a href="#{{ $section['id'] }}">{{ $section['heading'] }}</a></li>
                @endforeach
            </ul>
        </nav>
        <div class="wiki-page__content"><div class="wiki-content">
            <h1>开始使用 OMS</h1>
            @foreach ($sections as $section)
                @if (in_array($section['id'], ['java-ir', 'openlr2-ir'], true))
                    <h3 id="{{ $section['id'] }}">{{ $section['heading'] }}</h3>
                @else
                    <h2 id="{{ $section['id'] }}">{{ $section['heading'] }}</h2>
                @endif
                @foreach (explode("\n", $section['text']) as $line)
                    @if (trim($line) !== '')<p>{{ $line }}</p>@endif
                @endforeach
                @if (!empty($section['links']))
                    @php
                        [$references, $links] = collect($section['links'])->partition(fn ($link) => preg_match('/(?:versions\.json|LICENSE[^\/]*\.txt)$/D', $link['href']) === 1);
                    @endphp
                    <ul class="wiki-page__section-links">
                        @foreach ($links as $link)
                            <li><a href="{{ $link['href'] }}"
                                @if (str_starts_with($link['href'], '/ir/adapters/') || $link['href'] === '/omsir-openlr2.example.json') data-turbo="false" @endif
                                @if ($link['href'] === '/omsir-openlr2.example.json') download="omsir.json" @endif
                            >{{ $link['label'] }}</a></li>
                        @endforeach
                    </ul>
                    @if ($references->isNotEmpty())
                        <details><summary>插件校验与许可</summary><ul>
                            @foreach ($references as $link)
                                <li><a href="{{ $link['href'] }}" data-turbo="false">{{ $link['label'] }}</a></li>
                            @endforeach
                        </ul></details>
                    @endif
                @endif
            @endforeach
        </div></div>
    </div></div>
@endsection
