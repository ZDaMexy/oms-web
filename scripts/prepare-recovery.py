# Licensed under AGPL-3.0-or-later; see LICENCE.
"""Prepare isolated recovery policy and capture it; root must freeze other local writers first."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
from uuid import uuid4

import httpx


WEB = Path('/mnt/f/zdamexy-workspace/websites/oms-web')
BACKEND = Path('/mnt/f/zdamexy-workspace/oms-server/oms-backend')
CONTROL = WEB / '.dev-cache/local-runtime'
LIVE = CONTROL / 'live.db'
PYTHON = WEB / '.dev-cache/backend-venv/bin/python'
BASE = 'http://127.0.0.1:8090'
V1 = '/api/ir/v1'


def regular_task_file(filename):
    if filename.resolve() != filename or filename.is_symlink() or not filename.is_file():
        raise ValueError('A fixed local task file is unavailable or symbolic')
    return filename


def readonly_database():
    connection = sqlite3.connect(LIVE.as_uri() + '?mode=ro', uri=True, isolation_level=None, timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA query_only=ON')
    return connection


def new_json(filename, value):
    # The file is protected at creation, before any test password or original key secret is written.
    descriptor = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8') as output:
        json.dump(value, output, ensure_ascii=False, indent=2)
        output.write('\n')
        output.flush()
        os.fsync(output.fileno())


class Preparation:
    def __init__(self, args):
        if sys.platform != 'linux' or sqlite3.sqlite_version_info < (3, 51, 3):
            raise ValueError('Run in the existing Alpine WSL with the required SQLite WAL fix')
        self.args = args
        self.round = args.round
        self.reader = None
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.report = {'round': self.round, 'startedAt': self.started_at, 'complete': False,
                       'phase': 'preflight', 'rootMustFreezeOtherLocalWriters': True,
                       'onlyTaskOwnedLocalDatabase': True, 'base': BASE,
                       'playerAcceptance': False, 'productionDeployment': False}
        for directory in (WEB, BACKEND, CONTROL, WEB / 'artifacts'):
            if not directory.is_dir() or directory.resolve() != directory or directory.is_symlink():
                raise ValueError('A fixed task directory is unavailable or symbolic')
        regular_task_file(LIVE)
        regular_task_file(WEB / 'scripts/snapshot-local.py')
        if not re.fullmatch(r'/usr/bin/python3(?:\.\d+)?', str(PYTHON.resolve())):
            raise ValueError('Use the task venv bound to the recorded installed OS Python')
        self.state_path = CONTROL / ('recovery-state-' + self.round + '.json')
        self.key_journal = CONTROL / ('recovery-created-key-' + self.round + '.json')
        self.report_path = WEB / ('artifacts/prepare-recovery-' + self.round + '.json')
        self.hide_log = WEB / ('artifacts/prepare-recovery-' + self.round + '-hide.log')
        self.snapshot_log = WEB / ('artifacts/prepare-recovery-' + self.round + '-snapshot.log')
        for filename in (self.state_path, self.key_journal, self.report_path, self.hide_log, self.snapshot_log,
                         WEB / ('artifacts/local-recovery/' + self.round)):
            if os.path.lexists(filename):
                raise FileExistsError('An existing recovery round or evidence file must remain untouched: ' + str(filename))
        self.original = json.loads(regular_task_file(CONTROL / 'acceptance-state.json').read_text())
        self.owner = self.original['users'][0]
        if self.original['usernames'][0] != self.owner['username'] or type(self.owner['id']) is not int \
                or self.owner['id'] <= 0 or not isinstance(self.original['password'], str) or not self.original['password']:
            raise ValueError('The latest task-owned acceptance account state is incomplete')
        self.headers = {'Origin': BASE, 'X-OMS-IR': '1', 'X-OMS-Actor': str(self.owner['id'])}
        self.environment = {**os.environ, 'PYTHONPATH': str(BACKEND), 'PYTHONDONTWRITEBYTECODE': '1',
                            'TMPDIR': str(WEB / '.dev-cache/temp')}
        for service in ('nginx', 'php-fpm', 'backend', 'catalog'):
            pid = int(regular_task_file(CONTROL / (service + '.pid')).read_text())
            command = (Path('/proc') / str(pid) / 'cmdline').read_bytes().replace(b'\0', b' ')
            if str(WEB).encode() not in command:
                raise ValueError('The loopback stack must belong to the original task checkout before preparation')
        connection = readonly_database()
        try:
            if connection.execute('PRAGMA user_version').fetchone()[0] != 3 \
                    or connection.execute('PRAGMA journal_mode').fetchone()[0] != 'wal':
                raise ValueError('The original running task database must be current schema 3 in WAL mode')
            row = connection.execute('SELECT username FROM users WHERE id=?', (self.owner['id'],)).fetchone()
            if row is None or row['username'] != self.owner['username']:
                raise ValueError('The current acceptance account does not own this task database identity')
        finally:
            connection.close()

    def api(self, client, method, route, *, status=200, **kwargs):
        response = client.request(method, route, **kwargs)
        if response.status_code != status:
            # API bodies, passwords, cookies and bearer secrets never enter console or public reports.
            raise RuntimeError('Actual local HTTP ' + method + ' ' + route + ' returned '
                               + str(response.status_code) + ', expected ' + str(status))
        return response.json() if response.content else None

    def policy(self, connection):
        key = connection.execute('SELECT user_id,source,token_hash,revoked FROM integration_keys WHERE id=?',
                                 (self.key['id'],)).fetchone()
        post = connection.execute('SELECT user_id,deleted,hidden FROM community_posts WHERE id=?', (self.post_id,)).fetchone()
        if key is None or post is None or key['user_id'] != self.owner['id'] or post['user_id'] != self.owner['id'] \
                or key['source'] != 'lr2oraja_ed' or key['token_hash'] != hashlib.sha256(self.secret.encode()).hexdigest() \
                or post['deleted'] != 0:
            raise ValueError('The prepared key or independent post lost its actual source/account ownership')
        return {'key_revoked': key['revoked'], 'post_hidden': post['hidden']}

    def child(self, command, log):
        result = subprocess.run(command, cwd=WEB, env=self.environment, text=True, capture_output=True)
        descriptor = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, 'w', encoding='utf-8') as output:
            output.write(result.stdout)
            output.write(result.stderr)
        result.check_returncode()
        return result.stdout

    def run(self):
        with httpx.Client(base_url=BASE, timeout=35, trust_env=False, follow_redirects=False) as owner:
            self.report['phase'] = 'browser-login'
            login = self.api(owner, 'POST', V1 + '/auth/login', json={
                'username': self.owner['username'], 'password': self.original['password'], 'transport': 'browser'},
                headers={'Origin': BASE, 'X-OMS-IR': '1'})
            if login.get('user') != self.owner or 'access_token' in login \
                    or self.api(owner, 'GET', V1 + '/user/me')['user'] != self.owner:
                raise ValueError('The real browser login did not preserve the original OMS account')
            self.report['phase'] = 'create-new-source-key'
            created = self.api(owner, 'POST', V1 + '/integration-keys', status=201, headers=self.headers,
                               json={'source': 'lr2oraja_ed', 'label': 'local recovery ' + self.round + ' only'})
            self.key, self.secret = created['key'], created['secret']
            if self.key['source'] != 'lr2oraja_ed' or self.key['revoked'] != 0 or not isinstance(self.secret, str) or not self.secret:
                raise ValueError('Actual source key creation returned an unexpected state')
            # Preserve the one-time secret even if a later post, hide or snapshot operation fails.
            new_json(self.key_journal, {'round': self.round, 'owner_id': self.owner['id'],
                                        'key': self.key, 'secret': self.secret, 'createdAt': self.started_at})
            self.report['createdKeyId'] = self.key['id']
            self.report['phase'] = 'create-independent-plaintext-post'
            posted = self.api(owner, 'POST', V1 + '/community/posts', status=201, headers=self.headers,
                              json={'submission_id': str(uuid4()), 'title': '恢复检查 ' + self.round,
                                    'category': 'discussion', 'body': '本地恢复检查。仅为隔离测试数据。'})
            self.post_id = posted['post']['id']
            if posted['duplicate'] or posted['post']['author'] != self.owner or posted['post']['deleted']:
                raise ValueError('Actual plain-text post creation did not create this owner\'s independent content')
            self.report['createdPostId'] = self.post_id
            state = {**self.original, 'revoked_key': {'id': self.key['id'], 'secret': self.secret},
                     'hidden_post_id': self.post_id}
            state.pop('hidden_reply_id', None)
            if self.args.with_reply:
                self.report['phase'] = 'create-independent-plaintext-reply'
                reply = self.api(owner, 'POST', V1 + '/community/posts/' + str(self.post_id) + '/replies', status=201,
                                 headers=self.headers, json={'submission_id': str(uuid4()), 'body': '本地恢复检查回复。'})
                if reply['duplicate'] or reply['reply']['author'] != self.owner or reply['reply']['post_id'] != self.post_id:
                    raise ValueError('Actual reply creation did not preserve the new thread and account')
                state['hidden_reply_id'] = reply['reply']['id']
                self.report['createdReplyId'] = reply['reply']['id']
            # Write once. Policy names identify the forthcoming test targets; success is checked against actual core rows.
            new_json(self.state_path, state)
            self.report['stateFile'] = str(self.state_path)
            connection = readonly_database()
            try:
                if self.policy(connection) != {'key_revoked': 0, 'post_hidden': 0}:
                    raise ValueError('Fresh key and post must be committed, active and visible before policy preparation')
            finally:
                connection.close()
            if self.round == 'r2':
                self.report['phase'] = 'checkpoint-fresh-visible-baseline'
                self.reader = sqlite3.connect(LIVE.as_uri() + '?mode=rw', uri=True, isolation_level=None, timeout=5)
                self.reader.row_factory = sqlite3.Row
                checkpoint = self.reader.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone()
                if tuple(checkpoint) != (0, 0, 0):
                    raise RuntimeError('The actual baseline checkpoint is busy or incomplete; keep the evidence and stop other writers')
                self.report['baselineCheckpoint'] = list(checkpoint)
                self.reader.execute('PRAGMA query_only=ON')
                self.reader.execute('BEGIN')
                if self.policy(self.reader) != {'key_revoked': 0, 'post_hidden': 0}:
                    raise ValueError('The pinned read transaction does not retain the old active/visible baseline')
                self.report['oldReaderPinnedBeforePolicy'] = True
            self.report['phase'] = 'revoke-through-actual-browser-api'
            revoked = self.api(owner, 'POST', V1 + '/integration-keys/' + str(self.key['id']) + '/revoke',
                               headers=self.headers, json={})
            if revoked != {'revoked': True}:
                raise ValueError('Actual browser key revocation did not return its declared result')
            self.report['phase'] = 'hide-through-existing-maintenance-cli'
            self.child([str(PYTHON), '-m', 'oms_ir', 'hide-post', '--db', str(LIVE), '--post-id', str(self.post_id),
                        '--reason', 'OMS Web local recovery ' + self.round + ': synthetic independent test post only'], self.hide_log)
            connection = readonly_database()
            try:
                if self.policy(connection) != {'key_revoked': 1, 'post_hidden': 1}:
                    raise ValueError('Actual API/CLI policy changes were not committed to the current WAL view')
                if connection.execute("SELECT COUNT(*) FROM community_moderation WHERE post_id=? AND action='hide'",
                                      (self.post_id,)).fetchone()[0] != 1:
                    raise ValueError('The new independent hide does not have exactly one maintenance audit record')
            finally:
                connection.close()
            if self.reader is not None and self.policy(self.reader) != {'key_revoked': 0, 'post_hidden': 0}:
                raise ValueError('The old reader stopped retaining the pre-policy baseline')
            self.report['phase'] = 'sqlite-backup-api-snapshot'
            command = [str(PYTHON), str(WEB / 'scripts/snapshot-local.py'), '--round', self.round,
                       '--task-owned-test-data', '--acceptance-state', str(self.state_path)]
            if self.round == 'r2':
                command.append('--require-wal-policy-delta')
            snapshot = json.loads(self.child(command, self.snapshot_log))
            if snapshot.get('round') != self.round or snapshot.get('sqliteIntegrityCheck') != 'ok' \
                    or snapshot.get('walPolicyDeltaCaptured') != (self.round == 'r2') \
                    or snapshot.get('publicProjectionCopied') is not False or snapshot.get('httpVerified') is not False:
                raise ValueError('The actual snapshot command did not produce the expected local recovery evidence')
            if self.reader is not None and self.policy(self.reader) != {'key_revoked': 0, 'post_hidden': 0}:
                raise ValueError('The old baseline reader was not held through the entire snapshot subprocess')
            self.report.update(phase='policy-and-snapshot-complete', complete=True, snapshot=snapshot,
                               readerHeldThroughSnapshot=self.reader is not None,
                               privateStateAndOneTimeSecretRemainOutsideRecoveryArchive=True)

    def finish(self):
        if self.reader is not None:
            try:
                self.reader.rollback()
            finally:
                self.reader.close()
        self.report['completedAt'] = datetime.now(timezone.utc).isoformat()
        new_json(self.report_path, self.report)
        print(json.dumps({'round': self.round, 'complete': self.report['complete'], 'phase': self.report['phase'],
                          'stateFile': self.report.get('stateFile'), 'snapshotCaptured': self.report['complete'],
                          'playerAcceptance': False, 'productionDeployment': False}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--round', choices=('r1', 'r2'), required=True)
    parser.add_argument('--with-reply', action='store_true', help='Create one actual plain-text reply before the policy baseline')
    args = parser.parse_args()
    preparation = Preparation(args)
    try:
        preparation.run()
    finally:
        preparation.finish()


if __name__ == '__main__':
    main()
