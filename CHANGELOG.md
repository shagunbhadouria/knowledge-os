# Merge Log — knowledge-os-best-merged + knowledge-os-final → this build

## mongodb-atlas-local abandoned for local dev — reverted to plain `mongo:7`

Second architecture reversal on the MongoDB service this project has
now made (see the atlas-local entry below for the first). Found this
time through direct, live `docker compose up` testing on the actual
target machine — Windows 11, Docker Desktop with the WSL2 backend —
not through reading documentation or trusting a prior session's
"verified" claim.

**What failed.** `mongodb/mongodb-atlas-local:latest` consistently
failed to start with:

```
{"c":"ACCESS","msg":"Read security file failed","attr":{"error":{
  "code":30,"codeName":"InvalidPath",
  "errmsg":"Error reading file /data/configdb/keyfile: No such file or directory"}}}
{"c":"CONTROL","msg":"Error creating service context",
  "attr":{"error":"Location5579201: Unable to acquire security key[s]"}}
```
followed by a hard panic (`error checking mongod: ... connection
refused`) and container exit code 2. The container gets far enough to
start mongod, run normal WiredTiger/thread-pool startup for several
real seconds, then dies attempting to read a keyfile it never
generated in the first place — this is not a slow-start race; watching
`docker logs -f` live confirmed the read attempt happens well after
mongod had time to write the file, had writing been attempted at all.

**What was ruled out before concluding this is image/host-specific,
not a config mistake:**
- Missing `hostname: mongodb` — MongoDB's own docs list this as
  *Required* for the bundled replica set to function. Added it;
  progress was real (mongod's own log started correctly reporting
  `"host":"mongodb"` and got further into startup) but the keyfile
  failure was identical afterward.
- Missing volumes — MongoDB's official reference `docker-compose.yml`
  mounts `db:/data/db`, `configdb:/data/configdb`, and
  `mongot:/data/mongot`; ours only had `/data/db`. Added all three
  matching named volumes. No change in outcome.
- Stale data from a prior run — confirmed via `docker volume inspect`
  that a `mongodb_data` volume from 2026-08-01 existed and could
  plausibly hold a mismatched keyfile from an earlier attempt. Removed
  it and every related volume (`docker compose down -v` plus manual
  `docker volume rm` on orphans), rebuilt from a verified-fresh empty
  volume. Identical failure, first boot, on data that had never
  existed before.
- A known MongoDB community-forum report
  (community/forums/t/mongodb-atlas-local-error-related-to-volumes-configured/301214)
  describes the identical `errmsg` on the identical image, but only
  after a restart cycle, with the explanation that `/data/configdb`
  being ephemeral (not a named volume) means the keyfile generated on
  first boot is lost on recreation. That does not match our case: ours
  failed on a **first boot**, with `/data/configdb` correctly mounted
  as a named, empty, freshly-created volume. This looks like a
  different or more severe manifestation of the same underlying
  keyfile-generation fragility in this image, and no fix for our exact
  first-boot case was found publicly documented at time of writing.

**Decision: dropped `mongodb-atlas-local`, reverted `mongodb` service
to plain `mongo:7`.** This is a second, real deviation from Blueprint
2.2/2.3's locked stack line ("MongoDB Atlas Vector Search... Community
8.2 local sidecar") — first the two-container mongod+mongot wiring was
dropped for atlas-local, now atlas-local itself is dropped. Plain
`mongo:7` has no bundled `mongot`/Atlas Search process and therefore
none of this keyfile machinery — it started healthy on the first try
with zero special configuration.

**Consequence, not a footnote: local MongoDB Atlas Vector Search
capability is gone as of this change.** Any Phase 7 retrieval work
planned against `MongoDB Atlas Vector Search` (Blueprint 2.2, 8.2) has
no local backing store as currently configured. Options for later,
none chosen yet: (a) retry `mongodb-atlas-local` on a non-Windows /
non-WSL2 host to isolate whether this is a host-specific bug, (b) swap
the vector store per Blueprint 2.2's own rejected-alternatives list
(Qdrant was rejected only for adding "another Docker container,
another connection" — a real but smaller cost than a non-functional
vector store), (c) wait for a newer `mongodb-atlas-local` release and
retest, since the image is new enough (per project notes, first
encountered mid-2026) that this may be an unreported bug rather than a
permanent limitation.

**Also fixed in the same session, logged together since both were
found via the same live-testing pass:**
- `docker-compose.yml`'s `redis` service was hard-coded to publish
  host port `6379:6379`. On this dev machine that collided with an
  unrelated project's Redis container already bound to host 6379,
  causing `docker compose up` to fail with "port is already
  allocated." Remapped to `6380:6379` (container-internal port
  unchanged; `REDIS_URL` env var — `redis://redis:6379/0` — is
  correct as-is since it addresses the container's internal port over
  the Docker network, not the host mapping). This is host-specific
  and may not reproduce on a machine without a colliding service, but
  the remap is harmless either way.
- Confirmed and fixed a `docker-compose.yml` structural bug introduced
  during this session's own editing (not present before tonight): the
  mongodb service's volume mount list was briefly misplaced under
  `ports:` instead of `volumes:` due to a miscounted line-index edit,
  which produced an opaque `invalid proto:` error from `docker compose
  config`/`up` with no line number or field name — traced to a known
  Compose bug class (port-string validation running before the
  YAML section boundary is respected on malformed structure). Fixed by
  moving the volume mount back under the correct key. Worth noting for
  future sessions: `invalid proto:` with no further detail from Compose
  is not necessarily a URL/env-var problem — check for volume/port
  section misplacement first, it's a one-line fix once found but very
  hard to spot by reading the file normally since the YAML still looks
  plausible at a glance.

**Verified independently after all fixes** — `docker compose ps`
showing all 5 containers `healthy`/`Up`, and a direct
`curl http://localhost:3001/api/v1/health` returning the correct
envelope (`mongodb`/`neo4j`/`redis`: `healthy`, `ollama`: `starting` —
expected until Phase 5 wires up real Ollama calls) — not taken from a
container status flag alone, since tonight's session also surfaced a
case where `neo4j` briefly reported `unhealthy` due to the healthcheck
window being shorter than APOC's one-time plugin-install startup cost
on first boot, not any real fault; a `docker compose restart neo4j`
against the now-initialized volume resolved that cleanly. Full
Phase 2/3 test suite has not yet been re-run against this new
`mongo:7` service — do not assume it passes until that happens.

## R-16 cleanup + MONGODB_URI default drift, found by independent audit

External audit (not self-reported — ruff/mypy/pytest run fresh in a
clean venv, file lengths checked with `wc -l`, `.env.example` diffed
against Blueprint 7.1's required-vars table) flagged two real gaps this
CHANGELOG hadn't caught: two files over Rule R-16's 300-line limit, and
`docker-compose.yml`'s `MONGODB_URI` default silently missing
`replicaSet=rs0` while `.env.example`'s copy of the same default had
it.

**R-16 violations.** `app/test_health.py` had grown to 455 lines and
`app/database/test_mongo_repository.py` to 351 — both flew under the
radar because R-17 (tests live next to source) was satisfied and
nobody re-checked R-16 against test files specifically after Phase 2/3
accretion. Split by responsibility, not by line count alone:

- `app/test_health.py` (455 → 66 lines) kept only the three tests that
  actually exercise `GET /health`. The rest moved out:
  - `app/test_route_stubs.py` — Phase 2's 18-endpoint 501-stub coverage
    and the `_STUB_ENDPOINTS` table.
  - `app/test_error_envelope.py` — the generic Rule R-28
    envelope/error-handler seam tests (404/405 on unmatched routes,
    request-id propagation, the `UnauthorizedError`/`TokenExpiredError`
    401 seam tests for Phase 4 to build against). These never belonged
    to "health" specifically; they test middleware every route shares.
  - `app/test_graph_routes_phase3.py` — the Phase-3-made-real routes
    (`/workspace/status`, `/graph/nodes`, `/graph/node/{id}`).
  - `app/testing_support.py` — the shared `api_client()` ASGI-transport
    helper all four files import. Named `testing_support.py`, not
    `test_support.py`, specifically so pytest's `test_*.py` collection
    pattern doesn't try to collect it and report zero tests found in
    it.
- `app/database/test_mongo_repository.py` (351 → 229 lines): its own
  `TestVectorSearchIndex` class was testing `app/database/mongodb.py`
  (`ensure_vector_search_index()`, `list_search_indexes()`), not
  `mongo_repository.py`, despite the file's header docstring claiming
  otherwise. Moved to `app/database/test_mongodb_vector_search.py`, a
  correctly-labeled file. This was a mislabel this CHANGELOG never
  caught, independent of the length rule.

No test logic changed — same assertions, same mocks. Re-ran the full
suite after the split: ruff clean, mypy strict clean on 87 source files
(was 82 — new files, same code), 112 passed / 32 deselected on
`pytest -m "not integration"`, identical to the pre-split count. Repo
max file length is now 290 lines (`app/database/test_database.py`).

**MONGODB_URI drift.** `.env.example` documented
`mongodb://mongodb:27017/omnirag?replicaSet=rs0&directConnection=true`;
`docker-compose.yml`'s inline fallback default
(`${MONGODB_URI:-...}`) had the same string minus `replicaSet=rs0`.
`directConnection=true` makes the driver skip topology discovery
regardless, so this was very unlikely to cause an actual connection
failure against `mongodb-atlas-local`'s internal single-node replica
set — but two files documenting the "same" default while disagreeing
is exactly the kind of unlogged drift that becomes a real bug later
(e.g. if `directConnection=true` is ever removed without someone
checking both files). Made the compose default match `.env.example`
exactly.

## Cross-phase audit: infra provisioning built but never invoked, plus one stale test docstring

User asked for an integrated check across all 3 phases together,
specifically for conflicts between them. Found a real one, distinct
from anything a single-phase pass would surface: `ensure_streams()`
(Redis consumer group + dead-letter stream) and
`ensure_vector_search_index()` (MongoDB Atlas Vector Search index) —
both fully built, tested, and previously reported "Done" in this
CHANGELOG — were **never called by anything runnable**. Not the app's
`_lifespan`, not `make seed`. Only `apply_schema()` (Neo4j) was
actually wired in, via `make seed`. This is a real gap against
Blueprint Phase 3's own deliverable text ("Redis connection confirmed
with PING. Streams and pub/sub channels configured" /
"MongoDB Atlas Vector Search index active") — provable statically
(grep for callers), not something needing Docker to confirm. Earlier
CHANGELOG entries reporting these functions "Done" were accurate about
the function's own correctness, not about whether anything actually
invokes it in a real environment; that distinction wasn't called out
before, so a later reader could reasonably assume "Done" meant "wired
in" too. Correcting that going forward.

**Root cause, once found, was smaller than it first looked:** a
`make migrate` target already existed in the Makefile, already
correctly separated from `make seed`'s demo-data concern (a senior
review of the two options — bundle setup into `make seed`, vs. use the
already-separate `make migrate` — favored keeping them apart, since
staging/prod runs migrations but never runs demo seeding, so bundling
them would make it impossible to provision real infra without also
loading fake data). `make migrate` was just missing `ensure_streams()`
and, more importantly, was never referenced by anything — not README,
not CI, not docker-compose.yml — so nothing actually told a developer
or CI to run it.

**Fixes:**
- `Makefile`: `migrate` target now also calls `ensure_streams()`,
  alongside the `apply_schema()` and `ensure_vector_search_index()`
  it already called.
- `.github/workflows/ci.yml`: `integration-tests` job now runs the
  same three-function provisioning step after services report healthy
  and before `pytest -m integration` runs, so integration tests
  actually exercise provisioned infra by design instead of by
  incidental luck (see below).
- `README.md`: documented `make migrate` as a required first-time
  setup step, run once after `make dev`, before `make seed`. Also
  corrected an unrelated but adjacent stale line in the same section —
  "`make seed` is reserved for Phase 3 and currently fails
  intentionally until the database seed script exists" — which
  stopped being true once Phase 3 was completed several commits ago
  and was never updated.
- `tests/test_phase3_integration_infra.py`: added
  `TestRedisStreamsAgainstRealServer`, the one Phase 3 setup function
  (`ensure_streams()`) with no real-server integration test at all —
  `apply_schema()` and `ensure_vector_search_index()` both already had
  one, each self-contained (calls the function on itself before
  asserting, not dependent on test file/class ordering — verified by
  reading each class, not assumed). Also corrected
  `TestMongoVectorSearchIndexAgainstRealServer`'s docstring, which
  claimed CI runs a plain `mongo:7` service container with no
  vector-search capability — true at some earlier point, no longer
  true since `.github/workflows/ci.yml` was confirmed to run
  `mongodb/mongodb-atlas-local:latest`, identical to
  docker-compose.yml, not `mongo:7`.

**Verified:** `xinfo_groups()`'s return shape (list of dicts with a
`"name"` key) confirmed against redis-py documentation/examples before
writing assertions against it — could not run this new test against a
real Redis in this sandbox, so getting the assumed API shape right
mattered more than usual. `mypy`/`ruff check`/`ruff format --check` on
the modified test file: clean. Pytest collection: the new test
collects correctly (11 tests in the file, up from 10; 32 integration
tests total repo-wide, up from 31). `.github/workflows/ci.yml`
re-parsed with PyYAML after editing to confirm the new step is valid
YAML in the right position (after "Wait for service containers",
before "Pytest (integration)"). Full non-integration suite unaffected:
112 passed, 0 failed. `pre-commit run --all-files`: still 4/4 passing.

## Phase 3 audit — missing test coverage for SUPERSEDES write-ordering found and fixed

User asked for a Phase 3 re-check with the same rigor as the Phase 1/2
passes: verify Cypher syntax against the pinned Neo4j 4.4 manual
specifically (not just "current" docs), verify the injection defenses
in `app/graph/repository.py` with a real payload rather than trust the
code comments, and field-by-field diff every seeded node's properties
against Blueprint 2.3 rather than just check counts.

**Verified, no defect (worth recording since these were genuine open
questions, not assumptions):**
- `schema.py`'s `CREATE FULLTEXT INDEX ... IF NOT EXISTS FOR (n:Label)
  ON EACH [...]`, `CREATE INDEX ... IF NOT EXISTS FOR (n:Label) ON
  (n.prop)`, and `CREATE CONSTRAINT ... REQUIRE n.prop IS UNIQUE` all
  checked directly against `neo4j.com/docs/cypher-manual/4.4/` (the
  exact pinned server version, not "current") — all three forms are
  correct, valid 4.4 syntax, character-for-character.
- `app/graph/repository.py`'s label/key_property interpolation (the
  one place in the whole codebase where an identifier, not a value,
  is put into an f-string Cypher query — necessary because Cypher has
  no parameter syntax for labels/property names): tested live with an
  actual injection payload (`key_property="name}) DETACH DELETE n
  //"`) — correctly rejected with `ValueError` before reaching Neo4j.
  Also tested the same attack at the HTTP boundary via `GET
  /graph/nodes?type=...DETACH DELETE...` — correctly rejected with
  `400 VALIDATION_ERROR` by Pydantic's closed `Literal[NodeLabel]`
  before the request handler even runs. Both layers are real, not
  just documented.
- All 4 seeded node types' properties (Concept, Entity, Decision,
  Source) diffed field-by-field against Blueprint 2.3's node tables,
  programmatically, not spot-checked — zero drift in either direction
  on any of the 4 labels.
- `app/entity_resolution/repository.py` has zero f-string Cypher
  interpolation (fully parameterized throughout) — a prior session's
  notes claimed a specific injection-rejection test existed in this
  module; that claim was checked and found incorrect (no such test
  exists, nor is one needed, since there's no identifier-interpolation
  surface here to test in the first place). Correcting the record
  rather than repeating the inaccurate claim.
- The dead-letter-stream creation pattern in `app/database/redis.py`
  (`XADD` then `XTRIM ... MAXLEN 0` to leave an empty-but-existing
  stream) confirmed against Redis's own documentation as the correct,
  intended technique for this — not an invented workaround.

**Defect found and fixed:** `app/database/seeds/test_seeds.py` tested
that Entities are written before Decisions/Sources (both MATCH an
Entity by name — writing them out of order means the MATCH silently
finds nothing, no exception, and the relationship is just never
created), but nothing tested the equivalent ordering requirement for
`_MERGE_SUPERSEDES`, which MATCHes two Decision nodes by statement and
has the exact same silent-failure risk. The actual code in `run.py`
has always had the correct order (Decisions written on line 145,
SUPERSEDES on line 158) — this was a test-coverage gap, not a live
bug, but it meant a future refactor could silently break the one
relationship this seed's 3rd Decision node exists specifically to
exercise (the temporal-reversal pattern, Blueprint 2.3's most
important design decision per its own text), and nothing would catch
it.

**Fix:** added `test_decisions_written_before_supersedes_links`,
matching the existing ordering test's exact style and reasoning.
**Verified per Rule R-66** ("AI-generated tests must actually fail
when the code is wrong"): deliberately moved the SUPERSEDES-writing
loop before the Decision-writing loop in `run.py`, reran the new test
alone, confirmed it failed with a precise assertion (`9 < 6`), then
reverted `run.py` to its original (correct) state via `git diff`
showing zero changes to that file. Full suite after the revert: 17/17
passed in `test_seeds.py`, 112/112 passed repo-wide (up from 111 —
the one new test), `mypy`/`ruff` clean on the modified file,
`pre-commit run --all-files` still 4/4 passing.

User asked for Phase 1 to be re-checked from scratch after a prior pass
had only verified `mypy app`, `ruff check`, and `ruff format --check`
directly (i.e. the same commands CI runs) — never `pre-commit run
--all-files` itself, which is the actual Phase 1 deliverable ("Pre-commit
hooks — Ruff lint, mypy strict compile, no-secrets scanner"). Running the
real hooks surfaced two defects invisible to every prior check:

**Defect 1 — `.pre-commit-config.yaml`'s mypy hook was missing almost
every runtime dependency.** `additional_dependencies` listed only
`pydantic==2.10.4` and `pydantic-settings==2.7.1` — no `fastapi`,
`starlette`, `neo4j`, `motor`, `redis`, `structlog`, or
`python-multipart`. Pre-commit's mypy hook runs mypy inside its own
isolated virtualenv containing only what's listed there — it does not
inherit `requirements.txt`/`requirements-dev.txt` the way CI's `mypy
app` step does (CI runs `pip install -r requirements-dev.txt` first,
which pulls in `requirements.txt` too, giving mypy real types for
every dependency). Because of this, `pre-commit run --all-files`
reported **62 mypy errors across 14 files** — every FastAPI route
decorator flagged as "Untyped decorator" (FastAPI's own decorator
typing wasn't visible without the `fastapi` package present), plus
attribute-not-found errors on Motor/redis calls. None of these errors
are real; CI's `mypy app` (full deps) has always passed clean, and
still does. But a developer running the hook as intended — before
committing, per the whole point of pre-commit — would see a wall of
alarming failures unrelated to whatever they'd actually changed. That
either trains people to `git commit --no-verify` past a hook that's
correctly catching real issues elsewhere, or wastes time chasing
phantom errors.

**Fix:** `additional_dependencies` now lists the exact same pins as
`requirements.txt`, plus `pytest`/`pytest-asyncio` (needed because
mypy's `packages = ["app"]` scope in `pyproject.toml` includes
`app/test_health.py` and `app/database/test_database.py`, which use
`pytest.mark.asyncio` — CI has these via `requirements-dev.txt`, so
the hook needs them too for parity). Re-running `pre-commit run mypy
--all-files` after the fix: **0 errors** (down from 62).

**Defect 2 — `.secrets.baseline` was stale**, never updated after
`.github/workflows/ci.yml` was added/modified. That workflow sets
`NEO4J_PASSWORD: test-password` as a plain env var for the ephemeral
Neo4j service container GitHub Actions spins up for integration tests
— a fake, non-sensitive value, not a real credential. detect-secrets'
"Secret Keyword" plugin correctly flags any `*_PASSWORD:` assignment
regardless of the value, which is the intended behavior; a human is
supposed to confirm each flagged line is a false positive and record
that in the baseline. That confirmation had never happened for this
file, so `pre-commit run --all-files` failed with "Potential secrets
about to be committed" on every run.

**Fix:** verified the flagged value directly — `sha1sum` of the
literal string `test-password` matches the hash detect-secrets
recorded byte-for-byte, confirming the baseline entry corresponds to
exactly this known-fake value and not some other secret coincidentally
sharing a line number. Regenerated `.secrets.baseline` via
`detect-secrets scan --baseline .secrets.baseline` (never hand-edited —
the file's hashes/line-numbers must come from the tool itself).
Re-running `pre-commit run detect-secrets --all-files`: **passed**.

**Verified this pass:** `pre-commit run --all-files` — **all 4 hooks
pass** (ruff, ruff-format, mypy, detect-secrets), for what appears to
be the first time in this project's history; nothing in prior sessions'
notes recorded ever having run the hooks directly rather than the
underlying commands. Whole-repo `mypy app` (CI's actual command, full
deps): still clean, 82 files, unaffected by this fix since CI was
never the broken path. `pytest -m "not integration"`: still 111
passed, 0 failed, unaffected.

## Stale corpus-size caveat in benchmark_neo4j.py

`app/scripts/benchmark_neo4j.py`'s corpus-size print statement was
hardcoded as "3 Concepts, 3 Entities, **2** Decisions, 5 Sources" —
stale since an earlier session's disclosed deviation added a third
Decision node to `app/database/seeds/data.py` (see the "3 Decision
nodes, not 2" entry further below). Fixed to import `CONCEPTS`,
`ENTITIES`, `DECISIONS`, `SOURCES` from `app.database.seeds.data` and
print `len()` of each directly, so the Journal 5.1 latency-baseline
output can no longer drift out of sync with the actual seed data —
whoever pastes this script's output into the Engineering Journal now
gets the true corpus size automatically, not a number someone typed
once and forgot to update.

**Verified:** `mypy app/scripts/benchmark_neo4j.py --strict` clean.
`ruff check` / `ruff format --check` clean. Confirmed the module
imports without error and the new print statement outputs "3
Concepts, 3 Entities, 3 Decisions, 5 Sources" — matching
`len(CONCEPTS)==3, len(ENTITIES)==3, len(DECISIONS)==3,
len(SOURCES)==5` read directly from `data.py`. Did not run the actual
benchmark queries — no live Neo4j in this sandbox; the fix is to the
static print statement, not to the query-timing logic, which was
already correct.

## Full-repo Phase 1–3 re-audit — 1 real bug found and fixed (previously known, unresolved)

Whole-repo `ruff check`, `ruff format --check`, `mypy app` (strict),
`pip-audit` (both requirement files), and `pytest -m "not integration"`
all run fresh, not re-asserted from a prior session's notes.

**Bug (regression from the `create_collection()` fix in Phase 3):**
`app/database/test_mongo_repository.py::TestVectorSearchIndex` had 3
tests failing — not against a live MongoDB (correctly absent per this
file's own header: "Mocked Motor collection objects — no real MongoDB
in Stage 1 CI"), but with `pymongo.errors.ServerSelectionTimeoutError`
after a 30s connect timeout, meaning they were genuinely reaching the
network. Root cause: `mongodb.ensure_vector_search_index()` calls
`get_database().create_collection("embeddings")` *before* it calls
`get_embeddings_collection()` (needed because `create_search_index()`
requires the collection to exist server-side first, and a fresh
database genuinely doesn't have it yet — see that function's own
docstring). These 3 tests mocked only `get_embeddings_collection()`,
so `get_database()` fell through to a real Motor client on every run.

**Fix:** added `get_database()` mocking (via a shared `_mock_database()`
helper) to all 3 existing tests, and added a 4th
(`test_swallows_collection_already_exists_error`) covering the
`create_collection`-level `CollectionInvalid` idempotency guard, which
none of the original 3 exercised — only the search-index-level
`OperationFailure` guard was covered before.

**Verified:** all 4 tests in `TestVectorSearchIndex` now run in
**0.25s** (down from ~90-120s of network timeout waiting) —
confirms they're now genuinely isolated unit tests, not just passing
by luck. Full non-integration suite: **111 passed, 0 failed** (up
from 107 passed / 3 failed), 31.14s total (down from 122.9s). Whole-repo
`mypy app --strict`: clean, 82 files. Whole-repo `ruff check` /
`ruff format --check`: clean, 88 files. `pip-audit` on both requirement
files: no known vulnerabilities.

## Phase 2 exit-criteria audit — 2 gaps found, both closed

User asked for a line-by-line Phase 2 (Backend Skeleton) audit against
Blueprint 2.4/3.1 and Rules v4, independent of Phase 3's already-verified
state. Found two real gaps; both fixed this pass, verified live rather
than by reading code.

**Gap 1 — undisclosed deviation (Rule R-68 violation).** `GET
/api/v1/health` (`app/shared/health.py`) deliberately does **not**
wrap its response in the standard envelope (`{success, data, error,
meta}`) — it returns `{status, services}` directly, so uptime monitors
and load balancers can parse it without envelope-awareness. That is a
reasonable call, and it was explained in a code comment at the point of
decision — but Rule R-28 states the envelope applies "no exceptions,"
and Blueprint 2.4 lists `/health` in the same endpoint table as the
other 17, with no stated exception. A code comment is not the decision
log; per R-68/R-76 every blueprint deviation belongs here the same
session it's made. This entry is that log entry, written after the
fact for a deviation that predates it — logging it now rather than
leaving it silent.
- **Decision:** keep `/health` unwrapped.
- **Reason:** infra convention (unversioned or minimally-shaped health
  endpoints for probes) outweighs strict envelope consistency for this
  one endpoint; wrapping it would make every existing and future
  uptime-monitor / container-orchestrator health probe need
  envelope-aware parsing for no operational benefit.
- **Scope:** `/api/v1/health` only. No other endpoint deviates from
  the standard envelope.

**Gap 2 — Phase 2 exit criterion "Invalid JWT returns 401
UNAUTHORIZED — never 500" had no test proving it, and no code path
exercises it yet.** Real JWT validation (reading the `Authorization`
header, verifying the token) is explicitly a Phase 4 deliverable
("JWT middleware on all protected routes") per Blueprint Phase 4 —
Phase 2's own deliverables list never mentions JWT. Building real
token verification now would front-run Phase 4's actual work
(Authlib, RS256 keys, Redis-backed refresh tokens) and risk having to
redo it. What Phase 2 *does* own, per its deliverables list, is the
error-handler middleware (`install_error_handlers`, Rule R-28) — the
piece that turns any raised error into the correct envelope+status.
**Resolution:** scoped the fix to what Phase 2 controls. Added
`test_unauthorized_error_returns_401_not_500` and
`test_token_expired_error_returns_401_not_500` to
`app/test_health.py`, each mounting a throwaway route that raises
`UnauthorizedError` / `TokenExpiredError` directly against the same
`install_error_handlers()` wiring `create_app()` uses, and asserting
401 with the correct `error.code`. This proves the seam Phase 2 is
responsible for — when Phase 4 wires real JWT middleware and raises
these same exception classes, the error handler already turns them
into 401, never 500, with zero changes needed on the Phase 4 side.
No JWT-checking production code was added; `UnauthorizedError` and
`TokenExpiredError` already existed in `app/shared/errors.py`
unused by any route.

**Verified this pass:** `pytest app/test_health.py -m "not
integration"` — **31 passed** (29 pre-existing + 2 new), 0 failed.
`mypy app/test_health.py --strict` — clean. `ruff check` / `ruff
format --check` on the modified file — clean. Did not re-run the
Phase 3+ integration suite or whole-repo mypy/ruff — out of scope for
a Phase 2-only audit; scoping this way avoids misattributing any
Phase 3+ issue to Phase 2's exit criteria.

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

## Addendum: mongodb-atlas-local confirmed NOT host-broken — isolated single-container test passes healthy

Follow-up to the "mongodb-atlas-local abandoned for local dev" entry immediately below. That entry concluded the image was unreliable on this specific host (Windows 11 / Docker Desktop / WSL2) after three separate fix attempts inside our `docker-compose.yml` all reproduced the identical keyfile failure. That conclusion was too broad and is now corrected.

**Test performed:** ran the image standalone, with none of our compose file's configuration, exactly matching MongoDB's own bare quickstart:

No `hostname:`, no named volumes, no `depends_on`, no other services on the same Docker network. Result: `Up 10 minutes (healthy)`, confirmed via `docker ps` and `docker logs`, with no keyfile error at any point. The image itself is not broken on this host.

**Revised conclusion:** the keyfile failure was triggered by something specific to our `docker-compose.yml` configuration — most likely candidate is the custom `hostname: mongodb` directive we added per MongoDB's own "Required" guidance (never tested in isolation on its own, only ever stacked together with volumes, `depends_on` health-condition chains, and other services on the same network), though this was not conclusively isolated before the session ended. Other candidates not yet ruled out: interaction with the `depends_on: condition: service_healthy` graph from other services, or the specific combination of all four documented-required volumes together rather than individually.

**Updated next step for DEBT-007 (see Blueprint 7.3):** before retrying `mongodb-atlas-local` on a different host, first retry it *inside* `docker-compose.yml` but changed one variable at a time against this now-confirmed-working baseline — starting with removing `hostname: mongodb` and re-testing, since that is the most-suspected untested variable. If compose-level integration succeeds with that removed, the `mongo:7` reversion in this build was avoidable and should be revisited. `mongo:7` remains the working local default until this is retested — do not switch back without re-running the full integration suite (`pytest -m integration`, expect 31 passed / 1 skipped) against whatever configuration is tried.