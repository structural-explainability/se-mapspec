"""Read the canonical MapSpec schema and structural alignment documents."""

from importlib.resources import files
from pathlib import Path
import shutil
import subprocess
import tomllib
from typing import Any, Final

from se_mapspec.record import Alignment

__all__ = [
    "get_git_tag",
    "load_alignments",
    "load_schema",
    "load_toml",
    "packaged_schema_text",
    "repo_root_schema_path",
    "schema_text",
]

SCHEMA_FILENAME: Final[str] = "alignment-schema.toml"
PACKAGE_NAME: Final[str] = "se_mapspec"


def get_git_tag() -> str:
    """Return the tag at HEAD, requiring an exact tag match."""
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("git executable not found on PATH")
    try:
        return subprocess.check_output(
            [git, "describe", "--tags", "--exact-match"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("Repository is not on a tagged commit") from exc


def load_toml(path: Path) -> dict[str, Any]:
    """Parse a TOML file, raising an exception if reading or parsing fails."""
    with path.open("rb") as stream:
        return tomllib.load(stream)


def packaged_schema_text() -> str:
    """Return the schema distributed with the installed Python package."""
    return files(PACKAGE_NAME).joinpath(SCHEMA_FILENAME).read_text(encoding="utf-8")


def repo_root_schema_path() -> Path | None:
    """Find the canonical root schema when executing from a source checkout."""
    root = Path(__file__).resolve().parents[2]
    path = root / SCHEMA_FILENAME
    if (
        path.is_file()
        and (root / "src" / PACKAGE_NAME).resolve() == Path(__file__).resolve().parent
    ):
        return path
    return None


def schema_text(path: Path | None = None) -> str:
    """Read an explicit schema or the canonical root/packaged schema."""
    if path is not None:
        return path.read_text(encoding="utf-8")
    root_schema = repo_root_schema_path()
    if root_schema is not None:
        return root_schema.read_text(encoding="utf-8")
    return packaged_schema_text()


def load_schema(path: Path | None = None) -> dict[str, Any]:
    """Parse an explicit or canonical alignment schema."""
    return tomllib.loads(schema_text(path))


def load_alignments(path: Path, *, schema_path: Path | None = None) -> list[Alignment]:
    """Load alignments, rejecting structurally invalid documents.

    The result preserves declared assertions; it does not verify their truth.
    """
    from se_mapspec.validate import validate_alignments
    from se_mapspec.validate_schema import validate_schema_internal

    document = load_toml(path)
    schema = load_schema(schema_path)
    schema_errors = validate_schema_internal(schema)
    if schema_errors:
        raise ValueError("Invalid alignment schema: " + "; ".join(schema_errors))
    result = validate_alignments(document, schema)
    if not result.ok:
        details = "; ".join(f"{i.field}: {i.message}" for i in result.issues)
        raise ValueError(f"Invalid alignment document: {details}")
    return [Alignment.from_dict(item) for item in document["alignment"]]
