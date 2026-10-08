// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import { sourceNames } from 'oms/page';
import { BmsDetail, IrChart, ManiaDetail } from 'oms/types';
import { formatBytes } from 'utils/html';
import * as React from 'react';
export default function Info({detail}:{detail:BmsDetail|ManiaDetail}) {
  return <div className='beatmapset-info u-fancy-scrollbar'>
    <div className='beatmapset-info__box'><div className='beatmapset-info__scrollable'><div className='beatmapset-info__row'>
      <h3 className='beatmapset-info__header'>谱包</h3>
      {detail.ruleset==='bms'?detail.candidates.map(candidate=><p key={candidate.source}>{candidate.package.name} · {candidate.package.size_bytes==null?'大小未知':formatBytes(candidate.package.size_bytes)}</p>):
        <p>{detail.mixed_modes?'这个谱包包含多种玩法，OMS 只导入其中的 mania 谱面。':'mania 谱包。'}</p>}
    </div></div></div>
    <div className='beatmapset-info__box'><div className='beatmapset-info__scrollable'><div className='beatmapset-info__row'><h3 className='beatmapset-info__header'>来源</h3>
      {detail.ruleset==='bms'?detail.candidates.map(candidate=>candidate.source_url!=null&&<p key={candidate.source}><a className='beatmapset-info__link' href={candidate.source_url} target='_blank' rel='noopener noreferrer'>{sourceNames[candidate.source]??candidate.source}</a></p>):
        detail.set.source_url!=null&&<a className='beatmapset-info__link' href={detail.set.source_url} target='_blank' rel='noopener noreferrer'>Sayobot</a>}
      <p>谱包由原站提供。下载后在 OMS 中添加谱库。</p>
    </div></div></div>
  </div>;
}

export function IrInfo({detail}:{detail:IrChart}) {
  return <div className='beatmapset-info u-fancy-scrollbar'>
    <div className='beatmapset-info__box'><div className='beatmapset-info__scrollable'><div className='beatmapset-info__row'>
      <h3 className='beatmapset-info__header'>谱面标识</h3>
      <p className='beatmapset-info__link'>MD5 {detail.chart.md5}</p>
      <p className='beatmapset-info__link'>SHA256 {detail.chart.sha256??'未知'}</p>
      <p>{detail.content_identity==='md5-only'?'按原 MD5 关联':detail.content_identity==='sha256-reported'?'来源提供 SHA256':detail.content_identity}</p>
    </div></div></div>
    <div className='beatmapset-info__box'><div className='beatmapset-info__scrollable'><div className='beatmapset-info__row'>
      <h3 className='beatmapset-info__header'>成绩来源</h3>
      {detail.available_sources.length===0?<p>暂无公开成绩来源。</p>:detail.available_sources.map(source=><p key={source}>{sourceNames[source]??source}</p>)}
      {detail.archive_suspended&&<p>LR2IR 历史目录标记为暂停。</p>}
    </div></div></div>
    <div className='beatmapset-info__box'><div className='beatmapset-info__scrollable'><div className='beatmapset-info__row'>
      <h3 className='beatmapset-info__header'>OMS 计分条件</h3>
      {detail.groups.length===0?<p>暂无公开 OMS 条件。</p>:detail.groups.map(group=><p key={group.id}>{group.label}</p>)}
    </div></div></div>
  </div>;
}
