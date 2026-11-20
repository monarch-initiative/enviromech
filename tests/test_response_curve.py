"""A response relationship draws a curve only when its parameters are transcribed."""

from enviromech import render
from enviromech.paths import PAGES_DIR


def rr(ec50=None, emax=None, hill=None):
    params = [{"name": "EC50", "value": ec50, "unit": "uM"},
              {"name": "Emax", "value": emax, "unit": "fold-over-control"}]
    if hill is not None:
        params.append({"name": "Hill", "value": hill})
    return {"response_variable": "SRXN1 protein", "model_type": "HILL", "parameters": params}


def test_curve_is_drawn_when_ec50_and_emax_are_numbers():
    svg = render.response_curve_svg(rr(ec50=5.0, emax=10.0, hill=2.0))
    assert svg is not None
    assert "resp-curve" in svg and "<path" in svg and "EC50 5" in svg


def test_no_curve_without_transcribed_values():
    assert render.response_curve_svg(rr(ec50=None, emax=None)) is None
    assert render.response_curve_svg(rr(ec50=5.0, emax=None)) is None


def test_the_committed_record_shows_its_parameters_without_a_fake_curve():
    pages = render.build()
    ker = pages[PAGES_DIR / "records" / "KER-nrf2-srxn1.html"]
    # The NRF2->SRXN1 model is an ODE, not a dose-response, and its parameters are
    # transcribed from Table S3: show the parameter table, never a fabricated curve,
    # and do not claim a curve is pending once the parameters are in.
    assert "resp-curve" not in ker
    assert "Response curve pending" not in ker
    assert "130492" in ker  # a transcribed value (Vmax) renders
