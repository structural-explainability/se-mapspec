"""CLI command to validate structural alignment records."""

from pathlib import Path
import tomllib

from se_mapspec.load import load_schema, load_toml
from se_mapspec.validate import validate_alignments
from se_mapspec.validate_schema import validate_schema_internal

__all__ = ["run"]


def run(*, path: Path, schema_path: Path | None = None, strict: bool = False) -> int:
    """Check alignment structure without evaluating substantive correctness."""
    try:
        schema = load_schema(schema_path)
        document = load_toml(path)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        print(f"[validate-alignment] ERROR: {exc}")
        return 1
    schema_errors = validate_schema_internal(schema)
    if schema_errors:
        for message in schema_errors:
            print(f"[validate-alignment] SCHEMA ERROR: {message}")
        return 1
    result = validate_alignments(document, schema)
    for issue in result.issues:
        print(
            f"[validate-alignment] {issue.severity.upper()}: {issue.field}: {issue.message}"
        )
    if not result.ok or (strict and result.issues):
        return 1
    print(
        f"[validate-alignment] OK: {len(document['alignment'])} alignment(s) structurally valid"
    )
    return 0
