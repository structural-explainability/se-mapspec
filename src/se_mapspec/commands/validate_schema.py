"""CLI command to check the internal consistency of an alignment schema."""

from pathlib import Path
import tomllib

from se_mapspec.load import load_schema
from se_mapspec.validate_schema import validate_schema_internal

__all__ = ["run"]


def run(*, path: Path | None = None, strict: bool = False) -> int:
    """Validate an explicit or canonical alignment schema; never rewrite it."""
    try:
        schema = load_schema(path)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        print(f"[validate-schema] ERROR: {exc}")
        return 1
    errors = validate_schema_internal(schema)
    for message in errors:
        print(f"[validate-schema] ERROR: {message}")
    if errors:
        return 1
    print("[validate-schema] OK: alignment schema is internally consistent")
    return 0
