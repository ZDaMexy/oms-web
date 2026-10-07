"""30-minute Linux loopback observation, never a production-host capacity gate."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import statistics
import sys
import threading
import time
from uuid import uuid4

import httpx

ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / ".dev-cache/local-runtime"
BASE = "http://127.0.0.1:8090"
STATE = json.loads((CONTROL / "acceptance-state.json").read_text())
WEB = {"Origin": BASE, "X-OMS-IR": "1", "X-OMS-Actor": str(STATE["users"][0]["id"])}
samples = []
requests = []
failures = []
finished = threading.Event()


def processes():
    root_pids = {int((CONTROL / (name + ".pid")).read_text()) for name in ("nginx", "php-fpm", "backend", "catalog")}
    rows = {}
    for directory in Path("/proc").iterdir():
        if not directory.name.isdigit():
            continue
        try:
            fields = (directory / "stat").read_text().rsplit(")", 1)[1].split()
            rows[int(directory.name)] = {"ppid": int(fields[1]), "ticks": int(fields[11]) + int(fields[12]), "rss_kib": int(fields[21]) * os.sysconf("SC_PAGE_SIZE") // 1024}
        except FileNotFoundError:
            continue  # A real worker can exit between /proc enumeration and read.
    selected = set(root_pids)
    while True:
        children = {pid for pid, row in rows.items() if row["ppid"] in selected}
        before = len(selected)
        selected |= children
        if len(selected) == before:
            break
    groups = {"frontend": set(), "backend": set(), "catalog": set()}
    for group, services in (("frontend", ("nginx", "php-fpm")), ("backend", ("backend",)), ("catalog", ("catalog",))):
        group_pids = {int((CONTROL / (service + ".pid")).read_text()) for service in services}
        while True:
            children = {pid for pid, row in rows.items() if row["ppid"] in group_pids}
            before = len(group_pids)
            group_pids |= children
            if len(group_pids) == before:
                break
        groups[group] = group_pids
    result = {group: {"rss_kib": 0, "pss_kib": 0, "ticks": 0, "processes": 0, "pid_ticks": {}} for group in groups}
    for group, pids in groups.items():
        for pid in pids:
            if pid not in rows:
                continue
            try:
                rollup = Path(f"/proc/{pid}/smaps_rollup").read_text()
            except FileNotFoundError:
                continue
            pss = sum(int(line.split()[1]) for line in rollup.splitlines() if line.startswith("Pss:"))
            for name in ("rss_kib", "ticks"):
                result[group][name] += rows[pid][name]
            result[group]["pss_kib"] += pss
            result[group]["processes"] += 1
            result[group]["pid_ticks"][str(pid)] = rows[pid]["ticks"]
    return result


def monitor():
    with (ROOT / "artifacts/local-memory-samples.jsonl").open("w") as log:
        while not finished.is_set():
            sample = {"t": round(time.monotonic() - began, 3), "groups": processes()}
            samples.append(sample)
            log.write(json.dumps(sample) + "\n")
            log.flush()
            finished.wait(0.25)


def timed(client, method, path, **kwargs):
    start = time.monotonic()
    response = client.request(method, path, **kwargs)
    duration = (time.monotonic() - start) * 1000
    requests.append({"t": round(time.monotonic() - began, 3), "kind": "write" if method != "GET" else path.split("?")[0], "ms": round(duration, 3), "status": response.status_code})
    if response.status_code not in (200, 201, 204):
        failures.append({"t": round(time.monotonic() - began, 3), "path": path.split("?")[0], "status": response.status_code, "retry_after": response.headers.get("retry-after")})
    return response


def quantiles(values):
    values = sorted(values)
    return {"count": len(values), "p50_ms": round(statistics.median(values), 3), "p95_ms": round(values[min(len(values) - 1, int(len(values) * .95))], 3), "max_ms": round(max(values), 3)}


if sys.argv[1:] == ["--probe"]:
    print(json.dumps(processes()))
    raise SystemExit(0)

began = time.monotonic()
started_at = datetime.now(timezone.utc).isoformat()
thread = threading.Thread(target=monitor)
thread.start()
try:
    with httpx.Client(base_url=BASE, trust_env=False, timeout=35) as owner:
        login = owner.post("/api/ir/v1/auth/login", json={"username": STATE["usernames"][0], "password": STATE["password"], "transport": "browser"}, headers={"Origin": BASE, "X-OMS-IR": "1"})
        if login.status_code != 200:
            raise RuntimeError("Local test account login failed")
        routes = ["/", "/news", "/ir?page=2", "/community", "/rankings", "/api/ir/v1/multisource/scores/chart/" + STATE["md5"] + "?limit=20&page=2", "/api/ir/v1/users/" + str(STATE["users"][0]["id"]) + "/public-bests?ruleset=bms&keymode=bms_7k&sources=oms,lr2oraja_ed"]
        for path in routes:
            timed(owner, "GET", path)
        next_write = began + 45
        cycle = 0
        while time.monotonic() - began < 1800:
            cycle_start = time.monotonic()
            for path in routes:
                timed(owner, "GET", path)
            if time.monotonic() >= next_write:
                timed(owner, "POST", "/api/ir/v1/community/posts/" + str(STATE["post_id"]) + "/replies", json={"submission_id": str(uuid4()), "body": "本地持续读写检查 " + str(cycle)}, headers=WEB)
                next_write += 45
            if cycle in (1, 100, 300):
                def burst(index):
                    with httpx.Client(base_url=BASE, trust_env=False, timeout=35) as client:
                        return timed(client, "GET", routes[index % len(routes)])
                with ThreadPoolExecutor(max_workers=8) as pool:
                    list(pool.map(burst, range(24)))
            cycle += 1
            finished.wait(max(0, 2 - (time.monotonic() - cycle_start)))
finally:
    finished.set()
    thread.join()
    duration = time.monotonic() - began
    stats = {kind: quantiles([row["ms"] for row in requests if row["kind"] == kind]) for kind in {row["kind"] for row in requests}}
    peaks = {group: {name: max(sample["groups"][group][name] for sample in samples) for name in ("pss_kib", "rss_kib", "processes")} for group in ("frontend", "backend", "catalog")}
    cpu = {}
    for group in peaks:
        rates, elapsed, ticks = [], 0, 0
        for previous, current in zip(samples, samples[1:]):
            dt = current["t"] - previous["t"]
            before = previous["groups"][group]["pid_ticks"]
            after = current["groups"][group]["pid_ticks"]
            delta = sum(max(0, value - before[pid]) for pid, value in after.items() if pid in before)
            if dt > 0:
                rates.append(delta / os.sysconf("SC_CLK_TCK") / dt * 100)
                elapsed += dt
                ticks += delta
        cpu[group] = {"mean_percent_one_core": round(ticks / os.sysconf("SC_CLK_TCK") / elapsed * 100, 3),
                      "p95_percent_one_core": round(sorted(rates)[min(len(rates)-1, int(len(rates)*.95))], 3),
                      "max_percent_one_core": round(max(rates), 3)}
    report = {"started_at": started_at, "duration_seconds": round(duration, 3), "sample_span_seconds": [samples[0]["t"], samples[-1]["t"]], "environment": "Alpine 3.24.2 in F-backed WSL; source and test DB on F DrvFS; no cgroup/production equivalence", "workload": "Seven routes every two seconds; one reply every 45 seconds; three 24-request bursts at eight concurrent clients", "counts": {"requests": len(requests), "samples": len(samples), "writes": sum(row["kind"] == "write" for row in requests), "failures": len(failures)}, "latency": stats, "peaks": peaks, "cpu": cpu, "cpu_boundary": "250 ms samples; worker lifetimes shorter than one interval and startup ticks are not attributed", "failures": failures, "complete": duration >= 1800 and samples[-1]["t"] >= 1799 and len(failures) == 0, "frontend_pss_under_200_mib": peaks["frontend"]["pss_kib"] < 200 * 1024, "production_host_gate": False}
    (ROOT / "artifacts/local-performance.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False))
    if not report["complete"]:
        raise SystemExit(1)
