{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
<article class="forum-post" id="{{ $kind }}-{{ $entry['id'] }}">
    <div class="forum-post-info"><a class="forum-post-info__row forum-post-info__row--username" href="{{ route('users.show', $entry['author']['id']) }}">{{ $entry['author']['username'] }}</a></div>
    <div class="forum-post__body">
        <div class="forum-post__content forum-post__content--header"><div class="forum-post__header-content"><a class="forum-post__user" href="{{ route('users.show', $entry['author']['id']) }}">{{ $entry['author']['username'] }}</a>{!! timeago(new DateTimeImmutable($entry['created_at'])) !!}@if ($entry['edited_at'])<span>已编辑</span>@endif</div></div>
        <div class="forum-post__content forum-post__content--main"><div class="forum-post-content" data-oms-plain-text style="white-space: pre-wrap; overflow-wrap: anywhere">{{ $entry['deleted'] ? '此内容已由作者删除。' : $entry['body'] }}</div></div>
        <div class="forum-post__content forum-post__content--footer" data-oms-owner-id="{{ $entry['author']['id'] }}" hidden>
            @if (!$entry['deleted'] && !($post['deleted'] ?? false))
                <details><summary>修改</summary>
                    @include('forum.topics._post_edit_form', ['kind' => $kind.'-edit', 'id' => $entry['id'], 'owner' => $entry['author']['id'], 'content' => $entry['body'], 'postTitle' => $entry['title'] ?? '', 'category' => $entry['category'] ?? 'discussion'])
                </details>
            @endif
            <button class="btn-osu-big btn-osu-big--forum-secondary" type="button" data-oms-delete data-kind="{{ $kind }}" data-id="{{ $entry['id'] }}" data-owner-id="{{ $entry['author']['id'] }}"><span class="btn-osu-big__content">删除</span></button>
            <p data-oms-message role="status"></p>
        </div>
    </div>
</article>
