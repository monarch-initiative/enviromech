"""The committed NRF2->SRXN1 model run: a transcribed inputs.json, a derived
simulation.json that the generator reproduces deterministically, and the
observed-vs-simulated figure the record browser draws from them."""

import importlib.util
import json

from enviromech import render
from enviromech.paths import PAGES_DIR, REPO_ROOT

RUN = REPO_ROOT / "data/model_runs/nrf2_srxn1_sulforaphane_continuous"

spec = importlib.util.spec_from_file_location(
    "simulate_nrf2_srxn1", REPO_ROOT / "scripts/simulate_nrf2_srxn1.py")
sim = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sim)


def test_inputs_carry_transcription_provenance():
    inp = json.loads((RUN / "inputs.json").read_text())
    prov = inp["provenance"]
    assert prov["doi"] == "10.5281/zenodo.17181465"
    assert prov["publication"] == "PMID:40972999"
    # every source file is pinned by sha256
    assert prov["source_files"]
    for f in prov["source_files"]:
        assert len(f["sha256"]) == 64 and f["path"]
    assert len(inp["concentrations_uM"]) == 6


def test_committed_simulation_is_the_generator_output():
    """simulation.json must equal a fresh run of the generator, byte for byte —
    so it is never hand-edited and always matches inputs.json."""
    committed = (RUN / "simulation.json").read_text()
    regenerated = json.dumps(sim.build(RUN), indent=2) + "\n"
    assert committed == regenerated, "run `just simulate-nrf2-srxn1` and commit"


def test_simulation_reproduces_the_paper_fit():
    doc = json.loads((RUN / "simulation.json").read_text())
    assert doc["derived"] is True
    assert doc["fit"]["pooled_r2"] >= 0.95  # paper reports > 0.9
    assert doc["fit"]["n_points"] == 294     # 6 concentrations x 49 hours
    # the derived output records which parameter set it ran (the deposit's)
    assert doc["model"]["parameters"]["buildSrxn1Base"] == 0.02262


def test_fraction_starts_at_the_initial_fraction():
    doc = json.loads((RUN / "simulation.json").read_text())
    f0 = doc["series"]["16.25"]["fraction_modified_nrf2"][0]
    assert abs(f0 - 0.001) < 1e-6  # f(0) == f_i


def test_the_record_draws_observed_vs_simulated():
    pages = render.build()
    ker = pages[PAGES_DIR / "records" / "KER-nrf2-srxn1.html"]
    assert "Observed vs simulated SRXN1" in ker
    assert "pooled R" in ker and "0.9823" in ker
    assert "resp-band" in ker                       # the min/max envelope
    assert ker.count("resp-obs") >= 6               # observed points + legend
    assert "integrated from Eq I with" in ker       # the honest derived-sim note


def test_run_loads_and_degrades_gracefully():
    # obs_sim_svg returns None when no run is declared, and a 3-tuple when it is
    assert render.obs_sim_svg({"response_variable": "x"}) is None
    assert render.obs_sim_svg({"simulation_run": "data/model_runs/does_not_exist"}) is None
    rr = {"simulation_run": "data/model_runs/nrf2_srxn1_sulforaphane_continuous"}
    out = render.obs_sim_svg(rr)
    assert out is not None and len(out) == 3
    svg, conc, r2 = out
    assert "<svg" in svg and float(conc) == 16.25 and r2 == 0.9823
