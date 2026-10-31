"""AOPs, the third record kind: counted by the report and shown in the browser."""

from enviromech import render, report
from enviromech.paths import AOPS_DIR, KEY_EVENTS_DIR, PAGES_DIR
from enviromech.validate import iter_records, load

AOPS = iter_records(AOPS_DIR)


def test_report_counts_aops():
    stats = report.compute()
    assert stats["aops"] == len(AOPS)
    assert sum(stats["aops_by_status"].values()) == len(AOPS)


def test_browser_has_a_page_for_every_aop():
    pages = render.build()
    index = pages[PAGES_DIR / "index.html"]
    assert f"{len(AOPS)} AOP" in index
    for path in AOPS:
        title = load(path)["aop"]["title"].strip()
        page = pages[PAGES_DIR / "records" / f"{path.stem}.html"]
        assert f"<h1>{title}" in page.replace("&#39;", "'")
        assert f'href="records/{path.stem}.html"' in index


def test_aops_and_key_events_link_to_each_other():
    """An AOP's page links to each Key Event it names, and that Key Event's
    page links back with its role, although only the AOP's file records it."""
    pages = render.build()
    by_event_id = {load(p)["event"]["id"]: p.stem for p in iter_records(KEY_EVENTS_DIR)}
    linked = 0
    for path in AOPS:
        for member in load(path)["aop"]["events"]:
            stem = by_event_id.get(member["event_id"])
            if stem is None:
                continue
            assert f'href="{stem}.html"' in pages[PAGES_DIR / "records" / f"{path.stem}.html"]
            back = pages[PAGES_DIR / "records" / f"{stem}.html"]
            assert f'href="{path.stem}.html"' in back
            assert f"({render.enum_text(member['type'])})" in back
            linked += 1
    assert linked, "no AOP names a Key Event that has a record"


def test_enum_values_read_as_words():
    assert render.enum_text("MolecularInitiatingEvent") == "molecular initiating event"
    assert render.enum_text("NOT_SCREENED") == "not screened"
