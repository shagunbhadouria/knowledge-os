"""Typed domain models for Neo4j nodes and relationships.

Rule R-33: single source for these shapes — repository modules in
app/graph/, app/entity_resolution/, and (later) app/retrieval/,
app/agents/ all import from here rather than each hand-rolling a
similar dict shape.

Rule R-48 layer 3: repositories return these typed objects, never raw
Neo4j Record objects and never dict[str, Any] — that typing is the
whole point of a repository layer existing at all.

Every field name and type below is copied from Blueprint 2.3's node
label / relationship type tables verbatim — this file is a direct,
checkable transcription of that table into Pydantic, not an
approximation. Where the blueprint marks a field nullable (`X | null`
in the doc), the Python type carries `| None` here too.

These are distinct from the wire-shape models in app/shared/schemas.py
(e.g. GraphNode, which is a loosely-typed dict[str, Any] wrapper for
the generic /graph/nodes API response) — those exist to be flexible
across every possible node type on one API endpoint; these exist to be
strict per-label domain types inside the codebase.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ConceptNode(BaseModel):
    """Blueprint 2.3: Concept — a topic, technology, system, or idea
    discussed across sources."""

    name: str
    aliases: list[str]
    valid_from: datetime
    valid_until: datetime | None = None
    confidence_score: float
    source_count: int
    contradiction_count: int
    last_confirmed_at: datetime


class EntityNode(BaseModel):
    """Blueprint 2.3: Entity — a person: contributor, author, user."""

    canonical_name: str
    known_aliases: list[str]
    primary_source: str
    contribution_weight: float
    expertise_areas: list[str]
    last_active_at: datetime
    valid_from: datetime


class DecisionNode(BaseModel):
    """Blueprint 2.3: Decision — a concrete choice made."""

    statement: str
    decided_at: datetime
    decided_by: str
    source_url: str
    status: Literal["active", "reversed", "superseded"]
    reversed_at: datetime | None = None
    superseded_by: str | None = None
    valid_from: datetime
    valid_until: datetime | None = None


class SourceNode(BaseModel):
    """Blueprint 2.3: Source — a document, message, commit, or file
    that contributed knowledge."""

    source_type: Literal["github", "slack", "file"]
    external_id: str
    url: str | None = None
    author_id: str
    content_preview: str
    ingested_at: datetime
    privacy_level: Literal[
        "public_knowledge",
        "internal_knowledge",
        "sensitive_personal",
        "hr_matter",
    ]


class QuestionNode(BaseModel):
    """Blueprint 2.3: Question — an unanswered question from Slack or
    uploaded Q&A. Tracked for knowledge gap detection."""

    text: str
    asked_by: str
    asked_at: datetime
    answered: bool
    answer_source_id: str | None = None
    ask_count: int


class ContradictionNode(BaseModel):
    """Blueprint 2.3: Contradiction — a detected conflict between two
    nodes."""

    type: Literal["direct_factual", "temporal", "cross_source_ownership"]
    description: str
    detected_at: datetime
    resolved: bool
    resolution_notes: str | None = None


class CausedRelationship(BaseModel):
    """Blueprint 2.3: CAUSED — Decision -> Concept. Causal chain link
    used by CausalInferenceSpecialist (Phase 8) and graph expansion
    (Phase 7)."""

    established_at: datetime
    causal_evidence: str
    confidence: float


class DecidedRelationship(BaseModel):
    """Blueprint 2.3: DECIDED — Entity -> Decision."""

    decided_at: datetime
    confidence: float


class ExpertiseInRelationship(BaseModel):
    """Blueprint 2.3: EXPERTISE_IN — Entity -> Concept. Drives expert
    routing (Phase 9)."""

    contribution_score: float
    last_contribution_at: datetime
    contribution_count: int


class DecisionWithDecider(BaseModel):
    """A DecisionNode joined with the canonical_name of the Entity that
    made it, via the DECIDED relationship — the shape
    get_decision_history() and get_decisions_by_status() actually
    return, since callers (Phase 8's GraphTraversalSpecialist, Phase 6's
    contradiction detector) need the decider's name without a second
    round trip."""

    decision: DecisionNode
    decided_by_name: str
