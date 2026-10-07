{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
<form class="bbcode-editor bbcode-editor--create" data-state="write" data-oms-community-form data-kind="{{ $kind }}" data-id="{{ $id }}" data-owner-id="{{ $owner }}" method="POST" action="/api/ir/v1/community/posts">
    <div class="bbcode-editor__content">
    @if ($kind === 'post' || $kind === 'post-edit')
        <input class="bbcode-editor__input-title" aria-label="标题" placeholder="标题" name="title" value="{{ $postTitle }}" maxlength="100" required>
        <label class="account-edit-entry"><span class="account-edit-entry__label">分类</span><select class="account-edit-entry__input" name="category">
            @foreach (['discussion' => '讨论', 'help' => '求助', 'showcase' => '分享', 'development' => '开发记录'] as $key => $label)<option value="{{ $key }}" @selected($category === $key)>{{ $label }}</option>@endforeach
        </select></label>
    @endif
    <textarea class="bbcode-editor__body" aria-label="正文" placeholder="正文（纯文本）" name="body" rows="8" maxlength="{{ str_starts_with($kind, 'reply') ? 6000 : 12000 }}" required>{{ $content }}</textarea>
    <p data-oms-message role="status"></p>
    <div class="bbcode-editor__buttons-bar"><div class="bbcode-editor__buttons bbcode-editor__buttons--actions">
        <div class="bbcode-editor__button"><button type="button" class="btn-osu-big btn-osu-big--forum-secondary" data-oms-rebind-draft hidden><span class="btn-osu-big__content">用当前账号发布</span></button></div>
        <div class="bbcode-editor__button"><button class="btn-osu-big btn-osu-big--forum-primary" type="submit"><span class="btn-osu-big__content">{{ str_ends_with($kind, '-edit') ? '保存修改' : '发布' }}</span></button></div>
    </div></div>
    </div>
</form>
