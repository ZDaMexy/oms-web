// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import BeatmapsetPanel, { IrChartPanel } from 'beatmapset-panel';
import { useApi } from 'oms/api';
import { Paginator, Status } from 'oms/components';
import { chartUrl, keys } from 'oms/page';
import { CatalogSearch, IrChart, Page, Ruleset } from 'oms/types';
import * as React from 'react';
import { SearchFilter } from './search-filter';

interface Props { query: URLSearchParams; mode: Ruleset; update: (changes: Record<string,string|null>)=>void }
export function SearchContent({query,mode,update}:Props) {
  const source=query.get('source') ?? (mode==='bms'?'ginger':'sayobot');
  const page=query.get('page') ?? '1';
  const params=new URLSearchParams({ruleset:mode,source,q:query.get('q')??'',page,cursor:query.get('cursor')??'0'});
  const keymode=query.get('keys');
  if(keymode) params.set('keys',mode==='mania'?keymode.replace('mania_','').replace('k',''):keymode);
  const result=useApi<CatalogSearch>('/api/ir/v1/catalog/search?'+params);
  const [text,setText]=React.useState(query.get('q')??'');
  React.useEffect(() => { setText(query.get('q') ?? ''); }, [query.get('q')]);
  const search = (event: React.FormEvent) => {
    event.preventDefault();
    const value = text.trim();
    if (mode === 'bms' && /^[0-9a-f]{32}$/i.test(value)) { Turbo.visit(chartUrl(value.toLowerCase(), mode)); return; }
    if (mode === 'mania' && /^[0-9]+$/.test(value)) {
      const sid = BigInt(value);
      if (sid > BigInt(0) && sid <= BigInt(2147483647)) { Turbo.visit('/beatmaps?' + new URLSearchParams({ ruleset: mode, sid: sid.toString() })); return; }
    }
    update({q:value,cursor:'0',page:'1'});
  };
  return <>
    <div className='osu-page osu-page--beatmapsets-search-header'><div className='beatmapsets-search beatmapsets-search--expanded'>
      <form className='beatmapsets-search__input-container' onSubmit={search}>
        <input className='beatmapsets-search__input' type='search' aria-label='搜索谱面' value={text} maxLength={200} onChange={event=>setText(event.target.value)} placeholder={mode === 'bms' ? '标题、作者或原 MD5' : '标题、作者或集合编号'}/>
        <button className='beatmapsets-search__icon beatmapsets-search__icon--button' type='submit'><span className='fas fa-search'/><span className='sr-only'>搜索</span></button>
      </form>
      <div className='beatmapsets-search__filter-grid'>
        <SearchFilter grid title='玩法' options={[{id:'bms',name:'BMS'},{id:'mania',name:'mania'}]} selected={[mode]} onChange={values=>update({ruleset:values[0],source:values[0]==='bms'?'ginger':'sayobot',keys:null,page:'1',cursor:'0'})}/>
        <SearchFilter grid title='来源' options={mode==='bms'?[{id:'ginger',name:'Ginger Rush'},{id:'616',name:'616'}]:[{id:'sayobot',name:'Sayobot'}]} selected={[source]} onChange={values=>update({source:values[0],page:'1',cursor:'0'})}/>
        <SearchFilter grid title='键型' options={[{id:'',name:'全部'},...keys(mode).map(id=>({id,name:id.replace('bms_','BMS ').replace('pms_','PMS ').replace('mania_','')}))]} selected={[keymode??'']} onChange={values=>update({keys:values[0]||null,page:'1',cursor:'0'})}/>
      </div>
    </div></div>
    <div className='js-sticky-header'/>
    <div className='osu-page'><div className='beatmapsets'><div className='beatmapsets__content'>
      <Status error={result.error} ready={result.data!=null}/>
      {result.data!=null && <>
        <div className='beatmapsets__toolbar'>{result.data.total==null?'来源使用游标分页':`来源共 ${result.data.total} ${result.data.total_basis==='source-chart-rows'?'原谱行':'包'}`}</div>
        {result.data.source_status.filter(status=>status.status!=='ok').map(status=><p key={status.source} role='status'>{status.source}：{status.message??status.status}</p>)}
        {result.data.items.length===0?<div className='beatmapsets__empty'>本页没有匹配谱面。</div>:<div className='beatmapsets__items'>{result.data.items.map(set=><div className='beatmapsets__item' key={set.id}><BeatmapsetPanel beatmapset={set}/></div>)}</div>}
        <div className='beatmapsets__paginator'>
          {result.data.total!=null?<Paginator page={result.data.page} total={result.data.total} limit={result.data.limit} onPage={value=>update({page:String(value)})}/>:
            <div className='pagination-v2'><button type='button' className='pagination-v2__link' onClick={()=>update({page:'1',cursor:'0'})}>重新开始</button>
              <button type='button' className='pagination-v2__link' disabled={!result.data.has_more||result.data.next_cursor==null}
                onClick={()=>update({page:String(result.data!.page+1),cursor:String(result.data!.next_cursor)})}>下一批</button></div>}
        </div>
      </>}
    </div></div></div>
  </>;
}

export interface IrSearchData {
  context: { q?: string; page?: number|string; limit?: number|string };
  chart_list?: Page<IrChart>;
}
export function IrSearchContent({query,update,initial}:{query:URLSearchParams;update:Props['update'];initial:IrSearchData}) {
  const q = query.get('q') ?? '';
  const page = query.get('page') ?? '1';
  const limit = query.get('limit') ?? '20';
  const params = new URLSearchParams({ q, page, limit });
  const sameScope = q === (initial.context.q ?? '') && Number(page) === Number(initial.context.page ?? 1) && Number(limit) === Number(initial.context.limit ?? 20);
  const result = useApi<Page<IrChart>>('/api/ir/v2/charts?' + params, sameScope ? initial.chart_list : undefined);
  const [text,setText] = React.useState(q);
  React.useEffect(() => { setText(q); }, [q]);
  const search = (event:React.FormEvent) => {
    event.preventDefault();
    update({ q:text.trim(), page:'1' });
  };
  return <>
    <div className='osu-page osu-page--beatmapsets-search-header'><div className='beatmapsets-search beatmapsets-search--expanded'>
      <form className='beatmapsets-search__input-container' onSubmit={search}>
        <input className='beatmapsets-search__input' type='search' aria-label='搜索成绩谱面' value={text} maxLength={200} onChange={event=>setText(event.target.value)} placeholder='标题、作者或原 MD5'/>
        <button className='beatmapsets-search__icon beatmapsets-search__icon--button' type='submit'><span className='fas fa-search'/><span className='sr-only'>搜索</span></button>
      </form>
    </div></div>
    <div className='js-sticky-header'/>
    <div className='osu-page'><div className='beatmapsets'><div className='beatmapsets__content'>
      <Status error={result.error} ready={result.data!=null}/>
      {result.data!=null && <>
        <div className='beatmapsets__toolbar'>共 {result.data.total} 张成绩谱面</div>
        {result.data.items.length===0 ? <div className='beatmapsets__empty'>{result.data.total===0?'没有匹配谱面。':'本页没有谱面，请返回第一页。'}</div> :
          <div className='beatmapsets__items'>{result.data.items.map(detail=><div className='beatmapsets__item' key={detail.chart.md5}><IrChartPanel detail={detail}/></div>)}</div>}
        <div className='beatmapsets__paginator'><Paginator page={result.data.page} total={result.data.total} limit={result.data.limit} onPage={value=>update({page:String(value)})}/></div>
      </>}
    </div></div></div>
  </>;
}
