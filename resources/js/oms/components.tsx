import { SearchFilter } from 'beatmaps/search-filter';
import { Spinner } from 'components/spinner';
import * as React from 'react';
import { useApi } from './api';
import { keys, sourceNames } from './page';
import { Lamp, Ruleset, Source } from './types';

export function Status({ error, ready }: { error?: string; ready: boolean }) {
  if (error != null) return <p role='alert' className='beatmapset-scoreboard__notice'>{error}</p>;
  if (!ready) return <p className='beatmapset-scoreboard__notice' role='status'><Spinner /> 正在加载…</p>;
  return null;
}
export function Paginator({ page, limit, total, onPage }: { page: number; limit: number; total: number; onPage: (page: number) => void }) {
  const last = Math.max(1, Math.ceil(total / limit));
  return <div className='pagination-v2'>
    <button type='button' className='pagination-v2__link' disabled={page <= 1} onClick={() => onPage(1)}>第一页</button>
    <button type='button' className='pagination-v2__link' disabled={page <= 1} onClick={() => onPage(page - 1)}>上一页</button>
    <span className='pagination-v2__link pagination-v2__link--active'>{page} / {last}</span>
    <button type='button' className='pagination-v2__link' disabled={page >= last} onClick={() => onPage(page + 1)}>下一页</button>
    <button type='button' className='pagination-v2__link' disabled={page >= last} onClick={() => onPage(last)}>最后一页</button>
  </div>;
}
export function ModeFilters({ mode, keymode, onChange }: { mode: Ruleset; keymode: string; onChange: (changes: Record<string, string | null>) => void }) {
  return <>
    <SearchFilter title='玩法' options={[{id:'bms',name:'BMS'},{id:'mania',name:'mania'}]} selected={[mode]} onChange={values => onChange({ruleset:values[0],keymode:values[0] === 'bms' ? 'bms_7k' : 'mania_4k',sources:null,source:null,condition:null})} />
    <SearchFilter title='键型' options={keys(mode).map(id=>({id,name:id.replace('bms_','BMS ').replace('pms_','PMS ').replace('mania_','')}))} selected={[keymode]} onChange={values=>onChange({keymode:values[0],condition:null})}/>
  </>;
}
export function Sources({ value, onChange, live = false, mode = 'bms' }: { value: string | null; onChange: (value: string) => void; live?: boolean; mode?: Ruleset }) {
  const registry = useApi<{items: Source[]}>('/api/ir/v2/sources', undefined, 'public');
  if (registry.data == null) return <Status error={registry.error} ready={false} />;
  const sources = registry.data.items.filter(source => (mode !== 'mania' || source.code === 'oms') && (!live || source.record_kind !== 'archive_best'));
  const selected = value == null ? sources.filter(source => source.available).map(source => source.code) : value.split(',').filter(Boolean);
  const uncertain = sources.filter(source => ['lr2ir.v3.sbmp', 'lr2ir.v3.unknown'].includes(source.code));
  const clients = sources.filter(source => !uncertain.includes(source));
  const option = (source: Source) => <button type='button' key={source.code}
    className={'score-source-filter__option' + (selected.includes(source.code) ? ' score-source-filter__option--active' : '')}
    disabled={!source.available} aria-pressed={selected.includes(source.code)}
    title={source.code === 'lr2ir.v3.lr2' ? 'LR2 · 当前收录成绩来自旧库；经典 LR2 实时接入尚未提供' : source.label}
    onClick={() => onChange((selected.includes(source.code) ? selected.filter(code => code !== source.code) : [...selected, source.code]).join(','))}>
    <span className='score-source-filter__check' aria-hidden='true'><i className='fas fa-check' /></span>
    {sourceNames[source.code] ?? source.label}{!source.available && <small>未开放</small>}
  </button>;
  return <div className='score-source-filter' role='group' aria-label='客户端筛选'>
    <div className='score-source-filter__heading'><span>客户端</span><div className='score-source-filter__actions'>
      <button type='button' onClick={() => onChange(sources.filter(source => source.available).map(source => source.code).join(','))}>全选</button>
      <button type='button' onClick={() => onChange('')}>清空</button>
      <a href='/help#players'>接入说明</a>
    </div></div>
    <div className='score-source-filter__options'>{clients.map(option)}</div>
    <details className='score-source-filter__versions'><summary>版本与未确认标记</summary>
      <ul>{clients.map(source => <li key={source.code}>{source.code === 'lr2ir.v3.lr2' ? 'LR2：收录旧库成绩，经典 LR2 实时插件尚未提供。' : source.label}</li>)}</ul>
      {uncertain.length > 0 && <><p>旧库还有未确认的客户端标记，默认保留在榜单中；原值可在成绩详情查看。</p><div className='score-source-filter__options'>{uncertain.map(option)}</div></>}
    </details>
  </div>;
}
export function LampBadge({lamp}:{lamp?:Lamp|null}) {
  const label=lamp?.label??'未知灯';
  const tone=/full.?combo|perfect/i.test(label)?'combo':/failed|no play/i.test(label)?'failed':/hard|hazard/i.test(label)?'hard':/easy/i.test(label)?'easy':/clear/i.test(label)?'clear':'unknown';
  return <span className={'score-lamp score-lamp--'+tone} title={lamp==null?'来源未提供通关灯':`${lamp.family} · ${lamp.value}${lamp.rule_label==null?'':' · '+lamp.rule_label}`}>{label}</span>;
}
export function Details({ value, label = '查看成绩详情' }: { value: unknown; label?: string }) {
  return <details className='beatmapset-scoreboard__details'><summary>{label}</summary><pre className='u-fancy-scrollbar'>{JSON.stringify(value,null,2)}</pre></details>;
}
