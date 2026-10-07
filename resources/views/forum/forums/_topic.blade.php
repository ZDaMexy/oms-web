{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
<li class="forum-topic-entry clickable-row" data-topic-id="{{ $post['id'] }}">
    <div class="forum-item-stripe"><div class="forum-item-stripe__arrow"></div></div>
    <div class="forum-topic-entry__col forum-topic-entry__col--icon">
        <a class="forum-topic-entry__icon" href="{{ route('forum.topics.show', $post['id']) }}"><i class="far fa-comment-alt"></i></a>
    </div>
    <div class="forum-topic-entry__col forum-topic-entry__col--main">
        <div class="forum-topic-entry__content forum-topic-entry__content--left">
            <a class="clickable-row-link forum-topic-entry__title" href="{{ route('forum.topics.show', $post['id']) }}">{{ $post['title'] }}</a>
            <div><span class="forum-topic-entry__detail">{{ $categories[$post['category']] }}</span><span class="forum-topic-entry__detail"><a href="{{ route('users.show', $post['author']['id']) }}">{{ $post['author']['username'] }}</a></span></div>
        </div>
        <div class="forum-topic-entry__content forum-topic-entry__content--counts hidden-xs"><strong class="forum-topic-entry__count">{{ $post['reply_count'] }}</strong> 回复</div>
        <div class="forum-topic-entry__content forum-topic-entry__content--right">{!! timeago(new DateTimeImmutable($post['updated_at'])) !!}</div>
    </div>
</li>
