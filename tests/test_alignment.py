"""Typed record conversion tests."""

from pathlib import Path

from se_mapspec.load import load_alignments, load_schema
from se_mapspec.record import Alignment

ROOT = Path(__file__).resolve().parents[1]


def test_schema_metadata() -> None:
    assert (
        load_schema(ROOT / "alignment-schema.toml")["alignment"]["table"] == "alignment"
    )


def test_typed_loading() -> None:
    items = load_alignments(
        ROOT / "examples" / "alignment.toml",
        schema_path=ROOT / "alignment-schema.toml",
    )
    assert len(items) == 1
    assert isinstance(items[0], Alignment)
    assert items[0].evidence == ()
