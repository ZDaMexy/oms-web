// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import * as React from 'react';
import { Performance } from 'oms/types';

type Lane = Performance['lanes'][number];
export default function Stats({ metrics, rankings }: Pick<Lane, 'metrics' | 'rankings'>) {
  const entries: [string, React.ReactNode][] = [
    ['公开谱面数', metrics.public_chart_count.toLocaleString('zh-CN')],
    ['公开最佳数', metrics.public_best_count.toLocaleString('zh-CN')],
  ];
  if (metrics.cleared_chart_count != null) entries.push(['通关谱面数', metrics.cleared_chart_count.toLocaleString('zh-CN')]);
  if (metrics.best_total_score != null) entries.push(['最佳总分合计', BigInt(metrics.best_total_score).toLocaleString('zh-CN')]);
  for (const rank of rankings) entries.push([rank.metric === 'best_total_score' ? '同条件总分名次' : '同条件通关名次',
    rank.rank == null ? '暂无名次' : `#${rank.rank.toLocaleString('zh-CN')} / ${rank.total_players.toLocaleString('zh-CN')}`]);
  return <div className='profile-stats'>{entries.map(([key, value]) =>
    <dl key={key} className='profile-stats__entry'><dt className='profile-stats__key'>{key}</dt><dd className='profile-stats__value'>{value}</dd></dl>)}</div>;
}
