"""Actual loopback HTTP gates; synthetic local writes are not player acceptance."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import secrets
import sqlite3
import time
from uuid import uuid4

import httpx

ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / ".dev-cache/local-runtime"
BASE = "http://127.0.0.1:8090"
V1 = "/api/ir/v1"
WEB = {"Origin": BASE, "X-OMS-IR": "1"}
report = {"started_at": datetime.now(timezone.utc).isoformat(), "base": BASE,
          "data": "synthetic local accounts; complete approved public projection", "checks": []}


def check(name, condition, **evidence):
    report["checks"].append({"name": name, "passed": bool(condition), **evidence})
    if not condition:
        raise AssertionError(name)


def api(client, method, path, status=200, **kwargs):
    response = client.request(method, path, **kwargs)
    if response.status_code != status:
        problem = response.json().get("error", {}) if "application/json" in response.headers.get("content-type", "") else {}
        raise AssertionError(f"{method} {path.split('?')[0]} status {response.status_code}, expected {status}; {problem.get('code')}")
    return response.json() if response.content else None


def play(md5, ruleset="bms"):
    chart_raw = f"Explicit local migration verification: {ruleset}".encode()
    payload = {
        "schema_version": 1, "submission_id": str(uuid4()), "ruleset": ruleset,
        "chart": {"md5": md5, "sha256": hashlib.sha256(chart_raw).hexdigest(),
                  "title": "本地迁移验收（合成成绩）", "artist": "OMS verification", "difficulty": "verification"},
        "keymode": "bms_7k" if ruleset == "bms" else "mania_4k", "played_at": "2026-10-07T00:00:00Z",
        "client_version": "OMS-local-migration-verification", "total_score_version": 30000016,
        "total_score": 175 if ruleset == "bms" else 900000, "accuracy": 0.95, "max_combo": 80, "passed": True,
        "statistics": {"perfect": 80, "great": 15, "good": 2, "miss": 3, "ok": 3},
        "maximum_statistics": {"perfect": 100}, "mods": [], "ruleset_data": None, "bms_chart": None,
    }
    if ruleset == "bms":
        payload["ruleset_data"] = {
            "version": 7, "gauge_type": "Normal", "gauge_rules_family": "Legacy", "gauge_auto_shift": False,
            "starting_gauge_type": "Normal", "floor_gauge_type": "Normal", "long_note_mode": "LN",
            "judge_mode": "OD", "clear_lamp": 4, "final_gauge": 0.85,
        }
        payload["bms_chart"] = {"judge_rank": 2, "branch_policy": "fixed-1-v1"}
    return payload


def main():
    archive = Path("/mnt/f/zdamexy-workspace/oms/artifacts/oms-ir-multisource-20261004/archive/lr2ir-public-v1.db")
    with sqlite3.connect(archive.as_uri() + "?mode=ro&immutable=1", uri=True) as connection:
        metadata = dict(connection.execute("SELECT key,value FROM metadata"))
        counts = {"charts": connection.execute("SELECT COUNT(*) FROM charts").fetchone()[0],
                  "summaries": connection.execute("SELECT COUNT(*) FROM bests").fetchone()[0]}
    check("complete public projection is read-only", metadata["complete"] == "1" and counts == {"charts": 334117, "summaries": 25562325}, **counts)
    with httpx.Client(base_url=BASE, timeout=35, trust_env=False) as anon, httpx.Client(base_url=BASE, timeout=35, trust_env=False) as owner, httpx.Client(base_url=BASE, timeout=35, trust_env=False) as other:
        first = api(anon, "GET", "/api/ir/v2/charts?limit=1")
        md5 = first["items"][0]["chart"]["md5"]
        check("full chart index includes historical projection", first["total"] >= counts["charts"], total=first["total"])
        board_path = V1 + "/multisource/scores/chart/" + md5
        previous = api(anon, "GET", board_path)
        previous_oms = api(anon, "GET", board_path + "?sources=oms")
        previous_ed = api(anon, "GET", board_path + "?sources=lr2oraja_ed")
        suffix = secrets.token_hex(4)
        password = secrets.token_urlsafe(24)
        usernames = ["local_test_a_" + suffix, "local_test_b_" + suffix]
        users = []
        for client, username in zip((owner, other), usernames):
            response = client.post(V1 + "/auth/register", json={"username": username, "password": password, "transport": "browser"}, headers=WEB)
            cookies = response.headers.get_list("set-cookie")
            check("same-origin registration uses only scoped cookies", response.status_code == 201 and len(cookies) == 2 and all("Path=/api/ir/v1" in value and "HttpOnly" in value and "SameSite=strict" in value for value in cookies), status=response.status_code)
            users.append(response.json()["user"])
            check("browser transport exposes no bearer", "access_token" not in response.json())
        me = api(owner, "GET", V1 + "/user/me")
        check("browser account is OMS authority", me["user"] == users[0])
        html = owner.get("/account")
        check("HTML request does not widen cookie scope", html.status_code == 200 and "cookie" not in html.request.headers and password not in html.text)
        api(owner, "POST", V1 + "/integration-keys", status=403, json={"source": "lr2oraja_ed", "label": "cross-origin rejected"}, headers={"Origin": "https://invalid.example", "X-OMS-IR": "1"})
        check("cross-origin key write is rejected", True)
        api(anon, "POST", V1 + "/auth/login", status=403, json={"username": usernames[0], "password": password, "transport": "desktop"}, headers={"Sec-Fetch-Site": "same-origin"})
        check("browser cannot request desktop transport", True)
        desktop = api(anon, "POST", V1 + "/auth/login", json={"username": usernames[0], "password": password, "transport": "desktop"})
        bearer = {"Authorization": "Bearer " + desktop["access_token"]}
        original = play(md5)
        saved = api(anon, "POST", V1 + "/scores/submit", status=201, json=original, headers=bearer)
        repeated = api(anon, "POST", V1 + "/scores/submit", json=original, headers=bearer)
        check("saved OMS UUID retry preserves account and one play", repeated["duplicate"] and saved["score"]["id"] == repeated["score"]["id"])
        changed = deepcopy(original)
        changed["max_combo"] = 70
        api(anon, "POST", V1 + "/scores/submit", status=409, json=changed, headers=bearer)
        lower = play(md5)
        lower["statistics"] = {"perfect": 50, "great": 0}
        lower["ruleset_data"]["clear_lamp"] = 6
        api(anon, "POST", V1 + "/scores/submit", status=201, json=lower, headers=bearer)
        key = api(owner, "POST", V1 + "/integration-keys", status=201, json={"source": "lr2oraja_ed", "label": "local verification only"}, headers=WEB)
        integration = {"Authorization": "Bearer " + key["secret"]}
        stats = dict.fromkeys(("pg", "gr", "gd", "bd", "pr", "max_combo", "minbp", "epg", "lpg", "egr", "lgr", "egd", "lgd", "ebd", "lbd", "epr", "lpr", "ems", "lms", "passnotes", "avgjudge"))
        stats.update(pg=90, gr=0, gd=0, bd=0, pr=0, max_combo=90, minbp=0, epg=90, lpg=0, egr=0, lgr=0, egd=0, lgd=0, ebd=0, lbd=0, epr=0, lpr=0, ems=0, lms=0, passnotes=90)
        observation = {"source": "lr2oraja_ed", "client_version": "v0.4.0", "adapter_version": "local-verification",
                       "chart": original["chart"], "keymode": "bms_7k", "ex_score": 180, "max_ex_score": 200,
                       "played_at": None, "native_lamp": {"value": 5},
                       "conditions": {"gauge": 2, "lntype": 0, "option": 0, "assist": 0, "seed": 0,
                                      "device_type": None, "judge_algorithm": None, "rule": None, "skin": None,
                                      "chart_has_cn": False, "chart_has_hcn": False, "chart_has_random": False},
                       "unknown_fields": ["judge_algorithm", "total", "branch_policy", "assist"], "statistics": stats, "eligibility": "host-approved"}
        updated = api(anon, "POST", "/api/ir/v2/external/update", json=observation, headers=integration)
        duplicated = api(anon, "POST", "/api/ir/v2/external/update", json=observation, headers=integration)
        check("external best update has no invented play history", updated["updated"] and not duplicated["updated"])
        with sqlite3.connect((CONTROL / "live.db").as_uri() + "?mode=ro", uri=True) as connection:
            check("OMS plays and external state stay distinct", connection.execute("SELECT COUNT(*) FROM scores WHERE user_id=?", (users[0]["id"],)).fetchone()[0] == 2 and connection.execute("SELECT COUNT(*) FROM external_bests WHERE user_id=?", (users[0]["id"],)).fetchone()[0] == 1)
        all_board = api(owner, "GET", board_path + "?limit=20")
        mine = all_board["me"]
        check("reference union uses one OMS identity with independent lamps", all_board["total"] == previous["total"] + 1 and mine["score"]["source"] == "lr2oraja_ed" and {lamp["source"]: lamp["value"] for lamp in mine["best_lamps"]} == {"oms": 6, "lr2oraja_ed": 5}, historical_players=previous["total"], union_players=all_board["total"])
        full_pages = [api(owner, "GET", board_path + f"?limit=20&page={page}") for page in range(1, (all_board["total"] + 19) // 20 + 1)]
        rows = [row for page in full_pages for row in page["items"]]
        check("complete mixed pagination has global ranks and no duplicate identity", len(rows) == all_board["total"] and len({(row["identity"]["namespace"], row["identity"]["id"]) for row in rows}) == len(rows) and all(page["me"]["rank"] == mine["rank"] for page in full_pages), pages=len(full_pages), rows=len(rows))
        check("history retains unknown time and native lamp", all(row["score"]["played_at"] is None and row["best_lamps"] == [] for row in rows if row["identity"]["namespace"] == "lr2ir"))
        oms_board = api(owner, "GET", board_path + "?sources=oms")
        ed_board = api(owner, "GET", board_path + "?sources=lr2oraja_ed")
        check("source selection changes score lamp population and rank", oms_board["total"] == previous_oms["total"] + 1 and ed_board["total"] == previous_ed["total"] + 1 and oms_board["me"]["score"]["ex_score"] == 175 and ed_board["me"]["score"]["ex_score"] == 180 and ed_board["me"]["rank"] == 1 and len(ed_board["me"]["best_lamps"]) == 1)
        empty = api(owner, "GET", board_path + "?sources=")
        check("explicit empty source returns empty", empty["total"] == 0 and empty["items"] == [] and empty["me"] is None)
        condition = saved["score"]["group_id"] + ":200"
        compared = api(owner, "GET", board_path, params={"mode": "comparable", "condition": condition})
        check("same condition excludes unproven historical and external states", compared["total"] >= 1 and compared["me"]["score"]["source"] == "oms" and all(row["score"]["source"] == "oms" for row in compared["items"]))
        personal = api(owner, "GET", V1 + f"/users/{users[0]['id']}/public-bests?ruleset=bms&keymode=bms_7k&sources=oms,lr2oraja_ed")
        check("public profile never exposes UUID or keys", all(original["submission_id"] not in json.dumps(value) and key["secret"] not in json.dumps(value) for value in (personal, all_board)))
        private = api(owner, "GET", V1 + f"/scores/user/{users[0]['id']}")
        check("private history is actual own UUID plays", private["total"] == 2)
        api(other, "GET", V1 + f"/scores/user/{users[0]['id']}", status=403)
        post_payload = {"submission_id": str(uuid4()), "title": "本地迁移验收（测试）", "category": "discussion", "body": '第一行\n<script>alert("unsafe")</script> https://example.com/'}
        posted = api(owner, "POST", V1 + "/community/posts", status=201, json=post_payload, headers=WEB)
        retry_post = api(owner, "POST", V1 + "/community/posts", json=post_payload, headers=WEB)
        post_id = posted["post"]["id"]
        check("community retry preserves submission identity", retry_post["duplicate"] and retry_post["post"]["id"] == post_id)
        stale_headers = {**WEB, "X-OMS-Actor": str(users[0]["id"])}
        api(other, "POST", V1 + "/community/posts", status=409, json={**post_payload, "submission_id": str(uuid4())}, headers=stale_headers)
        api(other, "POST", V1 + "/integration-keys", status=409, json={"source": "lr2oraja_ed", "label": "stale tab"}, headers=stale_headers)
        check("switched browser cookie cannot silently replace draft or key actor", True)
        reply_payload = {"submission_id": str(uuid4()), "body": "本地回复验证"}
        reply = api(owner, "POST", V1 + f"/community/posts/{post_id}/replies", status=201, json=reply_payload, headers=WEB)
        api(other, "POST", V1 + f"/community/posts/{post_id}/edit", status=403, json={"title": "not mine", "category": "discussion", "body": "not mine"}, headers=WEB)
        page = owner.get(f"/community/{post_id}")
        check("native community SSR escapes plaintext and keeps lines", page.status_code == 200 and "&lt;script&gt;" in page.text and '<script>alert("unsafe")</script>' not in page.text and "第一行\n" in page.text)
        search = anon.get("/community", params={"q": "本地迁移验收", "category": ""})
        check("community all-category search accepts native empty form value", search.status_code == 200 and "本地迁移验收（测试）" in search.text)
        old_url = anon.get(f"/community/posts/{post_id}?reply_page=2", follow_redirects=False)
        check("old community URL retains query", old_url.status_code == 302 and "reply_page=2" in old_url.headers["location"])
        mania_md5 = hashlib.md5(b"Explicit local mania verification").hexdigest()
        mania = play(mania_md5, "mania")
        api(anon, "POST", V1 + "/scores/submit", status=201, json=mania, headers=bearer)
        mania_page = anon.get(f"/beatmaps?ruleset=mania&md5={mania_md5}")
        check("mania MD5-only board does not invent mirror SID", mania_page.status_code == 200 and mania_md5 in mania_page.text)
        for path in ("/", "/news", "/news/2026-10-05-ir-trial", "/download", "/help", "/credits", "/account", "/ir", "/ir?md5=" + md5, "/users/" + str(users[0]["id"]), "/rankings", "/community", "/community/new", "/beatmapsets?ruleset=mania&keys=mania_4k"):
            response = anon.get(path)
            check("native page " + path.split("?")[0], response.status_code == 200 and "OMS" in response.text and "no-cache" in response.headers.get("cache-control", ""))
        for path in ("/.env", "/vendor/autoload.php", "/storage/logs/laravel.log", "/.dev-cache/local-runtime/live.db", "/index.php/anything", "/INDEX.PHP", "/chat", "/store", "/beatmapsets?q=x&ruleset[]=bms"):
            response = anon.get(path)
            check("unserved path " + path.split("?")[0], response.status_code in (403, 404, 422))
        adapter = anon.get("/ir/adapters/versions.json")
        check("published real adapters remain available", adapter.status_code == 200)
        check("unknown adapter is rejected", anon.get("/ir/adapters/not-approved.jar").status_code == 404)
        oversized = anon.post(V1 + "/auth/login", content="x" * 65537, headers={"Content-Type": "application/json"})
        check("64 KiB boundary returns actual OMS JSON", oversized.status_code == 413 and oversized.json()["error"]["code"] == "body_too_large")
        check("HTML security headers survive cache headers", anon.get("/").headers.get("x-content-type-options") == "nosniff" and anon.get("/").headers.get("referrer-policy") == "same-origin")
        api(owner, "POST", V1 + f"/integration-keys/{key['key']['id']}/revoke", json={}, headers=WEB)
        api(anon, "POST", "/api/ir/v2/external/update", status=401, json=observation, headers=integration)
        check("key revocation immediately rejects update", True)
        api(owner, "POST", V1 + "/auth/logout", status=204, json={}, headers=WEB)
        api(owner, "GET", V1 + "/user/me", status=401)
        api(owner, "POST", V1 + "/community/posts", status=401, json={**post_payload, "submission_id": str(uuid4())}, headers=WEB)
        check("logout rejects authenticated writes", True)
        state = {"usernames": usernames, "password": password, "users": users, "md5": md5,
                 "mania_md5": mania_md5, "post_id": post_id, "reply_id": reply["reply"]["id"],
                 "condition": condition, "submission_id": original["submission_id"]}
        (CONTROL / "acceptance-state.json").write_text(json.dumps(state), encoding="utf-8")
        (CONTROL / "acceptance-state.json").chmod(0o600)
    report["complete"] = True


if __name__ == "__main__":
    began = time.monotonic()
    try:
        main()
    finally:
        report["duration_seconds"] = round(time.monotonic() - began, 3)
        (ROOT / "artifacts/http-gates.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"complete": report.get("complete", False), "checks": len(report["checks"]), "duration_seconds": report["duration_seconds"]}))
