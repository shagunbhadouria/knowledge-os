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
