"""MapSpec structural-validation rules, not domain correctness tests."""

from copy import deepcopy
from pathlib import Path

from se_mapspec.load import load_schema
from se_mapspec.validate import validate_alignments

SCHEMA = load_schema(Path(__file__).resolve().parents[1] / "alignment-schema.toml")
VALID = {
    "source_id": "source.example",
    "target_id": "target.example",
    "relation": "overlaps",
    "confidence": 0.5,
    "method": "manual",
    "human_validated": False,
}


def issues(row: dict) -> list[str]:
    result = validate_alignments({"alignment": [row]}, SCHEMA)
    return [f"{i.field}: {i.message}" for i in result.issues]


def test_valid_alignment() -> None:
    assert issues(VALID) == []


def test_missing_required_field() -> None:
    row = deepcopy(VALID)
    del row["source_id"]
    assert any("source_id" in message for message in issues(row))


def test_invalid_relation() -> None:
    row = {**VALID, "relation": "causes"}
    assert any("relation" in message for message in issues(row))


def test_confidence_type_and_bounds() -> None:
    for bad in (True, -0.1, 1.1):
        assert any(
            "confidence" in message for message in issues({**VALID, "confidence": bad})
        )


def test_optional_metadata() -> None:
    row = {**VALID, "evidence": ["https://example.org/a"], "note": "provisional"}
    assert issues(row) == []


def test_boolean_human_validated() -> None:
    assert any(
        "human_validated" in s for s in issues({**VALID, "human_validated": "yes"})
    )


def test_no_unknown_fields() -> None:
    assert any("unknown" in s for s in issues({**VALID, "conclusion": "safe"}))


def test_current_schema_forbids_equal_local_ids() -> None:
    row = {**VALID, "target_id": VALID["source_id"]}
    assert any("must differ" in s for s in issues(row))


def test_optional_evidence_required_when_schema_says_so() -> None:
    schema = deepcopy(SCHEMA)
    schema["validation"]["traceability"]["evidence_required_when_human_validated"] = (
        True
    )
    row = {**VALID, "human_validated": True}
    assert not validate_alignments({"alignment": [row]}, schema).ok


def test_no_alignment_tables() -> None:
    assert not validate_alignments({}, SCHEMA).ok


def test_structural_success_is_not_semantic_truth() -> None:
    row = {**VALID, "relation": "equivalent", "method": "imported"}
    assert issues(row) == []
