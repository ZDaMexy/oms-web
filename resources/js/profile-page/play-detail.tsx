// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import * as React from 'react';
import { Details } from 'oms/components';
import { chartUrl, sourceNames } from 'oms/page';
import { PublicBest } from 'oms/types';

export default function PlayDetail({ item }: { item: PublicBest }) {
  const score = item.score;
  const name = item.chart.title ?? '曲名未提供';
  const received = item.activity?.order_at ?? score.received_at;
  return <div className='play-detail play-detail--highlightable'>
    <div className='play-detail__group play-detail__group--top'>
      <div className='play-detail__detail'>
        {item.chart.md5 == null
          ? <span className='play-detail__title'>{name}</span>
          : <a className='play-detail__title u-ellipsis-overflow' href={chartUrl(item.chart.md5, item.ruleset)}>{name}</a>}
        {item.chart.artist != null && <small className='play-detail__artist'> {item.chart.artist}</small>}
        <div className='play-detail__beatmap-and-time'>
          <span className='play-detail__beatmap'>{item.chart.difficulty ?? '难度名未提供'} · {sourceNames[score.source] ?? score.source}</span>
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
          <div>{score.lamp?.label ?? (score.passed == null ? '原灯未提供' : score.passed ? '通关' : '未通关')}</div>
        </div>
      </div>
      <div className='play-detail__mods-pp'>
        <div className='play-detail__mods'>{item.best_lamps.map(lamp =>
          <span key={lamp.family} title={lamp.rule_label}>{lamp.label} · {sourceNames[lamp.source ?? score.source] ?? lamp.source ?? score.source} </span>)}</div>
      </div>
      <div className='play-detail__more'><Details value={item} /></div>
    </div>
  </div>;
}
