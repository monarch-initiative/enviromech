#!/usr/bin/env python3
"""Regenerate the derived NRF2->SRXN1 simulation artifact for the sulforaphane
continuous-exposure model run.

This is a faithful stdlib-only port of the authors' model
(Sharma et al., Generic_model_final.R; PMID:40972999; deposit
doi:10.5281/zenodo.17181465), continuous-exposure branch:

    dSrxn1/dt = kp + Vmax * H(Nu; Km,  n_u) * H(Nm; Km_act, n_m) - kd * Srxn1
    Nu = NRF2(t) * (1 - f(t))      Nm = NRF2(t) * f(t)
    f(t) = 1 / ((1/f_i - 1) * exp(-t*r) + exp(t*decay))     (Eq V, single dose)
    H(x; K, n) = x**n / (K**n + x**n)

NRF2(t) is the *measured* GFP time course (monotone cubic Hermite spline, as the
R code's splinefun "monoH.FC"); SRXN1(t) is integrated (RK4). No number is
originated here: parameters and the NRF2 input are read verbatim from the
committed inputs.json (itself transcribed from the deposit). The SRXN1 curve is
the model's output and is labelled as a simulation wherever it is shown.

Usage:
    python scripts/simulate_nrf2_srxn1.py [RUN_DIR]
    # default RUN_DIR: data/model_runs/nrf2_srxn1_sulforaphane_continuous
Writes RUN_DIR/simulation.json. Deterministic: re-running reproduces it byte for
byte. Run via `just simulate-nrf2-srxn1`.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

DEFAULT_RUN = Path("data/model_runs/nrf2_srxn1_sulforaphane_continuous")
STEP = 0.025         # RK4 step (h); divides RECORD_EVERY exactly
RECORD_EVERY = 0.25  # output grid (h)


def _pchip_slopes(x, y):
    """Fritsch-Carlson monotone tangents (R's splinefun method='monoH.FC')."""
    n = len(x)
    h = [x[i + 1] - x[i] for i in range(n - 1)]
    d = [(y[i + 1] - y[i]) / h[i] for i in range(n - 1)]
    m = [0.0] * n
    for i in range(1, n - 1):
        if d[i - 1] * d[i] <= 0:
            m[i] = 0.0
        else:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    m[0], m[-1] = d[0], d[-1]
    return m


def _pchip(x, y, m, t):
    if t <= x[0]:
        return y[0]
    if t >= x[-1]:
        return y[-1]
    lo, hi = 0, len(x) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if x[mid] <= t:
            lo = mid
        else:
            hi = mid
    h = x[hi] - x[lo]
    s = (t - x[lo]) / h
    h00 = 2 * s**3 - 3 * s**2 + 1
    h10 = s**3 - 2 * s**2 + s
    h01 = -2 * s**3 + 3 * s**2
    h11 = s**3 - s**2
    return h00 * y[lo] + h10 * h * m[lo] + h01 * y[hi] + h11 * h * m[hi]


def _fraction(t, f_i, r, decay):
    return 1.0 / ((1.0 / f_i - 1.0) * math.exp(-t * r) + math.exp(t * decay))


def simulate(times, nrf2_series, p):
    """Integrate SRXN1(t) for one measured NRF2 input. Returns (grid, srxn1, f)."""
    kp, kd = p["buildSrxn1Base"], p["degradSrxn1"]
    vmax, km, hill = p["Vmax_buildSrxn1"], p["Km_Srxn1"], p["hill_Srxn1"]
    f_i = p["initial_fraction"]
    km_act, hill_act = p["Km_NRF2_ACETYLATED_SRXN1"], p["hill_acetylated_SRXN1"]
    r, decay = p["r_Sul"], p["decay_Sul"]
    xt = [float(v) for v in times]
    slopes = _pchip_slopes(xt, [float(v) for v in nrf2_series])

    def deriv(t, s):
        n = _pchip(xt, nrf2_series, slopes, t)
        f = _fraction(t, f_i, r, decay)
        nu, nm = n * (1.0 - f), n * f
        prod = (vmax * nu**hill * nm**hill_act
                / ((km**hill + nu**hill) * (km_act**hill_act + nm**hill_act)))
        return kp + prod - kd * s

    t0, t1 = xt[0], xt[-1]
    nsteps = int(round((t1 - t0) / STEP))
    t, s = t0, 0.0
    grid, srxn1, frac = [t0], [0.0], [_fraction(t0, f_i, r, decay)]
    next_rec = RECORD_EVERY
    for _ in range(nsteps):
        k1 = deriv(t, s)
        k2 = deriv(t + STEP / 2, s + STEP / 2 * k1)
        k3 = deriv(t + STEP / 2, s + STEP / 2 * k2)
        k4 = deriv(t + STEP, s + STEP * k3)
        s += STEP / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        t += STEP
        if t >= next_rec - 1e-9:
            grid.append(round(t, 4))
            srxn1.append(s)
            frac.append(_fraction(t, f_i, r, decay))
            next_rec += RECORD_EVERY
    return grid, srxn1, frac


def _lin_interp(grid, ys, t):
    if t <= grid[0]:
        return ys[0]
    if t >= grid[-1]:
        return ys[-1]
    for i in range(len(grid) - 1):
        if grid[i] <= t <= grid[i + 1]:
            w = (t - grid[i]) / (grid[i + 1] - grid[i])
            return ys[i] * (1 - w) + ys[i + 1] * w
    return ys[-1]


def _r2(obs, pred):
    n = len(obs)
    mo, mp = sum(obs) / n, sum(pred) / n
    cov = sum((o - mo) * (p - mp) for o, p in zip(obs, pred, strict=True))
    so = sum((o - mo) ** 2 for o in obs)
    sp = sum((p - mp) ** 2 for p in pred)
    return (cov * cov) / (so * sp) if so and sp else 0.0


def build(run_dir: Path) -> dict:
    raw = (run_dir / "inputs.json").read_bytes()
    inp = json.loads(raw)
    p = inp["parameters"]
    times = inp["times"]
    out_series, obs_all, pred_all = {}, [], []
    for conc, s in inp["series"].items():
        grid, sim_mean, frac = simulate(times, s["nrf2_mean"], p)
        _, sim_min, _ = simulate(times, s["nrf2_min"], p)
        _, sim_max, _ = simulate(times, s["nrf2_max"], p)
        out_series[conc] = {
            "srxn1_sim_mean": [round(v, 5) for v in sim_mean],
            "srxn1_sim_min": [round(v, 5) for v in sim_min],
            "srxn1_sim_max": [round(v, 5) for v in sim_max],
            "fraction_modified_nrf2": [round(v, 6) for v in frac],
        }
        for ti, obs in zip(times, s["srxn1_mean"], strict=True):
            obs_all.append(obs)
            pred_all.append(_lin_interp(grid, sim_mean, ti))
    # the output time grid is shared across concentrations (same STEP/RECORD_EVERY)
    shared_grid, _, _ = simulate(times, inp["series"][next(iter(inp["series"]))]["nrf2_mean"], p)
    return {
        "schema": "enviromech.model_run.simulation/1",
        "title": "Simulated SRXN1(t) for " + inp["title"],
        "derived": True,
        "generated_by": "scripts/simulate_nrf2_srxn1.py",
        "model": {
            "source": "Sharma et al. Generic_model_final.R (continuous branch)",
            "publication": inp["provenance"]["publication"],
            "doi": inp["provenance"]["doi"],
            "equations": ("dSrxn1/dt = kp + Vmax*H(Nu;Km,n_u)*H(Nm;Km_act,n_m) "
                          "- kd*Srxn1; Nu=NRF2*(1-f), Nm=NRF2*f; "
                          "f(t)=1/((1/f_i-1)*exp(-t*r)+exp(t*decay))"),
            "integrator": f"RK4 dt={STEP} h; monotone cubic Hermite NRF2 input",
            "parameters": p,
        },
        "inputs_sha256": hashlib.sha256(raw).hexdigest(),
        "time_unit": inp["time_unit"],
        "value_unit": inp["value_unit"],
        "concentrations_uM": inp["concentrations_uM"],
        "fit": {
            "pooled_r2": round(_r2(obs_all, pred_all), 4),
            "n_points": len(obs_all),
            "note": ("observed vs simulated (mean NRF2 input) SRXN1 at integer "
                     "hours, pooled across all concentrations"),
        },
        "times": shared_grid,
        "series": out_series,
    }


def main(argv):
    run_dir = Path(argv[1]) if len(argv) > 1 else DEFAULT_RUN
    doc = build(run_dir)
    out = run_dir / "simulation.json"
    out.write_text(json.dumps(doc, indent=2) + "\n")
    print(f"wrote {out}: pooled R2={doc['fit']['pooled_r2']} "
          f"over {doc['fit']['n_points']} points")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
