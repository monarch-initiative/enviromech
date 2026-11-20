"""Faithful model figures: the ODE modified-NRF2 fraction f(t) and the Hill
production arms. Every point is computed from transcribed parameters alone; the
SRXN1 trajectory is deliberately never simulated, because Eq I needs a measured
NRF2 input that is not a transcribed parameter."""

import re

from enviromech import render

# The transcribed sulforaphane / single-exposure parameters (Sharma et al.,
# Table S3), as the committed KER record carries them.
SUL = {
    "response_variable": "SRXN1 protein",
    "model_type": "ODE_SEMIMECHANISTIC",
    "parameters": [
        {"name": "kp", "value": 0.0023, "unit": "1/h"},
        {"name": "kd", "value": 0.016, "unit": "1/h"},
        {"name": "Vmax", "value": 130492, "unit": "au/h"},
        {"name": "Km_modified", "value": 0.014, "unit": "au"},
        {"name": "Km_unmodified", "value": 107110, "unit": "au"},
        {"name": "n_modified", "value": 9.90},
        {"name": "n_unmodified", "value": 1.003},
        {"name": "f_i", "value": 0.001},
        {"name": "r1", "value": 8.90, "unit": "1/h"},
        {"name": "d1", "value": 0.2, "unit": "1/h"},
    ],
}


def _points(svg: str) -> list[tuple[float, float]]:
    """Every (x, y) coordinate in the SVG's path/polyline data."""
    d = " ".join(re.findall(r'd="([^"]+)"', str(svg)))
    return [(float(a), float(b)) for a, b in re.findall(r"(-?\d+\.?\d*),(-?\d+\.?\d*)", d)]


# --- f(t) ------------------------------------------------------------------

def test_fraction_curve_is_a_pulse_rise_then_fall():
    svg = render.ode_fraction_svg(SUL)
    assert svg is not None
    ys = [y for _, y in _points(svg)]
    # In SVG, smaller y is higher f. The curve starts low (y near the baseline),
    # rises to a peak (min y) in the interior, then falls back.
    peak_i = ys.index(min(ys))
    assert 0 < peak_i < len(ys) - 1, "peak should be interior, not at an end"
    assert ys[0] > min(ys) and ys[-1] > min(ys), "both ends below the peak"
    # The transcribed peak is ~0.77 at ~1.2 h; the label states it.
    assert "peak f=0.77" in svg and "1.2 h" in svg


def test_fraction_curve_needs_all_three_parameters():
    # Drop r1: no f(t) can be computed, so no figure.
    without_r1 = {**SUL, "parameters": [p for p in SUL["parameters"] if p["name"] != "r1"]}
    assert render.ode_fraction_svg(without_r1) is None
    # f_i must be a proper fraction.
    bad_fi = {**SUL, "parameters": [
        (p if p["name"] != "f_i" else {**p, "value": 1.5}) for p in SUL["parameters"]]}
    assert render.ode_fraction_svg(bad_fi) is None


# --- Hill arms -------------------------------------------------------------

def test_hill_arms_modified_is_steeper_than_unmodified():
    svg = render.hill_arms_svg(SUL)
    assert svg is not None
    assert svg.count("<path") == 2  # two arms
    assert "modified · n=9.9" in svg and "unmodified · n=1.003" in svg


def test_hill_arms_need_both_coefficients():
    only_mod = {**SUL, "parameters": [p for p in SUL["parameters"] if p["name"] != "n_unmodified"]}
    assert render.hill_arms_svg(only_mod) is None


# --- the honest boundary ---------------------------------------------------

def test_figures_are_general_not_hardcoded_to_nrf2():
    # A different ODE relationship with the same parameter names still draws.
    other = {**SUL, "response_variable": "some other protein",
             "scenario": {"causal_agent": "fictional agonist"}}
    figs = render.model_figures(other)
    assert len(figs) == 3  # f(t), Hill arms, and the note


def test_srxn1_trajectory_is_never_claimed_to_be_simulated():
    figs = "".join(render.model_figures(SUL))
    # The note must state why SRXN1(t) is not drawn, so a reader never mistakes
    # the gating-fraction figure for a simulated SRXN1 time course.
    assert "SRXN1(t) itself is not drawn" in figs
    assert "measured NRF2 input N(t)" in figs


def test_no_figures_for_a_plain_dose_response_record():
    hill = {"response_variable": "x", "model_type": "HILL",
            "parameters": [{"name": "EC50", "value": 5.0}, {"name": "Emax", "value": 10.0}]}
    assert render.model_figures(hill) == []
