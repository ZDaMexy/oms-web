import * as React from 'react';

export const bmsJudgements = ['pg', 'gr', 'gd', 'bd', 'pr', 'ep'] as const;
export const maniaJudgements = ['perfect', 'great', 'good', 'ok', 'meh', 'miss'] as const;
export const judgementLabels: Record<string, string> = { pg: 'PG', gr: 'GR', gd: 'GD', bd: 'BD', pr: 'PR', ep: 'EP', perfect: 'MAX', great: '300', good: '200', ok: '100', meh: '50', miss: 'MISS' };
export const judgementHelp: Record<string, string> = { pg: 'PGREAT', gr: 'GREAT', gd: 'GOOD', bd: 'BAD', pr: 'POOR · 沿用来源定义；OpenLR2 包含空 POOR', ep: '空 POOR · OMS 与 Java 单独收录，旧库与 OpenLR2 无法拆分' };

export function Judgements({ statistics, mania = false }: { statistics: Record<string, number | null>; mania?: boolean }) {
  const bn = 'beatmap-scoreboard-table';
  return <dl className={bn + '__judgements'}>{(mania ? maniaJudgements : bmsJudgements).map(key => {
    const count = mania ? statistics[key] ?? 0 : statistics[key];
    return <div key={key} className={bn + '__judgement ' + bn + '__judgement--' + key} title={judgementHelp[key]}>
      <dt>{judgementLabels[key]}</dt><dd className={count === 0 ? bn + '__zero' : undefined}>{count == null ? '—' : count.toLocaleString('zh-CN')}</dd>
    </div>;
  })}</dl>;
}
