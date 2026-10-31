"""Run dismech's AOP crosswalk for one EnviroMech AOP record, and keep its output.

    python scripts/crosswalk.py AOP_ID ENTRY [ENTRY ...] [--rules FILE] [--output DIRECTORY]

The crosswalk itself is dismech's: scripts/aop_dismech_crosswalk.py in a dismech
checkout, run in that checkout's own environment. It reports which pathophysiology
nodes and phenotypes of each dismech ENTRY match each Key Event of the AOP, on what
basis, and whether the levels agree. Its matches are candidates for a Key Event
record's aggregation, not mappings. This script only runs it the same way every time:

- against the snapshot the AOP record was read from: the record's
  aop_wiki_snapshot (YYYY-MM-DD) is passed as the MM-DD-YYYY the script takes;
- against the dismech checkout at $DISMECH_ROOT (default ~/Developer/dismech) and
  the aop-wiki-cli data directory at $AOP_WIKI_CLI_DATA_DIR (default
  ~/Developer/aop_wiki_cli);
- refusing a dismech checkout with uncommitted changes under kb/, so that the
  commit recorded is the content the crosswalk read.

It writes, under OUTPUT (default build/crosswalk), AOP-<id>.json, the script's JSON
output with a "run" block naming the dismech commit, the snapshot and the command,
and AOP-<id>.txt, its summary. build/ is not committed.

Not part of just qc: it needs a dismech checkout and an aop-wiki-cli data directory,
which CI does not have.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

SCRIPT = Path("scripts/aop_dismech_crosswalk.py")
DEFAULT_DISMECH = Path("~/Developer/dismech")
DEFAULT_DATA_DIR = Path("~/Developer/aop_wiki_cli")


def snapshot_date(aop_record: Path) -> str:
    """The record's aop_wiki_snapshot, as the MM-DD-YYYY aop-wiki-cli takes."""
    record = yaml.safe_load(aop_record.read_text()) or {}
    value = record.get("aop_wiki_snapshot")
    if not value:
        raise SystemExit(f"{aop_record} has no aop_wiki_snapshot")
    year, month, day = str(value).split("-")
    return f"{month}-{day}-{year}"


def location(variable: str, default: Path) -> Path:
    return Path(os.environ.get(variable) or default).expanduser()


def dismech_commit(root: Path) -> str:
    """The checkout's commit, refusing one with uncommitted changes under kb/."""
    if not (root / SCRIPT).exists():
        raise SystemExit(
            f"{root / SCRIPT} does not exist. Set DISMECH_ROOT to a dismech checkout that has "
            "it (added by monarch-initiative/dismech#16232)."
        )
    dirty = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--", "kb"],
        capture_output=True, text=True, check=True,
    ).stdout
    if dirty.strip():
        raise SystemExit(f"{root} has uncommitted changes under kb/; commit or stash them first")
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()


def command(root: Path, data_dir: Path, date: str, aop_id: str, entries: list[str],
            rules: Path | None, output_format: str) -> list[str]:
    """The command that runs the dismech script in the dismech checkout's environment."""
    found = [
        "uv", "run", "--project", str(root), "python", str(root / SCRIPT),
        "--root", str(root), "--data-dir", str(data_dir), "--date", date, "--aop", aop_id,
    ]
    for entry in entries:
        found += ["--entry", entry]
    if rules:
        found += ["--rules", str(rules)]
    return found + ["--format", output_format]


def run(found: list[str], root: Path) -> str:
    # The dismech environment, not this one: uv warns when VIRTUAL_ENV names another.
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    env["DISMECH_ROOT"] = str(root)
    done = subprocess.run(found, capture_output=True, text=True, env=env)
    if done.returncode:
        sys.stderr.write(done.stderr)
        raise SystemExit(f"the dismech crosswalk failed (exit {done.returncode})")
    return done.stdout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("aop_id", help="the AOP's number, as in data/aops/AOP-<id>.yaml")
    parser.add_argument("entries", nargs="+", help="dismech entry slugs, e.g. Contact_Dermatitis")
    parser.add_argument("--rules", type=Path, help="hand-written matching rules, passed through")
    parser.add_argument("--output", type=Path, default=Path("build/crosswalk"))
    parser.add_argument("--aops", type=Path, default=Path("data/aops"))
    args = parser.parse_args(argv)

    aop_record = args.aops / f"AOP-{args.aop_id}.yaml"
    if not aop_record.exists():
        raise SystemExit(f"no AOP record {aop_record}")
    date = snapshot_date(aop_record)
    root = location("DISMECH_ROOT", DEFAULT_DISMECH)
    data_dir = location("AOP_WIKI_CLI_DATA_DIR", DEFAULT_DATA_DIR)
    commit = dismech_commit(root)

    as_json = command(root, data_dir, date, args.aop_id, args.entries, args.rules, "json")
    result = json.loads(run(as_json, root))
    result["run"] = {
        "dismech_root": str(root),
        "dismech_commit": commit,
        "aop_record": str(aop_record),
        "aop_wiki_snapshot": date,
        "aop_wiki_cli_data_dir": str(data_dir),
        "command": as_json,
        "run_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    summary = run(command(root, data_dir, date, args.aop_id, args.entries, args.rules, "summary"), root)

    args.output.mkdir(parents=True, exist_ok=True)
    stem = args.output / f"AOP-{args.aop_id}"
    stem.with_suffix(".json").write_text(json.dumps(result, indent=1) + "\n")
    stem.with_suffix(".txt").write_text(f"dismech {commit[:11]} at {root}\n\n{summary}")
    print(summary, end="")
    print(f"\nWrote {stem}.json and {stem}.txt (dismech {commit[:11]}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
