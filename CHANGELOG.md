# Merge Log — knowledge-os-best-merged + knowledge-os-final → this build

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
