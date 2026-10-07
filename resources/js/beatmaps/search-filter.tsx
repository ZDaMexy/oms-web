// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import * as React from 'react';
import { classWithModifiers } from 'utils/css';

export interface FilterOption { id: string; name: string; disabled?: boolean }
interface Props { title: string; options: FilterOption[]; selected: string[]; multiselect?: boolean; grid?: boolean; onChange: (selected: string[]) => void }
export function SearchFilter({ title, options, selected, multiselect = false, grid = false, onChange }: Props) {
  return <div className={classWithModifiers('beatmapsets-search-filter', { grid })}>
    <span className='beatmapsets-search-filter__header'>{title}</span>
    <div className='beatmapsets-search-filter__items'>{options.map(option =>
      <button type='button' key={option.id} disabled={option.disabled}
        className={classWithModifiers('beatmapsets-search-filter__item', { active: selected.includes(option.id) })}
        aria-pressed={selected.includes(option.id)}
        onClick={() => onChange(multiselect ? selected.includes(option.id) ? selected.filter(id => id !== option.id) : [...selected, option.id] : [option.id])}>
        {option.name}
      </button>)}</div>
  </div>;
}
