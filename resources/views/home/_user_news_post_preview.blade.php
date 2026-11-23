{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@php
    $publishedAt = Carbon\Carbon::parse($post['published_at']);
@endphp
<a class="news-post-preview" href="{{ route('news.show', $post['slug']) }}">
    @if (!empty($post['image']))
        <span class="news-post-preview__image" style="--bg: url('{{ $post['image'] }}')"></span>
    @endif
    <div class="news-post-preview__body">
        <time class="news-post-preview__post-date" datetime="{{ $post['published_at'] }}">{{ $publishedAt->format('Y.m.d') }}</time>
        <div class="news-post-preview__post-right">
            <h3 class="news-post-preview__post-title">{{ $post['title'] }}</h3>
            <p class="news-post-preview__post-content">{{ $post['excerpt'] }}</p>
        </div>
        <span class="news-post-preview__arrow" aria-hidden="true">→</span>
    </div>
</a>
