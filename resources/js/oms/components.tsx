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
export function Sources({ value, onChange, live = false, single = false, mode = 'bms' }: { value: string | null; onChange: (value: string) => void; live?: boolean; single?: boolean; mode?: Ruleset }) {
  const registry = useApi<{items:Source[]}>('/api/ir/v2/sources');
  if (registry.data == null) return <Status error={registry.error} ready={false}/>;
  const sources = registry.data.items.filter(source => (mode !== 'mania' || source.code === 'oms') && (!live || source.record_kind !== 'archive_best'));
  const selected = value == null ? sources.filter(source=>source.available).map(source=>source.code) : value.split(',').filter(Boolean);
  const chosen=single?selected.slice(0,1):selected;
  return <div className='score-source-filter' role='group' aria-label='成绩来源'>
    <div className='score-source-filter__heading'><span>成绩来源</span>{!single&&<div className='score-source-filter__actions'>
      <button type='button' onClick={()=>onChange(sources.filter(source=>source.available).map(source=>source.code).join(','))}>全选</button>
      <button type='button' onClick={()=>onChange('')}>清空</button>
    </div>}</div>
    {(['live','archive'] as const).map(kind=>{
      const options=sources.filter(source=>(source.record_kind==='archive_best')===(kind==='archive'));
      if(options.length===0)return null;
      return <div className='score-source-filter__group' key={kind}>
        <span className='score-source-filter__label'>{kind==='archive'?'LR2IR 历史':'播放器'}</span>
        <div className='score-source-filter__options'>{options.map(source=><button type='button' key={source.code}
          className={'score-source-filter__option'+(chosen.includes(source.code)?' score-source-filter__option--active':'')}
          disabled={!source.available} aria-pressed={chosen.includes(source.code)} aria-label={source.label}
          title={source.label+(source.available?'':' · 未开放')}
          onClick={()=>onChange((single?[source.code]:chosen.includes(source.code)?chosen.filter(id=>id!==source.code):[...chosen,source.code]).join(','))}>
          <span className='score-source-filter__check' aria-hidden='true'><i className='fas fa-check'/></span>
          {kind==='archive'?source.code==='lr2ir.v3.lr2'?'LR2':source.code==='lr2ir.v3.sbmp'?'SBMP':'未知客户端':sourceNames[source.code]??source.label}
          {!source.available&&<small>未开放</small>}
        </button>)}</div>
      </div>;
    })}
    <details className='score-source-filter__versions'><summary>版本与来源说明</summary><ul>{sources.map(source=><li key={source.code}>{source.label}{source.record_kind==='archive_best'?' · 单谱历史摘要':''}</li>)}</ul></details>
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
