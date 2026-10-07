// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import { Chart } from 'oms/types';
import * as React from 'react';
export default function Stats({chart}:{chart:Chart|null}) {
  const values:[string,string|number|null|undefined][]=[['键型',chart?.keymode],['BPM',chart?.bpm],['物量',chart?.notes],['长度（秒）',chart?.length_seconds]];
  return <div className='beatmapset-stats'><div className='beatmapset-stats__row beatmapset-stats__row--advanced'><table className='beatmap-stats-table'><tbody>
    {values.map(([label,value])=><tr className='beatmap-stats-table__row' key={label}><td className='beatmap-stats-table__label'>{label}</td><td className='beatmap-stats-table__value'>{value??'未知'}</td></tr>)}
  </tbody></table></div></div>;
}
