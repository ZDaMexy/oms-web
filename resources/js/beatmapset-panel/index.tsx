// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import { CatalogSet, IrChart } from 'oms/types';
import { chartUrl, sourceNames } from 'oms/page';
import * as React from 'react';
import { formatBytes } from 'utils/html';
import { urlPresence } from 'utils/css';

export default function BeatmapsetPanel({ beatmapset }: { beatmapset: CatalogSet }) {
  const [expanded, setExpanded] = React.useState(false);
  const mode = beatmapset.kind === 'mania-set' ? 'mania' : 'bms';
  const cover = <div className='beatmapset-cover beatmapset-cover--full' style={{ backgroundImage: urlPresence(beatmapset.cover_url) }} />;
  return <div className={'beatmapset-panel beatmapset-panel--size-normal' + (expanded ? ' beatmapset-panel--mobile-expanded' : '')}>
    <a className='beatmapset-panel__cover-container' href={beatmapset.detail_url}>
      <div className='beatmapset-panel__cover-col beatmapset-panel__cover-col--play'>{cover}</div>
      <div className='beatmapset-panel__cover-col beatmapset-panel__cover-col--info'>{cover}</div>
    </a>
    <div className='beatmapset-panel__content'>
      <div className='beatmapset-panel__play-container' />
      <div className='beatmapset-panel__info'>
        <div className='beatmapset-panel__info-row beatmapset-panel__info-row--title'><a className='beatmapset-panel__main-link u-ellipsis-overflow' href={beatmapset.detail_url}>{beatmapset.title}</a></div>
        <div className='beatmapset-panel__info-row beatmapset-panel__info-row--artist'><a className='beatmapset-panel__main-link u-ellipsis-overflow' href={beatmapset.detail_url}>{beatmapset.artist ?? '艺术家未知'}</a></div>
        {beatmapset.creator != null && <div className='beatmapset-panel__info-row beatmapset-panel__info-row--mapper'><div className='u-ellipsis-overflow'>{beatmapset.creator}</div></div>}
        <div className='beatmapset-panel__info-row beatmapset-panel__info-row--stats'>
          <div className='beatmapset-panel__stats-item'>{sourceNames[beatmapset.source] ?? beatmapset.source}</div>
          {beatmapset.package?.size_bytes != null && <div className='beatmapset-panel__stats-item'>{formatBytes(beatmapset.package.size_bytes)}</div>}
        </div>
        <div className='beatmapset-panel__info-row beatmapset-panel__info-row--extra'>{beatmapset.charts.map((chart, index) =>
          <a className='beatmapset-panel__extra-item' key={chart.md5 ?? chart.bid ?? index} href={chart.md5 != null ? chartUrl(chart.md5, mode, beatmapset.sid == null ? {} : {sid: String(beatmapset.sid)}) : beatmapset.detail_url}>
            {chart.difficulty ?? '难度名未知'} · {chart.keymode ?? '键型未知'}{chart.star_rating == null ? '' : ` · ${chart.star_rating.toFixed(2)}★（镜像）`}
          </a>)}</div>
      </div>
      <div className='beatmapset-panel__menu-container'><div className='beatmapset-panel__menu'>
        <a className='beatmapset-panel__menu-item' href={beatmapset.detail_url} title='查看谱面'><span className='fas fa-info-circle' /></a>
        {beatmapset.source_url != null && <a className='beatmapset-panel__menu-item' href={beatmapset.source_url} rel='noopener noreferrer' target='_blank' title='来源页面'><span className='fas fa-external-link-alt' /></a>}
      </div></div>
    </div>
    <button type='button' className='beatmapset-panel__mobile-expand' onClick={() => setExpanded(!expanded)} aria-expanded={expanded} aria-label={expanded ? '收起谱面信息' : '展开谱面信息'}><span className={expanded ? 'fas fa-angle-up' : 'fas fa-angle-down'} /></button>
  </div>;
}

export function IrChartPanel({detail}:{detail:IrChart}) {
  const [expanded,setExpanded] = React.useState(false);
  const href = '/ir?' + new URLSearchParams({md5:detail.chart.md5});
  const cover = <div className='beatmapset-cover beatmapset-cover--full'/>;
  return <div className={'beatmapset-panel beatmapset-panel--size-normal'+(expanded?' beatmapset-panel--mobile-expanded':'')}>
    <a className='beatmapset-panel__cover-container' href={href}>
      <div className='beatmapset-panel__cover-col beatmapset-panel__cover-col--play'>{cover}</div>
      <div className='beatmapset-panel__cover-col beatmapset-panel__cover-col--info'>{cover}</div>
    </a>
    <div className='beatmapset-panel__content'>
      <div className='beatmapset-panel__play-container'/>
      <div className='beatmapset-panel__info'>
        <div className='beatmapset-panel__info-row beatmapset-panel__info-row--title'><a className='beatmapset-panel__main-link u-ellipsis-overflow' href={href}>{detail.chart.title??'标题未知'}</a></div>
        <div className='beatmapset-panel__info-row beatmapset-panel__info-row--artist'><a className='beatmapset-panel__main-link u-ellipsis-overflow' href={href}>{detail.chart.artist??'艺术家未知'}</a></div>
        <div className='beatmapset-panel__info-row beatmapset-panel__info-row--mapper'><div className='u-ellipsis-overflow'>{detail.chart.difficulty??'难度名未知'}</div></div>
        <div className='beatmapset-panel__info-row beatmapset-panel__info-row--stats'>
          <div className='beatmapset-panel__stats-item'>{detail.ruleset==='bms'?'BMS':'mania'}</div>
          {detail.available_sources.map(source=><div className='beatmapset-panel__stats-item' key={source}>{sourceNames[source]??source}</div>)}
        </div>
        <div className='beatmapset-panel__info-row beatmapset-panel__info-row--extra'><a className='beatmapset-panel__extra-item' href={href}>MD5 {detail.chart.md5}</a></div>
      </div>
      <div className='beatmapset-panel__menu-container'><div className='beatmapset-panel__menu'><a className='beatmapset-panel__menu-item' href={href} title='查看成绩榜'><span className='fas fa-list-ol'/></a></div></div>
    </div>
    <button type='button' className='beatmapset-panel__mobile-expand' onClick={()=>setExpanded(!expanded)} aria-expanded={expanded} aria-label={expanded?'收起谱面信息':'展开谱面信息'}><span className={expanded?'fas fa-angle-up':'fas fa-angle-down'}/></button>
  </div>;
}
