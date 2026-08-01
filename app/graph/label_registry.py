"""Node-label registry and shared Neo4j record helpers.

Extracted from app/graph/repository.py (which had grown to 330 lines,
over Rule R-16's 300-line limit) rather than left inline. This module
holds no Cypher and no queries — it is pure metadata (the closed list
of valid node labels and their Pydantic field sets) plus two small
record-shape converters that both app/graph/repository.py and any
future Phase 6 writer module need identically. Splitting it out here,
rather than duplicating it, is Rule R-33 (shared types/constants live
in one place, never duplicated) applied at the module level.

Rule R-48 layer note: this is a "shared utility" (constants + pure
functions, no database calls) per Blueprint 3.2's module dependency
rules, so it is importable from any layer without violating the
downward-only dependency direction.
"""

from __future__ import annotations

from typing import Any, Literal, get_type_hints

from app.graph.models import (
    ConceptNode,
    ContradictionNode,
    DecisionNode,
    EntityNode,
    QuestionNode,
    SourceNode,
)

# The only node labels that exist in the schema (Blueprint 2.3) - used
# to build the workspace status aggregate query. This is a closed,
# hardcoded list defined in this module, never derived from request
# input, so interpolating it into Cypher in repository.py does not
# reopen the injection risk Rule R-54 exists to prevent.
_COUNTABLE_LABELS: tuple[str, ...] = (
    "Concept",
    "Entity",
    "Decision",
    "Source",
    "Question",
    "Contradiction",
)

NodeLabel = Literal[
    "Concept", "Entity", "Decision", "Source", "Question", "Contradiction"
]

_LABEL_TO_MODEL: dict[str, type[Any]] = {
    "Concept": ConceptNode,
    "Entity": EntityNode,
    "Decision": DecisionNode,
    "Source": SourceNode,
    "Question": QuestionNode,
    "Contradiction": ContradictionNode,
}

# Derived, not hand-maintained: the only Cypher-safe property names for
# a given label are exactly that label's own Pydantic model fields
# (app/graph/models.py) - deriving this from get_type_hints() means it
# can never silently drift out of sync with the model the way a
# separately hand-typed allowlist could.
_VALID_KEY_PROPERTIES_BY_LABEL: dict[str, frozenset[str]] = {
    label: frozenset(get_type_hints(model)) for label, model in _LABEL_TO_MODEL.items()
}


def _record_properties(record: Any, key: str) -> dict[str, Any]:
    """Neo4j's driver returns node properties as a Node object under
    `record[key]`; `dict(...)` extracts a plain property dict from it.
    Centralised here so every query in repository.py converts the same
    way. `record` is typed `Any` rather than `neo4j.Record` because
    both `Record` (from `session.run().single()`) and the plain dicts
    `AsyncResult.data()` returns reach this helper, and only the
    dict-style subscript access is actually used."""

    return dict(record[key])


def _coerce_neo4j_datetimes(properties: dict[str, Any]) -> dict[str, Any]:
    """Neo4j's driver returns temporal properties as its own
    `neo4j.time.DateTime` type, not a stdlib `datetime` - Pydantic's
    `datetime` validator does not accept it directly. This converts
    every neo4j.time.DateTime value in a properties dict to a native
    `datetime` via its documented `.to_native()` method, in place, so
    every *Node.model_validate(...) call in repository.py gets a dict
    Pydantic can actually parse."""

    from neo4j.time import DateTime as Neo4jDateTime

    return {
        k: (v.to_native() if isinstance(v, Neo4jDateTime) else v)
        for k, v in properties.items()
    }
