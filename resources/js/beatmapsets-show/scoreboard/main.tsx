// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import { useApi } from 'oms/api';
import { Paginator, Sources, Status } from 'oms/components';
import { useQuery } from 'oms/page';
import { Board, Page, Ruleset } from 'oms/types';
import * as React from 'react';
import Table, { ManiaRow, ScoreHighlights } from './table';

export default function Main({md5,mode}:{md5:string;mode:Ruleset}) {
  const [query,update]=useQuery();
  const reference=query.get('mode')!=='comparable';
  const condition=query.get('condition');
  const group=query.get('group');
  const source=query.get('sources');
  const maniaEnabled=source==null||source==='oms';
  const page=query.get('page')??'1';
  const info=useApi<{groups:{id:string;label:string}[]}>(mode==='mania'?'/api/ir/v2/charts/'+md5:null, undefined, 'public');
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
      <button type='button' aria-pressed={reference} className={'page-tabs__tab'+(reference?' page-tabs__tab--active':'')} onClick={()=>update({mode:'reference',condition:null})}>参考榜</button>
      <button type='button' aria-pressed={!reference} className={'page-tabs__tab'+(!reference?' page-tabs__tab--active':'')} onClick={()=>update({mode:'comparable',condition:null})}>同条件榜</button>
    </>:<span className='page-tabs__tab page-tabs__tab--active'>OMS 成绩榜</span>}</div>
    <Sources mode={mode} value={source} onChange={value=>update(mode==='bms'?{sources:value,condition:null,mode:'reference'}:{sources:value})}/>
    {mode==='bms'?<>
      {!reference&&<label className='score-condition-filter'>比较条件 <select value={condition??''} onChange={event=>update({condition:event.target.value||null})}><option value=''>请选择条件</option>{conditions.map(value=><option key={value.id} value={value.id}>{value.label}</option>)}</select></label>}
    </>:<label className='score-condition-filter'>计分条件 <select value={chosenGroup??''} onChange={event=>update({group:event.target.value})}>{info.data?.groups.map(value=><option key={value.id} value={value.id}>{value.label}</option>)}</select></label>}
    <div className='beatmapset-scoreboard__main'>
      {mode==='mania'&&!maniaEnabled?<p className='beatmapset-scoreboard__notice'>选择 OMS 查看 mania 成绩。</p>:mode==='bms'&&!reference&&!condition?<><Status error={available.error} ready={available.data!=null}/>{available.data != null && <p className='beatmapset-scoreboard__notice'>{available.data.conditions.length===0?'所选客户端暂无同条件成绩。':'选择一种条件，查看规则和物量相同的 OMS 成绩。'}</p>}</>:
      <><Status error={mode==='bms'?result.error:mania.error??info.error} ready={data!=null}/>
        {data!=null&&<>
          <div className='beatmapset-scoreboard__scope'><h2>{mode==='bms'?'EX SCORE 排名':'总分排名'}</h2><span>{data.total.toLocaleString('zh-CN')} 位玩家</span></div>
          <p className='beatmapset-scoreboard__description'><a href='/help#scores'>榜单说明</a></p>
          <ScoreHighlights board={result.data} mania={mania.data?.items}/>
          {data.items.length===0?<p className='beatmapset-scoreboard__notice'>{data.total===0?(source===''?'选择客户端后查看成绩。':'暂无符合筛选的成绩。'):'这一页没有成绩。'}</p>:mode==='bms'?<Table board={result.data!}/>:<Table mania={mania.data!.items}/>}
          {result.data?.me!=null&&!result.data.items.some(row=>row.identity.namespace===result.data!.me!.identity.namespace&&row.identity.id===result.data!.me!.identity.id)&&<><h3 className='title title--page-extra'>我的成绩详情</h3><Table board={{...result.data,items:[result.data.me]}}/></>}
          <Paginator page={data.page} limit={data.limit} total={data.total} onPage={value=>update({page:String(value)},false)}/>
        </>}
      </>}
    </div>
  </div>;
}
