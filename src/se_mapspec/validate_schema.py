"""Check the internal consistency of the MapSpec alignment schema."""

from typing import Any

__all__ = ["validate_schema_internal"]

KNOWN_TYPES = {"string", "float", "boolean", "list[string]"}
REQUIRED_RULES = {
    "require_known_fields_only",
    "require_required_fields",
    "require_allowed_relation",
    "require_allowed_method",
    "require_confidence_range",
    "require_boolean_human_validated",
}
NESTED_RULES = {
    "identity": {"source_id_must_not_equal_target_id"},
    "traceability": {"evidence_required_when_human_validated", "source_text_allowed"},
}


def _string_list(value: object) -> bool:
    """Whether a value is a list of nonempty strings."""
    return isinstance(value, list) and all(
        isinstance(item, str) and bool(item) for item in value
    )


def _is_number(value: object) -> bool:
    """Exclude booleans when testing TOML numeric fields."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_schema_internal(schema: dict[str, Any]) -> list[str]:
    """Report schema-definition defects without inspecting a mapping claim."""
    errors: list[str] = []
    meta = schema.get("meta")
    if (
        not isinstance(meta, dict)
        or not isinstance(meta.get("schema"), str)
        or not meta["schema"].strip()
    ):
        errors.append("meta.schema: nonempty string required")

    alignment = schema.get("alignment")
    if not isinstance(alignment, dict):
        return [*errors, "alignment: required table missing"]
    if alignment.get("table") != "alignment":
        errors.append("alignment.table: must be 'alignment'")
    if alignment.get("toml_form") != "array-of-tables":
        errors.append("alignment.toml_form: must be 'array-of-tables'")
    if alignment.get("required") is not True:
        errors.append("alignment.required: must be true")

    required = alignment.get("required_fields")
    optional = alignment.get("optional_fields")
    required_fields: list[str] = []
    optional_fields: list[str] = []

    if isinstance(required, dict):
        required_fields = required.get("fields") or []
    if isinstance(optional, dict):
        optional_fields = optional.get("fields") or []

    if not _string_list(required_fields) or not required_fields:
        errors.append(
            "alignment.required_fields.fields: nonempty list[string] required"
        )
        required_fields = []
    if not _string_list(optional_fields):
        errors.append("alignment.optional_fields.fields: list[string] required")
        optional_fields = []

    all_fields = [*required_fields, *optional_fields]
    if len(all_fields) != len(set(all_fields)):
        errors.append("alignment: required and optional field names must be unique")

    fields = schema.get("field")
    if not isinstance(fields, dict):
        return [*errors, "field: required table missing"]
    for name in all_fields:
        definition = fields.get(name)
        if not isinstance(definition, dict):
            errors.append(f"field.{name}: required field definition missing")
            continue
        field_type = definition.get("type")
        if field_type not in KNOWN_TYPES:
            errors.append(f"field.{name}.type: unsupported type {field_type!r}")
        if definition.get("required") is not (name in required_fields):
            errors.append(
                f"field.{name}.required: conflicts with alignment field lists"
            )
        constraints = definition.get("constraints", [])
        if not _string_list(constraints) or any(c != "nonempty" for c in constraints):
            errors.append(f"field.{name}.constraints: unsupported constraint")
        if "nonempty" in constraints and field_type != "string":
            errors.append(f"field.{name}.constraints: nonempty requires string type")
        if "allowed" in definition:
            allowed = definition["allowed"]
            if field_type != "string" or not _string_list(allowed) or not allowed:
                errors.append(
                    f"field.{name}.allowed: nonempty list[string] on string required"
                )
            elif len(allowed) != len(set(allowed)):
                errors.append(f"field.{name}.allowed: duplicate values")
        if "minimum" in definition or "maximum" in definition:
            minimum = definition.get("minimum")
            maximum = definition.get("maximum")
            if (
                field_type != "float"
                or not _is_number(minimum)
                or not _is_number(maximum)
                or minimum > maximum
            ):
                errors.append(f"field.{name}: invalid numeric minimum/maximum")

    extra_definitions = fields.keys() - set(all_fields)
    if extra_definitions:
        errors.append(
            f"field: unlisted definitions: {', '.join(sorted(extra_definitions))}"
        )

    validation = schema.get("validation")
    if not isinstance(validation, dict):
        errors.append("validation: required table missing")
        return errors
    for key in sorted(REQUIRED_RULES):
        if validation.get(key) is not True:
            errors.append(f"validation.{key}: must be true for this schema version")
    for key in sorted(validation.keys() - REQUIRED_RULES - NESTED_RULES.keys()):
        errors.append(f"validation.{key}: unknown rule")
    for section, names in NESTED_RULES.items():
        rules = validation.get(section)
        if not isinstance(rules, dict):
            errors.append(f"validation.{section}: required table missing")
            continue
        for name in names:
            if not isinstance(rules.get(name), bool):
                errors.append(f"validation.{section}.{name}: boolean required")
        for name in sorted(rules.keys() - names):
            errors.append(f"validation.{section}.{name}: unknown rule")
    return errors
