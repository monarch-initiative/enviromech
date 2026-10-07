"""scripts/aop_evidence.py: structured ratings, nested prose paths, broken chains.

The fixture is a miniature AOP-Wiki export rather than the real 50 MB one, so
these tests pin the shape of the export this script depends on. If AOP-Wiki
renames an element the fixture and the script have to change together, which is
the point: three of the paths here are ones a reader would guess wrongly.
"""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "aop_evidence.py"

# One AOP whose chain holds together (1 -> 2 adjacent, 2 -> 3 non-adjacent) and
# one whose Molecular Initiating Event is attached to nothing, which is the
# shape AOP 51 has in the real export.
FIXTURE = """<?xml version="1.0" encoding="UTF-8"?>
<data xmlns="http://www.aopkb.org/aop-xml">
  <key-event id="ke-a"><title>Antagonism, receptor</title><short-name>AR antag</short-name>
    <biological-organization-level>Molecular</biological-organization-level></key-event>
  <key-event id="ke-b"><title>Decrease, activation</title><short-name>less activation</short-name>
    <biological-organization-level>Tissue</biological-organization-level></key-event>
  <key-event id="ke-c"><title>Outcome, bad</title><short-name>bad</short-name>
    <biological-organization-level>Individual</biological-organization-level></key-event>
  <key-event id="ke-d"><title>Orphan event</title><short-name>orphan</short-name>
    <biological-organization-level>Molecular</biological-organization-level></key-event>
  <key-event-relationship id="ker-1">
    <title><upstream-id>ke-a</upstream-id><downstream-id>ke-b</downstream-id></title>
    <description>&lt;p&gt;It happens.&lt;/p&gt;</description>
    <weight-of-evidence>
      <value></value>
      <biological-plausibility>&lt;p&gt;Plausible.&lt;/p&gt;</biological-plausibility>
      <emperical-support-linkage>&lt;p&gt;Shown.&lt;/p&gt;&lt;table&gt;x&lt;/table&gt;</emperical-support-linkage>
      <uncertainties-or-inconsistencies></uncertainties-or-inconsistencies>
    </weight-of-evidence>
    <quantitative-understanding><description></description>
      <response-response-relationship></response-response-relationship>
      <time-scale></time-scale><feedforward-feedback-loops></feedforward-feedback-loops>
    </quantitative-understanding>
    <known-modulating-factors></known-modulating-factors>
    <evidence-collection-strategy></evidence-collection-strategy>
  </key-event-relationship>
  <key-event-relationship id="ker-2">
    <title><upstream-id>ke-b</upstream-id><downstream-id>ke-c</downstream-id></title>
    <description></description>
    <weight-of-evidence><value></value><biological-plausibility></biological-plausibility>
      <emperical-support-linkage></emperical-support-linkage>
      <uncertainties-or-inconsistencies></uncertainties-or-inconsistencies></weight-of-evidence>
    <quantitative-understanding><description></description>
      <response-response-relationship></response-response-relationship>
      <time-scale></time-scale><feedforward-feedback-loops></feedforward-feedback-loops>
    </quantitative-understanding>
    <known-modulating-factors></known-modulating-factors>
    <evidence-collection-strategy></evidence-collection-strategy>
  </key-event-relationship>
  <aop id="aop-1">
    <title>A pathway that holds together</title><short-name>holds</short-name>
    <status><wiki-license>BY-SA</wiki-license><oecd-status>Under Review</oecd-status></status>
    <molecular-initiating-event key-event-id="ke-a">
      <evidence-supporting-chemical-initiation/></molecular-initiating-event>
    <key-events><key-event id="ke-b"/></key-events>
    <adverse-outcome key-event-id="ke-c"><examples/></adverse-outcome>
    <key-event-relationships>
      <relationship id="ker-1"><adjacency>adjacent</adjacency>
        <quantitative-understanding-value>Moderate</quantitative-understanding-value>
        <evidence>High</evidence></relationship>
      <relationship id="ker-2"><adjacency>non-adjacent</adjacency>
        <quantitative-understanding-value>Not Specified</quantitative-understanding-value>
        <evidence>Low</evidence></relationship>
    </key-event-relationships>
    <overall-assessment>
      <weight-of-evidence-summary>&lt;p&gt;The support is strong.&lt;/p&gt;</weight-of-evidence-summary>
      <key-event-essentiality-summary></key-event-essentiality-summary>
    </overall-assessment>
  </aop>
  <aop id="aop-2">
    <title>A pathway with an orphaned initiating event</title><short-name>orphaned</short-name>
    <status><wiki-license>BY-SA</wiki-license><oecd-status>Under Development</oecd-status></status>
    <molecular-initiating-event key-event-id="ke-d">
      <evidence-supporting-chemical-initiation/></molecular-initiating-event>
    <key-events><key-event id="ke-b"/></key-events>
    <adverse-outcome key-event-id="ke-c"><examples/></adverse-outcome>
    <key-event-relationships>
      <relationship id="ker-2"><adjacency>non-adjacent</adjacency>
        <quantitative-understanding-value>Not Specified</quantitative-understanding-value>
        <evidence>Moderate</evidence></relationship>
    </key-event-relationships>
    <overall-assessment><weight-of-evidence-summary></weight-of-evidence-summary>
      <key-event-essentiality-summary></key-event-essentiality-summary></overall-assessment>
  </aop>
  <vendor-specific>
    <key-event-reference id="ke-a" aop-wiki-id="26"/>
    <key-event-reference id="ke-b" aop-wiki-id="1614"/>
    <key-event-reference id="ke-c" aop-wiki-id="1786"/>
    <key-event-reference id="ke-d" aop-wiki-id="227"/>
    <key-event-relationship-reference id="ker-1" aop-wiki-id="2130"/>
    <key-event-relationship-reference id="ker-2" aop-wiki-id="3348"/>
    <aop-reference id="aop-1" aop-wiki-id="344"/>
    <aop-reference id="aop-2" aop-wiki-id="51"/>
  </vendor-specific>
</data>
"""


@pytest.fixture(scope="module")
def aop_evidence():
    spec = importlib.util.spec_from_file_location("aop_evidence", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def export(tmp_path_factory):
    path = tmp_path_factory.mktemp("export") / "aop-wiki-xml-0000-00-00"
    path.write_text(FIXTURE)
    return path


def test_ratings_come_from_the_structured_fields(aop_evidence, export):
    """Weight of evidence is the export's <evidence>, not a word found in prose."""
    result = aop_evidence.collect(export, ["344"])
    by_ker = {row["ker_id"]: row for row in result["aops"]["344"]["relationships"]}
    assert by_ker["2130"]["weight_of_evidence"] == "High"
    assert by_ker["2130"]["quantitative_understanding"] == "Moderate"
    assert by_ker["3348"]["weight_of_evidence"] == "Low"
    assert by_ker["2130"]["adjacency"] == "adjacent"
    assert by_ker["3348"]["adjacency"] == "non-adjacent"


def test_the_same_ker_is_rated_per_aop(aop_evidence, export):
    """KER3348 is Low in AOP 344 and Moderate in AOP 51. The rating is not the KER's."""
    result = aop_evidence.collect(export, ["344", "51"])
    rating = {
        aop: next(
            row["weight_of_evidence"]
            for row in result["aops"][aop]["relationships"]
            if row["ker_id"] == "3348"
        )
        for aop in ("344", "51")
    }
    assert rating == {"344": "Low", "51": "Moderate"}


def test_nested_prose_paths_resolve(aop_evidence, export):
    """The prose blocks are nested, and the export misspells empirical support."""
    result = aop_evidence.collect(export, ["344"])
    filled = next(
        row for row in result["aops"]["344"]["relationships"] if row["ker_id"] == "2130"
    )
    assert "biological_plausibility" in filled["populated_prose_fields"]
    assert "empirical_support" in filled["populated_prose_fields"]
    assert "uncertainties" in filled["empty_prose_fields"]
    assert filled["has_tabulated_evidence"] is True
    empty = next(
        row for row in result["aops"]["344"]["relationships"] if row["ker_id"] == "3348"
    )
    assert empty["populated_prose_fields"] == []
    assert empty["has_tabulated_evidence"] is False


def test_roles_and_order(aop_evidence, export):
    """The order runs from the initiating event along the adjacent relationships."""
    sequence = aop_evidence.collect(export, ["344"])["aops"]["344"]["sequence"]
    assert [(event["ke_id"], event["role"]) for event in sequence] == [
        ("26", "MIE"),
        ("1614", "KE"),
        ("1786", "AO"),
    ]


def test_order_is_stable(aop_evidence, export):
    """Two runs give the same order, which is what makes the output citable."""
    first = aop_evidence.collect(export, ["344", "51"])
    second = aop_evidence.collect(export, ["344", "51"])
    assert first == second


def test_a_broken_chain_is_reported(aop_evidence, export):
    """An orphaned initiating event and an outcome reached only non-adjacently."""
    structure = aop_evidence.collect(export, ["51"])["aops"]["51"]["structure"]
    assert structure["initiating_events_without_adjacent_outflow"] == ["227"]
    assert structure["events_in_no_relationship"] == ["227"]
    assert structure["adverse_outcomes_without_adjacent_inflow"] == ["1786"]

    holds = aop_evidence.collect(export, ["344"])["aops"]["344"]["structure"]
    assert holds["initiating_events_without_adjacent_outflow"] == []
    # AOP 344's outcome is reached only by a non-adjacent relationship, which is
    # true of the real AOP 344 as well.
    assert holds["adverse_outcomes_without_adjacent_inflow"] == ["1786"]


def test_assessment_vocabulary_mismatch_is_flagged(aop_evidence, export):
    """A summary grading evidence "strong" does not share the export's vocabulary."""
    result = aop_evidence.collect(export, ["344", "51"])
    assert result["aops"]["344"]["assessment_table_vocabulary_differs"] == ["strong"]
    assert result["aops"]["51"]["assessment_table_vocabulary_differs"] == []
    assert result["aops"]["51"]["has_weight_of_evidence_summary"] is False


def test_a_missing_aop_is_reported_not_ignored(aop_evidence, export):
    result = aop_evidence.collect(export, ["344", "9999"])
    assert result["missing_aops"] == ["9999"]
    assert list(result["aops"]) == ["344"]


def test_markdown_renders_every_requested_aop(aop_evidence, export):
    rendered = aop_evidence.as_markdown(aop_evidence.collect(export, ["344", "51"]))
    assert "## AOP 344" in rendered and "## AOP 51" in rendered
    assert "| KER2130 | KE26 → KE1614 | adjacent | High |" in rendered
