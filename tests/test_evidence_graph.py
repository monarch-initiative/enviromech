"""Evidence records are linked to their observations and KER, and drawn as a pairing."""

from enviromech import render
from enviromech.paths import PAGES_DIR

PAGES = render.build()


def page(stem):
    return PAGES[PAGES_DIR / "records" / f"{stem}.html"]


def test_evidence_page_links_its_observations_and_ker_and_draws_the_pairing():
    ev = page("nrf2-srxn1-coupling")
    assert "nrf2_activation_by_soft_electrophiles_in_hepg2.html" in ev
    assert "srxn1_induction_by_soft_electrophiles_in_hepg2.html" in ev
    assert "KER-nrf2-srxn1.html" in ev
    assert "Evidence pairing" in ev


def test_the_ker_and_each_observation_link_back_to_the_evidence():
    assert "nrf2-srxn1-coupling.html" in page("KER-nrf2-srxn1")
    assert "nrf2-srxn1-coupling.html" in page("nrf2_activation_by_soft_electrophiles_in_hepg2")
    assert "nrf2-srxn1-coupling.html" in page("srxn1_induction_by_soft_electrophiles_in_hepg2")
