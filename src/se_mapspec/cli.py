"""Command-line interface for se-mapspec.

Argument parsing lives here; command behavior lives in se_mapspec.commands.

Commands:
    uv run se_mapspec validate-schema [--path alignment-schema.toml] [--strict]
    uv run se_mapspec validate-alignment --path examples/alignment.toml [--strict]
    uv run se_mapspec check-version [--require-tag]
"""

import argparse
from collections.abc import Callable, Sequence
from pathlib import Path

from se_mapspec.commands import check_version, validate_alignment, validate_schema

__all__ = ["build_parser", "main"]

CommandFunc = Callable[[argparse.Namespace], int]
EXIT_NO_COMMAND = 2


def _run_check_version(args: argparse.Namespace) -> int:
    """Check the release version without changing repository files."""
    return check_version.run(require_tag=args.require_tag)


def _run_validate_schema(args: argparse.Namespace) -> int:
    """Check the internal consistency of an alignment schema."""
    return validate_schema.run(path=args.path, strict=args.strict)


def _run_validate_alignment(args: argparse.Namespace) -> int:
    """Validate declared alignment record structure."""
    return validate_alignment.run(
        path=args.path,
        schema_path=args.schema_path,
        strict=args.strict,
    )


def build_parser() -> argparse.ArgumentParser:
    """Construct the MapSpec command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="se_mapspec",
        description="Validate MapSpec alignment schemas and structural mapping records.",
    )
    subparsers = parser.add_subparsers(dest="command")

    version_parser = subparsers.add_parser(
        "check-version",
        help="Compare CITATION.cff with the pyproject fallback version and optional Git tag.",
    )
    version_parser.add_argument(
        "--require-tag", action="store_true", help="Also require a matching Git tag."
    )
    version_parser.set_defaults(func=_run_check_version)

    schema_parser = subparsers.add_parser(
        "validate-schema", help="Check alignment-schema.toml internal consistency."
    )
    schema_parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Schema path; defaults to the canonical schema.",
    )
    schema_parser.add_argument(
        "--strict", action="store_true", help="Treat any warnings as errors."
    )
    schema_parser.set_defaults(func=_run_validate_schema)

    alignment_parser = subparsers.add_parser(
        "validate-alignment", help="Validate one or more [[alignment]] tables."
    )
    alignment_parser.add_argument(
        "--path", type=Path, required=True, help="TOML file with alignment records."
    )
    alignment_parser.add_argument(
        "--schema-path",
        type=Path,
        default=None,
        help="Alternative alignment schema path.",
    )
    alignment_parser.add_argument(
        "--strict", action="store_true", help="Treat any warnings as errors."
    )
    alignment_parser.set_defaults(func=_run_validate_alignment)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Dispatch a CLI command and return its exit status."""
    parser = build_parser()
    args = parser.parse_args(argv)
    func: CommandFunc | None = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return EXIT_NO_COMMAND
    return func(args)


if __name__ == "__main__":
    raise SystemExit(main())
