// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

import { useApi, useSession } from 'oms/api';
import { pageData, ruleset, useQuery } from 'oms/page';
import { OmsPlay, Page, Performance, PublicBest, User } from 'oms/types';

interface InitialData { context: { id: string }; profile?: { user: User } }
export default function useController() {
  const initial = pageData<InitialData>().data;
  const [query, update] = useQuery();
  const account = useSession();
  const id = initial.context.id;
  const profile = useApi<{ user: User }>(initial.profile == null ? `/api/ir/v1/users/${encodeURIComponent(id)}/profile` : null);
  const user = initial.profile?.user ?? profile.data?.user;
  const own = user != null && account.user?.id === user.id;
  const mode = ruleset(query);
  const keymode = query.get('keymode') ?? (mode === 'bms' ? 'bms_7k' : 'mania_4k');
  const section = query.get('section') === 'history' ? 'history' : query.get('section') === 'recent' ? 'recent' : 'best';
  const scope = new URLSearchParams({ ruleset: mode, keymode });
  if (query.has('sources')) scope.set('sources', query.get('sources')!);
  const performance = useApi<Performance>(user == null || section === 'history' ? null : `/api/ir/v1/users/${encodeURIComponent(id)}/performance?${scope}`);
  const selected = new URLSearchParams(scope);
  if (query.has('condition')) selected.set('condition', query.get('condition')!);
  selected.set('page', query.get('page') ?? '1');
  selected.set('limit', '20');
  const records = useApi<Page<PublicBest>>(user == null || section === 'history' ? null : `/api/ir/v1/users/${encodeURIComponent(id)}/public-${section === 'best' ? 'bests' : 'recent'}?${selected}`);
  const historyPage = new URLSearchParams({ page:query.get('page') ?? '1', limit:'20' });
  const history = useApi<Page<OmsPlay>>(own && section === 'history' ? `/api/ir/v1/scores/user/${encodeURIComponent(id)}?${historyPage}` : null);
  return { id, user, profile, mode, keymode, section, query, update, performance, records, history, own };
}
export type Controller = ReturnType<typeof useController>;
