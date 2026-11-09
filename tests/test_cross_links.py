"""Cross-linking records by AOP-Wiki id: a reference that names no Key Event
must match no record, not a record that has no id of its own (issue #56)."""

from enviromech import render

# A Key Event file with no event.id. EMOD makes the id an identifier, so this
# cannot validate, but the browser renders the working tree, where a
# half-written record has none yet.
UNNUMBERED = {"stem": "KE-unnumbered", "data": {"kind": "Key Event", "name": "No id", "event": {}}}


def test_a_key_event_with_no_id_is_left_out_of_the_map():
    numbered = {"stem": "KE-9", "data": {"kind": "Key Event", "name": "A start", "event": {"id": 9}}}
    by_event_id = render.key_events_by_event_id([UNNUMBERED, numbered])
    assert list(by_event_id) == [9]
    assert None not in by_event_id


def test_an_observation_naming_no_key_event_links_to_nothing():
    records = [
        dict(UNNUMBERED),
        {"stem": "obs-1", "data": {"kind": "Observation", "name": "An observation",
                                   "observation": {"events": [None]}}},
    ]
    render.cross_link(records)
    assert "observations" not in records[0]["data"]
    assert records[1]["data"]["observation"]["events"] == [None]


def test_an_aop_member_naming_no_key_event_links_to_nothing():
    """EMOD leaves event_id optional, so an AOP that validates can hold one."""
    records = [
        dict(UNNUMBERED),
        {"stem": "AOP-1", "data": {"kind": "AOP", "name": "A pathway",
                                   "aop": {"events": [{"type": "KeyEvent"}]}}},
    ]
    render.cross_link_aops(records)
    assert "aops" not in records[0]["data"]
    assert records[1]["data"]["aop"]["events"] == [{"type": "KeyEvent"}]
