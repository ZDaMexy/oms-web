# Licensed under AGPL-3.0-or-later; see LICENCE.
"""Measure one explicitly owned Linux staging runtime, never the live database.

The release is immutable; work must be /opt/oms-web/acceptance/<release-id>/<round>.
The owner creates work/staging-runtime.json and the PHP/Nginx units first. This
driver creates only synthetic accounts and serves only loopback HTTP. Run it in
its own finite systemd unit (256 MiB / 50%, RemainAfterExit=yes, no --collect).

Required runtime control (no credentials):
  {"format":1,"release":"...","work":"...","base":"http://127.0.0.1:18090",
   "backend_port":18084,"frontend":{
     "php":{"unit":"oms-web-accept-<id>.service","pid":123,"config":"..."},
     "nginx":{"unit":"oms-web-nginx-<id>.service","pid":124,"config":"..."}},
   "catalog":{"unit":"oms-ir-catalog.service","pid":125,
              "base":"http://127.0.0.1:8082"},
   "cache":{"unit":"oms-web-cache-<id>.service"}}

PHP: High 160 / Max 200 MiB / CPU 50%. Nginx: Max <=96 MiB / CPU <=25%.
The optional nginx budget is {"memory_max_mib":96,"cpu_percent":25}; cache
is an already completed 128 MiB / 50% oneshot. Catalog is observed, not stopped.
Both staging frontend units must retain their loaded terminal state. This driver
closes those exact registered units after HTTP checks. Its own final terminal
must be collected by the invoking owner after it exits. Evidence is deliberately
separate from browser/player acceptance and a fresh operating-system recovery.
"""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
from datetime import datetime, timezone
import hashlib
import http.client
from http.cookies import SimpleCookie
import importlib.util
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import socket
import sqlite3
import subprocess
import sys
import threading
import time
from types import MethodType, SimpleNamespace
from urllib.parse import urlencode, urlsplit
import uuid


MIB = 1024 * 1024
GIB = 1024 * MIB
OWNERSHIP = "oms-native-production-staging-v1"
TABLES = {
    "users", "sessions", "refresh_tokens", "rate_limits", "charts", "score_groups", "scores",
    "community_posts", "community_replies", "community_moderation", "integration_keys",
    "external_charts", "external_bests", "native_identities", "archive_visibility",
    "player_population_version", "player_population_scopes", "player_population_dirty",
    "player_population_charts", "player_population_users", "sqlite_sequence", "player_population_bms_counts",
}
CGROUP_FILES = (
    "memory.current", "memory.peak", "memory.high", "memory.max", "memory.swap.current",
    "memory.swap.max", "memory.events", "cpu.max", "cpu.stat", "pids.current", "pids.max",
)
UNIT_PROPERTIES = (
    "LoadState", "ActiveState", "SubState", "MainPID", "ExecMainPID", "ExecMainCode", "ExecMainStatus",
    "Result", "Transient", "RemainAfterExit", "MemoryAccounting", "MemoryHigh", "MemoryMax", "MemoryPeak",
    "MemorySwapMax", "CPUQuotaPerSecUSec", "TasksMax", "ControlGroup", "WorkingDirectory", "Restart",
    "IPAddressDeny", "IPAddressAllow", "RootDirectory", "BindReadOnlyPaths", "BindPaths",
)


class GateFailure(RuntimeError):
    """A fixed evidence label, never an HTTP body or a secret."""


def require(condition, label):
    if not condition:
        raise GateFailure(label)


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_hash(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(MIB), b""):
            result.update(block)
    return result.hexdigest()


def read_json(path):
    require(path.is_file() and not path.is_symlink(), "explicit_regular_control_file")
    with path.open("rb") as stream:
        data = stream.read(4 * MIB + 1)
    require(len(data) <= 4 * MIB, "bounded_control_file")
    return json.loads(data)


def runtime_files(release, manifest):
    if "files_manifest" not in manifest:
        return manifest["files"]
    reference = manifest["files_manifest"]
    require(reference["path"] == "runtime-files.json", "native_runtime_files_manifest_name")
    path = release / reference["path"]
    require(path.is_file() and not path.is_symlink() and path.stat().st_size == reference["bytes"]
            and file_hash(path) == reference["sha256"], "native_runtime_files_manifest_binding")
    value = read_json(path)
    files = value["files"]
    require(len(files) == reference["count"], "native_runtime_file_count")
    return files


def native_nginx_config(config, work, release):
    text = config.read_text()
    includes = re.findall(r"\binclude\s+([^;\s]+/nginx-native\.conf)\s*;", text)
    require(len(includes) == 1, "one_registered_native_Nginx_routes_include")
    routes = direct_path(includes[0])
    require(routes.is_file() and routes.is_relative_to(work), "only_owned_native_Nginx_routes")
    rules = routes.read_text()
    require("listen 127.0.0.1:18090;" in text and f"root {release}/web/public;" in rules
            and "fastcgi_pass 127.0.0.1:19070;" in rules
            and "proxy_pass http://127.0.0.1:18084;" in rules
            and "proxy_set_header X-Forwarded-For $remote_addr;" in rules
            and "real_ip_header" not in text + rules
            and "fastcgi_param REMOTE_ADDR $http_" not in text + rules,
            "actual_native_static_root_and_trusted_peer_routes")
    return {"main_sha256": file_hash(config), "routes_sha256": file_hash(routes)}


def new_json(path, value):
    temporary = path.with_name(path.name + ".new-" + uuid.uuid4().hex)
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)  # Publish a complete file without overwriting.
    finally:
        if temporary.exists():
            temporary.unlink()  # Only the private temporary created above.


def replace_owned_json(path, value):
    temporary = path.with_name(path.name + ".writing-" + uuid.uuid4().hex)
    new_json(temporary, value)
    os.replace(temporary, path)


def direct_path(path):
    path = Path(path).absolute()
    require(path.resolve() == path and "private-data" not in path.parts, "direct_nonprivate_path")
    return path


def properties(unit):
    require(re.fullmatch(r"[A-Za-z0-9_-]+\.service", unit) is not None, "explicit_unit_name")
    raw = subprocess.check_output(
        ["systemctl", "show", unit, "--no-pager", "--property=" + ",".join(UNIT_PROPERTIES)],
        text=True, timeout=10,
    )
    return dict(line.split("=", 1) for line in raw.splitlines() if "=" in line)


def identity(pid):
    process = Path("/proc") / str(pid)
    fields = process.joinpath("stat").read_text().rsplit(")", 1)[1].split()
    return {
        "pid": pid, "starttime_ticks": int(fields[19]), "state": fields[0],
        "cwd": str(process.joinpath("cwd").resolve()),
        "argv": [part.decode() for part in process.joinpath("cmdline").read_bytes().split(b"\0") if part],
    }


def same_process(first, second):
    return all(first[name] == second[name] for name in ("pid", "starttime_ticks", "cwd", "argv")) \
        and second["state"] not in ("Z", "X", "x")


def cgroup_path(pid):
    entries = Path(f"/proc/{pid}/cgroup").read_text().splitlines()
    entry = next(row[3:] for row in entries if row.startswith("0::"))
    root = Path("/sys/fs/cgroup")
    path = (root / entry.lstrip("/")).resolve()
    require(path.is_relative_to(root), "unified_cgroup_path")
    return path


def cgroup_values(path):
    return {name: (path / name).read_text().strip() for name in CGROUP_FILES}


def clean_memory(values):
    events = dict(line.split() for line in values["memory.events"].splitlines())
    return values["memory.swap.current"] == values["memory.swap.max"] == "0" \
        and all(events.get(name, "0") == "0" for name in ("oom", "oom_kill", "oom_group_kill"))


def cache_evidence(entry, work, release, storage):
    """Bind an actual ExecStartPost cgroup capture to this completed cache unit.

    The owner captures a live 128 MiB unit, records the exact collector source,
    then keeps the loaded terminal. Missing systemd MemoryPeak stays unavailable;
    the operation's real kernel lifetime peak/events/swap are required instead.
    """
    unit = entry["unit"]
    terminal = properties(unit)
    path = direct_path(entry["live_receipt"])
    require(path.is_file() and path.is_relative_to(work) and file_hash(path) == entry["live_receipt_sha256"],
            "bound_actual_cache_live_receipt")
    live = read_json(path)
    require(live["format"] == "oms-native-cache-live-v1" and live["unit"] == unit
            and live["release"] == str(release) and live["storage"] == str(storage)
            and live["exec_main_pid"] == int(terminal["ExecMainPID"])
            and live["collector_pid"] > 0 and live["collector_starttime_ticks"] > 0
            and live["cgroup"] == "/sys/fs/cgroup/system.slice/" + unit,
            "cache_exact_PID_cgroup_source_binding")
    source = direct_path(live["capture_source"])
    require(source.is_file() and source.is_relative_to(work) and file_hash(source) == live["capture_source_sha256"],
            "actual_cache_capture_source_sha256")
    values = live["values"]
    require(set(CGROUP_FILES).issubset(values) and limits(values, 128, 0.5) and clean_memory(values)
            and values["memory.peak"].isdecimal() and int(values["memory.peak"]) <= 128 * MIB,
            "cache_actual_live_128MiB_swap0_OOM0_CPU50")
    require(unit.startswith("oms-web-cache-") and terminal["LoadState"] == "loaded"
            and terminal["ActiveState"] == "active" and terminal["SubState"] == "exited"
            and terminal["MainPID"] == "0" and terminal["Result"] == "success"
            and terminal["RemainAfterExit"] == terminal["MemoryAccounting"] == "yes"
            and terminal["ExecMainCode"] == "1" and terminal["ExecMainStatus"] == "0"
            and terminal["MemoryMax"] == str(128 * MIB) and terminal["MemorySwapMax"] == "0"
            and str(release / "web") + ":/app" in terminal["BindReadOnlyPaths"]
            and str(storage) + ":/app/storage" in terminal["BindPaths"], "actual_cache_loaded_terminal")
    cached = terminal.get("MemoryPeak", "")
    if cached.isdecimal():
        require(int(cached) <= 128 * MIB, "actual_cache_cached_peak_if_available")
    return {"unit": unit, "actual_terminal": terminal, "live_receipt_sha256": file_hash(path), "actual_live_capture": live,
            "cached_systemd_peak_bytes": int(cached) if cached.isdecimal() else None,
            "cached_systemd_peak_raw": cached, "cached_peak_unavailable_not_zero": not cached.isdecimal(),
            "memory_gate_source": "actual_post_operation_kernel_cgroup_lifetime_peak", "passed": True}


def limits(values, memory, cpu, high=None):
    quota, period = values["cpu.max"].split()
    return values["memory.max"] == str(memory * MIB) and quota != "max" \
        and int(quota) / int(period) <= cpu + 0.000001 and values["memory.swap.max"] == "0" \
        and (high is None or values["memory.high"] == str(high * MIB))


def process_usage(location):
    """PSS is supplementary; the actual whole unit cgroup is the memory gate."""
    pids = set()
    for directory in (location, *location.rglob("*")):
        if directory.is_dir():
            try:
                pids.update(int(value) for value in directory.joinpath("cgroup.procs").read_text().split())
            except FileNotFoundError:
                continue  # A child cgroup may disappear between enumeration and read.
    result = {"pss_kib": 0, "rss_kib": 0, "processes": 0}
    for pid in pids:
        try:
            fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
            rollup = Path(f"/proc/{pid}/smaps_rollup").read_text()
        except (FileNotFoundError, ProcessLookupError):
            continue  # PHP's ondemand workers may exit while being sampled.
        result["rss_kib"] += int(fields[21]) * os.sysconf("SC_PAGE_SIZE") // 1024
        result["pss_kib"] += sum(int(line.split()[1]) for line in rollup.splitlines() if line.startswith("Pss:"))
        result["processes"] += 1
    return result


def host_memory():
    data = {line.split(":", 1)[0]: int(line.split()[1]) * 1024
            for line in Path("/proc/meminfo").read_text().splitlines()}
    return {"available_bytes": data["MemAvailable"], "total_bytes": data["MemTotal"],
            "swap_used_bytes": data["SwapTotal"] - data["SwapFree"]}


def cpu_usec(values):
    return int(dict(line.split() for line in values["cpu.stat"].splitlines())["usage_usec"])


class Evidence:
    def __init__(self, work, phase, initial):
        self.work = work
        self.path = work / ("verification-" + phase + ".json")
        require(not os.path.lexists(self.path), "new_evidence_file_required")
        self.data = {"format": 1, "started_at": now(), "status": "running", "checks": [],
                     "stages": {}, "unit_terminals": [], "failures": [], **initial}
        new_json(self.path, self.data)

    def save(self):
        replace_owned_json(self.path, self.data)

    def check(self, condition, label):
        self.data["checks"].append({"name": label, "passed": bool(condition)})
        self.save()
        require(condition, label)

    def stage(self, label, result):
        require(label not in self.data["stages"], "stage_not_overwritten")
        self.data["stages"][label] = result
        self.save()


class BudgetUnit:
    def __init__(self, unit, pid, memory, cpu, high=None):
        self.unit, self.pid, self.memory, self.cpu, self.high = unit, pid, memory, cpu, high
        self.initial = properties(unit)
        require(self.initial["LoadState"] == "loaded" and int(self.initial["MainPID"]) == pid
                and pid > 0 and self.initial["MemoryAccounting"] == "yes", "actual_owned_unit_pid")
        self.identity = identity(pid)
        self.location = cgroup_path(pid)
        require(str(self.location) == "/sys/fs/cgroup" + self.initial["ControlGroup"], "actual_unit_cgroup")
        self.last = cgroup_values(self.location)
        require(limits(self.last, memory, cpu, high) and clean_memory(self.last), "actual_cgroup_budget")

    def frame(self):
        require(same_process(self.identity, identity(self.pid)), "owned_pid_not_reused")
        value = cgroup_values(self.location)
        self.last = value
        return {"unit": self.unit, "pid": self.pid, "cgroup": str(self.location), "values": value,
                "process_memory": process_usage(self.location)}

    def close(self, evidence, *, server_log=None):
        current = self.frame()
        require(self.initial["RemainAfterExit"] == "yes" and self.initial["Restart"] == "no",
                "retained_finite_unit_required")
        subprocess.run(["systemctl", "kill", "--kill-whom=main", "--signal=SIGTERM", self.unit],
                       check=True, timeout=10)
        deadline = time.monotonic() + 30
        while properties(self.unit)["MainPID"] != "0" and time.monotonic() < deadline:
            time.sleep(0.1)
        return self.terminal(evidence, current, server_log=server_log)

    def terminal(self, evidence, last_frame, *, server_log=None):
        terminal = properties(self.unit)
        normal = terminal["ExecMainCode"] == "1" and terminal["ExecMainStatus"] == "0"
        sigterm = server_log is not None and terminal["ExecMainCode"] == "2" and terminal["ExecMainStatus"] == "15"
        shutdown = None
        if server_log is not None:
            text = server_log.read_text()
            markers = ("Shutting down", "Waiting for application shutdown.", "Application shutdown complete.",
                       f"Finished server process [{self.pid}]")
            offsets = [text.rfind(marker) for marker in markers]
            shutdown = {"sha256": file_hash(server_log), "bytes": server_log.stat().st_size,
                        "ordered_shutdown_markers": all(index >= 0 for index in offsets) and offsets == sorted(offsets)}
        peak = terminal.get("MemoryPeak", "")
        kernel = None
        if self.location.is_dir():
            try:
                kernel = cgroup_values(self.location)
            except FileNotFoundError:
                require(not self.location.exists() and terminal["MainPID"] == "0", "terminal_cgroup_read_race")
        valid = terminal["LoadState"] == "loaded" and terminal["ActiveState"] == "active" \
            and terminal["SubState"] == "exited" and terminal["MainPID"] == "0" \
            and int(terminal["ExecMainPID"]) == self.pid and terminal["Result"] == "success" \
            and (normal or sigterm) and not Path(f"/proc/{self.pid}").exists() \
            and terminal["RemainAfterExit"] == terminal["MemoryAccounting"] == "yes" \
            and terminal["MemoryMax"] == str(self.memory * MIB) and terminal["MemorySwapMax"] == "0" \
            and terminal["MemoryHigh"] == self.initial["MemoryHigh"] \
            and terminal["CPUQuotaPerSecUSec"] == self.initial["CPUQuotaPerSecUSec"] \
            and terminal["TasksMax"] == self.initial["TasksMax"] \
            and terminal["WorkingDirectory"] == self.initial["WorkingDirectory"] \
            and (not peak.isdecimal() or int(peak) <= self.memory * MIB) \
            and limits(last_frame["values"], self.memory, self.cpu, self.high) \
            and clean_memory(last_frame["values"]) and int(last_frame["values"]["memory.peak"]) <= self.memory * MIB \
            and (shutdown is None or shutdown["ordered_shutdown_markers"])
        if kernel is not None:
            valid = valid and kernel["pids.current"] == "0" and clean_memory(kernel) \
                and int(kernel["memory.peak"]) <= self.memory * MIB
        result = {"unit": self.unit, "original_pid": self.pid, "initial": self.initial,
                  "actual_terminal": terminal, "original_pid_gone": not Path(f"/proc/{self.pid}").exists(),
                  "last_live_kernel": last_frame, "last_live_is_not_terminal": True,
                  "actual_terminal_kernel": kernel, "shutdown_log": shutdown,
                  "cached_systemd_peak_bytes": int(peak) if peak.isdecimal() else None,
                  "cached_systemd_peak_raw": peak, "cached_peak_unavailable_not_zero": not peak.isdecimal(),
                  "passed": valid}
        evidence.data["unit_terminals"].append(result)
        evidence.save()
        require(valid, "loaded_terminal_identity_exit_and_budget")
        return result


class Observation:
    """250 ms paired whole-host / driver / main / PHP / Nginx / catalog samples."""
    def __init__(self, context, label, backend=None, maintenance=None):
        self.context, self.label = context, label
        self.units = {"driver": context.driver}
        if not getattr(context, "frontend_closed", False):
            self.units.update(context.frontend)
        if context.catalog is not None:
            self.units["catalog"] = context.catalog
        if backend is not None:
            self.units["backend"] = backend
        if maintenance is not None:
            self.units["maintenance"] = maintenance
        self.path = context.work / ("samples-" + label + ".jsonl")
        self.done = threading.Event()
        self.first = self.last = None
        self.minimum = None
        self.minimum_disk_frame = None
        self.database_peak = {"main_bytes": 0, "wal_bytes": 0, "main_plus_wal_bytes": 0}
        self.databases = {"primary": context.database,
                          **{f"restore-{number}": context.work / f"empty-restore-{number}/live.db" for number in (1, 2)}}
        self.database_peaks = {name: dict(self.database_peak) for name in self.databases}
        self.maxima = {name: {"memory_current_bytes": 0, "memory_peak_bytes": 0, "pss_kib": 0,
                             "rss_kib": 0, "processes": 0} for name in self.units}
        self.cpu_rates = {name: [] for name in self.units}
        self.cpu_first, self.cpu_last = {}, {}
        self.frames = 0
        self.failure = None
        self.valid_resources = True

    def sample(self, stream):
        frame = {"monotonic": time.monotonic(), "host": host_memory(),
                 "disk_free_bytes": shutil.disk_usage(self.context.work).free,
                 "groups": {name: unit.frame() for name, unit in self.units.items()}}
        frame["owned_database_bytes"] = {}
        for name, main in self.databases.items():
            wal = main.with_name(main.name + "-wal")
            try:
                main_bytes = main.stat().st_size
            except FileNotFoundError:
                main_bytes = 0  # An explicitly owned stopped restore may be retired.
            try:
                wal_bytes = wal.stat().st_size
            except FileNotFoundError:
                wal_bytes = 0  # SQLite may checkpoint/unlink WAL during sampling.
            size = {"main_bytes": main_bytes, "wal_bytes": wal_bytes, "main_plus_wal_bytes": main_bytes + wal_bytes}
            frame["owned_database_bytes"][name] = {"path": str(main), **size}
            for field, number in size.items():
                self.database_peaks[name][field] = max(self.database_peaks[name][field], number)
        frame["owned_primary_database_bytes"] = frame["owned_database_bytes"]["primary"]
        self.database_peak = self.database_peaks["primary"]
        if self.first is None:
            self.first = frame
        if self.minimum is None or frame["host"]["available_bytes"] < self.minimum["host"]["available_bytes"]:
            self.minimum = frame
        if self.minimum_disk_frame is None or frame["disk_free_bytes"] < self.minimum_disk_frame["disk_free_bytes"]:
            self.minimum_disk_frame = frame
        self.valid_resources = self.valid_resources and frame["host"]["available_bytes"] >= 512 * MIB \
            and frame["host"]["swap_used_bytes"] == 0 and frame["disk_free_bytes"] >= 2 * GIB
        for name, value in frame["groups"].items():
            unit = self.units[name]
            values = value["values"]
            self.valid_resources = self.valid_resources and limits(values, unit.memory, unit.cpu, unit.high) \
                and clean_memory(values) and int(values["memory.peak"]) <= unit.memory * MIB
            measured = {"memory_current_bytes": int(values["memory.current"]), "memory_peak_bytes": int(values["memory.peak"]),
                        **value["process_memory"]}
            for metric, number in measured.items():
                self.maxima[name][metric] = max(self.maxima[name][metric], number)
            used = cpu_usec(values)
            self.cpu_first.setdefault(name, used)
            self.cpu_last[name] = used
            if self.last is not None:
                elapsed = frame["monotonic"] - self.last["monotonic"]
                prior = cpu_usec(self.last["groups"][name]["values"])
                self.cpu_rates[name].append(max(0, used - prior) / (elapsed * 10000))
        stream.write(canonical(frame) + "\n")
        stream.flush()
        self.last = frame
        self.frames += 1

    def observe(self):
        try:
            with self.path.open("x", encoding="utf-8") as stream:
                while not self.done.is_set():
                    self.sample(stream)
                    self.done.wait(0.25)
                self.sample(stream)
        except (OSError, GateFailure, ValueError, KeyError) as error:
            self.failure = error  # Surface a real sampling failure to the driving thread.

    def __enter__(self):
        self.thread = threading.Thread(target=self.observe, name="owned-resource-observer")
        self.thread.start()
        return self

    def __exit__(self, kind, value, traceback):
        self.done.set()
        self.thread.join()
        if self.failure is not None:
            raise self.failure
        require(self.frames >= 2 and self.first is not None and self.last is not None, "actual_resource_frames_required")
        self.context.evidence.stage("resources-" + self.label, self.result())
        require(self.valid_resources, "shared_host_512MiB_no_swap_no_OOM_and_disk_margin")

    def result(self):
        seconds = self.last["monotonic"] - self.first["monotonic"]
        return {
            "samples": self.frames, "interval_seconds": 0.25, "sample_span_seconds": seconds,
            "first": self.first, "last": self.last, "paired_minimum_available_frame": self.minimum,
            "minimum_disk_free_frame": self.minimum_disk_frame, "primary_database_peak": self.database_peak,
            "owned_database_peaks": self.database_peaks,
            "whole_filesystem_free_includes_other_host_activity": True,
            "peaks": self.maxima,
            "cpu": {name: {"mean_percent_one_core": (self.cpu_last[name] - self.cpu_first[name]) / (seconds * 10000),
                            "p95_sample_percent_one_core": percentile(rates, 0.95), "max_sample_percent_one_core": max(rates, default=0)}
                    for name, rates in self.cpu_rates.items()},
            "journal": self.path.name, "journal_sha256": file_hash(self.path), "passed": self.valid_resources,
            "whole_php_unit_includes_children_and_opcache": "php" in self.units,
        }


def percentile(values, fraction):
    return sorted(values)[max(0, math.ceil(len(values) * fraction) - 1)] if values else None


def summary(records):
    return {"requests": len(records), "statuses": dict(Counter(str(row["status"]) for row in records)),
            "p95_confirmation_ms": percentile([row["confirmation_ms"] for row in records], 0.95),
            "p95_http_ms": percentile([row["ms"] for row in records], 0.95),
            "max_http_ms": max((row["ms"] for row in records), default=None),
            "response_bytes": sum(row["response_bytes"] for row in records)}


class WebClient:
    def __init__(self, base):
        parts = urlsplit(base)
        require(parts.scheme == "http" and parts.hostname == "127.0.0.1" and parts.port == 18090
                and not parts.path and not parts.query and not parts.fragment and parts.username is None,
                "only_owned_loopback_staging_frontend")
        self.base, self.port = base, parts.port

    def request(self, path, *, peer="127.0.0.2", headers=None, scheduled_at=None, method="GET", body=None):
        require(path.startswith("/") and not path.startswith("//") and "\r" not in path and "\n" not in path,
                "bounded_relative_staging_request")
        require(re.fullmatch(r"127\.0\.0\.(?:[1-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-4])", peer) is not None,
                "loopback_source_peer")
        require(method in ("GET", "POST") and (body is None or method == "POST"), "owned_probe_HTTP_method")
        began = time.monotonic()
        delay = max(0, began - scheduled_at) * 1000 if scheduled_at is not None else 0
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=35, source_address=(peer, 0))
        result = {"status": 0, "ms": 0, "confirmation_ms": 0, "response_bytes": 0, "retry_after": None}
        response_body, response_headers = b"", {}
        try:
            encoded = canonical(body).encode() if body is not None else None
            connection.request(method, path, body=encoded, headers={"Accept": "text/html,application/json", **(headers or {})})
            response = connection.getresponse()
            response_body = response.read(32 * MIB + 1)
            require(len(response_body) <= 32 * MIB, "bounded_frontend_body")
            result["status"] = response.status
            result["response_bytes"] = len(response_body)
            result["retry_after"] = response.getheader("Retry-After")
            response_headers = {name.lower(): value for name, value in response.getheaders()}
        except (OSError, http.client.HTTPException) as error:
            result["transport_error"] = type(error).__name__
        finally:
            result["ms"] = (time.monotonic() - began) * 1000
            result["confirmation_ms"] = result["ms"] + delay
            connection.close()
        return result, response_body, response_headers


class Context:
    def __init__(self, args):
        require(sys.platform.startswith("linux") and os.geteuid() == 0, "actual_root_linux_systemd_host_required")
        os.umask(0o077)
        self.args = args
        self.release = direct_path(args.release)
        manifest_path = self.release / "release.json"
        self.manifest = read_json(manifest_path)
        release_id = self.manifest.get("release_id", "")
        require(re.fullmatch(r"[0-9a-f]{12}-[0-9a-f]{12}", release_id) is not None
                and self.release == Path("/opt/oms-ir/releases") / release_id, "actual_immutable_candidate_release")
        require(self.manifest.get("format") == 3 and self.manifest.get("database_schema_version") == 3
                and self.manifest.get("runtime_kind") == "native-osu-web-1", "native_format3_release")
        for name in ("backend", "website", "client"):
            require(re.fullmatch(r"[0-9a-f]{40}", self.manifest.get(name + "_commit", "")) is not None,
                    "actual_candidate_commits")
        require(release_id == self.manifest["backend_commit"][:12] + "-" + self.manifest["website_commit"][:12],
                "release_identity_matches_current_manifest")
        self.work = direct_path(args.work)
        require(self.work.is_dir() and self.work.parent == Path("/opt/oms-web/acceptance") / release_id
                and re.fullmatch(r"[A-Za-z0-9_-]+", self.work.name) is not None, "only_owned_acceptance_round")
        self.data = self.work / "data"
        self.database = self.data / "live.db"
        self.backend = self.release / "backend"
        self.python = self.backend / ".venv/bin/python"
        require(self.python.is_file() and Path(sys.executable).resolve() == self.python.resolve(), "candidate_python_runtime")
        self.base = args.base
        self.web = WebClient(self.base)
        self.runtime_path = self.work / "staging-runtime.json"
        self.runtime = read_json(self.runtime_path)
        require(self.runtime.get("format") == 1 and self.runtime.get("release") == str(self.release)
                and self.runtime.get("work") == str(self.work) and self.runtime.get("base") == self.base
                and self.runtime.get("backend_port") == 18084, "explicit_staging_runtime_binding")
        self.port = self.runtime["backend_port"]
        require(type(args.seconds) is int and args.seconds >= 10, "explicit_real_duration")
        self.source_hashes = {}
        self.runtime_files = runtime_files(self.release, self.manifest)
        for name, checksum in self.runtime_files.items():
            relative = PurePosixPath(name)
            require(not relative.is_absolute() and ".." not in relative.parts and ".env" not in relative.parts
                    and "private-data" not in relative.parts and re.fullmatch(r"[0-9a-f]{64}", checksum) is not None,
                    "release_file_allowlist")
            path = self.release / relative
            require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(self.release)
                    and file_hash(path) == checksum, "exact_candidate_runtime_file_sha256")
            if name.startswith(("backend/oms_ir/", "backend/scripts/", "web/scripts/")):
                self.source_hashes[name] = checksum
        script_path = Path(__file__).resolve()
        harness_hash = file_hash(script_path)
        embedded = script_path == self.release / "web/scripts/verify-production.py" \
            and self.source_hashes.get("web/scripts/verify-production.py") == harness_hash
        detached = script_path == self.work / "verify-production.py" and self.runtime.get("probe_sha256") == harness_hash
        require(embedded or detached, "explicit_source_bound_verification_harness")
        self.archive = self.release / "archive.db"
        approved = self.manifest["public_archive"]
        require(re.fullmatch(r"lr2ir-v3-public-1-[0-9a-f]{64}", approved["projection_version"]) is not None,
                "explicit_approved_projection_version")
        projection = Path("/opt/oms-ir/archives") / (approved["projection_version"] + ".db")
        require(self.archive.is_symlink() and self.archive.resolve() == projection and projection.resolve() == projection
                and projection.is_file() and not projection.is_symlink(), "only_approved_readonly_public_projection")
        self.archive_path = projection
        sys.path.insert(0, str(self.backend))
        if detached:
            probe_path = self.work / "multisource_probe.py"
            probe_hash = self.runtime.get("multisource_probe_sha256")
            probe_commit = self.runtime.get("multisource_probe_source_commit", "")
            require(probe_path.is_file() and not probe_path.is_symlink()
                    and re.fullmatch(r"[0-9a-f]{64}", probe_hash or "") is not None
                    and file_hash(probe_path) == probe_hash
                    and re.fullmatch(r"[0-9a-f]{40}", probe_commit) is not None,
                    "explicit_source_bound_detached_multisource_probe")
            spec = importlib.util.spec_from_file_location("verification_multisource_probe", probe_path)
            self.p = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.p)
        else:
            self.p = importlib.import_module("scripts.multisource_probe")
            require(Path(self.p.__file__).resolve() == self.backend / "scripts/multisource_probe.py", "candidate_probe_module")
            probe_hash = self.source_hashes["backend/scripts/multisource_probe.py"]
            probe_commit = self.manifest["backend_commit"]
        self.archive_info = self.p.archive_info(self.archive)
        require(self.archive_info == {"projection_version": approved["projection_version"], "rows": approved["total_summary_rows"],
                                      "bytes": approved["bytes"], "sha256": approved["sha256"]}, "actual_full_projection_binding")
        marker = self.work / "ownership.json"
        expected = {"format": OWNERSHIP, "work": str(self.work), "release": str(self.release),
                    "manifest_sha256": file_hash(manifest_path), "public_archive": self.archive_info, "synthetic_only": True}
        if args.phase in ("all", "seed"):
            require(not os.path.lexists(marker) and not os.path.lexists(self.data), "fresh_round_without_old_state")
            new_json(marker, expected)
        elif args.accept_transferred_seed:
            require(args.phase == "run" and not os.path.lexists(marker) and self.data.is_dir()
                    and self.database.is_file() and not self.database.is_symlink(), "explicit_transferred_seed_registration")
            transfer = self.runtime["seed_transfer"]["files"]
            require(set(transfer) == {"data/live.db", "data/seed.json", "data/credentials.json", "data/fixtures.json"},
                    "explicit_four_file_seed_transfer_receipt")
            for name, checksum in transfer.items():
                path = self.work / name
                require(path.is_file() and not path.is_symlink() and file_hash(path) == checksum,
                        "actual_transferred_seed_file_sha256")
            new_json(marker, expected)
        else:
            require(read_json(marker) == expected, "same_owned_staging_round")
        initial = {"release": str(self.release), "work": str(self.work), "base": self.base,
                   "manifest_sha256": expected["manifest_sha256"], "runtime_control_sha256": file_hash(self.runtime_path),
                   "source_sha256": self.source_hashes, "archive": self.archive_info,
                   "verification_harness_sha256": harness_hash, "harness_is_candidate_runtime_file": embedded,
                   "verification_probe_sha256": probe_hash, "verification_probe_source_commit": probe_commit,
                   "probe_is_candidate_runtime_file": not detached,
                   "data_scope": "synthetic task-owned staging DB plus immutable complete public projection",
                   "production_database_accessed": False, "browser_acceptance": False, "player_acceptance": False,
                   "fresh_operating_system_restore": False, "driver_terminal_owner_collection_required": True}
        self.evidence = Evidence(self.work, args.phase, initial)
        unit_name = cgroup_path(os.getpid()).name
        require(unit_name.startswith("oms-web-verify-"), "own_finite_driver_scope")
        driver_properties = properties(unit_name)
        require(unit_name.startswith("oms-web-verify-") and driver_properties["RemainAfterExit"] == "yes"
                and driver_properties["Restart"] == "no", "finite_owned_driver_unit")
        self.driver = BudgetUnit(unit_name, os.getpid(), 256, 0.5, 240)
        self.frontend = {}
        for name, prefix, maximum, quota, high in (("php", "oms-web-accept-", 200, 0.5, 160),
                                                  ("nginx", "oms-web-nginx-", 96, 0.25, None)):
            entry = self.runtime["frontend"][name]
            config = direct_path(entry["config"])
            require(config.is_file() and config.is_relative_to(self.work) and entry["unit"].startswith(prefix),
                    "registered_owned_frontend_config_and_unit")
            budget = entry.get("budget", {})
            memory = budget.get("memory_max_mib", maximum)
            cpu = budget.get("cpu_percent", quota * 100) / 100
            require(type(memory) is int and 0 < memory <= maximum and 0 < cpu <= quota,
                    "frontend_budget_not_widened")
            unit = BudgetUnit(entry["unit"], entry["pid"], memory, cpu, high)
            require(unit.initial["RemainAfterExit"] == "yes" and unit.initial["Restart"] == "no"
                    and (str(config) in " ".join(unit.identity["argv"]) or name == "php"),
                    "retained_registered_frontend_process")
            if name == "php":
                require(str(self.release / "web") + ":/app" in unit.initial["BindReadOnlyPaths"]
                        and str(config) + ":/etc/php85/oms-fpm.conf" in unit.initial["BindReadOnlyPaths"]
                        and str(self.work / "storage") + ":/app/storage" in unit.initial["BindPaths"],
                        "candidate_php_namespace_and_owned_writes")
            else:
                native_nginx_config(config, self.work, self.release)
            self.frontend[name] = unit
        require(self.frontend["php"].unit != self.frontend["nginx"].unit, "separate_php_nginx_cgroups")
        self.catalog = None
        catalog = self.runtime.get("catalog")
        if catalog is not None:
            require(catalog["base"] == "http://127.0.0.1:8082" and catalog["unit"] == "oms-ir-catalog.service",
                    "current_fixed_public_catalog_settings")
            self.catalog = BudgetUnit(catalog["unit"], catalog["pid"], 96, 0.25, 80)
        app_source = self.backend / "oms_ir/app.py"
        require('base_url="http://127.0.0.1:8082"' in app_source.read_text(), "actual_catalog_route_settings")
        cache = self.runtime.get("cache")
        if cache is not None:
            self.evidence.stage("cache-terminal", cache_evidence(cache, self.work, self.release, self.work / "storage"))
        temporary = self.work / "tmp"
        temporary.mkdir(mode=0o700, exist_ok=True)
        require(temporary.resolve() == temporary, "owned_temporary_directory")
        os.environ["TMPDIR"] = str(temporary)
        os.environ["PYTHONPATH"] = ""
        os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
        self.active_service = None
        self.frontend_closed = False

    def owned_file(self, path, *, exists=True):
        path = direct_path(path)
        require(path.is_relative_to(self.work) and path != self.work
                and (not exists or path.is_file() and not path.is_symlink()), "only_registered_staging_file")
        return path

    def load_state(self):
        self.metadata = read_json(self.owned_file(self.data / "seed.json"))
        credentials = read_json(self.owned_file(self.data / "credentials.json"))
        self.fixtures = read_json(self.owned_file(self.data / "fixtures.json"))
        self.users, self.keys = credentials["users"], credentials["keys"]
        require(self.metadata.get(self.p.MARKER) is True and self.metadata["database"] == "live.db"
                and self.metadata["archive"] == self.archive_info and self.metadata["oms_scores"] == 100000
                and self.metadata["native_rows"] == 29204 and self.metadata["synthetic_accounts"] == 30001
                and self.metadata.get("distinct_additions_per_ruleset") == {"bms": 100000, "mania": 100000}
                and len(self.users) == 50, "complete_owned_full_fixture")
        self.owned_file(self.database)
        if not getattr(self, "local_seed", False):
            for path in (self.data / "credentials.json", self.data / "fixtures.json"):
                require(path.stat().st_mode & 0o077 == 0, "protected_synthetic_credentials")
        with self.p.readonly(self.database) as connection:
            require(connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 30001
                    and connection.execute("SELECT COUNT(*) FROM users WHERE username_key NOT GLOB 'irms_[0-9][0-9][0-9][0-9][0-9]'").fetchone()[0] == 0,
                    "no_real_accounts_in_write_target")
            require({row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")} == TABLES,
                    "exact_22_table_fixture")
            compact = dict(connection.execute("""SELECT ruleset,COUNT(*) FROM (
                SELECT c.ruleset,s.user_id,s.chart_md5,s.group_id,s.max_ex_score FROM scores s
                JOIN score_groups g ON g.id=s.group_id JOIN charts c ON c.md5=s.chart_md5 WHERE g.public_board=1
                GROUP BY c.ruleset,s.user_id,s.chart_md5,s.group_id,s.max_ex_score) GROUP BY ruleset"""))
            require(compact.get("bms", 0) >= 100000 and compact.get("mania", 0) >= 100000
                    and connection.execute("SELECT COUNT(*) FROM scores").fetchone()[0] >= 300001,
                    "actual_complete_distinct_primary_populations")
        for index, user in enumerate(self.users):
            require(user["id"] == index + 1 and user["username"] == f"irms_{index:05d}", "only_owned_http_accounts")

    def install_services(self):
        context = self

        def start(service):
            require(context.active_service is None, "one_staging_backend_at_a_time")
            context.owned_file(service.database)
            require(service.port == context.port and service.archive == context.archive, "fixed_staging_service_endpoints")
            service.unit = "oms-web-ir-" + uuid.uuid4().hex[:16] + ".service"
            service.client.origin = context.base  # Browser Origin is the actual frontend, not the direct API port.
            service._log_path = service.directory / (service.label + "-" + uuid.uuid4().hex[:8] + ".log")
            with service._log_path.open("xb"):
                pass
            release = getattr(service, "runtime_release", context.release)
            require(release == context.release or release in
                    (context.work / "empty-restore-1/release", context.work / "empty-restore-2/release"),
                    "only_original_or_explicit_empty_restore_runtime")
            direct_path(release)
            backend = release / "backend"
            python = backend / ".venv/bin/python"
            require(file_hash(release / "release.json") == file_hash(context.release / "release.json"),
                    "API_runtime_matches_bound_candidate_manifest")
            runtime = json.loads(subprocess.check_output([str(python), "-B", "-c",
                "import json,sys,sqlite3,oms_ir; print(json.dumps({'prefix':sys.prefix,'module':oms_ir.__file__,'sqlite':sqlite3.sqlite_version}))"],
                cwd=backend, text=True, env={**os.environ, "PYTHONPATH": ""}))
            require(runtime["prefix"] == str(backend / ".venv") and runtime["module"] == str(backend / "oms_ir/__init__.py")
                    and tuple(map(int, runtime["sqlite"].split("."))) >= (3, 51, 3), "actual_API_venv_and_source_directory")
            command = [str(python), "-B", "-m", "oms_ir", "serve", "--db", str(service.database),
                       "--archive", str(context.archive_path), "--port", str(context.port), "--public-origin", context.base,
                       "--trusted-loopback-proxy", "--web-directory", str(release / "web/ir")]
            with socket.socket() as listener:
                listener.bind(("127.0.0.1", context.port))
            launch_unit(service.unit, command, context, service._log_path, 500, 150, high=384, backend=backend)
            values = properties(service.unit)
            service.pid = int(values["MainPID"])
            service._budget = BudgetUnit(service.unit, service.pid, 500, 1.5, 384)
            require(service._budget.identity["argv"] == command and service._budget.identity["cwd"] == str(backend),
                    "actual_candidate_backend_process")
            context.evidence.stage("API-runtime-" + service.unit, {"release": str(release), "backend": str(backend),
                "python": str(python), "environment_probe": runtime, "actual_process_identity": service._budget.identity,
                "restored_source_runtime": release != context.release})
            service._stopped = False
            context.active_service = service
            for _ in range(120):
                metric, body = service.client.request("GET", "/health")
                if metric["status"] == 200 and body.get("schema_version") == 3:
                    return service
                require(properties(service.unit)["MainPID"] == str(service.pid), "staging_startup_process_alive")
                time.sleep(0.1)
            raise GateFailure("staging_health_timeout")

        def stop(service):
            if getattr(service, "_stopped", True):
                return
            service._stopped = True
            context.evidence.stage("backend-before-stop-" + service.unit, service._budget.frame())
            service._budget.close(context.evidence, server_log=service._log_path)
            context.active_service = None

        self.p.Service.start, self.p.Service.stop = start, stop
        self.p.Service.systemd_services = True

    def close_frontend(self):
        if self.frontend_closed:
            return
        # Only exact units validated against owned configs and immutable app mounts.
        for name in ("nginx", "php"):
            self.frontend[name].close(self.evidence)
        self.frontend_closed = True


def launch_unit(unit, command, context, log, memory, cpu, *, high=None, backend=None):
    launch = ["systemd-run", "--quiet", "--unit=" + unit, "--property=Type=exec", "--property=RemainAfterExit=yes",
              "--property=Restart=no", "--property=MemoryAccounting=yes", "--property=CPUQuota=" + str(cpu) + "%",
              "--property=MemoryMax=" + str(memory) + "M", "--property=MemorySwapMax=0", "--property=TasksMax=96",
              "--property=UMask=0077", "--property=IPAddressDeny=any", "--property=IPAddressAllow=localhost",
              "--property=StandardOutput=append:" + str(log), "--property=StandardError=append:" + str(log),
              "--working-directory=" + str(context.backend if backend is None else backend), "--setenv=PYTHONPATH=", "--setenv=PYTHONDONTWRITEBYTECODE=1",
              "--setenv=PYTHONUNBUFFERED=1", "--setenv=TMPDIR=" + str(context.work / "tmp")]
    if high is not None:
        launch.append("--property=MemoryHigh=" + str(high) + "M")
    subprocess.run([*launch, *command], check=True, timeout=15)
    values = properties(unit)
    require(values["LoadState"] == "loaded" and values["Transient"] == "yes"
            and values["IPAddressDeny"] == "0.0.0.0/0 ::/0" and values["IPAddressAllow"] == "127.0.0.0/8 ::1/128",
            "actual_retained_loopback_unit")


def seed(context):
    p = context.p
    # Full native population + two 100k distinct player populations. This is a
    # conservative preflight, never a substitute for the measured disk peak.
    estimate = (300000 * 1800 + (4 * 29204 + 30001) * 3000 + 80 * MIB)
    free = shutil.disk_usage(context.work).free
    context.evidence.check(free >= 4 * estimate + 2 * GIB, "full_fixture_WAL_two_restores_and_2GiB_preflight")
    context.evidence.stage("seed-preflight", {"free_bytes": free, "estimated_live_bytes": estimate})
    with nullcontext() if getattr(context, "local_seed", False) else Observation(context, "seed"):
        p.seed(SimpleNamespace(directory=context.data, archive=context.archive, scores=100000, native_rows=29204, chart_md5=None))
    extend_seed(context)


def extend_seed(context):
    """Resume a validated, unchanged 100k/native base after a fixture failure."""
    p = context.p
    with nullcontext() if getattr(context, "local_seed", False) else Observation(context, "seed-extension"):
        metadata = read_json(context.data / "seed.json")
        require(metadata.get(p.MARKER) is True and metadata["archive"] == context.archive_info, "owned_seed_before_extension")
        database = p.Database(context.database)
        stamp = now()
        additions = {"bms": 0, "mania": 0}
        with database.transaction() as connection:
            require(connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 30001
                    and connection.execute("SELECT COUNT(*) FROM scores").fetchone()[0] == 100001,
                    "only_fresh_fixture_extended")
            for ruleset in ("bms", "mania"):
                for chart_index in range(2000):
                    chart = p.synthetic_chart(f"native-web-distinct/{ruleset}/{chart_index}")
                    for user_id in range(1, 51):
                        sequence = 40_000_000 + (0 if ruleset == "bms" else 100000) + chart_index * 50 + user_id
                        raw = p.oms_payload(chart, sequence)
                        raw["submission_id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, f"native-web-distinct/{ruleset}/{chart_index}/{user_id}"))
                        if ruleset == "mania":
                            raw.update(ruleset="mania", keymode="mania_7k", ruleset_data=None, bms_chart=None,
                                       total_score=9_007_199_254_740_000 if user_id <= 2 else 900000 + user_id * 100,
                                       passed=(chart_index + user_id) % 3 != 0)
                        else:
                            passed = (chart_index + user_id) % 7 != 0
                            raw["ruleset_data"].update(clear_lamp=4 if passed else 1, final_gauge=0.85 if passed else 0.1)
                            raw["passed"] = passed
                        model = p.Submission.model_validate(raw)
                        group, conditions, label, public = p.group_for(model)
                        require(public, "validated_distinct_fixture_public")
                        connection.execute("INSERT OR IGNORE INTO charts VALUES (?,?,?,?,?,?)",
                                           (chart["md5"], chart["sha256"], ruleset, chart["title"], chart["artist"], chart["difficulty"]))
                        connection.execute("INSERT OR IGNORE INTO score_groups VALUES (?,?,?,?,?)",
                                           (group, chart["md5"], conditions, label, int(public)))
                        encoded = p.canonical(model.model_dump(mode="json"))
                        connection.execute("""INSERT INTO scores(user_id,submission_id,payload_hash,payload_json,chart_md5,
                            group_id,metric,clear_lamp,received_at,max_ex_score) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                            (user_id, str(model.submission_id), hashlib.sha256(encoded.encode()).hexdigest(), encoded,
                             chart["md5"], group, model.ex_score if ruleset == "bms" else model.total_score,
                             model.ruleset_data.clear_lamp if ruleset == "bms" else None, stamp, model.max_ex_score))
                        additions[ruleset] += 1
        with database.connect() as connection:
            counts = dict(connection.execute("""SELECT ruleset,COUNT(*) FROM (
                SELECT c.ruleset,s.user_id,s.chart_md5,s.group_id,s.max_ex_score FROM scores s
                JOIN score_groups g ON g.id=s.group_id JOIN charts c ON c.md5=s.chart_md5 WHERE g.public_board=1
                GROUP BY c.ruleset,s.user_id,s.chart_md5,s.group_id,s.max_ex_score) GROUP BY ruleset"""))
            require(counts == {"bms": 100050, "mania": 100001}, "actual_two_100k_distinct_public_populations")
            require(not connection.execute("SELECT 1 FROM player_population_dirty").fetchone(), "full_fixture_population_ready")
            connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        metadata["distinct_additions_per_ruleset"] = additions
        metadata["actual_distinct_public_OMS_bests_by_ruleset"] = counts
        replace_owned_json(context.data / "seed.json", metadata)
    context.evidence.stage("seed", {"distinct_additions_per_ruleset": additions, "actual_distinct_public_bests": counts,
                                    "archive_rows_copied": 0, "database_bytes": context.database.stat().st_size})
    context.load_state()


def personal_path(p, owner, action, ruleset, **extra):
    return p.API + f"/users/{owner}/{action}?" + urlencode({"ruleset": ruleset, "keymode": ruleset + "_7k", "sources": "oms", **extra})


def raw_oms_oracle(context, database, ruleset):
    """Compute from complete core scores, never the derived population tables."""
    lanes = {}
    with context.p.readonly(database) as connection:
        rows = connection.execute("""WITH families AS (
            SELECT s.user_id,s.chart_md5,s.group_id,s.max_ex_score,MAX(s.metric) metric,MAX(s.clear_lamp) lamp
            FROM scores s JOIN score_groups g ON g.id=s.group_id JOIN charts c ON c.md5=s.chart_md5
            WHERE g.public_board=1 AND c.ruleset=? AND json_extract(g.conditions_json,'$.keymode')=?
              AND (?<>'mania' OR (json_extract(g.conditions_json,'$.total_score_version')=30000016
                   AND json_extract(g.conditions_json,'$.mods')='[]'))
            GROUP BY s.user_id,s.chart_md5,s.group_id,s.max_ex_score)
            SELECT f.*,g.conditions_json,g.label,(
                SELECT json_extract(b.payload_json,'$.passed') FROM scores b
                WHERE b.user_id=f.user_id AND b.chart_md5=f.chart_md5 AND b.group_id=f.group_id
                  AND b.max_ex_score IS f.max_ex_score AND b.metric=f.metric ORDER BY b.id LIMIT 1) passed
            FROM families f JOIN score_groups g ON g.id=f.group_id ORDER BY f.user_id,f.chart_md5""",
            (ruleset, ruleset + "_7k", ruleset))
        for row in rows:
            conditions = json.loads(row["conditions_json"])
            scope = digest({"source": "oms", "ruleset": ruleset, "keymode": ruleset + "_7k", "conditions": conditions})
            lane = lanes.setdefault(scope, {"conditions": conditions, "players": {}, "charts": {}})
            owner = row["user_id"]
            item = lane["players"].setdefault(owner, {"public_chart_count": 0, "public_best_count": 0,
                "cleared_chart_count": 0, "best_total_score": 0 if ruleset == "mania" else None})
            lane["charts"].setdefault(owner, set()).add(row["chart_md5"])
            item["public_best_count"] += 1
            item["cleared_chart_count"] += int(bool(row["passed"]) if ruleset == "mania" else row["lamp"] >= 2)
            if ruleset == "mania":
                item["best_total_score"] += row["metric"]  # Python integer: no SQLite SUM overflow.
    for lane in lanes.values():
        for owner, item in lane["players"].items():
            item["public_chart_count"] = len(lane["charts"][owner])
            if ruleset == "mania":
                item["best_total_score"] = str(item["best_total_score"])
    return lanes


def player_checks(context, service, *, fresh=False, label="player-checks"):
    p, owner = context.p, context.users[1]
    records, result = [], []
    # Measure the first actual profile request before oracle SQL warms live data.
    with Observation(context, label, service._budget):
        first_bodies = {}
        for ruleset in ("bms", "mania"):
            values, hashes = [], []
            for number in range(10 if fresh else 1):
                metric, body = service.client.request("GET", personal_path(p, owner["id"], "performance", ruleset), user=owner)
                context.evidence.stage(f"profile-HTTP-{label}-{ruleset}-{number}", metric)
                require(metric["status"] == 200 and body["lanes"] and body["totals"]["public_chart_count"] >= 2000,
                        "real_nonempty_large_player_profile")
                require(metric["ms"] <= 300, "first_and_repeated_profile_300ms")
                hashes.append(digest({name: value for name, value in body.items() if name != "snapshot"}))
                values.append(metric)
                records.append(metric)
                first_bodies[ruleset] = body
            require(len(set(hashes)) == 1, "stable_repeated_personal_body")
            result.append({"ruleset": ruleset, "first_ms": values[0]["ms"], "summary": summary(values),
                           "body_sha256_without_snapshot": hashes[0], "ten_requests": fresh,
                           "physical_cold_cache_claimed": False})
        for ruleset in ("bms", "mania"):
            oracle = raw_oms_oracle(context, service.database, ruleset)
            body = first_bodies[ruleset]
            expected_lanes = {scope: lane for scope, lane in oracle.items() if owner["id"] in lane["players"]}
            require({lane["condition_scope"]["id"] for lane in body["lanes"]} == set(expected_lanes), "raw_core_all_OMS_scopes")
            charts, bests = set(), 0
            for actual in body["lanes"]:
                scope = actual["condition_scope"]["id"]
                lane = expected_lanes[scope]
                wanted = lane["players"][owner["id"]]
                metric_key = "best_total_score" if ruleset == "mania" else "cleared_chart_count"
                metric_name = "best_total_score" if ruleset == "mania" else "cleared_charts"
                rank = 1 + sum(int(item[metric_key]) > int(wanted[metric_key]) for item in lane["players"].values())
                require(actual["source"] == "oms" and actual["metrics"] == wanted
                        and actual["rankings"] == [{"metric": metric_name, "rank": rank, "total_players": len(lane["players"])}],
                        "independent_raw_core_profile_and_rank")
                charts.update(lane["charts"][owner["id"]])
                bests += wanted["public_best_count"]
                ordered = sorted(lane["players"], key=lambda user_id: (-int(lane["players"][user_id][metric_key]), user_id))
                query = {"ruleset": ruleset, "keymode": ruleset + "_7k", "source": "oms", "condition": scope,
                         "metric": metric_name, "limit": 1}
                initial_me = None
                for page, expected_owner in ((1, ordered[0]), (len(ordered), ordered[-1]), (len(ordered) + 1, None)):
                    metric, ranked = service.client.request("GET", p.API + "/rankings/players?" + urlencode({**query, "page": page}), user=owner)
                    require(metric["status"] == 200 and metric["ms"] <= 1000 and ranked["total"] == len(ordered),
                            "real_global_rank_first_tail_1s")
                    if expected_owner is None:
                        require(ranked["items"] == [], "global_rank_outside_page_empty")
                    else:
                        require(len(ranked["items"]) == 1 and ranked["items"][0]["user"]["id"] == expected_owner
                                and ranked["items"][0]["value"] == str(lane["players"][expected_owner][metric_key]),
                                "raw_core_global_rank_order")
                    require(ranked["me"]["user"]["id"] == owner["id"] and ranked["me"]["rank"] == rank
                            and ranked["me"]["value"] == str(wanted[metric_key]), "offpage_me_rank")
                    if initial_me is not None:
                        require(ranked["me"] == initial_me, "same_me_on_all_rank_pages")
                    initial_me = ranked["me"]
                    records.append(metric)
            require(body["totals"] == {"public_chart_count": len(charts), "public_best_count": bests}, "raw_core_player_totals")
            for action in ("public-bests", "public-recent"):
                for page in (1, math.ceil(bests / 20)):
                    metric, listed = service.client.request("GET", personal_path(p, owner["id"], action, ruleset, page=page, limit=20), user=owner)
                    require(metric["status"] == 200 and metric["ms"] <= 1000 and listed["total"] == bests
                            and bool(listed["items"]), "large_public_best_first_tail_1s")
                    records.append(metric)
            require(all(owner[transport][field] not in p.canonical(body)
                        for transport in ("desktop", "browser") for field in ("access", "refresh", "session")),
                    "no_tokens_in_public_player_body")
            del oracle, expected_lanes, lane, charts, ordered, wanted
    return {"first_profile": result, "http": summary(records), "independent_complete_raw_core_math": True,
            "two_rulesets_distinct_primary_bests": context.metadata["distinct_additions_per_ruleset"]}


def frontend_routes(context):
    owner = context.users[1]["id"]
    return ["/", "/ir?md5=" + context.metadata["chart"]["md5"],
            "/beatmapsets/" + context.metadata["chart"]["md5"],
            f"/users/{owner}?ruleset=bms&keymode=bms_7k&sources=oms",
            f"/users/{owner}?ruleset=mania&keymode=mania_7k&sources=oms",
            "/rankings?ruleset=bms&keymode=bms_7k&source=oms&metric=coverage",
            "/rankings?ruleset=mania&keymode=mania_7k&source=oms&metric=best_total_score",
            "/community?limit=20"]


def frontend_checks(context, service, label):
    records = []
    with Observation(context, label, service._budget):
        for index, path in enumerate(frontend_routes(context)):
            metric, body, headers = context.web.request(path, peer=f"127.0.0.{2 + index}")
            require(metric["status"] == 200 and b"<html" in body.lower(), "actual_native_php_page")
            require(metric["ms"] <= 1000, "native_php_player_page_1s")
            require("no-cache" in headers.get("cache-control", "") or "no-store" in headers.get("cache-control", ""),
                    "mutable_page_revalidation")
            require("x-content-type-options" in headers and "content-security-policy" in headers, "native_security_headers")
            require(all(user[transport][field].encode() not in body for user in context.users
                        for transport in ("browser", "desktop") for field in ("access", "refresh")),
                    "no_auth_tokens_in_PHP_HTML")
            records.append(metric)
    return {"http": summary(records), "native_PHP_routes": len(records), "real_TCP_source_addresses": True,
            "browser_JavaScript_executed": False, "browser_and_player_acceptance_pending": True}


def full_pagination(context, service, label):
    p = context.p
    selected = list(p.SOURCE_LABELS)
    with Observation(context, label, service._budget):
        expected = p.expected_board(service.database, context.archive, context.metadata["chart"]["md5"], selected)
        require(len(expected) >= 10000, "real_full_maximum_archive_board")
        records = []
        for page in range(1, math.ceil(len(expected) / 20) + 2):
            metric, body = service.client.request("GET", p.board_path(context.metadata["chart"]["md5"], selected, page=page),
                                                  user=context.users[(page - 1) % 50])
            require(metric["status"] == 200 and metric["ms"] <= 300, "full_board_all_pages_300ms")
            p.check_board(body, expected, selected, page, mine=context.users[(page - 1) % 50]["id"])
            records.append(metric)
    return {"people": len(expected), "pages_with_rows": math.ceil(len(expected) / 20), "outside_page_verified": True,
            "all_pages_rank_best_lamp_source_identity_checked": True, "http": summary(records),
            "ordered_result_sha256": digest(expected), "personal_rows_in_report": False}


def fresh_source_queries(context):
    p, cases = context.p, []
    selections = [["oms"], ["lr2ir.v3.lr2"], ["lr2ir.v3.sbmp"], ["lr2ir.v3.unknown"],
                  ["oms", "lr2oraja_ed", "lr2ir.v3.lr2"], list(p.SOURCE_LABELS), []]
    for index, selected in enumerate(selections):
        service = p.Service(context.data, context.database, context.archive, context.port, f"fresh-query-{index}")
        service.start()
        try:
            with Observation(context, f"fresh-query-{index}", service._budget):
                cache_advice = p.evict_advice((context.database, context.archive))
                expected = p.expected_board(context.database, context.archive, context.metadata["chart"]["md5"], selected)
                first = None
                records = []
                for repeat in range(5):
                    for position, page in enumerate((1, max(1, math.ceil(len(expected) / 20)))):
                        metric, body = service.client.request("GET", p.board_path(context.metadata["chart"]["md5"], selected, page=page),
                                                              user=context.users[1])
                        context.evidence.stage(f"fresh-source-HTTP-{index}-{repeat}-{position}",
                            {"sources": selected, "page": page, "repeat": repeat, "position": position, "HTTP": metric})
                        require(metric["status"] == 200, "fresh_source_board_HTTP_200")
                        require(metric["ms"] <= 300, "fresh_and_warm_source_board_300ms")
                        p.check_board(body, expected, selected, page, mine=2)
                        if first is None:
                            first = metric["ms"]
                        records.append(metric)
                metric, body = service.client.request("GET", p.board_path(context.metadata["chart"]["md5"], selected, browser=True),
                                                      user=context.users[1], browser=True)
                context.evidence.stage(f"fresh-source-browser-HTTP-{index}", {"sources": selected, "HTTP": metric})
                require(metric["status"] == 200, "browser_source_board_HTTP_200")
                require(metric["ms"] <= 300, "browser_and_game_source_board_300ms")
                p.check_board(body, expected, selected, 1, mine=2)
                records.append(metric)
                cases.append({"sources": selected, "participants": len(expected), "first_process_request_ms": first,
                              "summary": summary(records), "cache_advice": cache_advice,
                              "physical_cold_cache_proven": False, "first_tail_and_browser_math_checked": True})
                del expected
        finally:
            service.stop()
    return {"cases": cases, "seven_actual_fresh_process_source_selections": True,
            "full_projection_not_source_TopN": True}


def adapter_checks(context, service):
    assets = {name.removeprefix("web/ir/adapters/"): checksum for name, checksum in context.runtime_files.items()
              if name.startswith("web/ir/adapters/")}
    require(len(assets) == 8, "real_eight_published_adapter_assets")
    records = []
    with Observation(context, "real-adapters", service._budget):
        for name, checksum in assets.items():
            metric, body, _ = context.web.request("/ir/adapters/" + name, peer="127.0.0.60")
            require(metric["status"] == 200 and hashlib.sha256(body).hexdigest() == checksum,
                    "real_adapter_bytes_through_candidate_Nginx")
            records.append(metric)
    return {"assets": len(assets), "actual_same_bytes_verified": True, "HTTP": summary(records),
            "target_player_launch_submission_and_native_UI_read_acceptance_pending": True}


def actor_checks(context, service):
    owner, other = context.users[:2]
    body = {"submission_id": str(uuid.uuid4()), "title": "Synthetic actor boundary",
            "body": "Only this isolated staging account and draft.", "category": "development"}
    headers = {"Origin": context.base, "Content-Type": "application/json", "X-OMS-IR": "1",
               "Cookie": context.p.Auth.ACCESS_COOKIE + "=" + owner["browser"]["access"]}
    records = []
    with Observation(context, "actual-browser-actor", service._budget):
        metric, raw, _ = context.web.request(context.p.API + "/community/posts", method="POST", body=body,
                                             peer="127.0.0.61", headers={**headers, "X-OMS-Actor": str(other["id"])})
        reply = json.loads(raw)
        require(metric["status"] == 409 and reply["error"]["code"] == "actor_changed", "actual_browser_actor_mismatch_409")
        with context.p.readonly(service.database) as connection:
            require(connection.execute("SELECT COUNT(*) FROM community_posts WHERE submission_id=?", (body["submission_id"],)).fetchone()[0] == 0,
                    "actor_mismatch_preserves_draft_without_post_write")
        records.append(metric)
        for status in (201, 200):
            metric, raw, _ = context.web.request(context.p.API + "/community/posts", method="POST", body=body,
                                                 peer="127.0.0.61", headers={**headers, "X-OMS-Actor": str(owner["id"])})
            reply = json.loads(raw)
            require(metric["status"] == status and reply["duplicate"] is (status == 200), "actor_same_UUID_new_and_duplicate")
            records.append(metric)
        target = context.p.key_for(context.keys, owner["id"], "lr2oraja_ed")
        metric, raw, _ = context.web.request(context.p.API + f"/integration-keys/{target['id']}/revoke", method="POST", body={},
                                             peer="127.0.0.61", headers={**headers, "X-OMS-Actor": str(other["id"])})
        require(metric["status"] == 409 and json.loads(raw)["error"]["code"] == "actor_changed", "actor_mismatch_cannot_revoke_key")
        with context.p.readonly(service.database) as connection:
            require(connection.execute("SELECT revoked FROM integration_keys WHERE id=?", (target["id"],)).fetchone()[0] == 0,
                    "actor_mismatch_key_remains_active")
        records.append(metric)
    return {"actual_Nginx_browser_boundary": True, "wrong_actor_409_without_post_or_key_write": True,
            "same_saved_UUID_preserved_across_retry": True, "HTTP": summary(records), "credentials_in_report": False}


def sustained(context, service):
    seconds = context.args.seconds
    routes = frontend_routes(context)
    records, started = [], time.monotonic()

    def php_load():
        def request(path, peer, planned):
            metric, body, _ = context.web.request(path, peer=peer, scheduled_at=planned)
            require(metric["status"] == 200 and b"<html" in body.lower(), "sustained_actual_native_PHP_success")
            return metric

        with ThreadPoolExecutor(max_workers=8) as executor:
            jobs = []
            count = math.ceil(seconds / 2)
            for index in range(count):
                planned = started + index * 2
                if planned > time.monotonic():
                    time.sleep(planned - time.monotonic())
                path = routes[index % len(routes)]
                jobs.append(executor.submit(request, path, f"127.0.0.{2 + index % 50}", planned))
            for job in jobs:
                records.append(job.result())

    with Observation(context, "sustained", service._budget) as observer:
        with ThreadPoolExecutor(max_workers=2) as executor:
            frontend = executor.submit(php_load)
            api = executor.submit(context.p.traffic_stage, service, context.metadata, context.users, context.keys,
                                  seconds, 5, phase="sustained")
            api_result = api.result()
            frontend.result()
        actual_http_completed = time.monotonic() - started
        php_summary = summary(records)
        http_result = {"requested_seconds": seconds, "actual_HTTP_completion_seconds": actual_http_completed,
                       "direct_API": api_result, "PHP_Nginx_full_stack": php_summary,
                       "PHP_request_rate_per_second": 0.5, "distinct_actual_loopback_source_peers": 50,
                       "visitor_forwarding_headers_used_to_choose_quota": False,
                       "same_interval_includes_original_UUID_external_best_and_community_writes": True}
        # Keep actual measurement alive to the complete requested window; do not
        # relabel the last request at (seconds - 0.2) as a 1800-second sample span.
        while observer.first is None or time.monotonic() - observer.first["monotonic"] < seconds:
            time.sleep(0.05)
        context.evidence.stage("sustained-HTTP-measurements", {
            **http_result, "actual_API_latency_and_write_gate_passed": api_result["traffic_gate_passed"],
            "actual_PHP_1s_gate_passed": php_summary["p95_confirmation_ms"] <= 1000,
            "resource_gate_consumed": False})
    require(api_result["traffic_gate_passed"], "actual_5_per_second_overlap_API_latency_and_write_gate")
    require(php_summary["p95_confirmation_ms"] <= 1000, "sustained_php_page_p95_1s")
    return {**http_result,
            "resource_sample_span_seconds": observer.result()["sample_span_seconds"],
            "actual_measured_1800_seconds": seconds >= 1800 and observer.result()["sample_span_seconds"] >= 1800}


def quota_probe(context, service):
    """Exercise real Nginx remote_addr for both proxy API and PHP SSR."""
    results = []
    with Observation(context, "real-egress-quota", service._budget):
        for peer, path in (("127.0.0.200", context.p.V2 + "/sources"), ("127.0.0.201", "/community?limit=1")):
            began = time.monotonic()
            with ThreadPoolExecutor(max_workers=24) as executor:
                futures = [executor.submit(context.web.request, path, peer=peer,
                            headers={"X-Forwarded-For": f"198.19.252.{1 + index % 250}"}) for index in range(650)]
                records = [future.result()[0] for future in futures]
            duration = time.monotonic() - began
            with context.p.readonly(service.database) as connection:
                row = connection.execute("SELECT hits,expires FROM rate_limits WHERE key=?", ("read:" + peer,)).fetchone()
                forged = connection.execute("SELECT COUNT(*) FROM rate_limits WHERE key LIKE 'read:198.19.252.%'").fetchone()[0]
            counts = Counter(record["status"] for record in records)
            require(duration < 60 and counts == {200: 600, 429: 50} and row is not None and row["hits"] == 600
                    and row["expires"] > time.time() and forged == 0, "real_same_egress_600_per_minute_no_forged_XFF_bypass")
            require(all(record["retry_after"] is not None and int(record["retry_after"]) > 0
                        for record in records if record["status"] == 429), "quota_actual_retry_after")
            results.append({"route": "PHP_SSR" if path.startswith("/community") else "Nginx_API_proxy",
                            "requests": 650, "summary": summary(records), "elapsed_seconds": duration,
                            "actual_peer_bucket_hits": row["hits"], "forged_forwarded_buckets": forged})
        different = []
        for peer in ("127.0.0.202", "127.0.0.203"):
            metric, _, _ = context.web.request("/community?limit=1", peer=peer, headers={"X-Forwarded-For": "127.0.0.201"})
            require(metric["status"] == 200, "different_real_peer_not_shared_quota")
            with context.p.readonly(service.database) as connection:
                row = connection.execute("SELECT hits FROM rate_limits WHERE key=?", ("read:" + peer,)).fetchone()
            require(row is not None and row["hits"] == 1, "PHP_SSR_actual_distinct_trusted_peer_bucket")
            different.append(metric)
    return {"cases": results, "different_real_peer_summary": summary(different), "visitor_XFF_cannot_select_bucket": True,
            "600_per_minute_observed_through_real_PHP_and_Nginx": True}


def maintenance(context, service, operation, source, destination, report):
    source, destination, report = (context.owned_file(source), context.owned_file(destination, exists=False),
                                   context.owned_file(report, exists=False))
    require(not os.path.lexists(destination) and not os.path.lexists(report), "maintenance_new_destinations")
    unit = "oms-web-maint-" + uuid.uuid4().hex[:16] + ".service"
    ready, go, final, close = (report.with_name(report.stem + "-" + name + ".json")
                               for name in ("ready", "go", "last-live", "close"))
    log = report.with_suffix(".log")
    with log.open("xb"):
        pass
    command = [str(context.python), "-B", str(Path(__file__).resolve()), "--phase", "maintenance",
               "--release", str(context.release), "--work", str(context.work), "--base", context.base,
               "--operation", operation, "--source", str(source), "--destination", str(destination),
               "--worker-report", str(report), "--unit", unit, "--ready", str(ready), "--go", str(go),
               "--last-live", str(final), "--close", str(close)]
    launch_unit(unit, command, context, log, 128, 50)
    deadline = time.monotonic() + 30
    while not ready.is_file() and time.monotonic() < deadline:
        require(properties(unit)["MainPID"] != "0", "maintenance_worker_startup_alive")
        time.sleep(0.05)
    require(ready.is_file(), "actual_maintenance_ready")
    state = read_json(ready)
    budget = BudgetUnit(unit, state["pid"], 128, 0.5)
    with Observation(context, "maintenance-" + operation + "-" + unit, service._budget, budget):
        new_json(go, {"unit": unit, "pid": budget.pid})
        deadline = time.monotonic() + 1800
        while not report.is_file() and time.monotonic() < deadline:
            require(properties(unit)["MainPID"] == str(budget.pid), "maintenance_operation_process_alive")
            time.sleep(0.1)
        require(report.is_file(), "maintenance_operation_completed_within_bound")
    new_json(close, {"unit": unit, "pid": budget.pid})
    deadline = time.monotonic() + 30
    while properties(unit)["MainPID"] != "0" and time.monotonic() < deadline:
        time.sleep(0.05)
    require(properties(unit)["MainPID"] == "0", "maintenance_finite_completion")
    last = read_json(final)
    budget.terminal(context.evidence, last)
    result = read_json(report)
    require(result["status"] == "completed", "actual_consistent_backup_or_restore_completed")
    return result


def wait_owner_file(path, *, seconds=3600):
    deadline = time.monotonic() + seconds
    while not path.is_file() and time.monotonic() < deadline:
        time.sleep(0.25)
    require(path.is_file(), "explicit_owner_restore_receipt_required")
    return read_json(path)


def bind_restored_frontend(context, destination, number):
    """Pause for the owner to restore full PHP sources/assets and fresh caches."""
    original_php = context.frontend["php"].initial
    context.close_frontend()
    release = destination / "release"
    cache = destination / "runtime"
    ready = context.work / f"restore-frontend-{number}-ready.json"
    receipt_path = context.work / f"restore-frontend-{number}-receipt.json"
    new_json(ready, {"round": number, "release_target": str(release), "cache_target": str(cache),
                     "database": str(destination / "live.db"), "base": context.base,
                     "original_release_manifest_sha256": file_hash(context.release / "release.json"),
                     "required": "restore the complete native package; offline frozen uv sync in restored/backend; rebuild fresh PHP caches; start one registered PHP/Nginx pair"})
    with Observation(context, f"owner-source-restore-{number}"):
        receipt = wait_owner_file(receipt_path)
    require(receipt["round"] == number and receipt["release"] == str(release) and receipt["cache_root"] == str(cache)
            and receipt["source_restored_from_package"] is True, "explicit_full_frontend_restore_receipt")
    environment = receipt["backend_environment"]
    require(environment["prefix"] == str(release / "backend/.venv")
            and environment["module"] == str(release / "backend/oms_ir/__init__.py")
            and tuple(map(int, environment["sqlite"].split("."))) >= (3, 51, 3), "restored_offline_backend_environment")
    owner_path = context.work / f"verification-owner-restore-{number}.json"
    owner = read_json(owner_path)
    require(file_hash(owner_path) == receipt["owner_report_sha256"] and owner["status"] == "completed"
            and owner["stages"][f"resources-owner-restore-{number}"]["passed"], "actual_owner_restore_resource_samples")
    direct_path(release)
    require(file_hash(release / "release.json") == file_hash(context.release / "release.json"), "restored_release_manifest_same_bytes")
    for name, checksum in context.runtime_files.items():
        path = release / name
        require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(release)
                and file_hash(path) == checksum, "each_full_restored_runtime_file_SHA256")
    units = {}
    for name, prefix, memory, cpu, high in (("php", "oms-web-accept-", 200, 0.5, 160),
                                          ("nginx", "oms-web-nginx-", 96, 0.25, None)):
        entry = receipt["frontend"][name]
        config = direct_path(entry["config"])
        require(config.is_file() and config.is_relative_to(context.work) and entry["unit"].startswith(prefix),
                "registered_restored_frontend_config")
        unit = BudgetUnit(entry["unit"], entry["pid"], memory, cpu, high)
        require(unit.initial["RemainAfterExit"] == "yes" and unit.initial["Restart"] == "no",
                "restored_finite_frontend_units")
        if name == "php":
            require(unit.initial["RootDirectory"] == original_php["RootDirectory"]
                    and str(release / "web") + ":/app" in unit.initial["BindReadOnlyPaths"]
                    and str(config) + ":/etc/php85/oms-fpm.conf" in unit.initial["BindReadOnlyPaths"]
                    and str(cache / "storage") + ":/app/storage" in unit.initial["BindPaths"]
                    and str(cache / "bootstrap") + ":/app/bootstrap/cache" in unit.initial["BindPaths"],
                    "restored_PHP_app_and_fresh_cache_mounts")
        else:
            require(str(config) in " ".join(unit.identity["argv"]), "actual_restored_Nginx_config")
            native_nginx_config(config, context.work, release)
        units[name] = unit
    values = cache_evidence(receipt["cache"], context.work, release, cache / "storage")
    context.frontend = units
    context.frontend_closed = False
    result = {"round": number, "full_files_verified": len(context.runtime_files), "restore_target": str(release),
              "receipt_sha256": file_hash(receipt_path), "manifest_sha256": file_hash(release / "release.json"),
              "fresh_cache_build_terminal": values, "shared_readonly_PHP_OS_runtime": original_php["RootDirectory"],
              "backend_environment": environment, "owner_report_sha256": file_hash(owner_path),
              "owner_runtime_disk_phases": receipt["runtime_disk_phases"],
              "complete_source_dependency_and_assets_verified": True, "fresh_OS_recovery": False}
    context.evidence.stage(f"complete-PHP-source-restore-{number}", result)
    return result


def serial_export(context, destination, compressed, number):
    """The owner exports/validates on F and removes only these stopped targets."""
    paths = [destination, compressed, compressed.with_name(compressed.name + ".json")]
    ready = context.work / f"recovery-export-{number}-ready.json"
    receipt = context.work / f"recovery-export-{number}-receipt.json"
    new_json(ready, {"round": number, "owned_stopped_paths": [str(path) for path in paths],
                    "gzip_sha256": file_hash(compressed), "sidecar_sha256": file_hash(paths[2]),
                    "restored_database_sha256": file_hash(destination / "live.db"),
                    "remove_only_after_complete_F_export_and_verification": True})
    with Observation(context, f"owner-export-{number}", context.active_service._budget):
        value = wait_owner_file(receipt)
    require(value["round"] == number and value["complete_F_export_verified"] is True
            and value["removed_owned_paths"] == [str(path) for path in paths]
            and not any(os.path.lexists(path) for path in paths), "verified_F_export_and_exact_owned_retirement")
    context.evidence.stage(f"serial-export-{number}", {"receipt_sha256": file_hash(receipt),
                                                      "root_executed_export_and_retirement": True,
                                                      "script_deleted_recovery_data": False})


def recovery(context, service):
    p, results = context.p, []
    original_mappings = {}
    for source in p.VERSIONS:
        metric, body = service.client.request("GET", p.V2 + "/external/me", key=p.key_for(context.keys, 2, source))
        require(metric["status"] == 200, "original_native_mapping_before_snapshot")
        original_mappings[source] = body["native_player_id"]
    for number in (1, 2):
        destination = context.work / f"empty-restore-{number}"
        require(not os.path.lexists(destination), "actual_new_empty_recovery_directory")
        destination.mkdir(mode=0o700)
        reader = None
        wal = {"uncheckpointed_committed_policy_delta_proven": False}
        try:
            renew_synthetic_sessions(context, service, label=f"pre-snapshot-owned-session-refresh-{number}")
            if number == 2:
                # Leave a real reader at the old committed frame while HTTP and
                # ordinary moderation commit changes to the same synthetic DB.
                with p.Database(context.database).connect() as connection:
                    checkpoint = connection.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
                    require(checkpoint[0] == 0, "pre_policy_WAL_checkpoint_not_busy")
                reader = sqlite3.connect(context.database.as_uri() + "?mode=ro", uri=True, isolation_level=None)
                reader.execute("BEGIN")
                target_key = p.key_for(context.keys, 1, "lr2oraja_ed")
                require(reader.execute("SELECT revoked FROM integration_keys WHERE id=?", (target_key["id"],)).fetchone()[0] == 0,
                        "pinned_old_key_active")
                require(reader.execute("SELECT hidden FROM community_posts WHERE id=?", (context.fixtures["posts"][0]["id"],)).fetchone()[0] == 0,
                        "pinned_old_post_visible")
                metric, _ = service.client.request("POST", p.API + f"/integration-keys/{target_key['id']}/revoke",
                                                   user=context.users[0], browser=True, body={})
                require(metric["status"] == 200, "actual_HTTP_policy_key_revocation")
                metric, _ = service.client.request("POST", p.API + "/auth/logout", user=context.users[0], body={})
                require(metric["status"] == 204, "actual_HTTP_policy_session_revocation")
                p.moderate_post(p.Database(context.database), context.fixtures["posts"][0]["id"], hidden=True, reason="synthetic staging restore")
                p.moderate_archive(p.Database(context.database), context.archive, context.fixtures["archive_hidden"][1], "",
                                  hidden=True, reason="synthetic staging restore")
                with p.Database(context.database).transaction() as connection:
                    connection.execute("UPDATE score_groups SET public_board=0 WHERE id=?", (context.metadata["distinct_hidden_group"],))
                with p.readonly(context.database, immutable=True) as base:
                    base_state = [base.execute("SELECT revoked FROM integration_keys WHERE id=?", (target_key["id"],)).fetchone()[0],
                                  base.execute("SELECT hidden FROM community_posts WHERE id=?", (context.fixtures["posts"][0]["id"],)).fetchone()[0],
                                  base.execute("SELECT public_board FROM score_groups WHERE id=?", (context.metadata["distinct_hidden_group"],)).fetchone()[0]]
                with p.readonly(context.database) as live:
                    current_state = [live.execute("SELECT revoked FROM integration_keys WHERE id=?", (target_key["id"],)).fetchone()[0],
                                     live.execute("SELECT hidden FROM community_posts WHERE id=?", (context.fixtures["posts"][0]["id"],)).fetchone()[0],
                                     live.execute("SELECT public_board FROM score_groups WHERE id=?", (context.metadata["distinct_hidden_group"],)).fetchone()[0]]
                wal_bytes = Path(str(context.database) + "-wal").stat().st_size
                require(base_state == [0, 0, 1] and current_state == [1, 1, 0] and wal_bytes > 0,
                        "main_file_differs_from_committed_WAL_policy")
                wal = {"uncheckpointed_committed_policy_delta_proven": True, "wal_bytes": wal_bytes,
                       "immutable_main_policy": base_state, "consistent_current_policy": current_state,
                       "reader_held_through_backup_and_restore": True}
            # Take all logical fingerprints before any recovered HTTP request.
            with Observation(context, f"recovery-fingerprint-{number}", service._budget):
                before = p.logical_fingerprint(context.database)
            require(set(before["tables"]) == TABLES, "all_22_tables_in_snapshot")
            compressed = context.work / f"snapshot-round-{number}.db.gz"
            backup = maintenance(context, service, "backup", context.database, compressed, destination / "backup-report.json")
            restored_path = destination / "live.db"
            restored_report = maintenance(context, service, "restore", compressed.with_name(compressed.name + ".json"),
                                          restored_path, destination / "restore-report.json")
            with Observation(context, f"restored-fingerprint-{number}", service._budget):
                after = p.logical_fingerprint(restored_path)
            require(before == after, "all_22_tables_and_schema_equal_before_restored_HTTP")
            if reader is not None:
                reader.rollback()
                reader.close()
                reader = None
            service.stop()
            unavailable, _, _ = context.web.request("/community?limit=1", peer="127.0.0.205")
            require(unavailable["status"] == 503, "actual_PHP_backend_unavailable_503")
            source_restore = None
            if context.args.external_frontend_restores:
                source_restore = bind_restored_frontend(context, destination, number)
            new_json(destination / "seed.json", {p.MARKER: True, "database": "live.db", "archive": context.archive_info, "recovery_round": number})
            recovered = p.Service(destination, restored_path, context.archive, context.port, "restored-" + str(number))
            if source_restore is not None:
                recovered.runtime_release = destination / "release"
            recovered.start()
            try:
                with Observation(context, f"recovered-api-{number}", recovered._budget):
                    checks = p.api_checks(recovered, context.metadata, context.users, context.keys, context.fixtures, revoked=number == 2)
                    for source, expected in original_mappings.items():
                        metric, body = recovered.client.request("GET", p.V2 + "/external/me", key=p.key_for(context.keys, 2, source))
                        require(metric["status"] == 200 and body["native_player_id"] == expected, "stable_native_identity_after_restore")
                player = player_checks(context, recovered, label=f"recovered-player-{number}")
                frontend = frontend_checks(context, recovered, f"recovered-frontend-{number}")
                pages = full_pagination(context, recovered, f"recovered-full-pages-{number}")
                with Observation(context, f"recovered-native-{number}", recovered._budget):
                    native = p.native_stage(recovered, context.metadata, context.keys)
                    require(native["under_10_seconds"] and native["gzip_wire_and_complete_decoded_bodies_verified"],
                            "full_native_read_boards_after_restore")
            finally:
                recovered.stop()
            results.append({"round": number, "actual_new_empty_directory": True, "backup": backup,
                            "restore": restored_report, "logical_state_equal_before_HTTP": True, "all_22_table_fingerprints": before,
                            "snapshot_bytes": restored_path.stat().st_size, "wal": wal, "actual_API": checks,
                            "public_profiles_and_rank": player, "PHP_Nginx": frontend, "full_maximum_board": pages,
                            "native": native, "native_mapping_sources_preserved": list(original_mappings),
                            "complete_PHP_source_restore": source_restore,
                            "one_backend_process_at_a_time": True, "same_immutable_projection_referenced": True})
            context.evidence.stage(f"recovery-{number}", results[-1])
            service.label = "resumed-original-" + str(number)
            service.start()
            if context.args.serial_export:
                # The restored frontend must stop before its source/cache tree
                # is exported and retired. The owner starts an original-source
                # pair for round 2 (or another explicit final validation).
                if context.args.external_frontend_restores:
                    context.close_frontend()
                serial_export(context, destination, compressed, number)
                if number == 1:
                    restart_ready = context.work / "restart-original-frontend-ready.json"
                    restart_receipt = context.work / "restart-original-frontend-receipt.json"
                    new_json(restart_ready, {"release": str(context.release), "base": context.base})
                    with Observation(context, "owner-restart-original-frontend", service._budget):
                        restart = wait_owner_file(restart_receipt)
                    require(restart["release"] == str(context.release), "original_frontend_restart_binding")
                    units = {}
                    for name, memory, cpu, high in (("php", 200, 0.5, 160), ("nginx", 96, 0.25, None)):
                        entry = restart["frontend"][name]
                        prefix = "oms-web-accept-" if name == "php" else "oms-web-nginx-"
                        config = direct_path(entry["config"])
                        require(entry["unit"].startswith(prefix) and config.is_file() and config.is_relative_to(context.work),
                                "owned_original_restart_config")
                        unit = BudgetUnit(entry["unit"], entry["pid"], memory, cpu, high)
                        require(unit.initial["RemainAfterExit"] == "yes" and unit.initial["Restart"] == "no",
                                "finite_original_frontend_restart")
                        if name == "php":
                            require(str(context.release / "web") + ":/app" in unit.initial["BindReadOnlyPaths"]
                                    and str(config) + ":/etc/php85/oms-fpm.conf" in unit.initial["BindReadOnlyPaths"]
                                    and str(context.work / "storage") + ":/app/storage" in unit.initial["BindPaths"],
                                    "original_source_and_owned_cache_restart")
                        else:
                            require(str(config) in " ".join(unit.identity["argv"]), "original_Nginx_restart_config")
                            native_nginx_config(config, context.work, context.release)
                        units[name] = unit
                    context.frontend = units
                    context.frontend_closed = False
        finally:
            if reader is not None:
                reader.rollback()
                reader.close()
    return {"rounds": results, "two_actual_empty_directory_HTTP_restores_passed": True,
            "fresh_operating_system_recovery_claimed": False, "live_production_database_written_or_restored": False}


def record_hideable_group(context):
    chart = context.p.synthetic_chart("native-web-distinct/bms/1999")
    with context.p.readonly(context.database) as connection:
        row = connection.execute("SELECT id FROM score_groups WHERE chart_md5=? AND public_board=1", (chart["md5"],)).fetchone()
    require(row is not None, "actual_distinct_hideable_scope_group")
    context.metadata["distinct_hidden_group"] = row[0]
    replace_owned_json(context.data / "seed.json", context.metadata)


def disk_gate(context, restore_result):
    maximum_gzip = max(row["backup"]["backup"]["gzip"]["bytes"] for row in restore_result["rounds"])
    maximum_raw = max(context.database.stat().st_size,
                      *(row["backup"]["backup"]["snapshot"]["bytes"] for row in restore_result["rounds"]))
    wal = Path(str(context.database) + "-wal")
    if wal.is_file():
        maximum_raw = max(maximum_raw, context.database.stat().st_size + wal.stat().st_size)
    samples = [row for name, row in context.evidence.data["stages"].items() if name.startswith("resources-")]
    require(samples, "actual_recovery_disk_observations")
    maximum_raw = max(maximum_raw, *(peak["main_plus_wal_bytes"] for row in samples for peak in row["owned_database_peaks"].values()))
    minimum_free = min(row["minimum_disk_free_frame"]["disk_free_bytes"] for row in samples)
    free = shutil.disk_usage(context.work).free
    retained_pairs = 8 * (maximum_gzip + MIB)
    required = retained_pairs + maximum_raw + 2 * GIB
    return {"actual_free_after_retained_releases_projection_and_two_restores_bytes": free,
            "actual_maximum_gzip_bytes": maximum_gzip, "actual_maximum_raw_or_main_plus_WAL_bytes": maximum_raw,
            "seven_daily_pairs_plus_one_atomic_write_and_one_raw_restore_bytes": required - 2 * GIB,
            "system_margin_bytes": 2 * GIB, "required_additional_free_bytes": required,
            "passed": free >= required and minimum_free >= retained_pairs + 2 * GIB,
            "actual_minimum_free_during_backup_restore_source_dependencies_cache_and_HTTP_bytes": minimum_free,
            "actual_2GiB_margin_throughout_sampled_recovery": minimum_free >= 2 * GIB,
            "eight_retained_pairs_fit_at_actual_recovery_peak": minimum_free >= retained_pairs + 2 * GIB,
            "actual_recovery_peak_additional_retention_bytes": retained_pairs,
            "synthetic_capacity_snapshots_only": True, "formal_production_daily_pairs_checked": False,
            "formal_live_DB_and_actual_daily_backups_require_separate_owner_evidence": True}


def renew_synthetic_sessions(context, service, *, label="real-owned-session-refresh"):
    """Keep long acceptance runs within the real, unchanged one-hour lifetime."""
    credentials = read_json(context.data / "credentials.json")
    credentials["users"] = context.users
    sessions = [(user[transport]["session"], user["id"], transport)
                for user in context.users for transport in ("desktop", "browser")]
    with context.p.readonly(context.database) as connection:
        require(all(tuple(connection.execute("SELECT user_id,transport,revoked FROM sessions WHERE id=?", (session,)).fetchone())
                    == (owner, transport, 0) for session, owner, transport in sessions), "owned_active_sessions_before_refresh")
    with Observation(context, label, service._budget):
        for user in context.users:
            for transport in ("desktop", "browser"):
                headers = {"Content-Type": "application/json"}
                if transport == "desktop":
                    body = {"refresh_token": user[transport]["refresh"]}
                else:
                    headers.update(Origin=context.base, Cookie="oms_ir_refresh=" + user[transport]["refresh"])
                    headers["X-OMS-IR"] = "1"
                    body = {}
                client = http.client.HTTPConnection("127.0.0.1", context.port, timeout=10)
                try:
                    began = time.monotonic()
                    client.request("POST", "/api/ir/v1/auth/refresh", json.dumps(body).encode(), headers)
                    response = client.getresponse()
                    payload = json.loads(response.read(65537))
                    elapsed = (time.monotonic() - began) * 1000
                    valid = response.status == 200 and payload["user"] == {"id": user["id"], "username": user["username"]} \
                        and payload["expires_in"] == 3600
                    if valid:
                        if transport == "desktop":
                            access, refresh = payload["access_token"], payload["refresh_token"]
                        else:
                            cookies = SimpleCookie()
                            for name, value in response.getheaders():
                                if name.lower() == "set-cookie":
                                    cookies.load(value)
                            access, refresh = cookies["oms_ir_access"].value, cookies["oms_ir_refresh"].value
                        user[transport].update(access=access, refresh=refresh)
                        # Rotation already committed; preserve each private new
                        # token before evidence I/O or another request can fail.
                        replace_owned_json(context.data / "credentials.json", credentials)
                    context.evidence.stage(f"{label}-HTTP-{user['id']}-{transport}",
                        {"transport": transport, "status": response.status, "ms": elapsed,
                         "error_code": payload.get("error", {}).get("code"), "retry_after": response.getheader("Retry-After"),
                         "normal_expires_in": payload.get("expires_in"), "credentials_in_report": False})
                    require(valid, "real_refresh_same_owner_and_normal_lifetime")
                finally:
                    client.close()
        with context.p.readonly(context.database) as connection:
            placeholders = ",".join("?" for _ in sessions)
            remaining = connection.execute(f"SELECT MIN(access_expires)-? FROM sessions WHERE id IN ({placeholders})",
                (int(time.time()), *(session for session, _, _ in sessions))).fetchone()[0]
            require(all(tuple(connection.execute("SELECT user_id,transport,revoked FROM sessions WHERE id=?", (session,)).fetchone())
                        == (owner, transport, 0) for session, owner, transport in sessions), "same_session_ownership_after_refresh")
        require(remaining >= 3590, "real_normal_session_lifetime_before_long_phase")
        context.evidence.stage(label, {"requests": len(sessions), "accounts": len(context.users),
            "minimum_access_seconds_remaining": remaining, "session_ownership_preserved": True,
            "expiry_extended_by_SQL": False, "credentials_remain_private": True})


def run(context):
    p = context.p
    context.load_state()
    record_hideable_group(context)
    context.install_services()
    initial = p.Service(context.data, context.database, context.archive, context.port, "initial-session-refresh")
    initial.start()
    try:
        renew_synthetic_sessions(context, initial, label="initial-owned-session-refresh")
    finally:
        initial.stop()
    context.evidence.stage("fresh-source-selections", fresh_source_queries(context))
    service = p.Service(context.data, context.database, context.archive, context.port, "main")
    service.start()
    try:
        context.evidence.stage("first-player", player_checks(context, service, fresh=True, label="first-player"))
        context.evidence.stage("initial-PHP", frontend_checks(context, service, "initial-PHP"))
        context.evidence.stage("real-adapters", adapter_checks(context, service))
        context.evidence.stage("actual-browser-actor", actor_checks(context, service))
        with Observation(context, "original-API", service._budget):
            api = p.api_checks(service, context.metadata, context.users, context.keys, context.fixtures)
            directory = p.directory_stage(service, context.metadata)
            native = p.native_stage(service, context.metadata, context.keys)
            context.evidence.stage("original-API-latency", {"API": api, "directory": directory, "native": native})
            require(directory["p95_gate_passed"] and native["under_10_seconds"]
                    and native["gzip_wire_and_complete_decoded_bodies_verified"], "original_directory_and_full_native_latency")
            with p.readonly(context.database) as connection:
                owners = [user["id"] for user in context.users]
                placeholders = ",".join("?" for _ in owners)
                prior = connection.execute(
                    f"SELECT id,user_id,metric,lamp_value FROM external_bests WHERE source=? AND chart_md5=? "
                    f"AND user_id IN ({placeholders}) AND metric>120 AND lamp_value<8 ORDER BY user_id,id LIMIT 1",
                    ("lr2oraja_ed", context.metadata["chart"]["md5"], *owners)).fetchone()
            require(prior is not None, "existing_owned_state_with_score_above_120_and_lamp_below_8")
            key = p.key_for(context.keys, prior["user_id"], "lr2oraja_ed")
            metric, body = service.client.request("POST", p.V2 + "/external/update", key=key,
                                                  body=p.external_payload(context.metadata["chart"], "lr2oraja_ed", 120, lamp=8))
            context.evidence.stage("independent-lamp-HTTP", {"HTTP": metric, "prior": dict(prior), "synthetic_only": True})
            require(metric["status"] == 200 and body["updated"] is True
                    and body["best_state"]["id"] == prior["id"] and body["best_state"]["ex_score"] == prior["metric"]
                    and body["best_state"]["lamp"]["value"] == 8, "independent_best_score_and_actual_lamp_improvement")
            with p.readonly(context.database) as connection:
                after = connection.execute("SELECT metric,lamp_value FROM external_bests WHERE id=?", (prior["id"],)).fetchone()
            require(after["metric"] == prior["metric"] and after["lamp_value"] == 8, "persisted_independent_lamp_improvement")
            lamp_result = {"prior": dict(prior), "after": dict(after), "updated": True, "synthetic_only": True}
        context.evidence.stage("original-API", {"API": api, "directory": directory, "native": native,
                                                "independent_best_lamp_checked": True, "independent_lamp": lamp_result})
        context.evidence.stage("full-max-board", full_pagination(context, service, "full-max-board"))
        with Observation(context, "burst", service._budget):
            burst = p.traffic_stage(service, context.metadata, context.users, context.keys, 10, 25, phase="burst")
        context.evidence.check(burst["traffic_gate_passed"], "actual_burst_read_write_confirmation")
        context.evidence.stage("burst", burst)
        context.evidence.stage("sustained", sustained(context, service))
        with Observation(context, "direct-trusted-egress", service._budget):
            same = p.same_egress_stage(service, context.users)
        context.evidence.check(same["read_quota_rejection_observed"] and same["queue_drained"], "direct_trusted_proxy_same_egress_queue")
        context.evidence.stage("direct-trusted-egress", same)
        context.evidence.stage("real-peer-quota", quota_probe(context, service))
        context.evidence.data["database_empty_restore_gate"] = False
        context.evidence.data["complete_PHP_empty_restore_gate"] = False
        context.evidence.data["complete_API_source_empty_restore_gate"] = False
        context.evidence.data["recovery_requires_separate_serial_owner_run"] = True
        with Observation(context, "projection-after", service._budget):
            after = p.archive_info(context.archive)
        context.evidence.check(after == context.archive_info, "full_public_projection_unchanged")
    finally:
        service.stop()
    context.close_frontend()
    context.evidence.data["staging_host_gate"] = context.args.seconds >= 1800
    context.evidence.data["run_scope"] = "actual shared host staging; formal live backup and owner driver terminal remain separate"


def run_recovery(context):
    context.load_state()
    require("distinct_hidden_group" in context.metadata, "same_fixture_after_actual_1800_run")
    context.install_services()
    service = context.p.Service(context.data, context.database, context.archive, context.port, "recovery-source")
    service.start()
    try:
        result = recovery(context, service)
        capacity = disk_gate(context, result)
        context.evidence.stage("recovery-capacity", capacity)
        context.evidence.check(capacity["passed"] and capacity["actual_2GiB_margin_throughout_sampled_recovery"],
                               "eight_daily_pairs_raw_restore_and_actual_recovery_disk_margin")
        context.evidence.stage("two-database-restores", {"passed": result["two_actual_empty_directory_HTTP_restores_passed"],
                                                        "rounds": [1, 2], "serial_backend": True,
                                                        "complete_PHP_source_restore_proven": context.args.external_frontend_restores})
        context.evidence.data["database_empty_restore_gate"] = True
        context.evidence.data["complete_PHP_empty_restore_gate"] = context.args.external_frontend_restores
        context.evidence.data["complete_API_source_empty_restore_gate"] = context.args.external_frontend_restores
    finally:
        service.stop()
    context.close_frontend()
    context.evidence.data["staging_host_gate"] = False
    context.evidence.data["run_scope"] = "serial recovery; use the separate completed 1800-second report"


def local_seed(args):
    """Generate the complete synthetic fixture on F before host disk decisions."""
    require(sys.platform.startswith("linux"), "F_backed_Linux_seed_runtime")
    os.umask(0o077)
    web = Path("/mnt/f/zdamexy-workspace/websites/oms-web")
    backend = Path("/mnt/f/zdamexy-workspace/oms-server/oms-backend")
    release, work = direct_path(args.release), direct_path(args.work)
    require(release.is_relative_to(web / "artifacts/production") and work.is_relative_to(web / "artifacts/production")
            and work.is_dir() and not os.path.lexists(work / "data"), "explicit_new_F_task_seed_directory")
    manifest = read_json(release / "release.json")
    files = runtime_files(release, manifest)
    require(manifest["format"] == 3 and manifest["runtime_kind"] == "native-osu-web-1"
            and manifest["database_schema_version"] == 3, "actual_local_candidate_manifest")
    for name, checksum in files.items():
        if name.startswith("backend/"):
            path = backend / name.removeprefix("backend/")
            require(path.is_file() and not path.is_symlink() and file_hash(path) == checksum, "local_seed_exact_backend_source")
    public = Path("/mnt/f/oms/artifacts/oms-ir-multisource-20261004/archive/lr2ir-public-v1.db")
    require(release.joinpath("archive.db").resolve() == public, "only_fixed_F_public_projection")
    sys.path.insert(0, str(backend))
    p = importlib.import_module("scripts.multisource_probe")
    require(Path(p.__file__).resolve() == backend / "scripts/multisource_probe.py", "local_candidate_seed_module")
    info = p.archive_info(public)
    approved = manifest["public_archive"]
    require(info == {"projection_version": approved["projection_version"], "rows": approved["total_summary_rows"],
                     "bytes": approved["bytes"], "sha256": approved["sha256"]}, "local_full_public_projection_binding")
    temporary = work / "tmp"
    temporary.mkdir(mode=0o700, exist_ok=False)
    os.environ["TMPDIR"] = str(temporary)
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    evidence = Evidence(work, "seed-only", {"release": str(release), "work": str(work), "public_archive": info,
                                          "verification_harness_sha256": file_hash(Path(__file__).resolve()),
                                          "shared_host_gate": False, "synthetic_only": True, "state_must_not_enter_Git": True})
    context = SimpleNamespace(p=p, release=release, backend=backend, work=work, data=work / "data",
                              database=work / "data/live.db", archive=release / "archive.db", archive_info=info,
                              evidence=evidence, local_seed=True)
    context.owned_file = MethodType(Context.owned_file, context)
    context.load_state = MethodType(Context.load_state, context)
    try:
        seed(context)
        compressed = work / "seed.db.gz"
        record = p.create_compressed_backup(context.database, compressed, release / "release.json")
        evidence.stage("actual-consistent-snapshot-size", {"snapshot": record["snapshot"], "gzip": record["gzip"],
            "sidecar_bytes": compressed.with_name(compressed.name + ".json").stat().st_size,
            "primary_raw_plus_one_restore_raw_plus_one_gzip_plus_2GiB_bytes": 2 * record["snapshot"]["bytes"] + record["gzip"]["bytes"] + 2 * GIB,
            "packages_runtime_and_retained_host_data_must_be_added_by_owner": True,
            "shared_host_capacity_not_measured": True})
        evidence.data["status"] = "completed"
    except (GateFailure, OSError, ValueError, RuntimeError, KeyError, sqlite3.Error) as error:
        evidence.data["status"] = "failed"
        evidence.data["failures"].append({"type": type(error).__name__, "label": str(error) if isinstance(error, GateFailure) else "local_seed_failed"})
        raise
    finally:
        evidence.data["finished_at"] = now()
        evidence.save()
        print(canonical({"status": evidence.data["status"], "report": str(evidence.path), "shared_host_gate": False}))


def maintenance_worker(args):
    """No Context: this worker has the smaller real 128 MiB maintenance budget."""
    require(sys.platform.startswith("linux") and os.geteuid() == 0, "root_linux_maintenance")
    os.umask(0o077)
    release, work = direct_path(args.release), direct_path(args.work)
    marker = read_json(work / "ownership.json")
    manifest = read_json(release / "release.json")
    require(marker["format"] == OWNERSHIP and marker["synthetic_only"] is True and marker["release"] == str(release)
            and marker["work"] == str(work) and marker["manifest_sha256"] == file_hash(release / "release.json")
            and work.parent == Path("/opt/oms-web/acceptance") / manifest["release_id"]
            and release == Path("/opt/oms-ir/releases") / manifest["release_id"], "only_registered_owned_maintenance_round")
    paths = [direct_path(path) for path in (args.source, args.destination, args.worker_report, args.ready, args.go, args.last_live, args.close)]
    require(all(path.is_relative_to(work) and path != work for path in paths)
            and paths[0].is_file() and not paths[0].is_symlink()
            and not any(os.path.lexists(path) for path in paths[1:]), "new_owned_maintenance_paths")
    source, destination, report, ready, go, final, close = paths
    require(args.unit.startswith("oms-web-maint-") and cgroup_path(os.getpid()).name == args.unit,
            "actual_owned_worker_unit")
    budget = BudgetUnit(args.unit, os.getpid(), 128, 0.5)
    sys.path.insert(0, str(release / "backend"))
    module = importlib.import_module("oms_ir.backup")
    require(Path(module.__file__).resolve() == release / "backend/oms_ir/backup.py", "candidate_maintenance_implementation")
    if args.operation == "backup":
        require(source == work / "data/live.db", "backup_only_owned_live_fixture")
        metadata = read_json(work / "data/seed.json")
        require(metadata.get("synthetic_multisource_probe") is True and metadata.get("distinct_additions_per_ruleset") == {"bms": 100000, "mania": 100000},
                "backup_only_complete_synthetic_fixture")
        with sqlite3.connect(source.as_uri() + "?mode=ro", uri=True) as connection:
            require(connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 30001
                    and connection.execute("SELECT COUNT(*) FROM users WHERE username_key NOT GLOB 'irms_[0-9][0-9][0-9][0-9][0-9]'").fetchone()[0] == 0,
                    "maintenance_has_no_real_accounts")
    else:
        require(source.parent == work and source.name in ("snapshot-round-1.db.gz.json", "snapshot-round-2.db.gz.json")
                and destination.parent.parent == work and destination.parent.name in ("empty-restore-1", "empty-restore-2")
                and destination.name == "live.db", "restore_only_owned_snapshot_to_empty_destination")
    new_json(ready, {"unit": args.unit, "pid": os.getpid(), "identity": budget.identity})
    deadline = time.monotonic() + 60
    while not go.is_file() and time.monotonic() < deadline:
        time.sleep(0.05)
    require(read_json(go) == {"unit": args.unit, "pid": os.getpid()}, "owner_observer_ready_before_maintenance")
    began = time.monotonic()
    result = {"status": "failed", "operation": args.operation}
    try:
        if args.operation == "backup":
            result["backup"] = module.create_compressed_backup(source, destination, release / "release.json")
        else:
            result["backup"] = module.restore_backup(source, destination, release / "release.json")
        result["status"] = "completed"
    finally:
        result["elapsed_ms"] = (time.monotonic() - began) * 1000
        new_json(report, result)
        deadline = time.monotonic() + 60
        while not close.is_file() and time.monotonic() < deadline:
            time.sleep(0.05)
        require(read_json(close) == {"unit": args.unit, "pid": os.getpid()}, "owner_final_sample_before_worker_exit")
        new_json(final, budget.frame())


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--base", default="http://127.0.0.1:18090")
    parser.add_argument("--seconds", type=int, default=1800)
    parser.add_argument("--phase", choices=("all", "seed", "seed-only", "run", "recovery", "maintenance"), default="run")
    parser.add_argument("--accept-transferred-seed", action="store_true")
    parser.add_argument("--external-frontend-restores", action="store_true")
    parser.add_argument("--serial-export", action="store_true")
    parser.add_argument("--operation", choices=("backup", "restore"))
    for name in ("source", "destination", "worker-report", "ready", "go", "last-live", "close"):
        parser.add_argument("--" + name, type=Path)
    parser.add_argument("--unit")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.phase == "seed-only":
        local_seed(args)
        return
    if args.phase == "maintenance":
        require(args.operation is not None and all(getattr(args, name) is not None for name in
                ("source", "destination", "worker_report", "ready", "go", "last_live", "close", "unit")), "explicit_worker_arguments")
        maintenance_worker(args)
        return
    context = None
    try:
        context = Context.__new__(Context)
        context.__init__(args)
        if args.phase in ("all", "seed"):
            seed(context)
        if args.phase in ("all", "run"):
            run(context)
        if args.phase == "recovery":
            run_recovery(context)
        context.evidence.data["status"] = "completed"
    except (GateFailure, OSError, subprocess.SubprocessError, ValueError, RuntimeError, KeyError, sqlite3.Error) as error:
        if context is not None and hasattr(context, "evidence"):
            context.evidence.data["status"] = "failed"
            context.evidence.data["staging_host_gate"] = False
            context.evidence.data["failures"].append({"type": type(error).__name__,
                "label": str(error) if isinstance(error, GateFailure) else "see_retained_owned_stage_log"})
            context.evidence.save()
        raise
    finally:
        if context is not None and hasattr(context, "evidence"):
            if sys.exc_info()[0] is not None and context.evidence.data["status"] != "failed":
                context.evidence.data["status"] = "failed"
                context.evidence.data["staging_host_gate"] = False
                context.evidence.data["failures"].append({"type": sys.exc_info()[0].__name__,
                                                          "label": "unhandled_programmer_or_runtime_error"})
            context.evidence.data["finished_at"] = now()
            if hasattr(context, "driver"):
                if getattr(context, "active_service", None) is not None:
                    context.active_service.stop()
                context.evidence.data["actual_driver_before_exit"] = {"properties": properties(context.driver.unit),
                                                                     "last_live": context.driver.frame(),
                                                                     "loaded_terminal_not_yet_observable": True}
            context.evidence.save()
            print(canonical({"status": context.evidence.data["status"], "report": str(context.evidence.path),
                             "staging_host_gate": context.evidence.data.get("staging_host_gate", False),
                             "owner_driver_terminal_and_formal_live_backup_evidence_required": True}))


if __name__ == "__main__":
    main()
