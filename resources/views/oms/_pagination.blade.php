@php
    $query = request()->query();
    $lastPage = max(1, (int) ceil($pagination['total'] / $pagination['limit']));
@endphp
<nav class="pagination-v2" aria-label="分页">
    @if ($pagination['page'] > 1)<a class="pagination-v2__link" href="{{ request()->url().'?'.http_build_query([...$query, 'page' => $pagination['page'] - 1]) }}">上一页</a>@endif
    <span class="pagination-v2__link pagination-v2__link--active">{{ $pagination['page'] }} / {{ $lastPage }}</span>
    @if ($pagination['page'] < $lastPage)<a class="pagination-v2__link" href="{{ request()->url().'?'.http_build_query([...$query, 'page' => $pagination['page'] + 1]) }}">下一页</a>@endif
</nav>