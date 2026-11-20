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


def test_the_committed_record_shows_faithful_model_figures_not_a_dose_response():
    pages = render.build()
    ker = pages[PAGES_DIR / "records" / "KER-nrf2-srxn1.html"]
    # The NRF2->SRXN1 model is a semi-mechanistic ODE, not a dose-response. Its
    # parameters are transcribed from Table S3, so the page shows the faithful
    # model figures (f(t) and the Hill arms) and the parameter table, never a
    # pending flag, and never an EC50 dose-response axis.
    assert "Response curve pending" not in ker
    assert "EC50" not in ker
    assert "130492" in ker  # a transcribed value (Vmax) renders
    # The two faithful figures, and the note that SRXN1(t) is deliberately not drawn.
    assert ker.count('class="resp-fig"') == 2
    assert "Dynamic modified-NRF2 fraction" in ker
    assert "Production arms" in ker
    assert "SRXN1(t) itself is not drawn" in ker
