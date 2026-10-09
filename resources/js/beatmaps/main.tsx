// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import HeaderV4 from 'components/header-v4';
import { pageData, ruleset, useQuery } from 'oms/page';
import * as React from 'react';
import { IrSearchContent, IrSearchData } from './difficulty-tables';
import { SearchContent } from './search-content';

export function Main() {
  const initial = pageData<IrSearchData>();
  const [query,update] = useQuery();
  const ir = initial.page === 'ir';
  return <><HeaderV4 theme='beatmapsets' links={[{title:ir?'谱面榜':'谱面',url:ir?'/ir':'/beatmapsets',active:true}]}/>
    {ir ? <IrSearchContent query={query} update={update} initial={initial.data}/> : <SearchContent query={query} update={update} mode={ruleset(query)}/>}</>;
}
