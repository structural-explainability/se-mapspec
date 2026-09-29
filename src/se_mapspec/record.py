"""Typed representation of a MapSpec structural alignment assertion.

An alignment records an asserted correspondence. Its construction or
structural validation does not establish the assertion's substantive truth.
"""

from dataclasses import dataclass
from typing import Any

__all__ = ["Alignment"]


@dataclass(frozen=True, slots=True)
class Alignment:
    """One source-to-target alignment, using the canonical schema's fields."""

    source_id: str
    target_id: str
    relation: str
    confidence: float
    method: str
    human_validated: bool
    source_text: str | None = None
    note: str | None = None
    evidence: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Alignment:
        """Construct from a schema-validated alignment table.

        Call validate_alignments on the containing document first; this
        method converts values and does not replace structural validation.
        """
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            relation=data["relation"],
            confidence=float(data["confidence"]),
            method=data["method"],
            human_validated=data["human_validated"],
            source_text=data.get("source_text"),
            note=data.get("note"),
            evidence=tuple(data.get("evidence", ())),
        )
