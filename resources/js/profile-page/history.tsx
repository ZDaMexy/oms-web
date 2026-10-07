// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import { Details, Paginator, Status } from 'oms/components';
import { chartUrl } from 'oms/page';
import * as React from 'react';
import { Controller } from './controller';

const lamps = ['NO PLAY','FAILED','ASSIST EASY','EASY CLEAR','CLEAR','HARD CLEAR','EX HARD','HAZARD CLEAR','FULL COMBO','PERFECT'];

export default function History({controller}:{controller:Controller}) {
  const {history,update} = controller;
  return <section className='page-extra' id='history'>
    <h2 className='title title--page-extra'>我的完整记录</h2>
    <p className='beatmapset-scoreboard__notice'>OMS 已上传的 BMS / mania 游玩，每局保留原 UUID，也包含不进入公开榜的记录。按接收顺序显示全部游玩，不受公开来源、键型和条件筛选影响。</p>
    <Status error={history.error} ready={history.data!=null}/>
    {history.data!=null && <>
      <p>{history.data.total.toLocaleString('zh-CN')} 局 OMS 游玩</p>
      <div className='play-detail-list'>{history.data.items.map(score=><div className='play-detail play-detail--highlightable' key={score.submission_id}>
        <div className='play-detail__group play-detail__group--top'><div className='play-detail__detail'>
          <a className='play-detail__title u-ellipsis-overflow' href={chartUrl(score.chart.md5,score.ruleset,{sha256:score.chart.sha256})}>{score.chart.title}</a>
          <small className='play-detail__artist'> {score.chart.artist}</small>
          <div className='play-detail__beatmap-and-time'>
            <span className='play-detail__beatmap'>{score.chart.difficulty} · {score.ruleset==='bms'?'BMS':'mania'} · {score.keymode}</span>
            <span className='play-detail__time'>游玩 <time dateTime={score.played_at} className='js-localtime'>{score.played_at}</time></span>
          </div>
        </div></div>
        <div className='play-detail__group play-detail__group--bottom'>
          <div className='play-detail__score-detail'><div className='play-detail__score-detail-top-right'>
            <div className='play-detail__accuracy-and-weighted-pp'><span className='play-detail__accuracy'>{score.ruleset==='bms'
              ? <>EX {score.ex_score==null?'未知':score.ex_score.toLocaleString('zh-CN')} / {score.max_ex_score==null?'未知':score.max_ex_score.toLocaleString('zh-CN')}</>
              : <>分数 {score.total_score.toLocaleString('zh-CN')}</>}</span></div>
            <div>{score.passed?'通关':'未通关'}{score.ruleset_data==null?'':` · ${score.ruleset_data.version===7?lamps[score.ruleset_data.clear_lamp]??'未知灯':'未知灯'}（原灯 ${score.ruleset_data.clear_lamp}）`}</div>
          </div></div>
          <div className='play-detail__mods-pp'><div className='play-detail__mods'>{score.group_label}</div></div>
          <div className='play-detail__more'><Details value={score}/></div>
        </div>
        <div className='play-detail__beatmap-and-time'>
          <span>UUID {score.submission_id}</span>
          <span className='play-detail__time'>接收 <time dateTime={score.received_at} className='js-localtime'>{score.received_at}</time></span>
          <span>{score.public_board?'公开榜条件':'不进入公开榜'}</span>
        </div>
      </div>)}</div>
      {history.data.items.length===0 && <p>{history.data.total===0?'尚未上传 OMS 游玩记录。':'本页没有记录，请返回第一页。'}</p>}
      <Paginator {...history.data} onPage={page=>update({page:String(page)},false)}/>
    </>}
  </section>;
}
