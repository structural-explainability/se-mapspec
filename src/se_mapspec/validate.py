"""Schema-driven structural validation of declared MapSpec alignments.

Validation concerns record structure and declared-field consistency only.
It cannot establish whether an asserted correspondence is correct.
"""

from dataclasses import dataclass, field
from typing import Any

__all__ = ["ValidationIssue", "ValidationResult", "validate_alignments"]


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """One field-specific structural validation diagnostic."""

    field: str
    message: str
    severity: str = "error"


@dataclass(slots=True)
class ValidationResult:
    """Combined results of validating an alignment document."""

    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Whether validation produced no errors."""
        return not any(issue.severity == "error" for issue in self.issues)


def _matches_type(value: object, type_name: str) -> bool:
    """Check the primitive field types supported by the canonical schema."""
    if type_name == "string":
        return isinstance(value, str)
    if type_name == "boolean":
        return isinstance(value, bool)
    if type_name == "float":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if type_name == "list[string]":
        return isinstance(value, list) and all(isinstance(v, str) for v in value)
    return False


def validate_alignments(
    document: dict[str, Any], schema: dict[str, Any]
) -> ValidationResult:
    """Validate a document containing one or more ``[[alignment]]`` tables.

    Rules are sourced from the provided canonical schema. `ok` indicates
    schema conformance, not factual accuracy or mapping correctness.
    """
    result = ValidationResult()

    def error(path: str, message: str) -> None:
        result.issues.append(ValidationIssue(path, message))

    alignment_schema = schema["alignment"]
    required_fields: list[str] = alignment_schema["required_fields"]["fields"]
    optional_fields: list[str] = alignment_schema["optional_fields"]["fields"]
    field_defs: dict[str, dict[str, Any]] = schema["field"]
    rules: dict[str, Any] = schema.get("validation", {})
    allowed_fields = set(required_fields) | set(optional_fields)

    rows = document.get("alignment")
    if not isinstance(rows, list) or not rows:
        error("alignment", "at least one [[alignment]] table is required")
        return result

    for index, row in enumerate(rows, start=1):
        prefix = f"alignment[{index}]"
        if not isinstance(row, dict):
            error(prefix, "alignment entry must be a table")
            continue

        if rules.get("require_known_fields_only", False):
            for name in sorted(row.keys() - allowed_fields):
                error(f"{prefix}.{name}", "unknown alignment field")

        if rules.get("require_required_fields", False):
            for name in required_fields:
                if name not in row:
                    error(f"{prefix}.{name}", "required field is missing")

        for name in sorted(row.keys() & allowed_fields):
            definition = field_defs[name]
            value = row[name]
            field_path = f"{prefix}.{name}"
            field_type = definition["type"]
            if not _matches_type(value, field_type):
                error(field_path, f"expected {field_type}")
                continue
            if "nonempty" in definition.get("constraints", []) and not value.strip():
                error(field_path, "must not be empty")
            allowed = definition.get("allowed")
            if allowed is not None and value not in allowed:
                error(field_path, f"must be one of {allowed!r}")
            if field_type == "float":
                if "minimum" in definition and value < definition["minimum"]:
                    error(field_path, f"must be >= {definition['minimum']}")
                if "maximum" in definition and value > definition["maximum"]:
                    error(field_path, f"must be <= {definition['maximum']}")

        identity = rules.get("identity", {})
        if (
            identity.get("source_id_must_not_equal_target_id", False)
            and isinstance(row.get("source_id"), str)
            and isinstance(row.get("target_id"), str)
            and row["source_id"] == row["target_id"]
        ):
            error(prefix, "source_id and target_id must differ under this schema")

        traceability = rules.get("traceability", {})
        if (
            traceability.get("evidence_required_when_human_validated", False)
            and row.get("human_validated") is True
            and not row.get("evidence")
        ):
            error(f"{prefix}.evidence", "evidence required when human_validated=true")
        if traceability.get("source_text_allowed") is False and "source_text" in row:
            error(f"{prefix}.source_text", "source_text is disallowed by the schema")

    return result
