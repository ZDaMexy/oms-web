// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import HeaderV4 from 'components/header-v4';
import { useApi } from 'oms/api';
import { Status } from 'oms/components';
import { pageData, ruleset, useQuery } from 'oms/page';
import { BmsDetail, DifficultyTable, DifficultyTableChart, IrChart, ManiaDetail } from 'oms/types';
import * as React from 'react';
import Header, { IrHeader } from './header';
import Info, { IrInfo } from './info';
import ScoreboardMain from './scoreboard/main';

export default function Main(_props: {container:HTMLElement}) {
  const initial=pageData<{context:{ruleset?:'bms'|'mania';md5?:string;sha256?:string;sid?:number;ir_only?:boolean};catalog?:BmsDetail|ManiaDetail;chart?:IrChart;table_chart?:DifficultyTableChart & {md5:string};difficulty_table?:DifficultyTable}>().data;
  const [query,update]=useQuery();
  const md5=initial.context.md5??query.get('md5');
  const irOnly=initial.context.ir_only===true;
  const tableChart=initial.table_chart;
  const irMetadata=useApi<IrChart>(irOnly&&initial.chart==null&&tableChart==null&&md5!=null?'/api/ir/v2/charts/'+md5:null);
  const ir=initial.chart??irMetadata.data;
  const mode=irOnly?ir?.ruleset??initial.context.ruleset??ruleset(query):initial.context.ruleset??ruleset(query);
  const sid=initial.context.sid??query.get('sid');
  const sha256=initial.context.sha256??query.get('sha256');
  const endpoint=mode==='bms'&&md5?'/api/ir/v1/catalog/bms/'+md5+(sha256==null?'':'?'+new URLSearchParams({sha256})):mode==='mania'&&sid?'/api/ir/v1/catalog/mania/sets/'+sid:null;
  const metadata=useApi<BmsDetail|ManiaDetail>(!irOnly&&initial.catalog==null?endpoint:null);
  const detail=initial.catalog??metadata.data;
  const tableQuery=new URLSearchParams();
  if(initial.difficulty_table!=null) {
    tableQuery.set('table',initial.difficulty_table.id);
    const level=query.get('level');
    if(level!=null) tableQuery.set('level',level);
  }
  return <div className='osu-layout osu-layout--full'>
    <HeaderV4 theme='beatmapset' links={[{title:irOnly?'谱面榜':'谱面',url:irOnly?'/ir'+(initial.difficulty_table==null?'':'?'+tableQuery):'/beatmapsets'},{title:'详情',url:location.pathname+location.search,active:true}]}/>
    <div className='osu-page osu-page--generic-compact'>
      {irOnly?tableChart!=null?<>
        <IrHeader detail={{ruleset:'bms',chart:{md5:tableChart.md5,sha256:null,title:tableChart.title,artist:tableChart.artist,difficulty:tableChart.level==null?null:(initial.difficulty_table?.symbol??'')+tableChart.level}}}/>
        <p className='difficulty-tables__provenance'>曲名与表内等级来自 {initial.difficulty_table!.name}；成绩按这张谱面的 MD5 查询。</p>
      </>:<><Status error={irMetadata.error} ready={ir!=null}/>{ir!=null&&<><IrHeader detail={ir}/><IrInfo detail={ir}/></>}</>:
        <>{endpoint==null?<p>{mode==='mania'&&md5!=null?'这张谱面尚未找到对应的 Sayobot 谱包。':'地址缺少谱面 MD5 或谱面集编号，请重新选择谱面。'}</p>:<Status error={metadata.error} ready={detail!=null}/>}
          {detail!=null&&<><Header detail={detail} md5={md5} sha256={sha256} selectedSource={query.get('download_source')} onSource={source=>update({download_source:source})}/><Info detail={detail}/></>}</>}
      <div className='user-profile-pages user-profile-pages--no-tabs'>
        {md5!=null?(!irOnly||ir!=null||tableChart!=null)&&<div className='page-extra'><ScoreboardMain md5={md5} mode={mode}/></div>:<div className='page-extra page-extra--compact'><p>来源未提供原 .osu 文件的 MD5，暂时无法显示这张谱面的成绩榜。</p></div>}
      </div>
    </div>
  </div>;
}
