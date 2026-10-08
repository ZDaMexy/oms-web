// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import { useApi } from 'oms/api';
import { Paginator, Sources, Status } from 'oms/components';
import { useQuery } from 'oms/page';
import { Board, Page, Ruleset } from 'oms/types';
import * as React from 'react';
import Table, { ManiaRow } from './table';

export default function Main({md5,mode}:{md5:string;mode:Ruleset}) {
  const [query,update]=useQuery();
  const reference=query.get('mode')!=='comparable';
  const condition=query.get('condition');
  const group=query.get('group');
  const source=query.get('sources');
  const maniaEnabled=source==null||source==='oms';
  const page=query.get('page')??'1';
  const info=useApi<{groups:{id:string;label:string}[]}>(mode==='mania'?'/api/ir/v2/charts/'+md5:null);
  const chosenGroup=group??info.data?.groups[0]?.id;
  const params=new URLSearchParams({page,limit:'20',mode:reference?'reference':'comparable'});
  if(source!=null) params.set('sources',source);
  if(!reference&&condition) params.set('condition',condition);
  const availableParams=new URLSearchParams({mode:'reference',limit:'1'});
  if(source!=null)availableParams.set('sources',source);
  const available=useApi<Board>(mode==='bms'&&!reference&&!condition?'/api/ir/v1/multisource/scores/chart/'+md5+'?'+availableParams:null);
  const result=useApi<Board>(mode==='bms'&&(reference||condition)?'/api/ir/v1/multisource/scores/chart/'+md5+'?'+params:null);
  const mania=useApi<Page<ManiaRow>>(mode==='mania'&&maniaEnabled&&chosenGroup?'/api/ir/v1/scores/chart/'+md5+'?'+new URLSearchParams({group:chosenGroup,page,limit:'20'}):null);
  const conditions=result.data?.conditions??available.data?.conditions??[];
  const data=mode==='bms'?result.data:mania.data;
  return <div className='beatmapset-scoreboard'>
    <div className='page-tabs'>{mode==='bms'?<>
      <button type='button' className={'page-tabs__tab'+(reference?' page-tabs__tab--active':'')} onClick={()=>update({mode:'reference',condition:null})}>参考混榜</button>
      <button type='button' className={'page-tabs__tab'+(!reference?' page-tabs__tab--active':'')} onClick={()=>update({mode:'comparable',condition:null})}>同条件榜</button>
    </>:<span className='page-tabs__tab page-tabs__tab--active'>OMS 成绩榜</span>}</div>
    <Sources mode={mode} value={source} onChange={value=>update(mode==='bms'?{sources:value,condition:null,mode:'reference'}:{sources:value})}/>
    {mode==='bms'?<>
      {!reference&&<label>比较条件 <select value={condition??''} onChange={event=>update({condition:event.target.value||null})}><option value=''>请选择条件</option>{conditions.map(value=><option key={value.id} value={value.id}>{value.label}</option>)}</select></label>}
    </>:<label>计分条件 <select value={chosenGroup??''} onChange={event=>update({group:event.target.value})}>{info.data?.groups.map(value=><option key={value.id} value={value.id}>{value.label}</option>)}</select></label>}
    <div className='beatmapset-scoreboard__main'>
      {mode==='mania'&&!maniaEnabled?<p className='beatmapset-scoreboard__notice'>{source===''?'未选择成绩来源 · 0 人':'mania 成绩榜目前只有 OMS 来源。'}</p>:mode==='bms'&&!reference&&!condition?<><Status error={available.error} ready={available.data!=null}/><p className='beatmapset-scoreboard__notice'>{available.data?.conditions.length===0?'所选来源暂无可比较的条件，可以返回参考混榜。':'先选择要比较的条件。这里只比较规则和物量相同的 OMS 成绩。'}</p></>:
      <><Status error={mode==='bms'?result.error:mania.error??info.error} ready={data!=null}/>
        {data!=null&&<>
          <p className='beatmapset-scoreboard__notice'>{mode==='bms'
            ? result.data!.selected_sources.length===0?'未选择成绩来源。':reference?'按 EX 分排列，保留各播放器的判定和通关灯。不同播放器的成绩仅供参考。':'只比较所选来源中规则和物量相同的 OMS 成绩，其他播放器和条件不明的历史成绩不计入。'
            : '按同一计分条件下的公开最佳总分排列，也包含未通关成绩。'} <a href='/help#scores'>榜单说明</a></p>
          <p className='beatmapset-scoreboard__notice'>{data.total.toLocaleString('zh-CN')} 位玩家</p>
          {data.items.length===0?<p className='beatmapset-scoreboard__notice'>{data.total===0?(source===''?'选择成绩来源后查看榜单。':mode==='bms'&&!reference?'没有符合这个条件的成绩，可以换个条件或返回参考混榜。':'所选来源下还没有成绩。'):'本页没有成绩，请返回第一页。'}</p>:mode==='bms'?<Table board={result.data!}/>:<Table mania={mania.data!.items}/>}
          {result.data?.me!=null&&!result.data.items.some(row=>row.identity.namespace===result.data!.me!.identity.namespace&&row.identity.id===result.data!.me!.identity.id)&&<><h3 className='title title--page-extra'>我的位置</h3><Table board={{...result.data,items:[result.data.me]}}/></>}
          <Paginator page={data.page} limit={data.limit} total={data.total} onPage={value=>update({page:String(value)},false)}/>
        </>}
      </>}
    </div>
  </div>;
}
