@extends('master')
@section('content')
    @include('layout._page_header_v4', ['params' => ['theme' => 'rankings', 'links' => [
        ['active' => true, 'title' => '查找玩家', 'url' => route('users.index')],
        ['title' => '玩家榜', 'url' => route('rankings')],
    ]]])
    <div class="osu-page osu-page--generic">
        <form action="{{ route('users.index') }}" method="GET" class="grid-items grid-items--ranking-filter">
            <label class="ranking-filter"><span class="ranking-filter__title">OMS 用户名</span>
                <input class="form-control" type="search" name="q" value="{{ $omsData['context']['q'] }}" maxlength="24" required placeholder="输入完整或部分用户名">
            </label>
            <button class="btn-osu-big" type="submit"><span class="btn-osu-big__content">查找</span></button>
        </form>
        @if ($omsData['players'] !== null)
            <p>{{ number_format($omsData['players']['total']) }} 位玩家</p>
            <div class="play-detail-list">
                @foreach ($omsData['players']['items'] as $player)
                    <div class="play-detail play-detail--oms"><a class="play-detail__title" href="{{ route('users.show', ['user' => (string) $player['id']]) }}">{{ $player['username'] }}</a></div>
                @endforeach
            </div>
            @if ($omsData['players']['total'] === 0)<p>没有找到匹配的公开玩家。</p>@endif
            @include('oms._pagination', ['pagination' => $omsData['players']])
        @endif
    </div>
@endsection
