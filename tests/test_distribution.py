"""Verify the canonical root schema and package-resource access agree."""

from pathlib import Path

import pytest

from se_mapspec.load import load_schema, packaged_schema_text

ROOT = Path(__file__).resolve().parents[1]


def test_root_schema_is_valid() -> None:
    assert (
        load_schema(ROOT / "alignment-schema.toml")["alignment"]["table"] == "alignment"
    )


def test_packaged_copy_matches_root_after_build() -> None:
    # For source checkouts, this test requires the built wheel's resource to
    # be installed or staged at src/se_mapspec/alignment-schema.toml.
    packaged = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "se_mapspec"
        / "alignment-schema.toml"
    )
    if not packaged.exists():
        pytest.skip("Packaged resource is not present until after a wheel build")
    assert packaged.read_text(encoding="utf-8") == packaged_schema_text()
    assert packaged.read_text(encoding="utf-8") == (
        ROOT / "alignment-schema.toml"
    ).read_text(encoding="utf-8")
