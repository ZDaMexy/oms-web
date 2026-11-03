// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import * as React from 'react';
import { Details, LampBadge } from 'oms/components';
import { Judgements } from 'oms/judgements';
import { chartUrl, sourceNames } from 'oms/page';
import { PublicBest } from 'oms/types';

export default function PlayDetail({ item }: { item: PublicBest }) {
  const score = item.score;
  const name = item.chart.title ?? '曲名未提供';
  const received = item.activity?.order_at ?? score.received_at;
  const analysis = item.analysis;
  return <div className='play-detail play-detail--highlightable play-detail--oms'>
    <div className='play-detail__group play-detail__group--top'>
      <div className='play-detail__detail'>
        {item.chart.md5 == null
          ? <span className='play-detail__title'>{name}</span>
          : <a className='play-detail__title u-ellipsis-overflow' href={chartUrl(item.chart.md5, item.ruleset)}>{name}</a>}
        {item.chart.artist != null && <small className='play-detail__artist'> {item.chart.artist}</small>}
        <div className='play-detail__beatmap-and-time'>
          <span className='play-detail__beatmap'>{item.chart.difficulty ?? '难度名未提供'} · {sourceNames[score.source] ?? score.source} · {score.record_kind === 'play' ? '游玩记录' : '最佳状态'}</span>
          <span className='play-detail__time'>{score.played_at == null
            ? <>接收 <time dateTime={received} className='js-localtime'>{received}</time></>
            : <>游玩 <time dateTime={score.played_at} className='js-localtime'>{score.played_at}</time></>}</span>
        </div>
      </div>
    </div>
    <div className='play-detail__group play-detail__group--bottom'>
      <div className='play-detail__score-detail'>
        <div className='play-detail__score-detail-top-right'>
          <div className='play-detail__accuracy-and-weighted-pp'>
            <span className='play-detail__accuracy'>{item.ruleset === 'bms'
              ? <>EX {score.ex_score == null ? '未知' : score.ex_score.toLocaleString('zh-CN')} / {score.max_ex_score == null ? '未知' : score.max_ex_score.toLocaleString('zh-CN')}</>
              : <>分数 {score.total_score == null ? '未知' : score.total_score.toLocaleString('zh-CN')}</>}</span>
          </div>
          <div>{item.ruleset === 'bms' ? <LampBadge lamp={score.lamp} /> : <>{score.accuracy != null && <span>{(score.accuracy * 100).toFixed(2)}% · </span>}{score.passed == null ? '未提供通关状态' : score.passed ? '已通关' : '未通关'}</>}</div>
        </div>
      </div>
    </div>
    <div className='play-detail__analysis'>
      <dl className='play-detail__facts'>
        {analysis.ex_rate != null && <div><dt>{analysis.grade} · EX 率</dt><dd>{(analysis.ex_rate * 100).toFixed(2)}%</dd></div>}
        <div><dt>最大连击</dt><dd>{score.max_combo?.toLocaleString('zh-CN') ?? '—'}</dd></div>
        <div><dt>{item.ruleset === 'bms' ? 'PG / GR' : 'MAX / 300'}</dt><dd>{analysis.perfect_great_ratio?.toFixed(2) ?? (score.statistics[item.ruleset === 'bms' ? 'gr' : 'great'] === 0 ? '无 ' + (item.ruleset === 'bms' ? 'GR' : '300') : '—')}</dd></div>
        {analysis.next_grade != null && <div><dt>距 {analysis.next_grade.grade}</dt><dd>+{analysis.next_grade.needed.toLocaleString('zh-CN')} EX</dd></div>}
      </dl>
      <Judgements statistics={score.statistics} mania={item.ruleset === 'mania'} />
      <a href={chartUrl(item.chart.md5, item.ruleset, item.ruleset === 'bms'
        ? { sources: score.source, mode: item.board_scope.mode, ...(item.board_scope.condition == null ? {} : { condition: item.board_scope.condition }) }
        : { group: item.board_scope.group! })}>查看这张谱的榜单</a>
    </div>
    <details className='play-detail__record'>
      <summary>条件与成绩详情</summary>
      <p>{item.condition_scope.label}</p>
      {item.best_lamps.length > 0 && <div className='play-detail__best-lamps'><span>独立最佳灯</span>{item.best_lamps.map(lamp =>
        <span key={lamp.family}><LampBadge lamp={lamp} /> <small>{sourceNames[lamp.source ?? score.source] ?? lamp.source ?? score.source} · {lamp.rule_label}</small></span>)}</div>}
      <Details value={item} label='原始记录' />
    </details>
  </div>;
}
