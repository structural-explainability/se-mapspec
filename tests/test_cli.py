"""Minimal CLI contract and status-code tests."""

from pathlib import Path

from se_mapspec.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_no_command_returns_usage_exit_code() -> None:
    assert main([]) == 2


def test_validate_schema_command() -> None:
    assert (
        main(
            [
                "validate-schema",
                "--path",
                str(ROOT / "alignment-schema.toml"),
                "--strict",
            ]
        )
        == 0
    )


def test_validate_alignment_command() -> None:
    assert (
        main(
            [
                "validate-alignment",
                "--path",
                str(ROOT / "examples" / "alignment.toml"),
                "--schema-path",
                str(ROOT / "alignment-schema.toml"),
                "--strict",
            ]
        )
        == 0
    )


def test_missing_alignment_file() -> None:
    assert (
        main(
            [
                "validate-alignment",
                "--path",
                str(ROOT / "does-not-exist.toml"),
                "--schema-path",
                str(ROOT / "alignment-schema.toml"),
            ]
        )
        == 1
    )


def test_validate_schema_uses_root_by_default() -> None:
    assert main(["validate-schema", "--strict"]) == 0
