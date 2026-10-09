// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import { Details, LampBadge } from 'oms/components';
import { lr2irClientNames, sourceNames } from 'oms/page';
import { omsOptions, ScoreOption, scoreOptions } from 'oms/score-options';
import { Board, BoardRow, OmsPlay } from 'oms/types';
import * as React from 'react';

export interface ManiaRow { rank: number; user: { id: number; username: string }; score: OmsPlay }

const bn = 'beatmap-scoreboard-table';
let tableId = 0;
const recordKinds: Record<string, string> = { play: '游玩记录', best_state: '最佳状态', archive_best: '继承的最佳成绩' };
const fields: Record<string, string> = {
  option_1: '原始选项 1', option_2: '原始选项 2', option_3: '原始选项 3', option_4: '原始选项 4', input: '输入设备',
  judge_algorithm: '判定算法', gauge_rules: '通关规则', total: 'TOTAL', long_note_mode: '长音符模式', branch_policy: '分支规则',
  assist: '辅助设置', frequency: '频率', played_at: '游玩时间', sha256: 'SHA256',
};
const bmsJudgements = ['pg', 'gr', 'gd', 'bd', 'pr', 'ep'] as const;
const maniaJudgements = ['perfect', 'great', 'good', 'ok', 'meh', 'miss'] as const;
const labels: Record<string, string> = { pg: 'PG', gr: 'GR', gd: 'GD', bd: 'BD', pr: 'PR', ep: 'EP', perfect: 'PERFECT', great: 'GREAT', good: 'GOOD', ok: 'OK', meh: 'MEH', miss: 'MISS' };
const judgementHelp: Record<string, string> = { pg: 'PGREAT', gr: 'GREAT', gd: 'GOOD', bd: 'BAD', pr: 'POOR · 沿用来源定义；OpenLR2 包含空 POOR', ep: '空 POOR · OMS 与 Java 单独收录，旧库与 OpenLR2 无法拆分' };

function Player({ row }: { row: BoardRow }) {
  return row.identity.namespace === 'oms'
    ? <a href={'/users/' + row.identity.id}>{row.identity.username}</a>
    : <span>{row.identity.username}</span>;
}

function Client({ row }: { row: BoardRow }) {
  return <span className={bn + '__client'} title={row.score.client_version ?? undefined}>
    {sourceNames[row.score.source] ?? row.score.source}
    {row.score.record_kind === 'archive_best' && <span className={bn + '__inherited'} title='从旧 LR2IR 数据库继承的最佳成绩'>旧库</span>}
  </span>;
}

function number(value: number | null | undefined) { return value == null ? '—' : value.toLocaleString('zh-CN'); }
function accuracy(value: number | null | undefined) { return value == null ? '—' : (value * 100).toFixed(2) + '%'; }

function PlayedAt({ value }: { value: string | null }) {
  return value == null ? <span title='来源未提供游玩时间'>—</span> : <time dateTime={value} className='js-localtime'>{value}</time>;
}

function Options({ options }: { options: ScoreOption[] }) {
  return <span className='score-options' aria-label='Mod / Option'>
    {options.length === 0 ? <span className='score-options__missing' title='来源未提供可识别选项'>—</span> : options.map((option, index) => <span key={index}
      className={'score-options__option score-options__option--' + option.family} title={option.label}>
      <i className={'fas fa-' + option.icon} aria-hidden='true' /><span>{option.code}</span>{option.detail && <small>{option.detail}</small>}
    </span>)}
  </span>;
}

function Judgements({ statistics, mania = false }: { statistics: Record<string, number | null>; mania?: boolean }) {
  return <dl className={bn + '__judgements'}>{(mania ? maniaJudgements : bmsJudgements).map(key => <div key={key} className={bn + '__judgement ' + bn + '__judgement--' + key} title={judgementHelp[key]}>
    <dt>{labels[key]}</dt><dd className={statistics[key] === 0 ? bn + '__zero' : undefined}>{number(statistics[key] ?? (mania ? 0 : null))}</dd>
  </div>)}</dl>;
}

function BmsDetails({ row }: { row: BoardRow }) {
  return <div className={bn + '__record-details'}>
    <p className={bn + '__missing'}>ACC = EX / 最大 EX。PR 沿用播放器原定义；EP 是单独收录的空 POOR，未收录显示「—」。</p>
    <dl className={bn + '__facts'}>
      <div><dt>玩家身份</dt><dd>{row.identity.namespace.toUpperCase()} #{row.identity.id}</dd></div>
      <div><dt>客户端</dt><dd><Client row={row} /></dd></div>
      <div><dt>记录类型</dt><dd>{recordKinds[row.score.record_kind] ?? row.score.record_kind}</dd></div>
      {lr2irClientNames[row.score.source] != null && <div><dt>旧库客户端原标记</dt><dd>{lr2irClientNames[row.score.source]}</dd></div>}
      <div><dt>游玩时间</dt><dd>{row.score.played_at == null ? '未收录' : <PlayedAt value={row.score.played_at} />}</dd></div>
      {row.score.client_version != null && <div><dt>客户端版本</dt><dd>{row.score.client_version}</dd></div>}
      {row.score.reported_accuracy != null && <div><dt>客户端原始 ACC</dt><dd>{accuracy(row.score.reported_accuracy)}</dd></div>}
      {Object.entries(row.score.conditions).map(([key, value]) => <div key={key}><dt>{fields[key] ?? key}</dt><dd>{value == null ? '未收录' : typeof value === 'object' ? JSON.stringify(value) : String(value)}</dd></div>)}
    </dl>
    {row.best_lamps.length > 0 && <div className={bn + '__best-lamps'}><span>独立最佳灯</span>{row.best_lamps.map(lamp => <span key={lamp.family}>
      <LampBadge lamp={lamp} /> <small>{sourceNames[lamp.source ?? ''] ?? lamp.source} · {lamp.rule_label}</small>
    </span>)}</div>}
    {row.score.unknown_fields.length > 0 && <p className={bn + '__missing'}>未收录：{row.score.unknown_fields.map(key => fields[key] ?? key).join('、')}</p>}
    <Details value={{ ...row.score, best_lamps: row.best_lamps, identity: row.identity }} label='原始判定与选项' />
  </div>;
}

function BmsHighlight({ row, me = false }: { row: BoardRow; me?: boolean }) {
  return <article className={'beatmapset-scoreboard__highlight' + (me ? ' beatmapset-scoreboard__highlight--me' : '')}>
    <div className='beatmapset-scoreboard__highlight-rank'><small>{me ? '我的成绩' : '当前榜首'}</small><strong>#{number(row.rank)}</strong><LampBadge lamp={row.score.lamp} /></div>
    <div className='beatmapset-scoreboard__highlight-player'><strong title={row.identity.namespace.toUpperCase() + ' #' + row.identity.id}><Player row={row} /></strong><Client row={row} /><small><PlayedAt value={row.score.played_at} /></small></div>
    <div className='beatmapset-scoreboard__highlight-result'>
      <dl className='beatmapset-scoreboard__highlight-metrics'><div><dt>EX SCORE</dt><dd>{number(row.score.ex_score)}<small> / {number(row.score.max_ex_score)}</small></dd></div><div title='EX / 最大 EX'><dt>ACC</dt><dd>{accuracy(row.score.accuracy)}</dd></div><div><dt>最大连击</dt><dd>{number(row.score.max_combo)}</dd></div></dl>
      <div className='beatmapset-scoreboard__highlight-options'><Judgements statistics={row.score.statistics} /><Options options={scoreOptions(row.score)} /></div>
    </div>
  </article>;
}

export function ScoreHighlights({ board, mania }: { board?: Board; mania?: ManiaRow[] }) {
  const top = board?.page === 1 && board.items[0]?.rank === 1 ? board.items[0] : null;
  const maniaTop = mania?.[0]?.rank === 1 ? mania[0] : null;
  const me = board?.me;
  if (top == null && maniaTop == null && me == null) return null;
  return <div className='beatmapset-scoreboard__highlights'>
    {top != null && <BmsHighlight row={top} />}
    {maniaTop != null && <article className='beatmapset-scoreboard__highlight'>
      <div className='beatmapset-scoreboard__highlight-rank'><small>当前榜首</small><strong>#1</strong><span className='score-lamp'>{maniaTop.score.passed ? 'CLEAR' : 'FAILED'}</span></div>
      <div className='beatmapset-scoreboard__highlight-player'><strong><a href={'/users/' + maniaTop.user.id}>{maniaTop.user.username}</a></strong><small>OMS</small><small><PlayedAt value={maniaTop.score.played_at} /></small></div>
      <div className='beatmapset-scoreboard__highlight-result'><dl className='beatmapset-scoreboard__highlight-metrics'><div><dt>总分</dt><dd>{number(maniaTop.score.total_score)}</dd></div><div><dt>ACC</dt><dd>{accuracy(maniaTop.score.accuracy)}</dd></div><div><dt>最大连击</dt><dd>{number(maniaTop.score.max_combo)}</dd></div></dl>
        <div className='beatmapset-scoreboard__highlight-options'><Judgements mania statistics={maniaTop.score.statistics} /><Options options={omsOptions(maniaTop.score.mods)} /></div></div>
    </article>}
    {me != null && <BmsHighlight row={me} me />}
  </div>;
}

export default function Table({ board, mania }: { board?: Board; mania?: ManiaRow[] }) {
  const [expanded, setExpanded] = React.useState<string | null>(null);
  const [id] = React.useState(() => 'oms-scoreboard-' + ++tableId);
  const toggle = (key: string, name: string) => <button type='button' className={bn + '__expand'} aria-label={'查看 ' + name + ' 的成绩详情'}
    aria-expanded={expanded === key} aria-controls={id + '-' + key} onClick={() => setExpanded(expanded === key ? null : key)}>
    <i className={'fas fa-chevron-' + (expanded === key ? 'up' : 'down')} aria-hidden='true' />
  </button>;
  const judgements = board ? bmsJudgements : maniaJudgements;
  return <div className={bn + ' ' + bn + '--oms'} role='region' aria-label='谱面成绩榜' tabIndex={0}>
    <table className={bn + '__table'}><thead><tr>
      <th scope='col' className={bn + '__header ' + bn + '__header--rank'}>排名</th>
      <th scope='col' className={bn + '__header ' + bn + '__header--lamp'}>{board ? '通关灯' : '通关'}</th>
      <th scope='col' className={bn + '__header ' + bn + '__header--score'}>{board ? 'EX SCORE' : '总分'}</th>
      <th scope='col' className={bn + '__header ' + bn + '__header--accuracy'} title={board ? 'EX / 最大 EX' : '播放器准确率'}>ACC</th>
      <th scope='col' className={bn + '__header ' + bn + '__header--player'}>玩家 / 客户端</th>
      <th scope='col' className={bn + '__header ' + bn + '__header--combo'}>最大连击</th>
      {judgements.map(key => <th scope='col' key={key} title={judgementHelp[key]} className={bn + '__header ' + bn + '__judgement--' + key}>{labels[key]}</th>)}
      <th scope='col' className={bn + '__header ' + bn + '__header--time'}>达成时间</th>
      <th scope='col' className={bn + '__header ' + bn + '__header--mods'}>MOD / OPTION</th>
      <th scope='col' className={bn + '__header ' + bn + '__header--details'}><span className='sr-only'>成绩详情</span></th>
    </tr></thead><tbody className={bn + '__body'}>
      {board?.items.map((row, index) => {
        const key = encodeURIComponent(row.identity.namespace + ':' + row.identity.id + ':' + row.score.record_id);
        return <React.Fragment key={key}><tr className={bn + '__body-row ' + bn + '__body-row--' + (index % 2 === 0 ? 'even' : 'odd') + (board.me?.identity.namespace === row.identity.namespace && board.me.identity.id === row.identity.id ? ' ' + bn + '__body-row--me' : '')}>
          <td className={bn + '__cell ' + bn + '__cell--rank'}>#{number(row.rank)}</td>
          <td className={bn + '__cell ' + bn + '__cell--lamp'}><LampBadge lamp={row.score.lamp} /></td>
          <td className={bn + '__cell ' + bn + '__cell--score'} title={'最大 EX：' + number(row.score.max_ex_score)}><strong>{number(row.score.ex_score)}</strong></td>
          <td className={bn + '__cell ' + bn + '__cell--accuracy'}>{accuracy(row.score.accuracy)}</td>
          <td className={bn + '__cell ' + bn + '__cell--player'}><strong title={row.identity.namespace.toUpperCase() + ' #' + row.identity.id}><Player row={row} /></strong><Client row={row} /></td>
          <td className={bn + '__cell ' + bn + '__cell--combo'}>{number(row.score.max_combo)}</td>
          {bmsJudgements.map(name => <td key={name} className={bn + '__cell ' + bn + '__cell--judgement ' + bn + '__judgement--' + name + (row.score.statistics[name] === 0 ? ' ' + bn + '__zero' : '')}>{number(row.score.statistics[name])}</td>)}
          <td className={bn + '__cell ' + bn + '__cell--time'}><PlayedAt value={row.score.played_at} /></td>
          <td className={bn + '__cell ' + bn + '__cell--mods'}><Options options={scoreOptions(row.score)} /></td>
          <td className={bn + '__cell ' + bn + '__cell--details'}>{toggle(key, row.identity.username)}</td>
        </tr>{expanded === key && <tr id={id + '-' + key} className={bn + '__detail-row'}><td colSpan={15}><BmsDetails row={row} /></td></tr>}</React.Fragment>;
      })}
      {mania?.map((row, index) => {
        const key = 'mania-' + row.score.id;
        return <React.Fragment key={key}><tr className={bn + '__body-row ' + bn + '__body-row--' + (index % 2 === 0 ? 'even' : 'odd')}>
          <td className={bn + '__cell ' + bn + '__cell--rank'}>#{number(row.rank)}</td>
          <td className={bn + '__cell ' + bn + '__cell--lamp'}><span className='score-lamp'>{row.score.passed ? 'CLEAR' : 'FAILED'}</span></td>
          <td className={bn + '__cell ' + bn + '__cell--score'}><strong>{number(row.score.total_score)}</strong></td>
          <td className={bn + '__cell ' + bn + '__cell--accuracy'}>{accuracy(row.score.accuracy)}</td>
          <td className={bn + '__cell ' + bn + '__cell--player'}><strong title={'OMS #' + row.user.id}><a href={'/users/' + row.user.id}>{row.user.username}</a></strong><span className={bn + '__client'}>OMS</span></td>
          <td className={bn + '__cell ' + bn + '__cell--combo'}>{number(row.score.max_combo)}</td>
          {maniaJudgements.map(name => <td key={name} className={bn + '__cell ' + bn + '__cell--judgement ' + bn + '__judgement--' + name + (!row.score.statistics[name] ? ' ' + bn + '__zero' : '')}>{number(row.score.statistics[name] ?? 0)}</td>)}
          <td className={bn + '__cell ' + bn + '__cell--time'}><PlayedAt value={row.score.played_at} /></td>
          <td className={bn + '__cell ' + bn + '__cell--mods'}><Options options={omsOptions(row.score.mods)} /></td>
          <td className={bn + '__cell ' + bn + '__cell--details'}>{toggle(key, row.user.username)}</td>
        </tr>{expanded === key && <tr id={id + '-' + key} className={bn + '__detail-row'}><td colSpan={15}><div className={bn + '__record-details'}>
          <dl className={bn + '__facts'}><div><dt>玩家身份</dt><dd>OMS #{row.user.id}</dd></div><div><dt>客户端</dt><dd>OMS · {row.score.client_version}</dd></div><div><dt>游玩时间</dt><dd><PlayedAt value={row.score.played_at} /></dd></div><div><dt>接收时间</dt><dd><PlayedAt value={row.score.received_at} /></dd></div></dl>
          <Details value={row.score} label='原始判定与选项' />
        </div></td></tr>}</React.Fragment>;
      })}
    </tbody></table>
  </div>;
}
