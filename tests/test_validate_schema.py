"""Self-validation of the MapSpec schema."""

from copy import deepcopy
from pathlib import Path

from se_mapspec.load import load_schema
from se_mapspec.validate_schema import validate_schema_internal

SCHEMA = load_schema(Path(__file__).resolve().parents[1] / "alignment-schema.toml")


def test_canonical_schema() -> None:
    assert validate_schema_internal(SCHEMA) == []


def test_missing_required_field_definition() -> None:
    schema = deepcopy(SCHEMA)
    del schema["field"]["relation"]
    assert any("relation" in error for error in validate_schema_internal(schema))


def test_duplicate_field_lists() -> None:
    schema = deepcopy(SCHEMA)
    schema["alignment"]["optional_fields"]["fields"].append("source_id")
    assert any("unique" in error for error in validate_schema_internal(schema))


def test_unknown_field_type() -> None:
    schema = deepcopy(SCHEMA)
    schema["field"]["relation"]["type"] = "sql"
    assert any(
        "unsupported type" in error for error in validate_schema_internal(schema)
    )


def test_unknown_validation_rule_is_rejected() -> None:
    schema = deepcopy(SCHEMA)
    schema["validation"]["verify_that_equivalence_is_true"] = True
    assert any("unknown rule" in error for error in validate_schema_internal(schema))
