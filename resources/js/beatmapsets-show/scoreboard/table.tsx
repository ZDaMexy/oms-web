// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import { Details, LampBadge } from 'oms/components';
import { lr2irClientNames, sourceNames } from 'oms/page';
import { Board, BoardRow } from 'oms/types';
import * as React from 'react';

export interface ManiaRow {
  rank: number;
  user: { id: number; username: string };
  score: { id: number; total_score: number; accuracy: number; passed: boolean; played_at: string; received_at: string; [key: string]: unknown };
}

const bn = 'beatmap-scoreboard-table';
let tableId = 0;
const recordKinds: Record<string, string> = { play: '游玩记录', best_state: '最佳状态', archive_best: '历史摘要' };
const fields: Record<string, string> = {
  option_1: '原始选项 1', option_2: '原始选项 2', option_3: '原始选项 3', option_4: '原始选项 4', input: '输入设备',
  judge_algorithm: '判定算法', gauge_rules: '通关规则', total: 'TOTAL', long_note_mode: '长音符模式', branch_policy: '分支规则',
  assist: '辅助设置', frequency: '频率', played_at: '游玩时间', sha256: 'SHA256',
};

function Player({ row }: { row: BoardRow }) {
  return row.identity.namespace === 'oms'
    ? <a href={'/users/' + row.identity.id}>{row.identity.username}</a>
    : <span>{row.identity.username}</span>;
}

function ExScore({ row }: { row: BoardRow }) {
  return <span className={bn + '__score'}>
    <strong>{row.score.ex_score?.toLocaleString('zh-CN') ?? '—'}</strong>
    <small> / {row.score.max_ex_score?.toLocaleString('zh-CN') ?? '—'}</small>
  </span>;
}

function PlayedAt({ value }: { value: string | null }) {
  return value == null ? <span title='来源未提供游玩时间'>—</span> : <time dateTime={value} className='js-localtime'>{value}</time>;
}

function BmsDetails({ row }: { row: BoardRow }) {
  return <div className={bn + '__record-details'}>
    <dl className={bn + '__facts'}>
      <div><dt>玩家身份</dt><dd>{row.identity.namespace.toUpperCase()} #{row.identity.id}</dd></div>
      <div><dt>成绩来源</dt><dd>{sourceNames[row.score.source] ?? row.score.source}</dd></div>
      <div><dt>记录类型</dt><dd>{recordKinds[row.score.record_kind] ?? row.score.record_kind}</dd></div>
      {lr2irClientNames[row.score.source] != null && <div><dt>原客户端标记</dt><dd>{lr2irClientNames[row.score.source]}</dd></div>}
      <div><dt>游玩时间</dt><dd>{row.score.played_at == null ? '来源未提供' : <PlayedAt value={row.score.played_at} />}</dd></div>
      {row.score.received_at != null && <div><dt>接收时间</dt><dd><PlayedAt value={row.score.received_at} /></dd></div>}
      {Object.entries(row.score.conditions).map(([key, value]) => <div key={key}><dt>{fields[key] ?? key}</dt><dd>{value == null ? '未提供' : typeof value === 'object' ? JSON.stringify(value) : String(value)}</dd></div>)}
    </dl>
    {row.best_lamps.length > 0 && <div className={bn + '__best-lamps'}><span>独立最佳灯</span>{row.best_lamps.map(lamp => <span key={lamp.family}>
      <LampBadge lamp={lamp} /> <small>{sourceNames[lamp.source ?? ''] ?? lamp.source} · {lamp.rule_label}</small>
    </span>)}</div>}
    {row.score.unknown_fields.length > 0 && <p className={bn + '__missing'}>来源未提供：{row.score.unknown_fields.map(key => fields[key] ?? key).join('、')}</p>}
    <Details value={{ ...row.score, best_lamps: row.best_lamps, identity: row.identity }} label='原始记录' />
  </div>;
}

export function ScoreHighlights({ board, mania }: { board?: Board; mania?: ManiaRow[] }) {
  const top = board?.page === 1 && board.items[0]?.rank === 1 ? board.items[0] : null;
  const maniaTop = mania?.[0]?.rank === 1 ? mania[0] : null;
  const me = board?.me;
  if (top == null && maniaTop == null && me == null) return null;
  return <div className='beatmapset-scoreboard__highlights'>
    {top != null && <div className='beatmapset-scoreboard__highlight'>
      <div className='beatmapset-scoreboard__highlight-player'><small>当前榜首</small><span className='beatmapset-scoreboard__highlight-rank'>#1</span><strong title={top.identity.namespace.toUpperCase() + ' #' + top.identity.id}><Player row={top} /></strong></div>
      <div className='beatmapset-scoreboard__highlight-score'><small>EX / 满分</small><ExScore row={top} /><div><LampBadge lamp={top.score.lamp} /> <small>{sourceNames[top.score.source] ?? top.score.source}</small></div></div>
    </div>}
    {maniaTop != null && <div className='beatmapset-scoreboard__highlight'>
      <div className='beatmapset-scoreboard__highlight-player'><small>当前榜首</small><span className='beatmapset-scoreboard__highlight-rank'>#1</span><strong><a href={'/users/' + maniaTop.user.id}>{maniaTop.user.username}</a></strong></div>
      <div className='beatmapset-scoreboard__highlight-score'><small>总分</small><strong className={bn + '__score'}>{maniaTop.score.total_score.toLocaleString('zh-CN')}</strong><small>{(maniaTop.score.accuracy * 100).toFixed(2)}% · {maniaTop.score.passed ? '已通关' : '未通关'}</small></div>
    </div>}
    {me != null && <div className='beatmapset-scoreboard__highlight beatmapset-scoreboard__highlight--me'>
      <div className='beatmapset-scoreboard__highlight-player'><small>我的位置</small><span className='beatmapset-scoreboard__highlight-rank'>#{me.rank.toLocaleString('zh-CN')}</span><strong><Player row={me} /></strong></div>
      <div className='beatmapset-scoreboard__highlight-score'><small>EX / 满分</small><ExScore row={me} /><div><LampBadge lamp={me.score.lamp} /> <small>{sourceNames[me.score.source] ?? me.score.source}</small></div></div>
    </div>}
  </div>;
}

export default function Table({ board, mania }: { board?: Board; mania?: ManiaRow[] }) {
  const [expanded, setExpanded] = React.useState<string | null>(null);
  const [id] = React.useState(() => 'oms-scoreboard-' + ++tableId);
  const toggle = (key: string, name: string) => <button type='button' className={bn + '__expand'} aria-label={'查看 ' + name + ' 的成绩详情'}
    aria-expanded={expanded === key} aria-controls={id + '-' + key} onClick={() => setExpanded(expanded === key ? null : key)}>
    <i className={'fas fa-chevron-' + (expanded === key ? 'up' : 'down')} aria-hidden='true' />
  </button>;
  return <div className={bn + ' ' + bn + '--oms'} role='region' aria-label='谱面成绩榜' tabIndex={0}>
    <table className={bn + '__table'}><thead><tr>
      <th scope='col' className={bn + '__header ' + bn + '__header--rank'}>排名</th>
      <th scope='col' className={bn + '__header ' + bn + '__header--score'}>{board ? 'EX / 满分' : '总分'}</th>
      <th scope='col' className={bn + '__header ' + bn + '__header--player'}>玩家</th>
      <th scope='col' className={bn + '__header'}>{board ? '通关灯' : '通关'}</th>
      <th scope='col' className={bn + '__header'}>{board ? '成绩来源' : '准确率'}</th>
      <th scope='col' className={bn + '__header ' + bn + '__header--time'}>游玩时间</th>
      <th scope='col' className={bn + '__header ' + bn + '__header--details'}><span className='sr-only'>成绩详情</span></th>
    </tr></thead><tbody className={bn + '__body'}>
      {board?.items.map((row, index) => {
        const key = encodeURIComponent(row.identity.namespace + ':' + row.identity.id + ':' + row.score.record_id);
        return <React.Fragment key={key}><tr className={bn + '__body-row ' + bn + '__body-row--' + (index % 2 === 0 ? 'even' : 'odd') + (board.me?.identity.namespace === row.identity.namespace && board.me.identity.id === row.identity.id ? ' ' + bn + '__body-row--me' : '')}>
          <td className={bn + '__cell ' + bn + '__cell--rank'}>#{row.rank.toLocaleString('zh-CN')}</td>
          <td className={bn + '__cell ' + bn + '__cell--score'}><ExScore row={row} /></td>
          <td className={bn + '__cell ' + bn + '__cell--player'}><strong title={row.identity.namespace.toUpperCase() + ' #' + row.identity.id}><Player row={row} /></strong></td>
          <td className={bn + '__cell'}><LampBadge lamp={row.score.lamp} /></td>
          <td className={bn + '__cell ' + bn + '__cell--source'}>{sourceNames[row.score.source] ?? row.score.source}</td>
          <td className={bn + '__cell ' + bn + '__cell--time'}><PlayedAt value={row.score.played_at} /></td>
          <td className={bn + '__cell ' + bn + '__cell--details'}>{toggle(key, row.identity.username)}</td>
        </tr>{expanded === key && <tr id={id + '-' + key} className={bn + '__detail-row'}><td colSpan={7}><BmsDetails row={row} /></td></tr>}</React.Fragment>;
      })}
      {mania?.map((row, index) => {
        const key = 'mania-' + row.score.id;
        return <React.Fragment key={key}><tr className={bn + '__body-row ' + bn + '__body-row--' + (index % 2 === 0 ? 'even' : 'odd')}>
          <td className={bn + '__cell ' + bn + '__cell--rank'}>#{row.rank.toLocaleString('zh-CN')}</td>
          <td className={bn + '__cell ' + bn + '__cell--score'}><strong>{row.score.total_score.toLocaleString('zh-CN')}</strong></td>
          <td className={bn + '__cell ' + bn + '__cell--player'}><strong title={'OMS #' + row.user.id}><a href={'/users/' + row.user.id}>{row.user.username}</a></strong></td>
          <td className={bn + '__cell'}>{row.score.passed ? '已通关' : '未通关'}</td>
          <td className={bn + '__cell'}>{(row.score.accuracy * 100).toFixed(2)}%</td>
          <td className={bn + '__cell ' + bn + '__cell--time'}><PlayedAt value={row.score.played_at} /></td>
          <td className={bn + '__cell ' + bn + '__cell--details'}>{toggle(key, row.user.username)}</td>
        </tr>{expanded === key && <tr id={id + '-' + key} className={bn + '__detail-row'}><td colSpan={7}><div className={bn + '__record-details'}>
          <dl className={bn + '__facts'}><div><dt>玩家身份</dt><dd>OMS #{row.user.id}</dd></div><div><dt>成绩来源</dt><dd>OMS · 游玩记录</dd></div><div><dt>游玩时间</dt><dd><PlayedAt value={row.score.played_at} /></dd></div><div><dt>接收时间</dt><dd><PlayedAt value={row.score.received_at} /></dd></div></dl>
          <Details value={row.score} label='原始记录' />
        </div></td></tr>}</React.Fragment>;
      })}
    </tbody></table>
  </div>;
}
