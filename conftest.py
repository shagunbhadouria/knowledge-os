"""Pytest-wide test configuration.

Rule R-36: the app fails fast without real config. Tests are not
production — they need config values present, but the values
themselves are fake/local placeholders, never real secrets (Rule R-51:
nothing here is a real credential). This module runs before any
`app.*` import that pytest collects, so `get_settings()` never sees a
missing-variable error during CI (Blueprint Phase 1 CI skeleton,
Section 5.2 Stage 1).
"""

import os

_TEST_ENV: dict[str, str] = {
    "MONGODB_URI": "mongodb://localhost:27017/omnirag_test",
    "NEO4J_URI": "bolt://localhost:7687",
    "NEO4J_USERNAME": "neo4j",
    "NEO4J_PASSWORD": "test-password",
    "REDIS_URL": "redis://localhost:6379/0",
    "GROQ_API_KEY": "gsk_test_placeholder",
    "GROQ_MODEL_FAST": "llama-3.1-8b-instant",
    "GROQ_MODEL_SMART": "llama-3.1-70b-versatile",
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "GOOGLE_CLIENT_ID": "test.apps.googleusercontent.com",
    "GOOGLE_CLIENT_SECRET": "test-secret",
    "JWT_PRIVATE_KEY": "test-private-key",
    "JWT_PUBLIC_KEY": "test-public-key",
    "GITHUB_WEBHOOK_SECRET": "test-github-secret",
    "SLACK_SIGNING_SECRET": "test-slack-secret",
    "ENTITY_MERGE_THRESHOLD": "0.85",
    "GRAPH_EXPANSION_HOPS": "2",
    "KTD_INACTIVITY_DAYS": "14",
    "FRONTEND_URL": "http://localhost:3000",
    "LOG_LEVEL": "INFO",
    "PORT": "3001",
    "NODE_ENV": "test",
}

for _key, _value in _TEST_ENV.items():
    os.environ.setdefault(_key, _value)

# Rule R-51/R-36 note: docker-compose.yml injects real MONGODB_URI
# into every omnirag-api container as an environment variable —
# including when pytest runs inside that same container.
# os.environ.setdefault() above is a no-op for keys that already
# exist, so the real MONGODB_URI (pointed at the live seeded
# `omnirag` database) was silently winning over the test-isolated
# `omnirag_test` database this file intends every test to use.
#
# The fix must only swap the *database name*, not the whole URI.
# Force-overriding the entire string back to
# "mongodb://localhost:27017/omnirag_test" (as an earlier version of
# this file did) throws away whatever host docker-compose.yml already
# set (the "mongodb" Docker-network service name) and silently
# reverts it to "localhost" - which only resolves to anything when
# pytest runs on the bare host, not inside the omnirag-api container
# itself. That breaks every MongoDB-touching integration test with
# ServerSelectionTimeoutError/ConnectionRefused the first time pytest
# actually runs where it's meant to run: inside the container, against
# mongodb-atlas-local. NEO4J_PASSWORD is deliberately NOT overridden at
# all, for the same host-preservation reason: these integration/health
# tests connect to the real Neo4j container, which uses the real
# docker-compose password, not a placeholder.
_existing_mongo_uri = os.environ["MONGODB_URI"]
if "/omnirag_test" not in _existing_mongo_uri:
    # Swap only the trailing "/omnirag" (or whatever default db name
    # is present) for "/omnirag_test", preserving host, port, and any
    # query string (e.g. ?directConnection=true) exactly as set.
    _base, _, _rest = _existing_mongo_uri.rpartition("/")
    _db_name, _, _query = _rest.partition("?")
    _new_rest = "omnirag_test" + ("?" + _query if _query else "")
    os.environ["MONGODB_URI"] = f"{_base}/{_new_rest}"
