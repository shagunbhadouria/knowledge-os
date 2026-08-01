"""Seed data definitions for `make seed` (Blueprint Phase 3 exit
criterion).

Blueprint Phase 3 deliverable, verbatim: "Seed script: make seed —
creates 3 Concept nodes, 3 Entity nodes, 2 Decision nodes, 5 Source
nodes with valid temporal properties. Enough to test retrieval."

This module only holds the *data* — plain Python dicts matching each
node label's property table in Blueprint 2.3 exactly (property names,
types, and required fields). app/database/seeds/run.py holds the
Cypher and orchestration; keeping the two separate means the seed
*content* can be reviewed/edited without touching any Cypher, and
vice versa.

Every node here is deliberately small and internally consistent: the
Decision node for "Move from PostgreSQL to MongoDB" is CAUSED by
concepts it actually relates to, DECIDED by an Entity that AUTHORED
the Source it came from — so Phase 7 retrieval and Phase 8 agent work
have real graph structure to traverse, not just isolated nodes.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

_T0 = datetime(2025, 1, 15, tzinfo=UTC)  # 6 months before "now" for the seed story
_T1 = datetime(2025, 4, 10, tzinfo=UTC)
_T2 = datetime(2025, 7, 1, tzinfo=UTC)  # decision reversal point

CONCEPTS: list[dict[str, Any]] = [
    {
        "name": "PostgreSQL",
        "aliases": ["Postgres", "psql"],
        "valid_from": _T0.isoformat(),
        "valid_until": None,
        "confidence_score": 0.9,
        "source_count": 2,
        "contradiction_count": 0,
        "last_confirmed_at": _T2.isoformat(),
    },
    {
        "name": "MongoDB",
        "aliases": ["Mongo"],
        "valid_from": _T1.isoformat(),
        "valid_until": None,
        "confidence_score": 0.85,
        "source_count": 2,
        "contradiction_count": 0,
        "last_confirmed_at": _T2.isoformat(),
    },
    {
        "name": "deployment pipeline",
        "aliases": ["CI/CD pipeline", "deploy pipeline"],
        "valid_from": _T0.isoformat(),
        "valid_until": None,
        "confidence_score": 0.7,
        "source_count": 1,
        "contradiction_count": 0,
        "last_confirmed_at": _T0.isoformat(),
    },
]

ENTITIES: list[dict[str, Any]] = [
    {
        "canonical_name": "Priya Sharma",
        "known_aliases": ["ps2024", "priya_s"],
        "primary_source": "github",
        "contribution_weight": 0.8,
        "expertise_areas": ["PostgreSQL", "MongoDB"],
        "last_active_at": _T2.isoformat(),
        "valid_from": _T0.isoformat(),
    },
    {
        "canonical_name": "Arjun Mehta",
        "known_aliases": ["arjun.m"],
        "primary_source": "slack",
        "contribution_weight": 0.6,
        "expertise_areas": ["deployment pipeline"],
        "last_active_at": _T1.isoformat(),
        "valid_from": _T0.isoformat(),
    },
    {
        "canonical_name": "Divya Rao",
        "known_aliases": ["divya.rao"],
        "primary_source": "file",
        "contribution_weight": 0.3,
        "expertise_areas": [],
        "last_active_at": _T0.isoformat(),
        "valid_from": _T0.isoformat(),
    },
]

DECISIONS: list[dict[str, Any]] = [
    {
        "statement": "Move from PostgreSQL to MongoDB for the events service",
        "decided_at": _T1.isoformat(),
        "decided_by": "Priya Sharma",
        "source_url": "https://github.com/example/omnirag/pull/147",
        "status": "active",
        "reversed_at": None,
        "superseded_by": None,
        "valid_from": _T1.isoformat(),
        "valid_until": None,
    },
    {
        "statement": "Use JWT for auth instead of session cookies",
        "decided_at": _T0.isoformat(),
        "decided_by": "Arjun Mehta",
        "source_url": "https://github.com/example/omnirag/pull/12",
        "status": "active",
        "reversed_at": None,
        "superseded_by": None,
        "valid_from": _T0.isoformat(),
        "valid_until": None,
    },
]

SOURCES: list[dict[str, Any]] = [
    {
        "source_type": "github",
        "external_id": "seed-pr-147",
        "url": "https://github.com/example/omnirag/pull/147",
        "author_id": "Priya Sharma",
        "content_preview": (
            "Switch events service from PostgreSQL to MongoDB " "for schema flexibility"
        ),
        "ingested_at": _T1.isoformat(),
        "privacy_level": "internal_knowledge",
    },
    {
        "source_type": "slack",
        "external_id": "seed-slack-0001",
        "url": None,
        "author_id": "Arjun Mehta",
        "content_preview": (
            "Going with JWT for auth, session cookies won't scale " "across services"
        ),
        "ingested_at": _T0.isoformat(),
        "privacy_level": "internal_knowledge",
    },
    {
        "source_type": "github",
        "external_id": "seed-pr-12",
        "url": "https://github.com/example/omnirag/pull/12",
        "author_id": "Arjun Mehta",
        "content_preview": "Add JWT middleware to all protected routes",
        "ingested_at": _T0.isoformat(),
        "privacy_level": "internal_knowledge",
    },
    {
        "source_type": "file",
        "external_id": "seed-file-os-notes",
        "url": None,
        "author_id": "Divya Rao",
        "content_preview": (
            "Operating systems lecture notes: process scheduling, deadlocks"
        ),
        "ingested_at": _T0.isoformat(),
        "privacy_level": "public_knowledge",
    },
    {
        "source_type": "slack",
        "external_id": "seed-slack-0002",
        "url": None,
        "author_id": "Priya Sharma",
        "content_preview": (
            "MongoDB migration is done, PostgreSQL instance can be " "decommissioned"
        ),
        "ingested_at": _T2.isoformat(),
        "privacy_level": "internal_knowledge",
    },
]
