"""Shared machinery for this task's verifier.

Paths, fixture loading, the unprivileged runner and the crafted-world
helpers live here so test_outputs.py carries assertions and nothing else.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

APP = Path("/app")
DATA = APP / "data"
WORKFLOW_PATH = APP / "workflow" / "link_parties.go"
ORIGINAL_WORKFLOW_PATH = APP / "workflow" / ".link_parties.original.go"
EXTRACT_PATH = DATA / "party_snapshot_pre_migration.json"
JOURNAL_PATH = DATA / "party_change_journal.json"
MASTER_PATH = DATA / "party_records.json"
SPEC_PATH = APP / "docs" / "match_contract.json"
# The contract is golden metadata: the verifier reads it from its own image,
# never from the agent-writable copy under /app.
GOLDEN_CONTRACT_PATH = Path("/tests/fixtures/contract_golden.json")
LOG_PATH = APP / "incident" / "stewardship_governance_log.md"
EXPECTED_FIXTURE = Path("/tests/fixtures/expected_report.json")
ALT_INPUT = Path("/tests/fixtures/alt_master.json")

FIXTURE = json.loads(EXPECTED_FIXTURE.read_text())
SPEC = json.loads(GOLDEN_CONTRACT_PATH.read_text())

RECORD_KEYS = set(SPEC["reconciled_inputs"]["party_records"]["record_fields"])
SUMMARY_KEYS = set(SPEC["outputs"]["summary"]["required_fields"])
GOLDEN_KEYS = set(SPEC["outputs"]["golden_records"]["element_fields"])
REVIEW_KEYS = set(SPEC["outputs"]["review_queue"]["element_fields"])
REVIEW_REASONS = set(SPEC["outputs"]["review_queue"]["reasons"])

# Budget published by the contract and stated in instruction.md. Held as a literal
# so it cannot be relaxed by editing the environment, and cross-checked below.
RUNTIME_BUDGET_SEC = 90.0
# The published budget IS the hard timeout: a run that exceeds it is killed and
# the suite fails deterministically, with no wall-clock comparison to go flaky.
HARD_TIMEOUT_SEC = int(RUNTIME_BUDGET_SEC)
_ELAPSED: dict[str, float] = {}

CANDIDATE_UID = 65534
_CWORK = Path("/candidate-work")
_SETPRIV = ["setpriv", f"--reuid={CANDIDATE_UID}", f"--regid={CANDIDATE_UID}",
            "--clear-groups", "--no-new-privs"]
CHILD_ENV = {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": "/candidate-work",
             "LANG": "C.UTF-8", "GOCACHE": "/candidate-work/gocache",
             "GO111MODULE": "off", "GOPATH": "/candidate-work/gopath"}
_BIN_CACHE: dict[str, str] = {}
_run_ctr = iter(range(1, 10_000))


def _digest(value) -> str:
    """Content digest of a decoded artifact, insensitive to free whitespace."""
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_jsonl(path):
    return [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]


def _write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build(script_path: Path) -> str:
    """Compile the submitted single-file planner, cached per source path.

    Compilation runs as root: it is the trusted verifier's own action. The source
    is copied to a temp dir as main.go first so the frozen snapshot and any
    sibling files in /app/workflow never join the build.
    """
    key = str(script_path)
    if key in _BIN_CACHE:
        return _BIN_CACHE[key]
    build_dir = tempfile.mkdtemp(prefix="gobuild_")
    os.chmod(build_dir, 0o755)
    src = Path(build_dir) / "main.go"
    shutil.copyfile(script_path, src)
    binary = Path(build_dir) / "linker"
    result = subprocess.run(
        ["go", "build", "-o", str(binary), str(src)],
        capture_output=True, text=True,
        env={**os.environ, "GOCACHE": "/tmp/gocache", "GO111MODULE": "off", "GOPATH": "/tmp/gopath"},
    )
    assert result.returncode == 0, f"go build failed:\n{result.stderr}"
    os.chmod(binary, 0o755)
    _BIN_CACHE[key] = str(binary)
    return str(binary)


def _candidate_dir() -> Path:
    d = _CWORK / f"run-{next(_run_ctr)}"
    d.mkdir(parents=True, exist_ok=True)
    os.chmod(d, 0o777)
    return d


def _publish_inputs() -> None:
    """Open read access on the agent-produced inputs before privileges drop.

    Never follows a link out of the agent-owned tree: os.chmod resolves symlinks,
    so a link planted at /app/... -> /tests would otherwise open the sealed
    fixtures to the unprivileged candidate.
    """
    app_root = APP.resolve()
    for path in sorted(APP.rglob("*")):
        if path.is_symlink():
            continue
        try:
            if not path.resolve().is_relative_to(app_root):
                continue
        except OSError:
            continue
        try:
            os.chmod(path, 0o755 if path.is_dir() else 0o644)
        except OSError:
            pass


def _run_agent(argv, cwd: Path):
    return subprocess.run(_SETPRIV + argv, cwd=str(cwd), capture_output=True, text=True,
                          env=dict(CHILD_ENV), timeout=HARD_TIMEOUT_SEC)


def _run_pipeline(script_path: Path = WORKFLOW_PATH, input_path: Path = MASTER_PATH):
    """Build and run the submitted planner as an unprivileged subprocess."""
    binary = _build(script_path)
    _publish_inputs()
    work = _candidate_dir()
    out_dir = work / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(out_dir, 0o777)
    staged = work / "master.json"
    shutil.copyfile(str(input_path), str(staged))
    os.chmod(staged, 0o644)
    started = time.monotonic()
    result = _run_agent([binary, "--input", str(staged), "--output-dir", str(out_dir)], cwd=work)
    _ELAPSED[str(input_path)] = time.monotonic() - started
    assert result.returncode == 0, f"linker failed:\n{result.stdout}\n{result.stderr}"
    return (out_dir,
            _load_json(out_dir / "summary.json"),
            _load_json(out_dir / "golden_records.json"),
            _load_jsonl(out_dir / "review_queue.jsonl"))


__all__ = [
    "GOLDEN_CONTRACT_PATH",
    "annotations",
    "hashlib",
    "json",
    "os",
    "re",
    "shutil",
    "subprocess",
    "sys",
    "tempfile",
    "time",
    "Path",
    "pytest",
    "APP",
    "DATA",
    "WORKFLOW_PATH",
    "ORIGINAL_WORKFLOW_PATH",
    "EXTRACT_PATH",
    "JOURNAL_PATH",
    "MASTER_PATH",
    "SPEC_PATH",
    "LOG_PATH",
    "EXPECTED_FIXTURE",
    "ALT_INPUT",
    "FIXTURE",
    "SPEC",
    "RECORD_KEYS",
    "SUMMARY_KEYS",
    "GOLDEN_KEYS",
    "REVIEW_KEYS",
    "REVIEW_REASONS",
    "RUNTIME_BUDGET_SEC",
    "HARD_TIMEOUT_SEC",
    "_ELAPSED",
    "CANDIDATE_UID",
    "_CWORK",
    "_SETPRIV",
    "CHILD_ENV",
    "_BIN_CACHE",
    "_run_ctr",
    "_digest",
    "_load_json",
    "_load_jsonl",
    "_write_json",
    "_build",
    "_candidate_dir",
    "_publish_inputs",
    "_run_agent",
    "_run_pipeline",
]
