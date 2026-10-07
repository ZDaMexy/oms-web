// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import { Details } from 'oms/components';
import { sourceNames } from 'oms/page';
import { Board } from 'oms/types';
import * as React from 'react';
export interface ManiaRow {rank:number;user:{id:number;username:string};score:{id:number;total_score:number;accuracy:number;passed:boolean;played_at:string;received_at:string;[key:string]:unknown}}
const bn='beatmap-scoreboard-table';
export default function Table({board,mania}:{board?:Board;mania?:ManiaRow[]}) {
  return <div className={bn}><table className={bn+'__table'}><thead><tr>
    <th className={bn+'__header '+bn+'__header--rank'}>排名</th><th className={bn+'__header '+bn+'__header--score'}>{board?'原 EX':'总分'}</th>
    <th className={bn+'__header '+bn+'__header--player'}>玩家</th><th className={bn+'__header'}>{board?'原灯／独立灯':'通过'}</th>
    <th className={bn+'__header'}>{board?'来源':'准确率'}</th><th className={bn+'__header '+bn+'__header--time'}>游玩时间</th><th className={bn+'__header'}>条件</th>
  </tr></thead><tbody className={bn+'__body'}>
    {board?.items.map(row=><tr className={bn+'__body-row '+bn+'__body-row--highlightable'} key={row.identity.namespace+':'+row.identity.id}>
      <td className={bn+'__cell '+bn+'__cell--rank'}>{row.rank}</td><td className={bn+'__cell '+bn+'__cell--score'}>{row.score.ex_score??'未知'} / {row.score.max_ex_score??'未知'}</td>
      <td className={bn+'__cell '+bn+'__cell--player'}>{row.identity.namespace==='oms'?<a href={'/users/'+row.identity.id}>{row.identity.username}</a>:row.identity.username}<small> · {row.identity.namespace}:{row.identity.id}</small></td>
      <td className={bn+'__cell'}>{row.score.lamp?.label??'未知'}{row.best_lamps.map(lamp=><div key={lamp.family} title={lamp.rule_label}>{lamp.label} · {sourceNames[lamp.source??'']??lamp.source}<small> · {lamp.record_id}</small></div>)}</td>
      <td className={bn+'__cell'}>{sourceNames[row.score.source]??row.score.source}<small> · {row.score.record_kind==='play'?'UUID 新局':row.score.record_kind==='best_state'?'最佳状态':'历史摘要'}</small></td>
      <td className={bn+'__cell '+bn+'__cell--time'}>{row.score.played_at==null?'未知':<time dateTime={row.score.played_at} className='js-localtime'>{row.score.played_at}</time>}</td>
      <td className={bn+'__cell'}><Details value={{...row.score,best_lamps:row.best_lamps,identity:row.identity}}/></td>
    </tr>)}
    {mania?.map(row=><tr className={bn+'__body-row '+bn+'__body-row--highlightable'} key={row.user.id}>
      <td className={bn+'__cell '+bn+'__cell--rank'}>{row.rank}</td><td className={bn+'__cell '+bn+'__cell--score'}>{row.score.total_score}</td>
      <td className={bn+'__cell '+bn+'__cell--player'}><a href={'/users/'+row.user.id}>{row.user.username}</a></td><td className={bn+'__cell'}>{row.score.passed?'通过':'未通过'}</td>
      <td className={bn+'__cell'}>{(row.score.accuracy*100).toFixed(2)}%</td><td className={bn+'__cell '+bn+'__cell--time'}><time dateTime={row.score.played_at} className='js-localtime'>{row.score.played_at}</time></td>
      <td className={bn+'__cell'}><Details value={row.score}/></td>
    </tr>)}
  </tbody></table></div>;
}
