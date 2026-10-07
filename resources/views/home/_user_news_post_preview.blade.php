{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@php
    $publishedAt = Carbon\Carbon::parse($post['published_at']);
@endphp
<div class="news-post-preview{{ $collapsed ? ' news-post-preview--collapsed' : '' }}">
    @if (!empty($post['image']))
        <a class="news-post-preview__image" href="{{ route('news.show', $post['slug']) }}" style="--bg: url('{{ $post['image'] }}')"></a>
    @endif
    <div class="news-post-preview__body">
        <div class="news-post-preview__post-date">
            <div class="news-post-preview__date">{{ $publishedAt->format('d') }}</div>
            <div class="news-post-preview__month-year">{{ $publishedAt->format('Y.m') }}</div>
        </div>
        <div class="news-post-preview__post-right">
            <a href="{{ route('news.show', $post['slug']) }}" class="news-post-preview__post-title">{{ $post['title'] }}</a>
            <div class="news-post-preview__post-content"><p>{{ $post['excerpt'] }}</p></div>
        </div>
    </div>
</div>