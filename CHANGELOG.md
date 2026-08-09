# Merge Log — knowledge-os-best-merged + knowledge-os-final → this build

## Final Blueprint Deliverable + Exit Criteria line-by-line pass

User asked, after the §3.1–3.3 sweep and the healthcheck reconciliation,
whether every Phase 3 demand and exit criterion was actually met (other
than local testing). Re-checked line by line against Blueprint Phase
3's Deliverables and Exit Criteria lists rather than re-asserting the
earlier summary. Found one more real gap and fixed it; the rest confirm
as complete.

**Real gap found and fixed:** Deliverable "Redis connection confirmed
with PING. **Streams and pub/sub channels configured.**" — pub/sub was
never built. `app/database/redis.py` had `verify_connectivity()`
(PING) and `ensure_streams()` (Streams), but zero pub/sub setup
existed anywhere in the codebase, confirmed via a full-codebase grep.
Fixed:
- Added `AGENT_STATUS_CHANNEL = "omnirag:agent_status"` to
  `app/shared/constants.py` (Blueprint 2.7 describes this channel by
  role — "SSE broadcast channel", "agent_status pub/sub events" — but
  never names it explicitly the way the ingestion stream is named;
  this is that missing name).
- Added `redis.verify_pubsub_ready()` — since Redis pub/sub channels
  have no server-side "create" concept the way streams do (a channel
  exists only while something is subscribed), this proves the
  mechanism works by subscribing, publishing a probe message, and
  confirming receipt, rather than pretending to "create" something
  that Redis has no notion of creating ahead of time.
- **First draft had a real bug the tests caught**: `client.pubsub()`
  was called before the `try:` block, so a connection failure there
  was unhandled and the `finally` block would reference an undefined
  variable. `test_returns_false_and_does_not_raise_on_connection_failure`
  failed against the first draft, exposing this; fixed by moving
  `pubsub = client.pubsub()` inside `try`, initialized to `None`
  beforehand so `finally` can check before using it.
- Added 4 unit tests (mocked) + 1 integration test (real Redis
  SUBSCRIBE/PUBLISH round trip).

**Also found and fixed while re-verifying full repository-function
integration coverage:** `get_source_by_external_id` and
`get_decision_history` (`app/graph/repository.py`),
`insert_embedding` and `find_embedding_by_neo4j_node_id`
(`app/database/mongo_repository.py`) had unit tests but no real-
service integration test — a gap in the same "unit test AND
integration test" checklist item already partially fixed in the
§3.1–3.3 pass, just not completely. Added 6 more integration tests to
close it. Every repository function across all three repository
modules now has integration coverage, either direct (function
imported and called by name in the test) or indirect (exercised
end-to-end through a route test that calls it internally — confirmed
by reading routes.py's actual implementation, not assumed).

**Deliverables — final count: 9/9 present.** Repository unit tests:
confirmed genuinely passing (36/36 repository-specific, 107/107 full
suite). MongoDB Atlas Vector Search: present via the mongot/Community
8.2 local equivalent (your explicit decision), not literal Atlas.

**Exit criteria — honest final accounting, not glossed over:**
- "Neo4j constraints/indexes verified via Neo4j Browser" — code and
  integration tests exist and are correct; the literal Browser
  verification step has not happened (no Docker/GUI in this sandbox).
- "MongoDB Atlas Vector Search index active, verified via Atlas
  dashboard" — same situation, substituted with a local integration
  test; no Atlas dashboard exists to check since this runs against
  mongot locally.
- "Seed script creates correct data, verified via Neo4j Browser" —
  same: code and 6 integration tests exist, Browser verification
  itself hasn't happened.
- "All repository unit tests passing" — **genuinely done**, verified
  by actually running pytest, not asserted.
- "Temporal query test passes" — the test exists, uses Blueprint 2.3's
  exact query pattern, and is correct; has not been run against a
  live Neo4j in this sandbox.
- "Baseline Neo4j query latency logged in Engineering Journal Part
  5.1" — **still blocked**, unchanged from earlier in this session:
  the Engineering Journal (DOC-03) has never been provided, so there
  is nothing to write the baseline into.

Net: every Phase 3 deliverable exists in code with test coverage.
Every exit criterion that can be satisfied by code+tests is satisfied.
The four criteria that specifically require a human clicking through
Neo4j Browser / Atlas dashboard / running `make test-integration`
against a live daemon remain exactly what the user's own question
already scoped them as: local testing, not something Claude can
complete from this sandbox. The Journal baseline is the one item that
needs either the missing document or the user filling it in directly.

Re-verified after every fix in this pass: `ruff check`/
`ruff format --check`/`mypy app tests` (strict)/`pip-audit` (both
requirement files) all clean. `pytest -m "not integration"` —
**107 passed**, 31 deselected (up from 103/24 before this pass).

## Reconciliation: pre-existing flagged gap, missed in the §3.1–3.3 sweep

User asked directly whether every deviation had actually been listed.
Re-checking rather than just re-asserting yes surfaced that the
§3.1–3.3 cross-check above was scoped to *this session's own* changes
and never reconciled against deviations already logged from **earlier
sessions** in this same CHANGELOG (the "Update 2/3/4" entries further
down this file, which predate any Phase 3 work).

One of those earlier entries was a live, correctly-predicted gap that
this session's own work should have triggered a fix for, and didn't
until now:

> **Update 3 (pre-Phase 3):** "no `depends_on: condition:
> service_healthy` / no `healthcheck:` blocks on mongodb/neo4j/redis/
> ollama. Not urgent *yet*... It will matter the moment Phase 3 adds
> real `neo4j`/`motor`/`redis-py` clients that connect at startup."

Phase 3 did exactly that — added real `neo4j`, `motor`, `redis-py`
clients wired into the app's `lifespan` — and the healthcheck gap was
never closed. `docker-compose.yml`'s `omnirag-api` `depends_on` was
still a plain list (no `condition:`) until this reconciliation, meaning
the API container could start and immediately fail its first
connection attempt before Neo4j/Redis finished booting (Neo4j in
particular is slow to accept Bolt connections after container start,
per that same earlier entry).

**Fixed now:**
- `neo4j` service — added a `cypher-shell -u ... -p ... 'RETURN 1'`
  healthcheck (`CMD-SHELL`, 30 retries, 20s start_period — Neo4j 4.4
  boot is slow). Pattern confirmed against multiple independent public
  docker-compose examples using neo4j:4.4/5.x images, not invented.
- `redis` service — added a `redis-cli ping` healthcheck.
- `omnirag-api`'s `depends_on` — upgraded from a plain service-name
  list to explicit `condition:` blocks: `service_healthy` for
  mongodb/neo4j/redis (all three now have real healthchecks and all
  three have real Python clients connecting at startup), `service_started`
  for mongot and ollama (neither has a simple documented CLI healthcheck,
  and neither has Phase 3 code connecting to it yet — ollama is Phase 5,
  mongot's vector search is unused until Phase 7).

Re-verified after this fix: `ruff check`/`mypy app tests` (strict)/
`pytest -m "not integration"` (**103 passed**, unchanged — this was a
YAML-only fix, no Python touched) all still clean.

**Lesson stated plainly, not glossed over:** asked to re-verify my own
"did you list every deviation" claim, the honest answer was no on
first check — this CHANGELOG has audit history from multiple sessions
and I had only re-surfaced the current session's findings, not
reconciled against what was already flagged and still open. Fixed by
actually reading back through the file rather than re-asserting the
same summary.

## Blueprint §3.1–3.3 Cross-Check (this session)

User asked for a thorough line-by-line cross-check of all Phase 3 work
against Blueprint §3.1 (Folder Structure), §3.2 (Coding Standards),
§3.3 (Git Workflow) and the Industrial Vibe Coding Rules — not a
re-summary, an actual re-verification. Findings:

**Real bugs found and fixed:**
- **Cypher property-injection vulnerability (real, exploitable)** —
  `app/graph/repository.py`'s `get_node_by_label_and_key()` interpolated
  `key_property` directly into a Cypher query with zero validation.
  `key_property` is fed straight from `GET /graph/node/{id}`'s
  free-text `?key_property=` query parameter (`app/graph/routes.py`) —
  an external caller could send e.g. `?key_property=name}) DETACH
  DELETE (n {x` to break out of the intended property-match clause.
  Fixed: derived an allowlist of valid property names per label from
  each Pydantic model's real fields (`_VALID_KEY_PROPERTIES_BY_LABEL`,
  built via `get_type_hints()` so it can't silently drift from
  `app/graph/models.py`), validated `key_property` against it before
  any Cypher runs, and wired the route to translate the rejection into
  a proper `400 VALIDATION_ERROR` (was previously going to be an
  unhandled 500). Added 3 regression tests including an adversarial
  injection-payload test, then **mutation-tested the fix** — reverted
  the validation, confirmed both tests failed correctly, restored —
  to prove the tests actually catch the vulnerability rather than
  passing trivially.
- **Rule R-34 violation (magic numbers)** — `384` (embedding
  dimensions) and `"all-MiniLM-L6-v2"` (embedding model name) were
  hardcoded directly in `app/database/mongodb.py` and
  `app/database/mongo_repository.py` instead of centralized named
  constants, despite Blueprint 8.2/Rule R-101 explicitly treating the
  embedding model as locked, migration-only infrastructure — exactly
  the kind of value R-34 exists to centralize. Fixed: added
  `EMBEDDING_MODEL_NAME`/`EMBEDDING_DIMENSIONS` to
  `app/shared/constants.py`, updated both source files and their tests
  to reference the constants instead of repeating literals.
- **PR-checklist-ambiguous Cypher string concatenation** —
  `get_decision_history()` used `+` to conditionally assemble a
  `WHERE` clause fragment. Every actual *value* stayed a bound
  `$status` parameter (the real R-54 safety property), so this was
  never exploitable — but it still literally matched Blueprint 3.3's
  PR checklist item "No Cypher string concatenation anywhere — grep
  for string interpolation in Cypher queries", which is written to be
  checkable by grep. Rewrote as two fixed literal query strings
  (branching in Python, not string-building) so a future grep-based
  check never has to manually re-clear this as a false positive.
- **Stale/inaccurate docstring** — `app/database/neo4j.py` claimed
  callers could import a `get_session()` helper from it; no such
  function was ever implemented or called anywhere in the codebase.
  Fixed the docstring to describe the actual pattern (`async with
  driver.session()` opened per call, no singleton session).
- **Missing integration tests (PR checklist item 5)** —
  `app/entity_resolution/repository.py` and
  `app/database/mongo_repository.py` had unit tests only, no real-
  service integration test, violating the PR checklist's "New feature
  has unit test AND at least one integration test." Added
  `TestEntityResolutionRepositoryAgainstRealServer` (3 tests) and
  `TestMongoRepositoryAgainstRealServer` (3 tests) to
  `tests/test_phase3_integration.py`.

**Contract deviation found, surfaced to user, resolved explicitly (not
silently):**
- `GET /graph/node/{id}` requires a `type` query param even though
  Blueprint 2.4 states `Request: None` for this endpoint. Neo4j has no
  single global node-ID space spanning labels the way a relational PK
  would; the alternatives (Neo4j `elementId()` as the public ID, or
  searching all 6 labels per lookup) both had worse tradeoffs. User
  confirmed keeping `type` as required — see Decision Log below and
  the `get_node` docstring in `app/graph/routes.py`.

**Confirmed clean (no issues found):** naming conventions (snake_case
files/functions, PascalCase Pydantic models, UPPER_SNAKE_CASE
constants) across every Phase 3 file; no bare/silent exception
swallowing (`except Exception:` blocks all log with `exc_info=True` and
return a typed `False`, never a silent pass); no module-level side
effects (AST-checked every new file for calls at import time — zero
found); no circular imports (imported every new module together in one
process, including `app.main`, with zero errors); mypy `--strict`
clean across all 81 source files; R-48 repository layering holds (no
repository imports another repository, no business-logic/threshold
logic found in any repository function).

**Not fully checked:** §3.3's branch-naming and commit-message-format
rules — this is an extracted zip, not a git clone, so there's no
commit history or branch list to check against R-72's `type/description`
convention. That part of §3.3 can only be verified once this is
actually committed to your repo.

Full suite re-verified after every fix in this cross-check:
`ruff check`/`ruff format --check`/`mypy app tests` (strict) all clean.
`pytest -m "not integration"` — **103 passed**, 24 deselected (up from
99/18 before this session — the new integration tests and the
decision-history no-status-branch test). `pip-audit` clean.

## Phase 3 — Database Layer (COMPLETE as of this entry)

Covers every Blueprint Phase 3 deliverable and exit criterion, across
two sessions (DB connections/health → schema/seed/streams →
repositories/routes → MongoDB 8.2 local vector search). Status against
the blueprint's own checklist:

| Deliverable | Status |
|---|---|
| Neo4j driver/session singleton + real `/health` checks | Done |
| MongoDB (Motor) client singleton + `raw_events`/`embeddings`/`generated_documents` collection getters | Done |
| Redis client singleton + real `/health` check | Done |
| Neo4j schema: 1 uniqueness constraint, 9 indexes, 1 fulltext index (Blueprint 2.3 table, verified against real Neo4j 4.4 docs) | Done |
| MongoDB Atlas Vector Search index | Done, upgraded scope — see Decision Log below |
| Redis Streams consumer group + dead-letter stream (idempotent `ensure_streams()`) | Done |
| Seed script — 3 Concept/3 Entity/2 Decision/5 Source nodes + `DECIDED`/`AUTHORED`/`CAUSED` relationships | Done |
| Repository modules — Neo4j (`app/graph/repository.py`, `app/entity_resolution/repository.py`) | Done |
| Repository modules — MongoDB (`app/database/mongo_repository.py`) | Done |
| `GET /workspace/status`, `GET /graph/nodes`, `GET /graph/node/{id}` wired to real Neo4j queries | Done — **not yet auth/rate-limited, see routes.py docstring; Phase 4 dependency** |
| Integration tests against real Neo4j/MongoDB/Redis (18 tests) | Written and collect correctly; **not run in this sandbox (no Docker available) — run `make test-integration` locally before fully trusting** |
| Repository unit tests (mocked drivers, Stage 1 CI) | Done — 99 unit tests total, all passing |
| Temporal query test (past-timestamp graph state) | Done, both unit-mocked and real-service versions |
| Baseline Neo4j query latency logged in Engineering Journal Part 5.1 | **Not done — Engineering Journal (DOC-03) was never provided to Claude; this cannot be filled in without that document. Run the `make test-integration` timing output through Journal 5.1 yourself, or share the doc.** |

### Decision Log additions (Rule R-60/CR-03 — log every decision the same session)

| Decision | Chosen | Rejected | Reason |
|---|---|---|---|
| Neo4j Python driver version | `neo4j==5.28.4` | `neo4j==6.x` (latest) | Locked server image is `neo4j:4.4`; Neo4j's driver-server compatibility matrix only guarantees 4.4 server with {4.3, 4.4, 5.x} drivers, not 6.x. Verified directly against Neo4j's compatibility docs, not assumed. |
| MongoDB Vector Search (local dev) | Upgrade `mongo:7` → `mongodb/mongodb-community-server:8.2-ubi8-slim` + `mongodb/mongodb-community-search:0.64.0` (mongot sidecar), replica-set mode | Stay on Atlas-only (Blueprint 2.2's original lock), or defer to Phase 7 | MongoDB Community Edition 8.2+ added local `$vectorSearch` (Sept 2025 GA) — no Atlas account needed for local dev. User explicitly chose to upgrade now rather than defer. Confirmed exact image tags directly against Docker Hub (`mongodb/mongodb-community-server`, `mongodb/mongodb-community-search`), not a third-party blog's claim alone. |
| CI integration-tests job database images | Kept plain `mongo:7` in GitHub Actions `services:` (no mongot sidecar in CI) | Rearchitect CI to manually `docker run` a dependent mongot sidecar | GitHub Actions `services:` containers can't express `depends_on`/custom startup ordering the way docker-compose can. Vector search is unused by any code until Phase 7 (retrieval); reworking CI's whole container orchestration for a capability nothing calls yet was not worth it now. `TestMongoVectorSearchIndexAgainstRealServer` (tests/test_phase3_integration.py) skips gracefully when mongot isn't reachable, so it only actually runs via local `make test-integration` against the full docker-compose stack. Revisit when Phase 7 needs CI coverage of real vector search. |
| `GET /workspace/status`, `/graph/nodes`, `/graph/node/{id}` — build now or wait for Phase 4 auth | Build the data-layer logic now, unauthenticated; flag clearly as unsafe to expose until Phase 4 | Wait for Phase 4 (JWT middleware, rate limiting) to exist first | `app/graph/routes.py`'s own pre-existing docstring already committed to "Implemented in Phase 3" for these three routes specifically. Rule R-70 (data model → repository → service → API → consumer, in order) supports building the data layer now and layering auth on top later via `Depends()`, rather than blocking Phase 3 on Phase 4 not existing yet. |
| `GET /graph/node/{id}` — Blueprint 2.4 says `Request: None`, but Neo4j has no single global node-ID space across labels | Kept `type` as a required query param (`?type=Concept`) | (a) Neo4j `elementId()` as node_id — matches contract literally but leaks an unstable internal identifier into the public API; (b) search all 6 labels for a match — matches contract but 6x slower and ambiguous on key collisions | User explicitly chose to keep human-readable, unambiguous IDs over literal contract compliance. Documented as a flagged deviation in `app/graph/routes.py`'s `get_node` docstring, not silently built around (Rule R-68). |

### Files changed this Phase 3 close-out pass (repositories/routes/vector search)

- `app/graph/models.py` — new. Typed Pydantic domain models (ConceptNode, EntityNode, DecisionNode, SourceNode, QuestionNode, ContradictionNode, + relationship types) transcribed directly from Blueprint 2.3's property tables.
- `app/graph/repository.py` — real implementation (was a 1-line stub). Node counts, last-ingested lookup, unanswered-question count, paginated node listing, node-by-key lookup, Source dedup lookup, decision history with decider join.
- `app/entity_resolution/repository.py` — real implementation (was a 1-line stub). Candidate pool listing for Stage 1, shared-neighbor-count for Stage 3, `ALIAS_OF` merge write.
- `app/database/mongo_repository.py` — new. Typed CRUD for `raw_events`, `embeddings`, `generated_documents` — the cross-cutting MongoDB repository Blueprint Phase 3 calls for.
- `app/database/mongodb.py` — added `ensure_vector_search_index()` and `list_search_indexes()`.
- `app/graph/routes.py` — `GET /workspace/status`, `GET /graph/nodes`, `GET /graph/node/{id}` now call real repository functions instead of raising `EndpointNotImplementedError`.
- `docker-compose.yml` — `mongodb` service upgraded to `mongodb/mongodb-community-server:8.2-ubi8-slim` (replica-set mode), new `mongot` sidecar service, new `mongot_data` volume.
- `.env.example` — `MONGODB_URI` updated for replica-set connection (`?replicaSet=rs0&directConnection=true`).
- `pyproject.toml` — added `flake8-bugbear` `extend-immutable-calls` for `fastapi.Query`/`Depends`/`Path`/`Body` (fixes a real false-positive B008 lint error on every FastAPI route using these, not just this session's routes).
- `app/test_health.py` — updated the Phase 2 stub-endpoint regression test to remove the 3 now-real routes from the generic 501 list; added dedicated tests for their real (mocked-repository) behavior.
- `tests/test_phase3_integration.py` — added `TestGraphRoutesAgainstRealServer` (4 tests) and `TestMongoVectorSearchIndexAgainstRealServer` (1 test, skips gracefully without mongot).
- New unit test files: `app/graph/test_repository.py` (13 tests), `app/entity_resolution/test_repository.py` (5 tests), `app/database/test_mongo_repository.py` (13 tests, 4 of them vector-search-specific).

**Verified this pass**: `ruff check`/`ruff format --check`/`mypy app tests` (strict) all clean. `pytest -m "not integration"` — **99 passed**, 18 deselected. `pip-audit` clean on both requirement files. Mutation-tested two assertions by deliberately breaking the code under test and confirming the test failed, then restored (Rule R-66). Did **not** run the 18 integration tests against real services — no Docker in this sandbox; run `make test-integration` locally to get the real proof, especially for the new MongoDB 8.2/mongot vector search path which is the newest and least-trodden piece.

## Merge Log — knowledge-os-best-merged + knowledge-os-final → this build

Base: `knowledge-os-final`. Reason: lazy `get_settings()` pattern
(no module-level side effects on `import app.config`), typed
per-endpoint response models matching Blueprint 2.4 exactly (not a
generic stub payload), complete `.gitignore` / `.dockerignore` /
`.secrets.baseline`, and a CI `ruff format --check` step — all absent
or worse in `knowledge-os-best-merged`.

## Fix ported from `knowledge-os-best-merged`

**Bug**: `GET`/any-method requests to an unmatched route, and requests
to a real route with an unsupported method, bypassed the envelope
system entirely and returned Starlette's raw default body
(`{"detail": "Not Found"}` / `{"detail": "Method Not Allowed"}`)
instead of the standard envelope. Silently broke Rule R-28 ("every
endpoint has a standard response envelope, no exceptions") — Starlette
raises these before any app route handler or `OmniRAGError` subclass
is ever reached, so no existing exception handler caught them.

Verified live in `knowledge-os-final` before fixing:
`GET /api/v1/this-route-does-not-exist` → `{"detail": "Not Found"}`.

**Fix**: registered a `StarletteHTTPException` handler in
`install_error_handlers()` (`app/shared/middleware.py`) that maps to
`NOT_FOUND` (404) or `HTTP_ERROR` (other codes, e.g. 405) inside the
standard envelope, with the same `request_id` propagation as every
other handler.

Re-verified live after the fix: both 404 and 405 now return
`{"success": false, "error": {"code": ...}, ...}` in the correct
shape.

## Regression tests added (`app/test_health.py`)

- `test_unknown_route_returns_standard_envelope_not_raw_404`
- `test_wrong_method_on_real_route_returns_standard_envelope_not_raw_405`
- `test_error_response_request_id_matches_header`

## Other changes

- `pyproject.toml`: added `follow_imports = "normal"` under
  `[tool.mypy]` (ported from `best-merged`; stricter import resolution,
  no behavior change, no cost).
- `.secrets.baseline`: the inherited file had `"plugins_used": []` —
  it existed but scanned with zero detectors, a no-op stub. Regenerated
  with `detect-secrets scan`'s full default plugin set (27 detectors).
  Baselines 10 pre-existing matches in `.env.example`, `conftest.py`,
  and the blueprint doc — all placeholder/example values, none real
  (Rule R-51). New genuine secrets introduced later will now actually
  fail the pre-commit hook and CI; before this fix they would not have
  been caught even with a correctly-present baseline file.

## Verification performed on this build

- `ruff check app tests conftest.py` — clean.
- `ruff format --check app tests` — clean, matches the CI gate exactly.
- `mypy app` (strict) — clean, 68 source files.
- `pytest` — 25/25 passing, run under a wiped environment
  (`env -i PATH="$PATH" HOME="$HOME"`, no inherited `.env`, no shell
  leakage) — matches what a fresh GitHub Actions runner sees.
- `detect-secrets scan --baseline .secrets.baseline` — 0 new findings,
  confirmed stable after a commit (re-run gives the same clean result).
- Both the 404 and 405 envelope fix and the original bug were each
  independently reproduced by running the app and calling the routes
  with `TestClient`, not inferred from reading the exception-handler
  registration.

## Update 2 — Blueprint Part 02 (2.1–2.7) audit

Requested: check the codebase against Blueprint sections 2.1–2.7 and
the rules doc. Findings, all verified by running tools, not by reading
code and assuming:

**1. Silent contract deviation, undisclosed (Rule R-68 violation).**
`GET /health` was mounted at `/health`, not `/api/v1/health`. Blueprint
2.4 lists `/health` in the same table as the other 17 endpoints, under
the same `/api/v1/` base URL, with no stated exception. Verified live:
`/health` → 200, `/api/v1/health` → 404 before the fix.

Fix: added `prefix="/api/v1"` to the health router. Updated the two
call sites that assumed the old path (`app/test_health.py`,
`README.md`'s curl example). Documented the tradeoff in the module
docstring instead of picking silently — the common infra convention
actually *is* an unversioned `/health` for load-balancer probes, so if
that's what you actually want, it's a one-line revert, not a bug.

**2. `pip-audit` installed, never invoked (Blueprint 2.5 A06 / Phase 11
exit criterion).** It sat in `requirements-dev.txt` unused since the
original scaffold. Added it as a CI step — and running it for the
first time immediately surfaced real, currently-known CVEs:

- `starlette==0.41.3` (pulled transitively via `fastapi==0.115.6`):
  7 known vulnerabilities (PYSEC-2026-161/248/249/1941/1942/2280/2281).
- `python-multipart==0.0.20`: 6 known vulnerabilities
  (PYSEC-2026-1852/3036/3037/3038/3039/3040).
- `pytest==8.3.4` (dev-only, but a supply-chain risk on CI runners
  regardless): PYSEC-2026-1845.

Fix: bumped `fastapi` → `0.139.2`, `starlette` → `1.3.1` (pinned
explicitly rather than left to float — a security-relevant transitive
dep should be an auditable line, not implicit), `python-multipart` →
`0.0.32`, `pytest` → `9.0.3`, `pytest-asyncio` → `1.4.0` (the only
version compatible with pytest 9). Re-ran the full app and full test
suite after — 25/25 still pass, `mypy --strict` still clean. `pip-audit`
now clean against both `requirements.txt` and `requirements-dev.txt`;
CI now runs it against both, not just prod.

Known follow-up, not fixed: the version bump surfaced a
`StarletteDeprecationWarning` — `starlette.testclient` now prefers
`httpx2` over `httpx`. Not a failure, tests still pass, but it's the
next thing pip-audit-driven maintenance will eventually force. Left
as-is this round to avoid scope creep on an unrelated dependency swap.

**3. `conftest.py` was invisible to CI linting.** `ruff check app
tests` never covered the repo-root `conftest.py`, despite it
containing real logic (the test-env-var seeding). Added it to both the
lint and format-check CI steps.

**4. R-40 regression from Update 1's own fix.** `install_error_handlers`
grew to ~100 lines after the `StarletteHTTPException` handler was added
last round. Extracted the four handlers to named module-level
functions; `install_error_handlers` is now a 4-line registration list.
Re-verified: `mypy --strict` clean, R-40 AST line-count sweep clean,
live 404/405 behavior unchanged.

**Checked and confirmed clean, no action needed:** 2.2 tech stack lock
(no rejected alternatives anywhere in the repo — grepped for Flask,
Django, Postgres, pgvector, Pinecone, Qdrant, Kafka, RabbitMQ, Express,
Celery-before-Phase-9, Apache Tika, Heroku, Podman); all 18 endpoints
present with exact method/path match; `.env.example` matches Blueprint
7.1's required-var table 1:1; no route file imports a DB driver
directly (2.7's single-writer-to-Neo4j rule can't be violated yet
because nothing writes to anything yet); `ServiceUnavailableError`
correctly mapped to Blueprint 2.6's failure table; no non-goal tech
(GraphQL, D3 direct, Prometheus/Grafana, Socket.io, Discord/Notion/
Drive connectors) present anywhere.


## Update 3 — Full re-audit before Docker Compose testing

Requested: start over, check whether anything is misplaced or
forgotten, ahead of actually testing this in `docker-compose`.

**Folder/file completeness — automated, not eyeballed.** Wrote a
script that extracts every path literally named in Blueprint 3.1's
table and checks it exists on disk. Result: 100% present, nothing
missing. (One note: Blueprint 3.1's table itself lists `omnirag/src/`
in its first row, then every subsequent row uses `omnirag/app/` —
this looks like a leftover/typo in the Blueprint, not an instruction
to create a second parallel source root. Building a `src/` folder
alongside `app/` would just create two conflicting Python roots when
`pyproject.toml` (`packages = ["app"]`) and the Dockerfile
(`COPY app ./app`) both already commit to `app/` being the one real
root. Did not create it; flagging the doc inconsistency instead of
silently resolving it either way.)

**Dockerfile — real Blueprint 5.1 violation, fixed.** The `production`
stage copied its entire venv from a `builder` stage that had installed
`requirements-dev.txt` — meaning pytest, ruff, mypy, pre-commit,
detect-secrets, and pip-audit were all shipping into the production
image. Blueprint 5.1 is explicit: *"Stage 2 (production)... Smaller
production image, no test frameworks or dev tools in production."*
Restructured into `builder` (prod deps only) → `production` (built
from `builder`, never touches dev tools) and a separate `dev-builder`
(layers `requirements-dev.txt` on top of `builder`) → `development`.
`make test`/`make lint` still work via the `development` target in
`docker-compose.yml`, unaffected.

**docker-compose.yml — real bug, fixed.** `NEO4J_AUTH` was hardcoded
to `neo4j/omnirag_password` while `omnirag-api`'s `NEO4J_PASSWORD` env
var was `${NEO4J_PASSWORD:-omnirag_password}` — meaning the moment
anyone sets a custom `NEO4J_PASSWORD` in their `.env`, the API service
picks up the new value but the Neo4j container itself keeps requiring
the old hardcoded one. Guaranteed auth failure on first customization.
Fixed to `neo4j/${NEO4J_PASSWORD:-omnirag_password}` — both sides now
read the same variable.

**Makefile — consistency fix.** `make lint` only ran `ruff check` and
`mypy`, missing the `ruff format --check` step CI now runs, and didn't
cover `conftest.py`. Brought it in line with what CI actually checks.

**Static validation performed (no Docker daemon available in this
sandbox — checked `docker --version`, not installed):**
- `docker-compose.yml` parsed with PyYAML — valid, 5 services match
  Blueprint Phase 1 exactly (mongodb, neo4j, redis, omnirag-api,
  ollama), 4 named volumes.
- Every env var referenced in `docker-compose.yml`'s `omnirag-api`
  block cross-checked against `.env.example` — 1:1 match, no
  orphaned or missing vars.
- Traced the multi-stage `Dockerfile` COPY/FROM chain by hand to
  confirm the `dev-builder`/`development` split still resolves
  `requirements-dev.txt`'s internal `-r requirements.txt` reference
  correctly (the file persists across `FROM builder AS dev-builder`
  since that's a continuation, not a `COPY --from`).

**Known, not fixed — flagged for when Phase 3 lands:** no
`depends_on: condition: service_healthy` / no `healthcheck:` blocks on
mongodb/neo4j/redis/ollama. Not urgent *yet* — nothing in this Phase 2
codebase actually opens a DB connection on startup, so there's nothing
to race against today. It will matter the moment Phase 3 adds real
`neo4j`/`motor`/`redis-py` clients that connect at startup, since
Neo4j in particular takes real time to accept Bolt connections after
container start.

**This round's tooling limitation, stated plainly:** I do not have a
Docker daemon in this environment, so none of the above was verified
by an actual `docker compose up` — only by parsing the YAML, reading
the Dockerfile stage-by-stage, and cross-referencing files. The actual
boot test — do all 5 containers reach a running state, does
`curl localhost:3001/api/v1/health` return 200 from *inside* a real
container network — has to happen on your machine or CI, not here.

## Update 4 — Independent verification of prior claims, on request

Requested: re-check the claims from Updates 1–3 rather than take them
on trust. Result: five confirmed, one contradicted, one fixed.

**Confirmed true, re-verified independently:**
- `fastapi==0.139.2` / `starlette==1.3.1` — real PyPI releases,
  confirmed with a direct HTTP 200 against `pypi.org`'s JSON API for
  both, not inferred from a prior successful `pip install`.
- CVE identifiers — I never cited CVE numbers, only PYSEC IDs.
  Checked pip-audit's own `aliases` field: `CVE-2026-48710` and
  `CVE-2026-54282` are real, confirmed aliases of `PYSEC-2026-161` and
  `PYSEC-2026-248` (both starlette 0.41.3). Not fabricated.
- The 404/405 envelope bug and its fix — re-reproduced live against
  the original `final` copy: bare `{"detail": "Not Found"}`, no
  envelope. Confirmed absent in the current build.
- `/health` → `/api/v1/health` — confirmed as the real, previously
  undisclosed deviation it was reported as.
- `install_error_handlers` R-40 fix — re-confirmed via the same AST
  line-count sweep; still clean.
- `.secrets.baseline`'s "10 findings, 3 files, stable across a rescan"
  — reproduced, with one caveat worth stating plainly: `detect-secrets
  scan` returns **zero results with no error** when run outside a git
  repository — it depends on git to enumerate files. The shipped zip
  correctly excludes `.git`, so a bare `detect-secrets scan` run
  before `git init` will silently under-report. Once `git init` +
  `git add` happens (which `pre-commit install` requires anyway), the
  real 10 findings across `.env.example`, `conftest.py`, and
  `docs/OmniRAG-Blueprint-v2.md` reappear exactly as reported. Not a
  new bug — a tool behavior worth knowing before trusting a "clean"
  scan result.

**Contradicted — the "lazy get_settings(), not a regression" claim was
wrong.** Tested both original `config.py` files directly: bare
`import app.config` with zero environment variables. `final`'s lazy
version: no crash. `best-merged`'s eager version
(`settings = get_settings()` at module scope): raises a `pydantic`
`ValidationError` listing every missing required field, immediately,
on import alone — reproduced fresh, not from memory. The original
finding stands as a genuine, structural difference between the two
source zips, not a restatement of something that was already fine in
both.

**Genuinely missed, now fixed:** two leftover unprefixed `/health`
mentions in `README.md` (lines describing the health endpoint and the
Phase 3 follow-up), inconsistent with the corrected curl example three
lines below them in the same file. I had dismissed this as "harmless
shorthand" when I made the original path fix — that was too quick;
inconsistent path references in the same document are exactly the
kind of thing that erodes trust in the rest of the docs. Fixed both.





- Every `entity_resolution/`, `graph/`, `retrieval/`, `agents/`,
  `intelligence/` module is still a 1-line docstring stub. Phases 3–12
  of the Blueprint (Execution Blueprint, Part 04) are entirely
  unbuilt — database layer, entity resolution, retrieval, agents,
  intelligence features, deployment, demo prep. This build is Phase 2
  complete, nothing more.
- JWT enforcement / `401` on invalid tokens — Phase 4 scope.
- Rate limiting (`slowapi`) — documented in the Blueprint, not
  enforced — Phase 4 scope.
- Real database connectivity in `/health` and repositories — Phase 3.
- Docker Compose has not been booted against a real daemon in this
  environment (no Docker available in this sandbox) — validated by
  parsing the YAML and tracing the Dockerfile stage-by-stage (see
  Update 3), not by an actual `docker compose up`.
- This has not run inside real GitHub Actions — only reproduced
  locally via a wiped environment to approximate a clean CI runner.

---

## 2026-08-08 — Post-Phase-3 local verification: mongot replaced, remaining TestClient converted

**Decision — MongoDB local vector search: `mongodb-community-server` +
standalone `mongot` sidecar → `mongodb/mongodb-atlas-local`**

The two-container wiring locked in the "MongoDB Vector Search (local
dev)" decision above (`mongodb-community-server:8.2` +
`mongodb-community-search:0.64.0`, manually pointed at each other via
`--setParameter searchIndexManagementHostAndPort` and a shared
`/etc/mongot/secrets/passwordFile`) never got past mongot's own
startup checks in practice:

1. mongot's strict Unix permission check on the password file
   (owner-read-only) cannot be satisfied by a Windows bind-mount —
   Docker Desktop's WSL2/Hyper-V translation layer does not preserve
   `chmod` bits from the host, so mongot always sees the file as "too
   permissive" regardless of what permissions are set on Windows.
2. Even setting that aside, the wiring never configured an actual
   auth user between mongod and mongot — the password file existed
   as a bind-mounted secret but nothing on the mongod side was set up
   to authenticate against it.

Replaced with `mongodb/mongodb-atlas-local:latest` — MongoDB's own
official single-container image for local dev, bundling `mongod` +
`mongot` + the runner process that wires the two together internally,
with no manual sync-source config or credential file needed. Same
`$vectorSearch` capability as the sidecar approach. Services dropped
from 6 to 5 in `docker-compose.yml` (the standalone `mongot`
container and `mongot_data` volume are gone).

**Rejected**: continuing to debug the sidecar wiring (the underlying
Windows permission-translation issue has no host-side fix — this
isn't specific to this project's config, it is a documented class of
problem with bind-mounting Unix-permission-strict secrets through
Docker Desktop on Windows). Reverting to Atlas-only (no local vector
search) was also considered and rejected — local `$vectorSearch` is a
real capability worth keeping, `mongodb-atlas-local` gets it without
the sidecar's operational fragility.

This is a deviation from Blueprint 2.2/2.3's locked stack line
("MongoDB Atlas Vector Search... Community 8.2 local sidecar") —
logged here per Rule R-68. The `docker-compose.yml` code comment on
the `mongodb` service instructed logging this and was not followed up
on until this entry; flagging that gap itself, since Rule R-76 is
explicit that the Journal/CHANGELOG must be updated the same session,
not reconstructed later from a comment that says "remember to write
this down."

**Verified**: `docker compose up -d` — all 5 services reach a running
state fresh (`mongodb` and `neo4j` report Docker healthcheck
`healthy`) on a clean pull with no prior local state. Confirmed on a
second machine (different Windows laptop, fresh `docker compose pull`
+ `up`), not just the original dev machine.

**Fixed — `app/test_health.py`: last remaining sync `TestClient`
usage converted to `httpx.AsyncClient`/`ASGITransport`**

The three `tests/test_phase3_integration_*.py` files were converted
from Starlette's sync `TestClient` to async `AsyncClient` earlier this
phase (to fix a real event-loop collision under session-scoped
pytest-asyncio fixtures — see the Phase 3 integration-test entries
above). `app/test_health.py` was missed in that pass — it's a
mock-based unit test file with no real database driver involved, so
it never hit the same event-loop *collision* bug, but it kept emitting
`StarletteDeprecationWarning: Using httpx with starlette.testclient is
deprecated; install httpx2 instead` on every run.

Converted all 15 test functions from sync `def` to `async def`
(2 helper/count-only tests that never touch the client stayed sync),
replaced the `_client() -> TestClient` helper with an async
context-manager version yielding `httpx.AsyncClient` against
`ASGITransport`, and rewrote every call site from `_client().get(...)`
to `async with _client() as client: await client.get(...)`.

**Verified**: assertion count (66) and test function count (17)
identical before and after the rewrite — nothing dropped in the
conversion. `ruff check`/`ruff format --check` clean. `mypy` strict
clean. All 29 collected tests (17 named + 13 parametrized cases from
`test_every_stub_endpoint_returns_standard_501_envelope`) pass. Ran
with `-W error::DeprecationWarning` to force any remaining deprecation
warning to fail the run — passed clean, confirming the warning is
actually gone rather than just not printed. Full non-integration suite
(`pytest -m "not integration"`) still passes at 108/108 after the
change, confirming no interaction with the shared `conftest.py`
session-scoped event loop fixture.

**Still outstanding**: CI has not been exercised against real GitHub
Actions — the `integration-tests` job (mongo/neo4j/redis service
containers) has only been validated by local `docker compose`
runs and YAML parsing, not an actual push. First real push and CI run
is the next step before this phase can be called fully closed.

---

## 2026-08-09 — First live run of `pytest -m integration` inside the running container stack: 2 real bugs found and fixed

Every previous integration-test run in this project's history was
either against a broken/never-fully-up container stack, or run via
`docker compose run --rm omnirag-api pytest ...` (a fresh, separate
container) rather than the actual long-running `omnirag-api` container
started by `docker compose up -d`. This is the first time the suite
ran against a genuinely healthy, fully-up stack — `docker compose ps`
confirmed all 5 services `healthy`/`Started` on a clean
`docker compose up -d --build` with no prior state (Windows laptop,
`mongodb-atlas-local`). Result: 22 passed, 1 skipped (expected — no
mongot sidecar in the atlas-local setup), 8 failed. All 8 traced back
to exactly two root causes.

**Fixed — `conftest.py`: `MONGODB_URI` override was clobbering the
Docker-internal hostname, not just the database name**

The override at the bottom of `conftest.py` existed to force every
test onto an isolated `omnirag_test` database rather than the real
seeded `omnirag` one (correct intent, comment explains it well) — but
it did this by replacing the *entire* `MONGODB_URI` string with a
hardcoded `mongodb://localhost:27017/omnirag_test`, discarding
whatever host `docker-compose.yml` had already set via
`MONGODB_URI: ${MONGODB_URI:-mongodb://mongodb:27017/omnirag?...}`.
`localhost` only resolves to anything when pytest runs on the bare
host; inside the `omnirag-api` container itself (where these tests are
actually meant to run — see the file's own comment), `localhost:27017`
means "port 27017 on this container," which nothing is listening on.
`NEO4J_URI` was never given this treatment (only
`os.environ.setdefault()`, correctly preserving whatever host was
already set) — the asymmetry between the two was the tell.

Fixed to swap only the trailing database-name segment of whatever URI
is already present, preserving host, port, and query string exactly
(e.g. `mongodb://mongodb:27017/omnirag?directConnection=true` becomes
`mongodb://mongodb:27017/omnirag_test?directConnection=true`).

**Verified**: this bug produced `pymongo.errors.ServerSelectionTimeoutError:
localhost:27017: [Errno 111] Connection refused` on every MongoDB-touching
integration test (5 tests), plus 2 further failures once traced through —
`mongodb.verify_connectivity()` returning `False` correctly cascaded
into the real `/api/v1/health` endpoint reporting `mongodb: unhealthy`
and overall `status: "degraded"` (the app's own logic was correct
throughout; it was accurately reporting a real connectivity failure
caused by this bug, not misbehaving).

**Fixed — stale decision-count assertion in
`test_get_decision_history_filters_by_status_against_real_index`**

`assert len(history) == len(DECISIONS)` with the comment "both seed
decisions are active" dates from before this session's earlier
addition of a third, `superseded` Decision node (to exercise the
temporal-reversal code path — see the "reversed Decision +
SUPERSEDES" entry above). `DECISIONS` now has 3 entries, 2 active —
filtering by `status="active"` correctly returns 2, which the stale
assertion read as a failure. Fixed to compare against the actual count
of active seed decisions rather than the total.

**Verified**: `ruff check`/`ruff format --check` clean on both changed
files. `mypy` strict clean. Full `docker compose ps` confirmed 5/5
containers healthy before the fix; the specific failing assertions
(`assert False is True`, `assert 'degraded' == 'starting'`, `assert 2
== 3`, and the 5 `ServerSelectionTimeoutError` tracebacks) map exactly
one-to-one onto these two root causes with no unexplained remainder.
Re-run against the live stack pending confirmation.

---

## 2026-08-09 (same day, continued) — 30/31 integration tests passing live; last skip root-caused and fixed

Re-ran `pytest -m integration` against the live stack after the
`conftest.py` and stale-assertion fixes above: **30 passed, 1 skipped**
— every failure from the previous run is gone. The 1 skip
(`TestMongoVectorSearchIndexAgainstRealServer::test_ensure_vector_search_index_creates_and_is_idempotent`)
was expected in principle (this class's own docstring says it only
runs where real `$vectorSearch` is available) but its skip *message*
was stale, still blaming an unreachable "mongot sidecar" from the
architecture this project no longer uses. Traced the actual swallowed
exception directly (bypassing the test's own broad `except Exception`)
via `docker compose run --rm omnirag-api python -c "..."` and found a
real, different, fixable bug underneath the stale message.

**Fixed — `app/database/mongodb.py`: `ensure_vector_search_index()`
requires the `embeddings` collection to exist before indexing it**

Real error: `pymongo.errors.OperationFailure: ... Collection
'omnirag.embeddings' does not exist ... 'codeName':
'NamespaceNotFound'`. `get_embeddings_collection()` returns a lazy
Python-side handle - referencing `database["embeddings"]` does not
create anything on the MongoDB server until a document is actually
inserted through it. On a fresh database (empty volume, no embeddings
ever written yet - exactly the state right after `docker compose up`
on a clean pull), `create_search_index()` fails outright because the
collection genuinely does not exist server-side yet. Not a
mongot/atlas-local capability problem at all - a real ordering
requirement this function never satisfied.

Fixed by explicitly calling `database.create_collection("embeddings")`
first, wrapped in the same idempotent-catch style already used for the
search index creation immediately below it (PyMongo's
`create_collection` has no `IF NOT EXISTS` equivalent either - it
raises `CollectionInvalid` if the collection is already there, which
is caught and logged rather than treated as an error).

Also updated the stale docstring and skip message on
`TestMongoVectorSearchIndexAgainstRealServer` (tests/test_phase3_integration_infra.py)
to describe the current `mongodb-atlas-local` architecture instead of
the retired sidecar setup - the class-level skip-on-CI behavior itself
was already correct and unchanged, only the wording was wrong.

---

## 2026-08-09 (same day, continued) — 31/31 integration tests confirmed; CI never actually run until now, two real bugs found in it

The previous entry ended with "expect 31/31... pending confirmation."
Re-ran `pytest -m integration` against the live stack after the
`ensure_vector_search_index()` fix: **31 passed, 0 failed, 0 skipped**
— every integration test in the suite now passes against real
Neo4j/MongoDB/Redis, including the vector-search index test that had
been skipping or failing in every prior run this project has had.

**Verified separately, same session: `pytest -m "not integration"` —
108 passed, 0 failed, no warnings summary at all** (the `httpx2`
warning present in every earlier run of this file is confirmed gone).

**Found — CI (`.github/workflows/ci.yml`) had never actually been run
against real GitHub Actions.** Every prior CHANGELOG entry says this
explicitly ("Still outstanding: CI has not been exercised against real
GitHub Actions"). Reading the file line-by-line before the first real
push surfaced two bugs that only running it live would otherwise have
caught — silently, on a failed push, at the worst possible time:

**Bug 1 — `integration-tests` job's `/health` verification step
imported a module-level `app` that has never existed.**
`from app.main import app` — `app/main.py` uses a `create_app()`
factory pattern; there is no module-level `app` variable, and never
has been. This is the exact same `ImportError` hit and diagnosed
earlier this session when trying to introspect routes directly inside
the container (`docker compose exec omnirag-api python -c "from
app.main import app; ..."`). The CI file was written against the same
wrong assumption and would have failed the `integration-tests` job on
literally the first real push, on a step that has nothing to do with
integration-test correctness — a false-negative CI failure. Fixed:
`from app.main import create_app`, `ASGITransport(app=create_app())`.

**Bug 2 — CI's `integration-tests` job ran `mongo:7`, not
`mongodb/mongodb-atlas-local` — silently untested vector search.**
`docker-compose.yml` has run `mongodb-atlas-local` since the mongot
replacement decision earlier this session; CI's `services:` block was
never updated to match and still pulled plain `mongo:7`, which has no
`$vectorSearch`/mongot capability at all. Nothing in the current test
suite depends on this yet (`TestMongoVectorSearchIndexAgainstRealServer`
skips gracefully when unavailable — see the prior entry's "1 skipped"
note), so this was not failing CI, only silently failing to *cover*
Atlas Vector Search in CI at all. Initially flagged as a known gap and
deliberately deferred (Rule R-68) rather than guessed at, since an
earlier web search suggested `mongodb-atlas-local` might not be
compatible with GitHub Actions' `services:` container contract at all
(bundles its own mongod+mongot+runner startup, unlike a plain
single-process image).

Re-searched properly before deferring further: the incompatibility was
real but time-boxed — a MongoDB image push in Feb 2025 briefly broke
`mongodb-atlas-local` specifically under GitHub Actions' `services:`
health-check polling (container reported permanently "unhealthy" on
Linux runners; worked fine under plain Docker Compose the whole time).
MongoDB's own maintainer confirmed and fixed it the same day on the
community forum (mongodb.com/community/forums/t/mongodb-mongodb-atlas-local-not-working-in-github-actions/311906).
Current images work as an ordinary `services:` container — same shape
as `mongo:7` — image/ports/health-cmd, nothing special. Fixed: swapped
to `mongodb/mongodb-atlas-local:latest`, health check copied verbatim
from `docker-compose.yml`'s own `mongodb` service
(`mongosh --quiet --eval "db.adminCommand('ping').ok"`, 30 retries,
20s start period) so both environments assert identical readiness
semantics rather than two independently-guessed checks.

**Also fixed this session, `app/database/test_database.py` — Mongo
connectivity-failure test was patching an object the code under test
never actually touched.** `test_verify_connectivity_returns_false_on_connection_failure`
did `client = mongodb.get_client(); patch.object(client.admin,
"command", ...)`. `get_client()` genuinely is a correct singleton
(verified: same object on repeated calls) — the bug is one level
deeper. Motor/PyMongo's `client.admin` is a computed property that
constructs a *new* `AsyncIOMotorDatabase` wrapper object on every
access, not a cached attribute (confirmed against Motor's own docs and
source before concluding this, not assumed from the symptom alone).
The test's `client.admin` and `verify_connectivity()`'s internal
`get_client().admin` calls were therefore two different objects; the
patched mock never engaged, `result is False` failed with `assert True
is False`. `app/database/neo4j.py`'s equivalent test never had this
bug — it patches `driver.session` directly, which *is* stable, and
that asymmetry between the two files was the actual tell. Fixed by
patching `get_client()` itself (via `patch.object(mongodb,
"get_client", return_value=mock_client)`) rather than a sub-attribute
of its return value, so every access — inside the test and inside
`verify_connectivity()` — resolves to the same controllable mock.

**Verified**: `ruff check`/`mypy app` strict clean across all changed
files. `pytest -m "not integration"` — 108 passed, 0 failed, 0
warnings, confirmed on two separate fresh working directories (a
mid-session zip and a later "final" zip pulled from the same repo
state) to rule out a fix that only happened to work in one copy.
`docker compose ps` reconfirmed all 5 services healthy on the second
working directory independently, not assumed carried over from the
first. CI fixes themselves have been read and reasoned through
line-by-line but **not yet verified against a real GitHub Actions
run** — that remains the one thing in this file that still says
"pending" honestly: push to `github.com/shagunbhadouria/knowledge-os`
and check the Actions tab is the actual verification step, not this
entry.

**Still outstanding, stated plainly, not glossed over:**
- First real GitHub Actions run — this CHANGELOG has said "CI has
  never been exercised against real GitHub Actions" for two
  consecutive entries now; this entry fixes two bugs that would have
  caused that first real run to fail, but does not itself constitute
  that run. Push, watch the Actions tab, report back what actually
  happens — a green run is the only remaining unverified claim in
  Phase 1–3's entire history.
- Baseline Neo4j query latency: **now actually done**, contradicting
  every earlier entry in this file that marked it blocked pending
  DOC-03. A benchmark script (`app/scripts/benchmark_neo4j.py`) was
  written and run live against the real seeded corpus: fulltext
  concept lookup p50 1.53ms / p95 3.52ms, 1-hop CAUSED traversal p50
  0.89ms / p95 1.53ms (50 runs each, corpus: 3 Concepts/3 Entities/3
  Decisions/5 Sources). The Engineering Journal (DOC-03) itself was
  still never provided to paste this into directly — the numbers
  exist and are verified; the act of writing them into that specific
  document is the user's remaining step, not a blocked one.