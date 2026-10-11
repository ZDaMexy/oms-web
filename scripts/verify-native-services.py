"""Real local HTTP checks for native consumers; never write to production."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import secrets
from uuid import uuid4

import httpx

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8090"
OUT = ROOT / "artifacts/native-services-20261011/local-native-http.json"
V1 = "/api/ir/v1"
checks = []


def check(name, passed, **evidence):
    checks.append({"name": name, "passed": bool(passed), **evidence})
    if not passed:
        raise AssertionError(name)


def main():
    with httpx.Client(base_url=BASE, timeout=35, trust_env=False, follow_redirects=False) as anon:
        response = anon.get("/client-content")
        data = response.json()
        check("native content is anonymous bounded JSON", response.status_code == 200 and data["version"] == 1
              and len(response.content) <= 256 * 1024 and "application/json" in response.headers["content-type"])
        cache = response.headers["cache-control"]
        etag = response.headers["etag"]
        tag = etag.removeprefix("W/")
        check("actual Nginx preserves public freshness", "max-age=300" in cache and "public" in cache
              and "no-cache" not in cache and "no-store" not in cache, cache_control=cache)
        check("ETag binds decoded body across gzip transformation", tag == '"' + hashlib.sha256(response.content).hexdigest() + '"',
              etag=etag, encoding=response.headers.get("content-encoding"))
        for candidate in (tag, "W/" + tag, '"different", ' + tag, "*"):
            conditional = anon.get("/client-content", headers={"If-None-Match": candidate})
            check("real conditional GET returns bodyless304", conditional.status_code == 304
                  and conditional.content == b"" and conditional.headers["etag"].removeprefix("W/") == tag)
        head = anon.head("/client-content")
        check("HEAD keeps metadata without body", head.status_code == 200 and head.content == b"" and head.headers["etag"].removeprefix("W/") == tag)
        changed = anon.get("/client-content", headers={"If-None-Match": '"different"'})
        check("different validator returns original content", changed.status_code == 200 and changed.content == response.content)
        check("news and help use original public sources", data["news"] == json.loads((ROOT / "resources/oms/news.json").read_text())
              and data["help"] == json.loads((ROOT / "resources/oms/help.json").read_text()))
        ids = {section["id"] for section in data["help"]}
        check("native help has stable complete anchors", ids == {"start", "library", "ir", "scores", "players", "java-ir", "openlr2-ir", "feedback"})
        html = anon.get("/help")
        check("web help shares native sections and anchors", html.status_code == 200 and all('id="' + value + '"' in html.text for value in ids))
        for value in ("/news", "/ir", "/rankings", "/community", "/account", "/beatmapsets?ruleset=mania"):
            page = anon.get(value)
            check("original web page remains available " + value, page.status_code == 200 and "no-cache" in page.headers["cache-control"])

        credentials = {"username": "native_http_" + secrets.token_hex(4), "password": secrets.token_urlsafe(20), "transport": "desktop"}
        registration = anon.post(V1 + "/auth/register", json=credentials)
        check("desktop registers through original auth", registration.status_code == 201)
        auth = registration.json()
        owner = auth["user"]["id"]
        bearer = {"Authorization": "Bearer " + auth["access_token"]}
        payload = {"submission_id": str(uuid4()), "title": "端内接线验收（本地合成）", "body": "第一段\n第二段", "category": "development"}
        created = anon.post(V1 + "/community/posts", headers=bearer, json=payload)
        check("desktop publishes via same community service", created.status_code == 201)
        post = created.json()["post"]
        post_id = post["id"]
        check("post receipt belongs to original desktop owner", post["author"]["id"] == owner and post["body"] == payload["body"])
        repeated = anon.post(V1 + "/community/posts", headers=bearer, json=payload)
        check("same UUID retry preserves one post", repeated.status_code == 200 and repeated.json()["post"]["id"] == post_id)
        conflict = anon.post(V1 + "/community/posts", headers=bearer, json={**payload, "body": "不同内容"})
        check("UUID conflict is explicit", conflict.status_code == 409 and conflict.json()["error"]["code"] == "submission_conflict")
        reply_payload = {"submission_id": str(uuid4()), "body": "端内回复（本地合成）"}
        replied = anon.post(V1 + f"/community/posts/{post_id}/replies", headers=bearer, json=reply_payload)
        check("desktop replies on original topic", replied.status_code == 201 and replied.json()["reply"]["post_id"] == post_id)
        reply_id = replied.json()["reply"]["id"]
        edited = anon.post(V1 + f"/community/posts/{post_id}/edit", headers=bearer,
                           json={"title": "本地合成更新", "body": "保留段落\n真实桌面编辑", "category": "help"})
        check("desktop edits its own post", edited.status_code == 200 and edited.json()["post"]["category"] == "help")
        edited_reply = anon.post(V1 + f"/community/replies/{reply_id}/edit", headers=bearer, json={"body": "回复编辑"})
        check("desktop edits its own reply", edited_reply.status_code == 200 and edited_reply.json()["reply"]["body"] == "回复编辑")
        anonymous_edit = anon.post(V1 + f"/community/posts/{post_id}/edit", json={"title": "x", "body": "x", "category": "help"})
        check("anonymous writes remain rejected", anonymous_edit.status_code == 401)
        for resource, item_id in (("replies", reply_id), ("posts", post_id)):
            removed = anon.post(V1 + f"/community/{resource}/{item_id}/delete", headers=bearer, json={})
            check("desktop delete keeps author placeholder " + resource, removed.status_code == 200 and removed.json()["reply" if resource == "replies" else "post"]["deleted"] is True)
        public = anon.get(V1 + f"/community/posts/{post_id}")
        check("anonymous reads retain deleted placeholder", public.status_code == 200 and public.json()["post"]["deleted"] is True)
        refresh = anon.post(V1 + "/auth/refresh", json={"refresh_token": auth["refresh_token"]})
        check("original desktop refresh still works", refresh.status_code == 200 and refresh.json()["user"]["id"] == owner)
        logout = anon.post(V1 + "/auth/logout", headers={"Authorization": "Bearer " + refresh.json()["access_token"]}, json={})
        check("desktop logout still revokes session", logout.status_code == 204)


report = {"started_at": datetime.now(timezone.utc).isoformat(), "base": BASE,
          "scope": "synthetic local desktop writes and real Nginx/PHP HTTP; no production accounts or writes", "checks": checks}
try:
    main()
    report["complete"] = True
finally:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"complete": report.get("complete", False), "checks": len(checks)}))
