"""Running dismech's AOP crosswalk for an AOP record, by scripts/crosswalk.py.

The dismech script itself is not run here: CI has no dismech checkout. These tests
check what this repository adds around it, with the dismech run replaced.
"""

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("crosswalk", REPO_ROOT / "scripts/crosswalk.py")
crosswalk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crosswalk)


def test_snapshot_date_is_the_record_date_as_mm_dd_yyyy():
    assert crosswalk.snapshot_date(REPO_ROOT / "data/aops/AOP-40.yaml") == "10-03-2026"


def test_command_runs_the_dismech_script_in_its_own_environment(tmp_path):
    found = crosswalk.command(
        tmp_path, Path("/data"), "10-03-2026", "40", ["Contact_Dermatitis", "Asthma"], None, "json"
    )
    assert found[:5] == ["uv", "run", "--project", str(tmp_path), "python"]
    assert found[5] == str(tmp_path / "scripts/aop_dismech_crosswalk.py")
    assert found[found.index("--date") + 1] == "10-03-2026"
    assert found[found.index("--aop") + 1] == "40"
    assert [found[i + 1] for i, a in enumerate(found) if a == "--entry"] == ["Contact_Dermatitis", "Asthma"]
    assert "--rules" not in found
    assert found[-2:] == ["--format", "json"]


def test_a_checkout_without_the_script_is_refused(tmp_path):
    with pytest.raises(SystemExit, match="dismech#16232"):
        crosswalk.dismech_commit(tmp_path)


def dismech_checkout(root: Path) -> None:
    (root / "scripts").mkdir(parents=True)
    (root / "scripts/aop_dismech_crosswalk.py").write_text("")
    (root / "kb").mkdir()
    (root / "kb/Entry.yaml").write_text("name: Entry\n")
    git = ["git", "-C", str(root)]
    subprocess.run([*git, "init", "-q"], check=True)
    subprocess.run([*git, "add", "."], check=True)
    subprocess.run(
        [*git, "-c", "user.name=t", "-c", "user.email=t@example.org", "commit", "-q", "-m", "x"],
        check=True,
    )


def test_a_checkout_with_uncommitted_kb_changes_is_refused(tmp_path):
    dismech_checkout(tmp_path)
    assert len(crosswalk.dismech_commit(tmp_path)) == 40
    (tmp_path / "kb/Entry.yaml").write_text("name: Changed\n")
    with pytest.raises(SystemExit, match="uncommitted changes under kb/"):
        crosswalk.dismech_commit(tmp_path)


def test_main_writes_the_output_with_the_run_recorded(tmp_path, monkeypatch, capsys):
    aops = tmp_path / "aops"
    aops.mkdir()
    (aops / "AOP-40.yaml").write_text(yaml.safe_dump({"id": "aop:40", "aop_wiki_snapshot": "2026-10-03"}))
    monkeypatch.setenv("DISMECH_ROOT", str(tmp_path / "dismech"))
    monkeypatch.setattr(crosswalk, "dismech_commit", lambda root: "a" * 40)
    calls = []

    def fake_run(found, root):
        calls.append(found)
        return json.dumps({"entries": []}) if found[-1] == "json" else "summary text\n"

    monkeypatch.setattr(crosswalk, "run", fake_run)
    out = tmp_path / "out"
    assert crosswalk.main(["40", "Contact_Dermatitis", "--aops", str(aops), "--output", str(out)]) == 0

    written = json.loads((out / "AOP-40.json").read_text())
    assert written["run"]["dismech_commit"] == "a" * 40
    assert written["run"]["aop_wiki_snapshot"] == "10-03-2026"
    assert written["run"]["command"] == calls[0]
    expected = f"dismech {'a' * 11} at {tmp_path / 'dismech'}\n\nsummary text\n"
    assert (out / "AOP-40.txt").read_text() == expected
    assert "Wrote" in capsys.readouterr().out


def test_main_refuses_an_aop_with_no_record(tmp_path):
    with pytest.raises(SystemExit, match="no AOP record"):
        crosswalk.main(["999", "Contact_Dermatitis", "--aops", str(tmp_path)])
