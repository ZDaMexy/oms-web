# Licensed under AGPL-3.0-or-later; see LICENCE.
"""Verify a running task-owned restore through actual loopback HTTP; no player sign-off."""
import argparse
from collections import Counter
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import time
from uuid import UUID

import httpx


WEB = Path('/mnt/f/zdamexy-workspace/websites/oms-web')
BACKUP = WEB / 'artifacts/local-recovery'
PUBLIC = Path('/mnt/f/oms/artifacts/oms-ir-multisource-20261004/archive/lr2ir-public-v1.db')
BASE = 'http://127.0.0.1:8090'
V1 = '/api/ir/v1'
WEB_HEADERS = {'Origin': BASE, 'X-OMS-IR': '1'}
ARCHIVE_SOURCES = {'lr2ir.v3.lr2': 1, 'lr2ir.v3.sbmp': 2, 'lr2ir.v3.unknown': 3}
EXTERNAL_SOURCES = ('beatoraja', 'lr2oraja', 'lr2oraja_ed', 'openlr2')
ALL_SOURCES = ['oms', *EXTERNAL_SOURCES, *ARCHIVE_SOURCES]


def file_digest(filename):
    result = hashlib.sha256()
    with filename.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def f_file(filename):
    filename = Path(filename).absolute()
    if not str(filename).startswith('/mnt/f/') or 'private-data' in filename.parts \
            or filename.resolve() != filename or not filename.is_file() or filename.is_symlink():
        raise ValueError('Use an explicit regular task file directly on F')
    return filename


def sqlite_read(filename, *, immutable=False):
    connection = sqlite3.connect(filename.as_uri() + '?mode=ro' + ('&immutable=1' if immutable else ''), uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA query_only=ON')
    return connection


class Verification:
    def __init__(self, args):
        self.args = args
        self.root = Path(args.restore_root).absolute()
        if not str(self.root).startswith('/mnt/f/') or 'private-data' in self.root.parts or self.root.resolve() != self.root:
            raise ValueError('Only a directly restored F-drive task directory is accepted')
        self.web = self.root / 'websites/oms-web'
        self.control = self.web / '.dev-cache/local-runtime'
        self.state = json.loads(f_file(args.acceptance_state).read_text())
        self.restoration = json.loads(f_file(self.root / 'restoration-report.json').read_text())
        if self.restoration.get('target') != str(self.root) \
                or self.restoration.get('scope') != 'same-existing-Alpine-WSL-file-and-SQLite-recovery' \
                or self.restoration.get('sqliteIntegrityCheck') != 'ok':
            raise ValueError('The target does not have a successful file/SQLite restoration report')
        manifest_path = f_file(BACKUP / args.round / 'source-manifest.json')
        self.manifest = json.loads(manifest_path.read_text())
        if self.manifest.get('round') != args.round \
                or file_digest(manifest_path) != self.restoration.get('backupManifestSha256'):
            raise ValueError('The running restore does not belong to the selected immutable snapshot round')
        self.output = Path(args.report).absolute() if args.report else self.web / ('artifacts/recovery-http-' + args.round + '.json')
        if not str(self.output).startswith('/mnt/f/') or 'private-data' in self.output.parts \
                or self.output.parent.resolve() != self.output.parent or not self.output.parent.is_dir() \
                or os.path.lexists(self.output):
            raise ValueError('Choose a new F-drive report file in an existing direct task artifacts directory')
        if self.output == Path(args.acceptance_state).absolute() or str(self.output).startswith(str(BACKUP) + '/'):
            raise ValueError('Acceptance state and the readonly snapshots must remain untouched')
        self.report = {'startedAt': datetime.now(timezone.utc).isoformat(), 'round': args.round,
                       'target': str(self.root), 'base': BASE,
                       'data': 'synthetic task-owned accounts/plays; complete approved public history',
                       'sameExistingOSOnly': True, 'playerAcceptance': False, 'productionDeployment': False,
                       'stateIncludedInRecoveryPackage': False, 'checks': []}
        self.next_request = 0.0
        self.requests = 0
        self.owner = self.state['users'][0]
        self.other = self.state['users'][1]
        if self.state['usernames'] != [user['username'] for user in self.state['users']] \
                or not isinstance(self.state['password'], str) or not self.state['password']:
            raise ValueError('The separately supplied task account state is incomplete')
        self.md5 = self.state['md5']
        if not re.fullmatch(r'[0-9a-f]{32}', self.md5):
            raise ValueError('The captured chart identity is invalid')
        UUID(self.state['submission_id'])
        self.revoked = self.state['revoked_key']
        if type(self.revoked['id']) is not int or self.revoked['id'] <= 0 \
                or not isinstance(self.revoked['secret'], str) or not self.revoked['secret'] \
                or type(self.state['hidden_post_id']) is not int or self.state['hidden_post_id'] <= 0:
            raise ValueError('Supply the actual revoked key and hidden post as separate protected acceptance state')

    def check(self, name, condition, **evidence):
        self.report['checks'].append({'name': name, 'passed': bool(condition), **evidence})
        if not condition:
            raise AssertionError(name)

    def request(self, client, method, path, status=200, **kwargs):
        delay = self.next_request - time.monotonic()
        if delay > 0:
            time.sleep(delay)
        self.next_request = time.monotonic() + 0.13  # Stay below the actual shared 600/min read quota.
        self.requests += 1
        response = client.request(method, path, **kwargs)
        expected_statuses = (status,) if isinstance(status, int) else status
        if response.status_code not in expected_statuses:
            # Do not print response bodies, submitted passwords, authorization or cookies.
            raise AssertionError('HTTP ' + method + ' ' + path.split('?')[0] + ': '
                                 + str(response.status_code) + ', expected ' + str(status))
        return response

    def api(self, client, method, path, status=200, **kwargs):
        response = self.request(client, method, path, status, **kwargs)
        return response.json() if response.content else None

    def running_ownership(self):
        for service in ('nginx', 'php-fpm', 'backend', 'catalog'):
            pid = int(f_file(self.control / (service + '.pid')).read_text())
            command = (Path('/proc') / str(pid) / 'cmdline').read_bytes().replace(b'\0', b' ')
            self.check('actual restored ' + service + ' process owns this root', str(self.root).encode() in command)
            if service == 'backend':
                self.check('running backend references only approved public projection', str(PUBLIC).encode() in command)

    def baseline(self):
        filename = f_file(self.control / 'live.db')
        with closing(sqlite_read(filename)) as connection:
            self.check('running restored test database is intact', connection.execute('PRAGMA integrity_check').fetchall()[0][0] == 'ok')
            for user in (self.owner, self.other):
                row = connection.execute('SELECT username FROM users WHERE id=?', (user['id'],)).fetchone()
                self.check('restored account ID keeps exact owner', row is not None and row['username'] == user['username'])
            rows = connection.execute('SELECT id,payload_json FROM scores WHERE user_id=? ORDER BY id', (self.owner['id'],)).fetchall()
            self.plays = {json.loads(row['payload_json'])['submission_id']: (row['id'], json.loads(row['payload_json'])) for row in rows}
            self.check('restored owner retains actual UUID BMS and mania plays', self.state['submission_id'] in self.plays
                       and {payload['ruleset'] for _, payload in self.plays.values()} == {'bms', 'mania'})
            key = connection.execute('SELECT user_id,source,token_hash,revoked FROM integration_keys WHERE id=?',
                                     (self.revoked['id'],)).fetchone()
            self.check('actual captured integration secret is revoked for its original owner', key is not None
                       and key['user_id'] == self.owner['id'] and key['revoked'] == 1
                       and key['token_hash'] == hashlib.sha256(self.revoked['secret'].encode()).hexdigest())
            self.key_source = key['source']
            payload = self.revoked.get('payload')
            if payload is None:
                best = connection.execute('SELECT best_json FROM external_bests WHERE user_id=? AND source=? AND chart_md5=? ORDER BY id LIMIT 1',
                                          (self.owner['id'], self.key_source, self.md5)).fetchone()
                if best is None:
                    raise ValueError('Supply revoked_key.payload when its source has no captured actual best state')
                payload = json.loads(best['best_json'])
            if payload.get('source') != self.key_source or payload.get('chart', {}).get('md5') != self.md5:
                raise ValueError('The revocation probe must use its actual source and captured chart')
            self.rejected_payload = payload
            post = connection.execute('SELECT hidden FROM community_posts WHERE id=?', (self.state['hidden_post_id'],)).fetchone()
            self.check('captured hidden post remains hidden in restored core', post is not None and post['hidden'] == 1)
            moderation = connection.execute("SELECT COUNT(*) FROM community_moderation WHERE post_id=? AND action='hide'",
                                            (self.state['hidden_post_id'],)).fetchone()[0]
            self.check('hidden policy keeps actual maintenance audit', moderation > 0)
            self.hidden_replies = [row[0] for row in connection.execute('SELECT id FROM community_replies WHERE post_id=?',
                                                                      (self.state['hidden_post_id'],))]
            witness = self.manifest['database'].get('walPolicyWitness')
            if self.args.round == 'r2':
                self.check('second restore captured new committed policy still absent from the source main file', witness is not None
                           and witness['liveWalView']['key_revoked'] == 1 and witness['liveWalView']['post_hidden'] == 1
                           and witness['mainFileViewIgnoringWal']['key_revoked'] != 1
                           and witness['mainFileViewIgnoringWal']['post_hidden'] != 1
                           and witness['liveWalView']['revoked_key_id'] == self.revoked['id']
                           and witness['liveWalView']['hidden_post_id'] == self.state['hidden_post_id'])

    def expected_board(self, md5, selected, *, comparable=False, condition=None):
        values = {}
        with closing(sqlite_read(f_file(self.control / 'live.db'))) as live:
            if 'oms' in selected:
                query = '''SELECT s.user_id,MAX(s.metric) metric FROM scores s JOIN score_groups g ON g.id=s.group_id
                           WHERE s.chart_md5=? AND g.public_board=1 AND s.max_ex_score>0'''
                parameters = [md5]
                if condition is not None:
                    query += " AND s.group_id||':'||s.max_ex_score=?"
                    parameters.append(condition)
                for row in live.execute(query + ' GROUP BY s.user_id', parameters):
                    values[('oms', str(row['user_id']))] = row['metric']
            if not comparable:
                for source in EXTERNAL_SOURCES:
                    if source in selected:
                        for row in live.execute('SELECT user_id,MAX(metric) metric FROM external_bests WHERE chart_md5=? AND source=? GROUP BY user_id',
                                                (md5, source)):
                            identity = ('oms', str(row['user_id']))
                            values[identity] = max(values.get(identity, row['metric']), row['metric'])
                hidden = {row[0] for row in live.execute("SELECT player_id FROM archive_visibility WHERE hidden=1 AND chart_md5 IN ('',?)", (md5,))}
            else:
                hidden = set()
        history = {}
        if not comparable and any(source in selected for source in ARCHIVE_SOURCES):
            with closing(sqlite_read(f_file(PUBLIC), immutable=True)) as archive:
                for row in archive.execute('''SELECT b.player_id,b.source_id,b.ex_score,b.max_ex_score,t.value lamp
                        FROM bests b JOIN charts c ON c.id=b.chart_id LEFT JOIN texts t ON t.id=b.lamp_id
                        WHERE c.md5=? AND b.quality_flags=0''', (md5,)):
                    code = next(code for code, value in ARCHIVE_SOURCES.items() if value == row['source_id'])
                    if code in selected and row['player_id'] not in hidden:
                        identity = ('lr2ir', str(row['player_id']))
                        values[identity] = row['ex_score']
                        history[identity] = {'source': code, 'max_ex_score': row['max_ex_score'], 'lamp': row['lamp']}
        counter = Counter(values.values())
        ranks = {}
        above = 0
        for score, count in sorted(counter.items(), reverse=True):
            ranks[score] = above + 1
            above += count
        return values, ranks, history

    def expected_owner_lamps(self, md5, selected, condition=None, comparable=False):
        result = {}
        with closing(sqlite_read(f_file(self.control / 'live.db'))) as live:
            if 'oms' in selected:
                query = '''SELECT s.group_id,s.max_ex_score,MAX(s.clear_lamp) value FROM scores s
                           JOIN score_groups g ON g.id=s.group_id WHERE s.chart_md5=? AND s.user_id=? AND g.public_board=1'''
                parameters = [md5, self.owner['id']]
                if condition is not None:
                    query += " AND s.group_id||':'||s.max_ex_score=?"
                    parameters.append(condition)
                for row in live.execute(query + ' GROUP BY s.group_id,s.max_ex_score', parameters):
                    result['oms:' + row['group_id'] + ':' + str(row['max_ex_score'])] = row['value']
            if not comparable:
                for row in live.execute('SELECT id,source,lamp_value FROM external_bests WHERE user_id=? AND chart_md5=?',
                                        (self.owner['id'], md5)):
                    if row['source'] in selected:
                        result['unknown:' + row['source'] + ':' + str(row['id'])] = row['lamp_value']
        return result

    def board(self, owner, md5, selected=None, *, comparable=False, condition=None):
        chosen = ALL_SOURCES if selected is None else selected
        expected, ranks, historical = self.expected_board(md5, chosen, comparable=comparable, condition=condition)
        params = {'limit': 50, 'page': 1}
        if selected is not None:
            params['sources'] = ','.join(selected)
        if comparable:
            params.update(mode='comparable', condition=condition)
        path = V1 + '/multisource/scores/chart/' + md5
        first = self.api(owner, 'GET', path, params=params)
        label = ('comparable' if comparable else 'reference') + ':' + ','.join(chosen)
        self.check('complete source population ' + label, first['total'] == len(expected) and first['selected_sources'] == chosen,
                   md5=md5, total=first['total'])
        identities = set()
        previous_score = None
        pages = max(1, math.ceil(first['total'] / 50))
        for page_number in range(1, pages + 1):
            page = first if page_number == 1 else self.api(owner, 'GET', path, params={**params, 'page': page_number})
            self.check('global population and owner remain stable across page ' + str(page_number),
                       page['total'] == len(expected) and page['me'] == first['me'] and page['page'] == page_number)
            if len(page['items']) != min(50, max(0, len(expected) - (page_number - 1) * 50)):
                raise AssertionError('Complete source page length differs')
            for row in page['items']:
                identity = (row['identity']['namespace'], row['identity']['id'])
                score = row['score']
                if identity in identities or identity not in expected or score['ex_score'] != expected[identity] \
                        or row['rank'] != ranks[score['ex_score']] or score['source'] not in chosen \
                        or previous_score is not None and previous_score < score['ex_score']:
                    raise AssertionError('Full mixed pagination has a missing/duplicate identity, wrong best score or global rank')
                identities.add(identity)
                previous_score = score['ex_score']
                if identity[0] == 'lr2ir':
                    expected_history = historical[identity]
                    lamp = score['lamp']['value'] if score['lamp'] else None
                    if score['record_kind'] != 'archive_best' or score['played_at'] is not None or row['best_lamps'] != [] \
                            or score['source'] != expected_history['source'] or score['max_ex_score'] != expected_history['max_ex_score'] \
                            or lamp != (expected_history['lamp'] or None) \
                            or not {'sha256', 'played_at'}.issubset(score['unknown_fields']):
                        raise AssertionError('Historical summary lost native unknown/identity semantics')
                elif score['record_kind'] != ('play' if score['source'] == 'oms' else 'best_state') \
                        or score['source'] != 'oms' and score['played_at'] is not None:
                    raise AssertionError('OMS plays and external states lost their distinct semantics')
        self.check('all identities and complete pages verified ' + label, identities == set(expected),
                   md5=md5, pages=pages, rows=len(identities))
        owner_identity = ('oms', str(self.owner['id']))
        mine = first['me']
        if owner_identity in expected:
            self.check('owner best and independent lamps reflect selected range ' + label, mine is not None
                       and (mine['identity']['namespace'], mine['identity']['id']) == owner_identity
                       and mine['score']['ex_score'] == expected[owner_identity] and mine['rank'] == ranks[expected[owner_identity]]
                       and {lamp['family']: lamp['value'] for lamp in mine['best_lamps']}
                       == self.expected_owner_lamps(md5, chosen, condition, comparable))
        else:
            self.check('owner is absent when source/condition excludes them ' + label, mine is None)
        return first

    def run(self):
        self.running_ownership()
        self.check('restored SQLite runtime preserves the required WAL fix', sqlite3.sqlite_version_info >= (3, 51, 3)
                   and sqlite3.sqlite_version == self.manifest['runtime']['sqlite'], version=sqlite3.sqlite_version)
        self.baseline()
        with closing(sqlite_read(f_file(PUBLIC), immutable=True)) as archive:
            metadata = dict(archive.execute('SELECT key,value FROM metadata'))
            charts = archive.execute('SELECT COUNT(*) FROM charts').fetchone()[0]
            summaries = archive.execute('SELECT COUNT(*) FROM bests').fetchone()[0]
        self.check('mounted history is the complete approved public projection', metadata.get('format') == 'oms-lr2ir-public-v1'
                   and metadata.get('complete') == '1' and charts == 334117 and summaries == 25562325,
                   charts=charts, summaries=summaries)
        with httpx.Client(base_url=BASE, timeout=35, trust_env=False) as anon, \
                httpx.Client(base_url=BASE, timeout=35, trust_env=False) as owner, \
                httpx.Client(base_url=BASE, timeout=35, trust_env=False) as other:
            for client, expected_user in ((owner, self.owner), (other, self.other)):
                response = self.request(client, 'POST', V1 + '/auth/login', json={
                    'username': expected_user['username'], 'password': self.state['password'], 'transport': 'browser'}, headers=WEB_HEADERS)
                data = response.json()
                cookies = response.headers.get_list('set-cookie')
                self.check('restored real account login preserves scoped browser identity', data['user'] == expected_user
                           and 'access_token' not in data and len(cookies) == 2
                           and all('Path=/api/ir/v1' in value and 'HttpOnly' in value and 'SameSite=strict' in value for value in cookies))
            self.check('restored own account identity is authoritative', self.api(owner, 'GET', V1 + '/user/me')['user'] == self.owner)
            history = self.api(owner, 'GET', V1 + '/scores/user/' + str(self.owner['id']), params={'limit': 50})
            self.check('private history population retained every actual saved play', history['total'] == len(self.plays), plays=history['total'])
            observed = {}
            for page_number in range(1, max(1, math.ceil(history['total'] / 50)) + 1):
                page = history if page_number == 1 else self.api(owner, 'GET', V1 + '/scores/user/' + str(self.owner['id']),
                                                               params={'limit': 50, 'page': page_number})
                for score in page['items']:
                    uuid = score['submission_id']
                    if uuid not in self.plays or uuid in observed:
                        raise AssertionError('Private UUID history contains an extra or duplicate play')
                    identity, payload = self.plays[uuid]
                    if score['id'] != identity or score['user_id'] != self.owner['id'] \
                            or any(score[field] != value for field, value in payload.items()):
                        raise AssertionError('Private UUID payload or original account changed on recovery')
                    observed[uuid] = identity
            self.check('actual private UUID bytes and account ownership survived', set(observed) == set(self.plays))
            self.api(anon, 'GET', V1 + '/scores/user/' + str(self.owner['id']), status=401)
            self.api(other, 'GET', V1 + '/scores/user/' + str(self.owner['id']), status=403)
            self.check('private history rejects anonymous and other account', True)
            desktop = self.api(anon, 'POST', V1 + '/auth/login', json={
                'username': self.owner['username'], 'password': self.state['password'], 'transport': 'desktop'})
            play_id, payload = self.plays[self.state['submission_id']]
            retry = self.api(anon, 'POST', V1 + '/scores/submit', json=payload,
                             headers={'Authorization': 'Bearer ' + desktop['access_token']})
            self.check('saved actual OMS UUID retry preserves exactly one original play', retry['duplicate']
                       and retry['score']['id'] == play_id and retry['score']['user_id'] == self.owner['id']
                       and retry['score']['submission_id'] == self.state['submission_id'])
            after_retry = self.api(owner, 'GET', V1 + '/scores/user/' + str(self.owner['id']), params={'limit': 1})
            self.check('UUID retry did not invent a new play', after_retry['total'] == len(self.plays))
            index = self.api(anon, 'GET', '/api/ir/v2/charts', params={'limit': 1})
            self.check('actual full historical chart index remains queryable', index['total'] >= charts, total=index['total'])
            sources = self.api(anon, 'GET', '/api/ir/v2/sources')['items']
            self.check('all approved source qualifications remain honest', [item['code'] for item in sources] == ALL_SOURCES
                       and all(item['available'] for item in sources)
                       and all(item['record_kind'] == 'archive_best' for item in sources if item['code'] in ARCHIVE_SOURCES))
            boards = [self.board(owner, self.md5), self.board(owner, self.md5, ['oms']),
                      self.board(owner, self.md5, ['lr2oraja_ed']), self.board(owner, self.md5, ['oms', 'lr2oraja_ed']),
                      self.board(owner, self.md5, list(ARCHIVE_SOURCES)), self.board(owner, self.md5, [])]
            for source in ARCHIVE_SOURCES:
                self.board(owner, self.md5, [source])
            self.board(owner, self.md5, comparable=True, condition=self.state['condition'])
            large = self.state.get('large_board_md5')
            if large is not None and large != self.md5:
                if not re.fullmatch(r'[0-9a-f]{32}', large):
                    raise ValueError('The separately specified large public chart identity is invalid')
                self.board(owner, large)
            public = self.api(anon, 'GET', V1 + '/users/' + str(self.owner['id']) + '/public-bests',
                              params={'ruleset': 'bms', 'keymode': 'bms_7k', 'sources': 'oms,lr2oraja_ed'})
            public_bytes = json.dumps([*boards, public])
            self.check('public views expose neither actual private UUIDs nor original integration secret',
                       all(uuid not in public_bytes for uuid in self.plays) and self.revoked['secret'] not in public_bytes)
            keys = self.api(owner, 'GET', V1 + '/integration-keys')['items']
            self.check('key management retained actual revoked record', any(key['id'] == self.revoked['id'] and key['revoked'] == 1 for key in keys))
            rejection = self.api(anon, 'POST', '/api/ir/v2/external/update', status=401,
                                 json=self.rejected_payload, headers={'Authorization': 'Bearer ' + self.revoked['secret']})
            self.check('captured revoked secret cannot update external best after real restart',
                       rejection['error']['code'] == 'invalid_integration_key')
            post_id = self.state['hidden_post_id']
            for client in (anon, owner):
                self.api(client, 'GET', V1 + '/community/posts/' + str(post_id), status=404)
                self.api(client, 'GET', V1 + '/community/posts/' + str(post_id) + '/replies', status=404)
            self.request(anon, 'GET', '/community/' + str(post_id), status=404)
            for reply_id in self.hidden_replies:
                self.api(owner, 'POST', V1 + '/community/replies/' + str(reply_id) + '/edit', status=404,
                         json={'body': 'recovery hidden-policy probe'}, headers=WEB_HEADERS)
            self.check('hidden post and replies stay unreadable and uneditable after restart', True, hiddenReplies=len(self.hidden_replies))
            for route in ('/', '/news', '/download', '/help', '/credits', '/account', '/ir?md5=' + self.md5,
                          '/users/' + str(self.owner['id']), '/rankings', '/community'):
                response = self.request(anon, 'GET', route)
                self.check('restored native page ' + route.split('?')[0], 'OMS' in response.text
                           and 'no-cache' in response.headers.get('cache-control', '')
                           and self.revoked['secret'] not in response.text and self.state['password'] not in response.text
                           and all(uuid not in response.text for uuid in self.plays))
            home = self.request(owner, 'GET', '/')
            self.check('homepage keeps scoped-cookie and security boundary', 'cookie' not in home.request.headers
                       and home.headers.get('x-content-type-options') == 'nosniff' and home.headers.get('referrer-policy') == 'same-origin')
            asset_path = f_file(self.web / 'public/assets/manifest.json')
            manifest_response = self.request(anon, 'GET', '/assets/manifest.json')
            self.check('HTTP generated manifest matches restored bytes', hashlib.sha256(manifest_response.content).hexdigest() == file_digest(asset_path))
            assets = json.loads(asset_path.read_text())
            asset_bytes = 0
            for value in sorted(set(assets.values())):
                if not isinstance(value, str) or not value.startswith('/assets/'):
                    raise ValueError('Generated manifest contains an unexpected asset route')
                local = f_file(self.web / ('public' + value))
                response = self.request(anon, 'GET', value)
                asset_bytes += len(response.content)
                self.check('restored built asset actual HTTP bytes', hashlib.sha256(response.content).hexdigest() == file_digest(local))
            adapters = self.control / 'legacy-ir/adapters'
            version_response = self.request(anon, 'GET', '/ir/adapters/versions.json')
            self.check('real published adapter manifest survives restart', hashlib.sha256(version_response.content).hexdigest()
                       == file_digest(f_file(adapters / 'versions.json')))
            versions = version_response.json()
            for item in versions['items']:
                name = item['file']
                if not isinstance(name, str) or '/' in name or '\\' in name or name in ('.', '..'):
                    raise ValueError('Unexpected published adapter file path')
                response = self.request(anon, 'GET', '/ir/adapters/' + name)
                self.check('real published adapter bytes and declared SHA remain exact', hashlib.sha256(response.content).hexdigest()
                           == item['sha256'] == file_digest(f_file(adapters / name)))
            self.request(anon, 'GET', '/ir/adapters/not-approved.jar', status=404)
            for route in ('/.env', '/.dev-cache/local-runtime/live.db', '/storage/logs/laravel.log', '/vendor/autoload.php'):
                response = self.request(anon, 'GET', route, status=(403, 404))
                self.check('runtime data is not a public resource ' + route, response.status_code in (403, 404))
            self.api(owner, 'POST', V1 + '/auth/logout', status=204, json={}, headers=WEB_HEADERS)
            self.api(owner, 'GET', V1 + '/user/me', status=401)
            self.check('restored account logout still removes access', True)
            self.report.update(assetBytesReceived=asset_bytes, generatedAssetsVerified=len(set(assets.values())),
                               realAdaptersVerified=len(versions['items']), fullPublicProjectionCharts=charts,
                               fullPublicProjectionSummaries=summaries)
        self.report['complete'] = True
        self.report['httpVerified'] = True

    def save(self, elapsed):
        self.report.update(completedAt=datetime.now(timezone.utc).isoformat(), durationSeconds=round(elapsed, 3),
                           requests=self.requests, httpVerified=self.report.get('httpVerified', False))
        with self.output.open('x', encoding='utf-8') as output:
            json.dump(self.report, output, ensure_ascii=False, indent=2)
            output.write('\n')
        self.output.chmod(0o600)
        print(json.dumps({'round': self.args.round, 'complete': self.report.get('complete', False),
                          'checks': len(self.report['checks']), 'httpVerified': self.report.get('httpVerified', False),
                          'playerAcceptance': False, 'productionDeployment': False}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--restore-root', required=True)
    parser.add_argument('--acceptance-state', required=True)
    parser.add_argument('--round', choices=('r1', 'r2'), required=True)
    parser.add_argument('--report')
    args = parser.parse_args()
    verification = Verification(args)
    started = time.monotonic()
    try:
        verification.run()
    finally:
        verification.save(time.monotonic() - started)


if __name__ == '__main__':
    main()
