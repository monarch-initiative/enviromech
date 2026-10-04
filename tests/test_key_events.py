"""Key Events, the second record kind: counted by the report and shown in the browser.

The tooling mechmaker wrote covers one kind of record, Observations. These
check the two places extended to read data/key_events/ as well.
"""

from enviromech import render, report
from enviromech.paths import KEY_EVENTS_DIR, PAGES_DIR
from enviromech.validate import iter_records, load

KEY_EVENTS = iter_records(KEY_EVENTS_DIR)


def test_report_counts_key_events_apart_from_observations():
    stats = report.compute()
    assert stats["key_events"] == len(KEY_EVENTS)
    assert stats["records"] == len(iter_records())
    assert sum(stats["key_events_by_status"].values()) == len(KEY_EVENTS)
    assert sum(stats["key_events_by_level_screening"].values()) == len(KEY_EVENTS)


def test_browser_has_a_page_for_every_key_event():
    pages = render.build()
    for path in KEY_EVENTS:
        title = load(path)["event"]["title"]
        page = pages[PAGES_DIR / "records" / f"{path.stem}.html"]
        assert f"<h1>{title}</h1>" in page.replace("&#39;", "'")


def test_front_page_lists_both_kinds():
    index = render.build()[PAGES_DIR / "index.html"]
    assert f"{len(KEY_EVENTS)} Key Event" in index
    assert f"{len(iter_records())} Observation" in index
    for path in KEY_EVENTS:
        assert f'href="records/{path.stem}.html"' in index


def test_observations_and_key_events_link_to_each_other():
    """An Observation's page links to each Key Event it names, and that Key
    Event's page links back, although only the Observation's file records it."""
    pages = render.build()
    by_event_id = {load(p)["event"]["id"]: p.stem for p in KEY_EVENTS}
    linked = 0
    for path in iter_records():
        record = load(path)
        for event_id in record["observation"].get("events") or []:
            if event_id not in by_event_id:
                continue
            stem = by_event_id[event_id]
            assert f'href="{stem}.html"' in pages[PAGES_DIR / "records" / f"{path.stem}.html"]
            assert f'href="{path.stem}.html"' in pages[PAGES_DIR / "records" / f"{stem}.html"]
            linked += 1
    assert linked, "no Observation names a Key Event that has a record"
