{{--
    Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
    See the LICENCE file in the repository root for full licence text.
--}}
@extends('master')
@php
    $context = $omsData['context'];
    $ranking = $omsData['ranking'];
    $scopes = $omsData['scopes'];
    $metrics = $context['ruleset'] === 'mania' ? ['best_total_score' => '最佳总分合计', 'coverage' => '有成绩的谱面数'] : ['coverage' => '有成绩的谱面数', 'cleared_charts' => '同条件通关数'];
    $sources = $context['ruleset'] === 'mania' ? ['oms' => 'OMS'] : ['oms' => 'OMS', 'beatoraja' => 'beatoraja', 'lr2oraja' => 'LR2oraja', 'lr2oraja_ed' => 'Endless Dream', 'openlr2' => 'OpenLR2'];
    $keymodes = $context['ruleset'] === 'mania' ? array_combine(array_map(fn($n) => 'mania_'.$n.'k', range(1, 18)), array_map(fn($n) => $n.'K', range(1, 18))) : ['bms_5k' => 'BMS 5K', 'bms_7k' => 'BMS 7K', 'bms_9k' => 'BMS 9K', 'pms_9k' => 'PMS 9K', 'bms_14k' => 'BMS 14K'];
    $formatValue = fn($value) => preg_replace('/\B(?=(\d{3})+(?!\d))/', ',', (string) $value);
@endphp
@section('content')
    @include('layout._page_header_v4', ['params' => ['theme' => 'rankings', 'links' => [
        ['active' => true, 'title' => '玩家榜', 'url' => route('rankings')],
        ['title' => '谱面榜', 'url' => route('ir')],
    ]]])
    <div class="osu-page osu-page--ranking-info">
        <div class="sort sort--ranking-header"><div class="sort__items">
            @foreach (['bms' => 'BMS', 'mania' => 'mania'] as $ruleset => $label)
                <a class="sort__item sort__item--button {{ $context['ruleset'] === $ruleset ? 'sort__item--active' : '' }}" href="{{ route('rankings', ['ruleset' => $ruleset]) }}">{{ $label }}</a>
            @endforeach
        </div></div>
        <form action="{{ route('rankings') }}" class="grid-items grid-items--ranking-filter grid-items--ranking-filter-oms" method="GET">
            <input type="hidden" name="ruleset" value="{{ $context['ruleset'] }}">
            <label class="ranking-filter"><span class="ranking-filter__title">键型</span><select class="form-control" name="keymode">
                @foreach ($keymodes as $key => $label)<option value="{{ $key }}" @selected($context['keymode'] === $key)>{{ $label }}</option>@endforeach
            </select></label>
            <label class="ranking-filter"><span class="ranking-filter__title">来源</span><select class="form-control" name="source">
                @foreach ($sources as $key => $label)<option value="{{ $key }}" @selected($context['source'] === $key)>{{ $label }}</option>@endforeach
            </select></label>
            <label class="ranking-filter"><span class="ranking-filter__title">排名依据</span><select class="form-control" name="metric">
                @foreach ($metrics as $key => $label)<option value="{{ $key }}" @selected($context['metric'] === $key)>{{ $label }}</option>@endforeach
            </select></label>
            <label class="ranking-filter"><span class="ranking-filter__title">条件</span><select class="form-control" name="condition">
                <option value="">选择条件</option>
                @foreach ($scopes['items'] as $scope)<option value="{{ $scope['id'] }}" @selected(($context['condition'] ?? '') === $scope['id'])>{{ $scope['label'] }}</option>@endforeach
            </select></label>
            <button class="btn-osu-big" type="submit"><span class="btn-osu-big__content">查看</span></button>
        </form>
        @if ($scopes['page'] * $scopes['limit'] < $scopes['total'])
            <a href="{{ route('rankings', [...$context, 'scope_page' => $scopes['page'] + 1]) }}">下一页条件</a>
        @endif
    </div>
    <div class="osu-page osu-page--generic oms-player-ranking">
        <div class="beatmapset-scoreboard__scope"><h2>{{ $metrics[$context['metric']] }}</h2>@if($ranking !== null)<span>{{ number_format($ranking['total']) }} 位玩家</span>@endif</div>
        <p class="beatmapset-scoreboard__description">{{ $sources[$context['source']] }} · {{ $keymodes[$context['keymode']] }} · 只统计当前范围内的公开成绩。<a href="/help#scores">榜单说明</a></p>
        @if ($ranking === null)
            <p>先在上方选择比较条件，再查看通关排名。</p>
        @else
            @isset($ranking['scope']['condition_scope'])<p class="beatmapset-scoreboard__description">{{ $ranking['scope']['condition_scope']['label'] }}</p>@endisset
            @if (($ranking['items'][0]['rank'] ?? null) === 1)
                @php($top = $ranking['items'][0])
                <div class="beatmapset-scoreboard__highlights"><div class="beatmapset-scoreboard__highlight">
                    <div class="beatmapset-scoreboard__highlight-player"><small>当前榜首</small><span class="beatmapset-scoreboard__highlight-rank">#1</span><strong><a href="{{ route('users.show', ['user' => $top['user']['id'], 'ruleset' => $context['ruleset'], 'keymode' => $context['keymode'], 'sources' => $context['source']]) }}">{{ $top['user']['username'] }}</a></strong></div>
                    <div class="beatmapset-scoreboard__highlight-score"><small>{{ $metrics[$context['metric']] }}</small><strong class="beatmap-scoreboard-table__score">{{ $formatValue($top['value']) }}</strong><small>{{ number_format($top['public_chart_count']) }} 张公开谱面</small></div>
                </div></div>
            @endif
            <div class="ranking-page oms-player-ranking__table" role="region" aria-label="玩家排名" tabindex="0"><table class="ranking-page-table ranking-page-table--oms"><thead><tr>
                <th scope="col" class="ranking-page-table__heading">排名</th><th scope="col" class="ranking-page-table__heading ranking-page-table__heading--main">玩家</th>
                <th scope="col" class="ranking-page-table__heading">{{ $metrics[$context['metric']] }}</th><th scope="col" class="ranking-page-table__heading">公开谱面</th>
            </tr></thead><tbody>
                @foreach ($ranking['items'] as $item)<tr class="ranking-page-table__row">
                    <td class="ranking-page-table__column">#{{ $item['rank'] }}</td>
                    <td class="ranking-page-table__column ranking-page-table__column--main"><a class="ranking-page-table__user-link" href="{{ route('users.show', ['user' => $item['user']['id'], 'ruleset' => $context['ruleset'], 'keymode' => $context['keymode'], 'sources' => $context['source']]) }}">{{ $item['user']['username'] }}</a></td>
                    <td class="ranking-page-table__column"><strong>{{ $formatValue($item['value']) }}</strong></td><td class="ranking-page-table__column">{{ number_format($item['public_chart_count']) }}</td>
                </tr>@endforeach
            </tbody></table></div>
            @if (count($ranking['items']) === 0)<p>此范围暂无公开成绩。</p>@endif
            @include('oms._pagination', ['pagination' => $ranking])
            <div class="beatmapset-scoreboard__highlights" data-oms-ranking-me data-metric-label="{{ $metrics[$context['metric']] }}"></div>
        @endif
    </div>
    @include('oms._page_data')
@endsection
