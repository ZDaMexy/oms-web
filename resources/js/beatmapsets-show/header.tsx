// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import { SearchFilter } from 'beatmaps/search-filter';
import BigButton from 'components/big-button';
import { sourceNames, chartUrl } from 'oms/page';
import { downloadBms, message } from 'oms/api';
import { BmsDetail, IrChart, ManiaDetail } from 'oms/types';
import * as React from 'react';
import Stats from './stats';

interface Props {detail:BmsDetail|ManiaDetail;md5:string|null;sha256:string|null;selectedSource:string|null;onSource:(source:string|null)=>void}
export default function Header({detail,md5,sha256,selectedSource,onSource}:Props) {
  const [downloading,setDownloading]=React.useState(false);
  const [downloadError,setDownloadError]=React.useState<string|null>(null);
  const downloadController=React.useRef<AbortController>();
  React.useEffect(()=>{
    setDownloading(false); setDownloadError(null);
    const cancelDownload=()=>{
      downloadController.current?.abort();
      setDownloading(false); setDownloadError(null);
    };
    document.addEventListener('turbo:before-visit',cancelDownload);
    return ()=>{
      document.removeEventListener('turbo:before-visit',cancelDownload);
      downloadController.current?.abort();
    };
  },[md5,selectedSource]);
  const candidate=detail.ruleset==='bms'?detail.candidates.find(value=>value.source===(selectedSource??detail.recommended_source)):null;
  const chart=detail.ruleset==='bms'?detail.chart:detail.set.charts[0];
  const cover=detail.ruleset==='bms'?candidate?.cover_url:detail.set.cover_url;
  const charts=detail.ruleset==='bms'?candidate?.charts:detail.set.charts;
  const automatic='/api/ir/v1/catalog/bms/'+md5+'/download'+(sha256==null?'':'?'+new URLSearchParams({sha256}));
  const download=detail.ruleset==='bms'?selectedSource==null?automatic:candidate?.eligible?candidate.package.download_url:null:detail.download.full_url;
  return <div className='beatmapset-header'>
    <div className='beatmapset-header__cover'>{cover!=null&&<div className='beatmapset-cover beatmapset-cover--full' style={{backgroundImage:`url("${cover}")`}}/>}</div>
    <div className='beatmapset-header__box beatmapset-header__box--main'>
      <div className='beatmapset-header__beatmap-picker-box'><div className='beatmap-picker'>
        {charts?.map(item=>item.md5!=null?<a className='beatmap-picker__beatmap' key={item.md5} href={chartUrl(item.md5,detail.ruleset,detail.ruleset==='mania'?{sid:String(detail.set.sid)}:{})}>{item.difficulty??'难度名未知'} · {item.keymode??'键型未知'}</a>:<span className='beatmap-picker__beatmap' key={item.bid}>{item.difficulty??'难度名未知'} · {item.keymode??'键型未知'}</span>)}
      </div></div>
      <span className='beatmapset-header__details-text beatmapset-header__details-text--title'>{(detail.ruleset==='bms'?chart?.title:detail.set.title)??md5??'标题未知'}</span>
      <span className='beatmapset-header__details-text beatmapset-header__details-text--artist'>{(detail.ruleset==='bms'?chart?.artist:detail.set.artist)??'艺术家未知'}</span>
      {detail.ruleset==='mania'&&detail.set.creator!=null&&<div className='beatmapset-mapping'>{detail.set.creator}</div>}
      {detail.ruleset==='bms'&&<SearchFilter title='下载来源' options={[{id:'auto',name:'自动'},...detail.candidates.map(value=>({id:value.source,name:sourceNames[value.source]??value.source,disabled:!value.eligible}))]} selected={[selectedSource??'auto']} onChange={values=>onSource(values[0]==='auto'?null:values[0])}/>}
      <div className='beatmapset-header__buttons'>
        <BigButton href={download??undefined} disabled={download==null||(detail.ruleset==='bms'&&detail.candidates.every(value=>!value.eligible))} icon='fas fa-download' modifiers='beatmapset-download'
          isBusy={downloading} text={{top:'下载谱包',bottom:detail.ruleset==='mania'?'Sayobot':selectedSource==null?'自动选择来源':sourceNames[selectedSource]??selectedSource}}
          props={{'data-turbo':'false',onClick:detail.ruleset==='bms'&&selectedSource==null?event=>{
            event.preventDefault();
            if (downloading) return;
            const controller=new AbortController();
            downloadController.current=controller;
            setDownloading(true); setDownloadError(null);
            void downloadBms(automatic,controller.signal).catch(error=>{if (!controller.signal.aborted) setDownloadError(message(error));})
              .finally(()=>{if (!controller.signal.aborted) setDownloading(false);});
          }:undefined}}/>
        {detail.ruleset==='mania'&&<BigButton href={detail.download.novideo_url} modifiers='beatmapset-download' text='下载（无视频）' icon='fas fa-download' props={{'data-turbo':'false'}}/>}
      </div>
      {downloadError!=null&&<p role='alert' className='beatmapset-header__availability-info'>{downloadError}</p>}
      {detail.ruleset==='bms'&&candidate!=null&&<p className='beatmapset-header__availability-info'>{candidate.identity==='md5-only'?'按谱面 MD5 找到，来源未提供 SHA256':'来源提供了 SHA256'} · {candidate.availability==='unchecked'?'下载链接尚未检查':candidate.availability}{candidate.reason==null?'':' · '+candidate.reason}</p>}
      {detail.ruleset==='bms'&&<details><summary>其他来源与状态</summary>{detail.source_status.map(status=><p key={status.source}>{sourceNames[status.source]??status.source}：{status.message??status.status}</p>)}</details>}
    </div>
    <div className='beatmapset-header__box beatmapset-header__box--stats'><Stats chart={chart??null}/></div>
  </div>;
}

export function IrHeader({detail}:{detail:Pick<IrChart, 'chart' | 'ruleset'>}) {
  const chart = detail.chart;
  const search = chartUrl(chart.md5,detail.ruleset,chart.sha256==null?{}:{sha256:chart.sha256});
  return <div className='beatmapset-header'>
    <div className='beatmapset-header__cover'/>
    <div className='beatmapset-header__box beatmapset-header__box--main'>
      <div className='beatmapset-header__beatmap-picker-box'><div className='beatmap-picker'><span className='beatmap-picker__beatmap'>{chart.difficulty??'难度名未知'}</span></div></div>
      <span className='beatmapset-header__details-text beatmapset-header__details-text--title'>{chart.title??'标题未知'}</span>
      <span className='beatmapset-header__details-text beatmapset-header__details-text--artist'>{chart.artist??'艺术家未知'}</span>
      {detail.ruleset==='bms'&&<div className='beatmapset-header__buttons'><BigButton href={search} modifiers='beatmapset-download' text={{top:'查找谱包',bottom:'Ginger Rush / 616'}} icon='fas fa-search'/></div>}
    </div>
    <div className='beatmapset-header__box beatmapset-header__box--stats'><Stats chart={null}/></div>
  </div>;
}
