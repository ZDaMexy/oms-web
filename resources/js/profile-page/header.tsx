// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import HeaderV4 from 'components/header-v4';
import * as React from 'react';
import { Controller } from './controller';

export default function Header({ controller }: { controller: Controller }) {
  const { mode, keymode, id } = controller;
  return <HeaderV4 theme='users' links={[
    { title: '个人', url: '/users/' + id, active: true },
    { title: '帖子', url: '/community?author_id=' + id },
    { title: '查找玩家', url: '/users' },
    { title: '玩家榜', url: '/rankings?' + new URLSearchParams({ ruleset: mode, keymode }) },
  ]} />;
}
