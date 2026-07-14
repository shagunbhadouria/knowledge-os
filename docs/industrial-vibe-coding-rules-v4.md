# Industrial Vibe Coding Rules

*Document 01 of 04 — Paste into every AI session*

Every rule, constraint, and principle for giving any AI a production-grade project. With the reason behind each one. From project foundation to AI/ML safety gates. Copy-paste ready. Enforce without exception.


## 00 — Session Management


### R-01 [Critical] — Every new AI session begins with three mandatory pastes — no exceptions

**Why:** AI has no memory between sessions. Without context, it invents assumptions that compound. By session 4, the architecture drifts from what you needed. Three pastes prevent this entirely. They are not optional even for a "quick fix" session — the fix will contradict your architecture if you skip them.

*Session Opener Template — Copy-Paste at Start of Every Session*

*Paste Block 1: Locked Tech Stack (from Blueprint 2.2)*
```
LOCKED TECH STACK — DO NOT DEVIATE:
Backend:   [value]
Database:  [value]
Cache:     [value]
Auth:      [value]
Frontend:  [value]
Infra:     [value]
CI/CD:     [value]

RULES:
- Do not replace any technology unless I explicitly say so
- Do not introduce new dependencies without asking first
- If a better tool exists, mention it — do not use it without approval
```

*Paste Block 2: Last Session Summary*
```
LAST SESSION SUMMARY:
What was built: [specific — not "worked on auth" but "JWT refresh token rotation with Redis blacklist"]
Decisions made: [decision + reason, one line each]
Current phase: Phase [N] — [Phase name from Blueprint]
Open blockers: [anything unresolved]
Next task: [exact first task for this session]
Blueprint version: v[N]
```

*Paste Block 3: Active Rules (this document header)*
```
These rules apply for this entire session.
Document: Industrial Vibe Coding Rules v4
Do not suggest patterns, libraries, or approaches that violate these rules.
If you are uncertain whether something violates a rule, ask before implementing.
```


### R-02 [New] — End every session with a written summary — not a mental note

**Why:** The session summary is what becomes Paste Block 2 next time. If you skip it, next session starts cold. Takes 3 minutes. Saves 20 minutes of re-orientation. Paste this prompt at the end of every session.

*End-of-Session Prompt — Paste This Before Closing*
```
Summarize this session in the following exact format:

WHAT WAS BUILT:
[Specific — function names, endpoints, components. No vague summaries.]

DECISIONS MADE:
[Decision — Reason — Tradeoff accepted]

CURRENT PHASE:
Phase [N] — [Phase name] — [% complete estimate]

OPEN BLOCKERS:
[Anything unresolved, any question unanswered]

NEXT SESSION FIRST TASK:
[Exact starting point — specific file, function, or feature]

BLUEPRINT DEVIATIONS THIS SESSION:
[Any divergence from the plan — or write NONE]
```


### R-03 [New] — Switching AI tools mid-project requires a full context dump — not just a summary

**Why:** Switching from one AI to another mid-project (e.g., Claude → ChatGPT → Gemini) is the highest-risk session transition. The new AI has zero context and will confidently invent architecture that contradicts everything built. A full context dump prevents this.

*AI Handoff Context Dump — Use When Switching AI Tools*
```
I am switching AI assistants mid-project. You are inheriting an active codebase.
Read everything below before writing a single line of code.

PROJECT: [Name] — [One-line description]
CURRENT PHASE: Phase [N] — [Phase name]
BLUEPRINT VERSION: v[N]

LOCKED TECH STACK:
[Paste full stack lock]

WHAT HAS BEEN BUILT (do not rebuild or refactor):
[List every completed module, file, endpoint]

ARCHITECTURE DECISIONS ALREADY MADE (do not override):
[List key decisions with reasons]

WHAT I NEED FROM YOU THIS SESSION:
[Exact task]

RULES GOVERNING THIS PROJECT:
[Paste Industrial Vibe Coding Rules header or full doc]

DO NOT:
- Suggest switching any technology in the locked stack
- Refactor code outside the scope of the current task
- Add dependencies without asking
- Implement placeholder logic — every function must be complete
```


## 01 — Project Foundation


### R-04 [Critical] — Always write a project blueprint first — goal, non-goals, users, constraints, success criteria

**Why:** An AI without context invents its own assumptions — and those compound. By session 5, the architecture has drifted from what you needed. A blueprint anchors every decision. The canonical format is the Engineering Master Blueprint (Doc-02). Use that. This template is a quick-start only.

**❌ Weak fill — fails the quality gate**
```
Project Name: My App
Goal: Build a good app that users like
Target Users: People who need this
Success Criteria: App works well
```

**✓ Strong fill — passes the quality gate**
```
Project Name: Deployguard
Goal: Detect high-risk deployments before they execute using ML-scored risk signals from git history, time-of-day, change volume, and reviewer count.
Target Users: Backend engineers at 50–500 person companies with CI/CD pipelines
Non-Goals: No manual deployment approval UI, no Jira integration, no mobile app
Success Criteria: Risk score computed in < 200ms p95, false positive rate < 8%, deployed to 3 internal teams within 60 days
Failure Criteria: Team bypasses it on > 20% of deploys because it cries wolf too often
Scaling: 500 concurrent CI jobs, 10M deployment records
```

*Blueprint Quick-Start Template*
```
Project Name: [Name]
Goal: [What this does — 1-2 sentences. No solution language, just the problem + outcome.]
Primary Focus: [Backend / Frontend / DevOps / Full-stack]
Target Users: [Specific — not "people" but "backend engineers at mid-size companies"]
Non-Goals: No [X], No [Y], No overengineering, No [Z]
Success Criteria: [Measurable — must have a number attached]
Failure Criteria: [What would make this a failure — be honest]
Scaling Expectations: [Specific numbers — users, requests/sec, records]
Deployment Target: [Docker / AWS / Vercel / etc.]
Maintainability: [Who maintains this, what skill level]
```


### R-05 — Define non-goals explicitly — what you're NOT building is as important as what you are

**Why:** AIs add features you never asked for — enterprise abstractions, microservices when a monolith was fine, admin dashboards when you just needed an API. Explicitly stating non-goals prevents feature creep from the start. Minimum three non-goals per project.


### R-06 — Never overengineer — match complexity to the problem

**Why:** A CRUD app doesn't need event sourcing. An MVP doesn't need a message queue. AI models default to complex patterns — microservices, CQRS, event sourcing — even for simple projects. Explicitly forbid complexity you don't need.

**❌ Anti-pattern**
```
// Generating factory patterns, strategy patterns, abstract base classes
// for something that could be a 40-line function
```


### R-07 [Critical] — No placeholder logic unless explicitly marked — every function must be complete and runnable

**Why:** AI often generates pass, // TODO: implement, or return null — which looks complete but silently fails at runtime. Every output must be complete and runnable. If the AI doesn't know how to implement something, it must say so explicitly — never leave silent stubs.

**❌ Silent stub — fails at runtime**
```
def send_email(to, subject, body):
    # TODO: implement
    pass  # silently does nothing
```

**✓ Complete or honest**
```
def send_email(to, subject, body):
    # Requires SENDGRID_API_KEY in env
    sg = sendgrid.SendGridAPIClient(api_key=config.SENDGRID_KEY)
    msg = Mail(to_emails=to, subject=subject, plain_text_content=body)
    return sg.send(msg)  # raises on failure — caller handles
```


### R-08 — Every decision must have a reason — approach, dependencies, tradeoffs — before implementing

**Why:** You own the codebase, not the AI. If you can't explain why Redis was chosen over a DB for this use case, you'll be lost when something breaks. Requiring reasoning before implementation forces deliberate choices. Add to every blueprint: "Before implementing any module, explain your approach, the dependencies required, and the tradeoffs vs alternatives."


### R-09 — Mark all tech debt explicitly — never silently

**Why:** Vibe coding naturally accumulates shortcuts. The key isn't avoiding all shortcuts — it's knowing where they are. A silent shortcut that looks like production code and breaks at scale is not acceptable.

**✓ Explicit tech debt marking**
```
// TECH DEBT: PERF-001 — naive O(n²) scan, replace with index when data > 1000 rows
// TECH DEBT: SEC-003 — rate limiting not implemented, add before public launch
// TECH DEBT: ARCH-007 — service coupling here, extract to event when team > 3
```


## 02 — Tech Stack Lock


### R-10 [Critical] — Define and lock the full tech stack upfront — every layer, decided and fixed before coding starts

**Why:** Without a locked stack, each session subtly introduces new libraries, alternative frameworks, or contradictory patterns. A stack lock document pasted into every new session forces the AI to work within your world, not its defaults.

*Stack Lock Template — Paste in Every Session*
```
LOCKED TECH STACK — DO NOT DEVIATE:
Backend:   [e.g. Python FastAPI]
Database:  [e.g. PostgreSQL + SQLAlchemy ORM]
Cache:     [e.g. Redis]
Auth:      [e.g. JWT with python-jose]
Queue:     [e.g. Celery + Redis]
Storage:   [e.g. AWS S3 via boto3]
Infra:     [e.g. Docker + Docker Compose]
CI/CD:     [e.g. GitHub Actions]
Cloud:     [e.g. AWS ECS]
Frontend:  [e.g. React + TypeScript + Tailwind]

RULES:
- Do not replace any technology unless I explicitly ask
- Do not introduce new dependencies without asking first
- Always remain compatible with existing architecture
- If a better tool exists, mention it — do not use it without approval
```


### R-11 — No new dependencies without approval — every package must be justified

**Why:** Each dependency is a security surface, a potential breaking change, and something someone must understand. Require justification: what does this add, can it be done with existing tools, what is the maintenance cost?


### R-12 — Avoid vendor lock-in unless it's a deliberate tradeoff — wrap vendor APIs in lib/

**Why:** If your payments flow uses Stripe-specific objects across 20 files, switching providers means rewriting 20 files. A thin wrapper in lib/payments.ts means the change is one file.


### R-13 — Container-first from day one — everything runs in Docker, no "works on my machine"

**Why:** Code that only runs with your exact OS version and local config is not production code. Docker from day one means identical environments across dev/staging/prod and easy onboarding. Exception: Rule 03's complexity constraint applies — a 2-day script does not need Docker.


### R-14 — Preserve backward compatibility — new modules must not break existing ones

**Why:** AI frequently rewrites things it shouldn't. A new auth module that changes the User model schema breaks every module that uses User. Explicitly state: "preserve backward compatibility" and "do not rewrite unrelated code."


## 03 — File & Folder Structure


### R-15 — Feature-based folder structure, not type-based — group by domain, not by file type

**Why:** Type-based structures (all models/ together, all views/ together) force you to navigate 4 folders to understand one feature. Feature-based structures (auth/, payments/, notifications/) keep everything related together. When you delete a feature, you delete one folder.

**❌ Type-based — navigational hell**
```
src/
  models/user.py  models/payment.py  models/order.py
  views/user.py   views/payment.py
  services/user.py services/payment.py
```

**✓ Feature-based — one folder per domain**
```
src/
  auth/         # model, service, router, tests — all here
  payments/     # model, service, router, tests — all here
  shared/       # truly shared utilities only
  core/         # app config, db init, middleware
```


### R-16 — No file longer than 300 lines — split when it grows

**Why:** Long files are a signal that one file is doing multiple jobs. AI loses context on long files and starts inventing. 300 lines is a hard limit, not a suggestion.


### R-17 — Test files live next to source files — not in a separate test/ directory

**Why:** A separate test/ directory means tests are always "somewhere else." Co-located tests (auth/test_auth.py next to auth/service.py) make it impossible to forget to write them.


### R-18 — No barrel files that re-export everything — explicit imports only

**Why:** Barrel files (index.ts that re-exports everything) create circular dependency nightmares and make tree-shaking unreliable. Import directly from the source file.


### R-19 — Config and secrets never hardcoded — always in environment variables

**Why:** Hardcoded config gets committed to git, duplicated across files, and becomes a security incident. Every config value lives in .env. Every new env var gets added to .env.example immediately.


### R-20 — Generated files are never committed — add them to .gitignore immediately

**Why:** Generated files (build/, dist/, __pycache__/, node_modules/) in git inflate repo size, cause conflicts, and create false diffs. Add to .gitignore before the first commit.


### R-21 — README is mandatory — setup in under 10 minutes or the README has failed

**Why:** A README that requires tribal knowledge is not a README. If a developer not on the project cannot run it from scratch in under 10 minutes using only the README, the README needs rewriting.


## 04 — Styling Rules


### R-22 — One styling approach per project — locked in Phase 0, never mixed

**Why:** Mixing CSS modules with Tailwind with styled-components in one project produces unmaintainable code. Pick one approach and enforce it. AI will default to whatever it last saw — be explicit.


### R-23 — Design tokens live in one file — never hardcoded values in component files

**Why:** Color: #1a1a1a scattered across 40 files makes a rebrand a grep-and-pray operation. All tokens in tokens.ts or variables.css. Components reference tokens. Never raw values.


### R-24 — No inline styles on production components — extract to class or token

**Why:** Inline styles cannot be themed, cannot be overridden, cannot be linted. They are acceptable in prototypes. They are not acceptable in production code.


### R-25 — Component variants use data attributes or class modifiers — never inline conditional logic

**Why:** style={{ color: isError ? 'red' : 'black' }} leaks business logic into presentation. Use data-variant="error" and handle in CSS. Keeps components predictable.


### R-26 — Responsive breakpoints are defined once — in the token file, referenced everywhere

**Why:** Magic numbers like @media (max-width: 768px) scattered across files become inconsistent. One source for breakpoints. Always.


## 05 — API & Routing


### R-27 [Critical] — API contracts are defined and locked in Phase 0 — before any frontend or consumer touches them

**Why:** A contract change after integration means rewriting both sides. Lock contracts first. Build to them. Never let the implementation define the contract.


### R-28 — Every endpoint has a standard response envelope — no exceptions

**Why:** Inconsistent response shapes mean every consumer writes different parsing logic. One envelope. One contract. Always the same shape whether success or error.

**✓ Standard envelope — every response**
```
{ "success": true,  "data": { ... },      "error": null,    "meta": { "version": "v1", "request_id": "..." } }
{ "success": false, "data": null,          "error": { "code": "VALIDATION_ERROR", "message": "...", "fields": [...] }, "meta": {...} }
```


### R-29 — All APIs are versioned from day one — /v1/ in the URL, never removed

**Why:** Unversioned APIs cannot be changed without breaking consumers. /v1/ costs nothing to add now and saves complete rewrites later. Breaking change protocol: deprecation header → 30-day notice → sunset.


### R-30 — Every endpoint has documented error codes — not just 500 Internal Server Error

**Why:** Generic 500s tell consumers nothing. VALIDATION_ERROR, RATE_LIMIT_EXCEEDED, TOKEN_EXPIRED are actionable. Generic 500 is a debugging nightmare.


### R-31 — Input validation happens at the boundary — never deep in the service layer

**Why:** Validation at the boundary (route handler or controller) catches bad data before it touches business logic. Validation deep in the service layer means invalid data can partially execute before failing.


### R-32 — Rate limiting is documented in the API contract — not added as an afterthought

**Why:** Rate limits that aren't in the API contract will surprise consumers when they hit them. Document the limit (100 req/min), the response (429 with Retry-After header), and the reset window upfront.


## 06 — Types, Constants & Config


### R-33 — All shared types live in types/ — never duplicated across files

**Why:** Duplicate type definitions diverge. UserType in auth/types.ts and UserType in payments/types.ts will eventually conflict. One source. Import from it.


### R-34 — Magic numbers are named constants — never raw numbers in business logic

**Why:** if (retries > 3) tells you nothing. if (retries > MAX_RETRY_ATTEMPTS) is self-documenting, centrally changeable, and testable.


### R-35 — Enums for all categorical values — never raw string comparisons

**Why:** if (status === "active") is a typo waiting to happen. if (status === UserStatus.ACTIVE) is caught by the type checker.


### R-36 — Config is validated on startup — the app fails fast with a clear error if config is wrong

**Why:** An app that starts successfully with missing config fails mysteriously at runtime when it first needs the missing value. Validate all required env vars on startup. Fail fast with: "Missing required env var: SENDGRID_API_KEY"


### R-37 — Feature flags are in config — not in if/else branches scattered through code

**Why:** Feature flags scattered in code become permanent fixtures. A feature flag in config is findable, removable, and togglable without a deploy.


### R-38 — Timeouts and retry counts are config values — never hardcoded

**Why:** Production environments have different latency characteristics than local. A hardcoded 1000ms timeout that works locally will fire constantly in production under load. Make it configurable.


## 07 — Code Quality


### R-39 — Functions do one thing — if you need "and" to describe it, split it

**Why:** validateAndSaveUser() is two functions. A function with two responsibilities has two reasons to change and two places to break. Single responsibility is not a preference — it is how you keep the AI from creating unmaintainable tangles.


### R-40 — No function longer than 50 lines — extract when it grows

**Why:** Long functions are hard to test, hard to reason about, and hard to name accurately. If it takes more than 50 lines, it's doing too much.


### R-41 — Error handling is explicit — never swallow exceptions silently

**Why:** try { ... } catch { } is a lie. It tells the runtime the error doesn't matter. Every catch block either handles the error, logs it, or re-throws it. Silent swallowing creates ghost failures.


### R-42 — Log structured data — not formatted strings

**Why:** logger.info(f"User {user_id} logged in at {time}") is unsearchable. logger.info("user.login", {"user_id": user_id, "time": time}) is queryable, filterable, and alertable.


### R-43 — No console.log in committed code — use the structured logger

**Why:** console.log is a debugging tool, not a logging strategy. It has no levels, no structure, no filtering. It leaks sensitive data. CI must reject it.


### R-44 — Tests are required — not optional, not "to add later"

**Why:** Code without tests is code you cannot safely change. AI-generated code especially benefits from tests — they are the only way to know the AI's output is actually correct.


### R-45 — Tests verify behavior — not that the code ran

**Why:** expect(result).toBeDefined() is not a test. It's a smoke check. Tests verify specific behavior: given this input, produce this output, handle this error, emit this event.


### R-46 — Code review checklist runs before every commit — not just before merge

**Why:** Problems caught at commit cost minutes. Problems caught at merge cost hours. Problems caught in production cost days. The checklist is: no secrets, no console.logs, no TODO stubs, no files outside PR scope, tests pass.


### R-47 — Naming is honest — functions and variables say exactly what they do

**Why:** data, result, temp, thing, handler are meaningless names. deploymentRiskScore, jwtRefreshToken, userAuthorizationResult are names you can grep, understand, and trust.


### R-48 — Dependencies flow downward only — service calls DB, DB does not call service

**Why:** Circular dependencies (A imports B, B imports A) cause mysterious import errors and untestable code. Layers: route → service → repository → database. Never the reverse.


### R-49 — Linting and formatting are automated — not enforced by memory

**Why:** Style discussions in code review are wasted time. Prettier and ESLint / Black and Flake8 handle it. Configure once, enforce in pre-commit hooks and CI.


### R-50 [Critical] — You must be able to explain every line of AI-generated code before merging it

**Why:** This is the most important code quality rule. If you cannot explain what a line does and why, you do not own that code. You are shipping something you don't understand into production. That is how production incidents happen at 3am.


> **⚠ FLAG:** The source HTML has an orphaned rule (`R-NEW` — "Observability standard: define log levels, mandatory fields, and correlation IDs in Blueprint before Phase 1") sitting outside every category `<div>` in the original file, right after Category 07 and before Category 08. Reproduced in full below, but you still need to decide which category it actually belongs in.


### R-NEW [New] — Observability standard: define log levels, mandatory fields, and correlation IDs in Blueprint before Phase 1

**Why:** R-42 says log structured data. R-84 says build observability in. But neither defines what every entry must contain, what log levels mean per environment, or how to trace a request across services. Without a standard, each developer logs differently and logs become unsearchable in production. Define this in Blueprint 2.1 before Phase 1. Every log entry must carry: `timestamp`, `level`, `service`, `correlation_id`, `event`. Correlation IDs must propagate across service boundaries via request headers.

**Log levels — define per environment**
```
DEBUG  → dev only. Never staging or prod.
INFO   → key operations: request in/out, state changes, job start/end.
WARN   → recoverable issues: retry triggered, fallback used.
ERROR  → operation failed: unhandled exception, DB unreachable.
FATAL  → system cannot continue: startup failure.

Prod: INFO minimum. WARN + ERROR → alerting. DEBUG → never.
```

**Mandatory fields on every log entry**
```
logger.info("user.login", {
  "correlation_id": req.headers.get("X-Correlation-ID") or generate_id(),
  "service":        "auth-service",
  "user_id":        user.id,
  "duration_ms":    elapsed,
  "env":            settings.ENV
})
```


## 08 — Security & Secrets


### R-51 [Critical] — Secrets never in code — .env only, .gitignored, .env.example always updated

**Why:** A secret committed to git is permanently compromised — even after deletion, git history preserves it. Zero exceptions.


### R-52 — Passwords are hashed with bcrypt or argon2 — never stored plain or MD5

**Why:** MD5 and SHA1 are broken for passwords. bcrypt and argon2 are slow by design — that's the point. A 10ms bcrypt hash is a 10ms brute force delay per attempt.


### R-53 — JWT tokens have expiry and refresh rotation — never non-expiring tokens

**Why:** A stolen non-expiring token is a permanent backdoor. Short-lived access tokens (15min) + refresh rotation + Redis blacklist limits the breach window.


### R-54 — All user input is validated and sanitized — SQL injection and XSS are never runtime discoveries

**Why:** Use parameterized queries always. Never string concatenation in SQL. Sanitize HTML output. Validate at the boundary (Rule 31). These are not advanced security — they are table stakes.


### R-55 — RBAC is defined in the blueprint before building — not added when you realize you need it

**Why:** Authorization added after the fact means retrofitting every endpoint. Define roles, permissions, and the authorization model in Phase 0. Build to it.


### R-56 — HTTPS everywhere — no exceptions, no HTTP fallback in production

**Why:** HTTP in production exposes tokens, session cookies, and user data to anyone on the network. HSTS headers prevent protocol downgrade attacks.


### R-57 — CORS is explicitly configured — not wildcard in production

**Why:** Access-Control-Allow-Origin: * in production allows any site to make credentialed requests to your API. Enumerate allowed origins explicitly.


### R-58 — Rate limiting is on every public endpoint — not just auth endpoints

**Why:** Scraping, enumeration, and denial-of-service attacks target every endpoint. Rate limiting on auth endpoints alone is insufficient.


### R-59 — Error messages never reveal stack traces or internal paths in production

**Why:** Stack traces reveal file paths, library versions, and code structure. In development they are invaluable. In production they are attack surface. Use generic messages externally, full traces in internal logs only.


### R-60 — Security decisions are ADRs — logged in the Blueprint Decision Register

**Why:** Security decisions (why JWT over sessions, why argon2 over bcrypt) are the decisions most likely to be questioned in audits and interviews. They must be in the Decision Register with explicit reasoning.


## 09 — Anti-Hallucination


### R-61 [Critical] — Verify every library exists before using it — AI invents plausible library names

**Why:** AI confidently invents non-existent npm packages, Python libraries, and API methods. Verify on npm/pypi/official docs before writing import or require statements.


### R-62 — Verify every API method exists in the version you are using

**Why:** AI training data includes deprecated APIs, old versions, and beta features. Check the official docs for the version in your stack lock. "I was trained on older data" is not a production excuse.


### R-63 — Run generated code before trusting it — AI output is a first draft, not production code

**Why:** Syntactically correct code can be logically wrong. Run it. Test it. Edge cases the AI missed will surface immediately in execution — not in a code review.


### R-64 — Ask the AI to explain its reasoning — confident wrong answers look identical to confident right answers

**Why:** AI confidence and AI accuracy are independent. Asking "why did you choose this approach and what are the alternatives?" forces the AI to expose its reasoning — and exposes when it's guessing.


### R-65 [Critical] — If AI generates infrastructure or deployment code, review it line by line before running

**Why:** A Dockerfile with the wrong base image, a Terraform config that opens port 22 to 0.0.0.0/0, or a GitHub Actions workflow with exposed secrets causes incidents that take hours to diagnose. Infrastructure code demands more scrutiny than application code.


### R-66 — AI-generated tests must actually fail when the code is wrong — verify this

**Why:** AI generates tests that always pass because they test the implementation, not the requirement. Break the code deliberately. If the test still passes, the test is worthless.


### R-67 — Never let AI decide the architecture — you decide, AI implements

**Why:** Architecture decisions belong to you. AI optimizes for plausibility, not for your specific constraints, team, timeline, and maintainability requirements. You use the Blueprint to decide. AI executes the decision.


### R-68 — If AI contradicts a decision in the Blueprint, stop and resolve explicitly — do not let it override silently

**Why:** AI will occasionally suggest something that contradicts the locked architecture. Catching it in the moment costs 2 minutes. Catching it after 3 sessions of code built on the wrong assumption costs days of refactoring.


## 10 — Workflow & Execution


### R-69 [Critical] — One module at a time — complete and test before starting the next

**Why:** Partial implementations of 4 modules simultaneously means 4 untested things that interact in unknown ways. Complete one module: implement, test, review, log in journal. Then the next.


### R-70 — Integration order matters — database before service, service before API, API before frontend

**Why:** Building the frontend before the API contracts are locked means the frontend needs to be rewritten when the API changes. Dependency order: data model → repository → service → API → consumer. Always.


### R-71 — Git commit after every working state — not after every feature

**Why:** Committing only at feature completion means losing hours of work if something goes wrong. Commit every time you have a working state — even if it's incomplete. Branches are free.


### R-72 — Branch naming: type/description — enforced, not optional

**Why:** Unstructured branch names make git history unreadable. Format: feature/jwt-refresh, fix/null-pointer-auth, chore/update-dependencies, refactor/extract-payment-service, perf/cache-user-lookup, test/integration-auth, docs/api-contracts. Max 50 characters.


### R-73 — CI runs on every push — not just on main

**Why:** CI only on main catches problems too late. Run lint, type check, unit tests on every push to every branch. Catch it before it becomes a merge conflict or a broken main.


### R-74 — Deployments to production require a written deploy checklist — not intuition

**Why:** The checklist: all CI passes, migrations tested on staging, rollback procedure documented, monitoring alerts active, team notified. Not intuition. Not "I think it's fine."


### R-75 — Database migrations are versioned and reversible — never manual SQL in production

**Why:** Manual SQL in production is not reproducible, not reviewable, and not rollbackable. Every schema change is a migration file. Every migration file has an up and a down.


### R-76 [Critical] — Update the Engineering Journal every session — not at project end

**Why:** Memory degrades within 48 hours. The debugging process that took 3 hours will be a vague recollection in 2 weeks. The Journal must be updated same-session. It is the source material for the Technical Deep Dive — garbage in, garbage out.


## 11 — Phase, Performance & Definition of Done


### R-77 [Critical] — Phase gate: Phase N cannot begin until Phase N-1 exit criteria are 100% complete

**Why:** Incomplete foundations compound. An untested database schema in Phase 3 becomes a rewrite when the service layer in Phase 4 discovers it can't support the required queries. Phase gates exist to prevent this. They are not bureaucracy — they are the mechanism that keeps the build sequential and coherent.


### R-78 — Definition of Done per feature: 11 criteria, all required

**Why:** Partial DoD is not DoD. A feature is done when all 11 criteria pass.

****
```
Feature DoD — All 11 must be true:
□ Happy path works end-to-end (HTTP → service → DB → response)
□ Edge cases handled (empty, null, max values, invalid input)
□ Failure cases return correct error codes and messages
□ Unit tests for all service-layer functions
□ Integration test for the full feature flow
□ All tests pass in CI (not just locally)
□ Structured logging added to key operations
□ Input validated at the boundary
□ API endpoint matches locked contract from Blueprint 2.4
□ Performance: endpoint meets latency budget (p95 < 200ms unless spec differs)
□ You can explain every line of this feature
```


### R-79 — p95 latency is the performance target — not average latency

**Why:** Average latency hides the worst 5% of your users. p95 = 95% of requests complete within this time. It's the number that determines whether your slowest users have an acceptable experience.


### R-80 — Load test before calling it production-ready — not after the first incident

**Why:** An app that handles 10 req/sec in development may collapse at 50 req/sec in production. Load testing reveals bottlenecks before users find them. Tools: locust (Python), k6 (JS), wrk.


### R-81 — N+1 queries are detected and fixed before merge — not after the DB becomes a bottleneck

**Why:** An N+1 query (one query to get 100 users, then 100 queries to get each user's orders) works fine with 10 records in development. With 10,000 records in production it causes timeouts. Use query analysis tools (Django Debug Toolbar, SQLAlchemy echo) and eager loading.


### R-82 — Every WHERE clause column is indexed — document indexing decisions in Blueprint 2.3

**Why:** A query on an unindexed column does a full table scan. At 1M rows, that's the difference between 2ms and 2000ms. Document every index and the query it serves.


### R-83 — Caching strategy is decided in Phase 0 — not added when the DB is already struggling

**Why:** Retrofitting a cache into an existing system requires invalidation logic, cache poisoning protection, and potential schema changes. Design the caching strategy before building the service layer.


### R-84 — Observability is built in — not bolted on after the first production incident

**Why:** Structured logs, metrics endpoints, and distributed traces cannot be added after the fact without touching every service. They are Phase 8 deliverables (see Blueprint) — not an afterthought.


### R-85 — Rollback plan exists before every deploy — not written after a failed one

**Why:** A rollback plan written under pressure during an incident is a bad rollback plan. Write it before the deploy. Test it on staging. Know the exact commands.


### R-86 — Staging mirrors production — not "close enough"

**Why:** Bugs that only reproduce in production are bugs caused by staging not matching production. Same OS, same Docker base, same env vars (different values), same data volume approximation. "Works on staging" must mean something.


### R-87 — Memory usage is measured — not assumed

**Why:** Memory leaks in production cause gradual degradation that looks like a performance issue. Measure baseline memory at startup and under load. Know your container's limit. Know when you're approaching it.


### R-88 — Async operations that can fail must have a retry strategy and a dead letter queue

**Why:** A background job that silently fails 2% of the time is a data integrity problem you won't notice until a customer reports missing data. Retry with exponential backoff. Dead letter queue for failures that exceed retry limit. Alert on DLQ depth.


### R-89 — Health check endpoints exist — /health returns meaningful status, not just 200 OK

**Why:** A health check that returns 200 while the DB connection pool is exhausted is not a health check. /health must verify: DB connectivity, cache connectivity, queue connectivity, and return each status explicitly.


### R-90 — Documentation is a Phase 11 deliverable — not optional, not "add later"

**Why:** Documentation written after the fact is documentation written from memory. Memory is inaccurate after 2 weeks. Documentation written alongside the code is accurate. Phase 11 exit criteria: a person not on the project can run and understand it from README alone.


### R-91 — Demo prep is Phase 12 — not the hour before the demo

**Why:** A demo with live edge cases, realistic data, a practiced narrative, and a tested backup plan is a different experience from a demo run for the first time in front of an interviewer. Phase 12 in the Blueprint. See Part 6 of the Demo Blueprint.


### R-92 — Security hardening is Phase 9 — not "we'll add it when we're bigger"

**Why:** Security added after the fact requires touching every layer. Phase 9 exit criteria: OWASP checklist complete, secrets audit passed, auth tested with invalid tokens, all inputs validated. These are not advanced security — they are the minimum bar.


## 12 — AI / ML Engineering


### R-93 — Every AI component has a defined role, inputs, outputs, and failure mode before building

**Why:** An LLM call without a defined output contract is a hallucination waiting to happen in production. Document in Blueprint 8.1 before writing the first line of AI code.


### R-94 — Build infrastructure first — AI components plug into a working system, never replace the foundation

**Why:** An AI feature that depends on a broken API, an untested DB, or an unmonitored service will fail in production in ways that make debugging impossible. Foundation first. AI second.


### R-95 — Every AI feature has a non-AI fallback that works before the AI version is built

**Why:** If the LLM API goes down, your system should degrade gracefully — not collapse. Build the rule-based fallback first. Build the AI enhancement second. The fallback is not a prototype — it is a permanent safety net.


### R-96 — LLM calls are logged with inputs, outputs, latency, and cost — every single call

**Why:** Without logging, you cannot debug wrong outputs, cannot track cost, cannot detect drift. Log the full prompt, the full response, the model, the latency, the token count, and the cost estimate. Every call.


### R-97 — RAG quality is measured — Precision@K, faithfulness, hallucination rate — not just tested manually

**Why:** Manual testing catches obvious failures. Systematic metrics catch subtle degradation. Without numbers, "the RAG seems to be working" is not a statement you can defend in production or in an interview.


### R-98 — Synthetic training data requires a documented transition plan — replace with real data after N examples

**Why:** Synthetic data lets you bootstrap when real data is scarce. But a model trained on synthetic data can silently degrade when the real distribution differs. Document: after 50 real examples begin online learning, after 200 retrain from scratch, after 500 retire synthetic data entirely.


### R-99 — Model drift detection is automated — not a manual check

**Why:** Model drift is invisible until it causes failures. Track prediction confidence distribution over a rolling window. Alert automatically when it shifts below threshold. Do not wait for someone to notice.

**✓ Automated drift detection**
```
async def check_model_drift():
    recent = get_predictions(last_30_days)
    mean_conf = mean([p.confidence for p in recent])
    if mean_conf < DRIFT_THRESHOLD:
        await alert("Model drift detected",
            f"Mean confidence: {mean_conf:.2f} (threshold: {DRIFT_THRESHOLD})")
```


### R-100 [Critical] — Autonomous actions require a three-gate safety system — confidence + risk + history

**Why:** A system that auto-executes when confidence > 0.82 will eventually auto-execute a wrong action confidently. Three independent gates: Gate 1 — confidence threshold. Gate 2 — action risk classification (HIGH risk never auto-executes). Gate 3 — historical success count (same action succeeded N+ times). All three must pass. One gate is gameable. Three are not.


### R-101 — Embeddings are generated with one model, one preprocessing pipeline — always

**Why:** Mixing embedding models makes cosine similarity meaningless. Lock the embedding model, tokenization, and preprocessing in one place. Any change requires re-embedding the entire corpus. Treat the embedding model as part of the data schema — changing it is a migration, not a config change.


### R-102 — AI component tests verify behavior — not just that the AI ran

**Why:** Testing that the LLM returned a response is not a test. Test what the system does when the LLM returns high confidence, low confidence, or a malformed response. Mock the LLM. Test every behavior path. The LLM itself is not under test — your system's response to different LLM outputs is.


### R-103 [AI] — MLflow or equivalent experiment tracking is set up before the first model training run

**Why:** A model trained without experiment tracking cannot be reproduced. The hyperparameters, data version, feature set, and evaluation metrics of every run must be recorded. "The model that worked" must be reproducible exactly.


## 13 — Conflict Resolution


### CR-01 [New] — When two rules conflict, the more specific rule wins

**Why:** General rules set defaults. Specific rules override them for a reason. Rule 06 (no overengineering) is general. Rule 13 (container-first) is specific to deployment requirements. Container-first wins — but only for projects where deployment is a requirement. For a 2-day script, Rule 06 applies.

- **Scenario:** Rule 06 (no overengineering) vs Rule 13 (container-first)
- **Resolution:** Rule 13 wins for production-targeted projects. Rule 06 wins for scripts and internal tools.
- **Principle:** More specific rule wins. Context determines specificity.


### CR-02 [New] — When specificity is equal, the rule that protects against the larger downside wins

**Why:** Risk asymmetry matters. A rule that prevents a 3-hour refactor wins over a rule that prevents a 30-minute convenience loss. A rule that prevents a security incident wins over a rule that speeds up development.

> ℹ️ Downside scale (smallest to largest): convenience loss → hours of rework → days of rework → security incident → data loss → production outage. The rule protecting against the larger downside wins.


### CR-03 [Critical] — If still unclear, stop and resolve explicitly — do not let the AI pick

**Why:** The AI will always pick something. It will not flag the conflict. It will make a choice based on its training data defaults, which may not match your constraints at all. Conflicts that aren't explicitly resolved become silent architecture decisions you didn't make.

*Conflict Resolution Template — Log in Blueprint Decision Register*
```
CONFLICT: Rule [X] vs Rule [Y]
CONTEXT: [What I was trying to do when the conflict surfaced]
SPECIFICITY: [Which rule is more specific to this situation]
DOWNSIDE ANALYSIS: [Downside of following Rule X: ... | Downside of following Rule Y: ...]
RESOLUTION: [Rule chosen] — because [reason]
APPLIES TO: [This decision only / This project / All future projects]
LOGGED IN BLUEPRINT: Decision Register — [date]
```

> ⚠️ Warning: A conflict resolution is a decision. Decisions live in the Blueprint Decision Register. If it's not logged, it will be forgotten and re-argued in session 7.
