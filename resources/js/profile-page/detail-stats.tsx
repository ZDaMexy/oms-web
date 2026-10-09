// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import * as React from 'react';
import { Details } from 'oms/components';
import { Performance } from 'oms/types';
import { sourceNames } from 'oms/page';
import Stats from './stats';

export default function DetailStats({ data }: { data: Performance }) {
  return <div className='profile-detail-stats profile-detail-stats--oms'>
    <div>
      <div className='profile-detail-stats__chart-numbers profile-detail-stats__chart-numbers--top'>
        <div className='profile-detail-stats__values'>
          <dl className='profile-stats__entry'><dt className='profile-stats__key'>有公开成绩的谱面</dt><dd className='profile-stats__value'>{data.totals.public_chart_count.toLocaleString('zh-CN')}</dd></dl>
          <dl className='profile-stats__entry'><dt className='profile-stats__key'>公开最佳</dt><dd className='profile-stats__value'>{data.totals.public_best_count.toLocaleString('zh-CN')}</dd></dl>
        </div>
      </div>
      <p>所选来源中的公开成绩</p>
    </div>
    <div className='profile-detail-stats__separator' />
    <div className='profile-detail-stats__lanes'>{data.lanes.length === 0 ? <p>这个范围还没有公开成绩。</p> : data.lanes.map(lane =>
      <div className='profile-detail-stats__lane' key={lane.condition_scope.id}>
        <h3>{sourceNames[lane.source] ?? lane.source}</h3><p>{lane.condition_scope.label}</p>
        <Stats metrics={lane.metrics} rankings={lane.rankings} />
        <Details value={lane.condition_scope} label='查看规则详情' />
      </div>)}</div>
  </div>;
}
