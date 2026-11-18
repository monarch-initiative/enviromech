"""Key Event Relationship records agree with the Key Events and AOPs that name them."""

from enviromech.paths import AOPS_DIR, KERS_DIR, KEY_EVENTS_DIR
from enviromech.validate import iter_records, load

KERS = {p: load(p) for p in iter_records(KERS_DIR)}
KEY_EVENT_IDS = {(load(p).get("event") or {}).get("id") for p in iter_records(KEY_EVENTS_DIR)}


def test_a_ker_file_id_matches_its_relationship_id():
    for path, data in KERS.items():
        number = data["ke_relationship"]["id"]
        assert data["id"] == f"aop.relationships:{number}", path
        assert path.stem == f"KER-{number}", path


def test_every_ker_endpoint_has_a_key_event_record():
    for path, data in KERS.items():
        rel = data["ke_relationship"]
        assert rel["upstream_event_id"] in KEY_EVENT_IDS, path
        assert rel["downstream_event_id"] in KEY_EVENT_IDS, path


def test_every_ker_an_aop_names_has_a_record():
    held = {d["ke_relationship"]["id"] for d in KERS.values()}
    for path in iter_records(AOPS_DIR):
        for rel in (load(path).get("aop") or {}).get("ke_relationships") or []:
            assert rel["relationship_id"] in held, (path, rel["relationship_id"])
