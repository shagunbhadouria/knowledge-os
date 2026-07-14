**OMNIRAG**

Engineering Master Blueprint

*Temporal Knowledge Graph System*

| **Document**  | **Value**                                                                                |
|---------------|------------------------------------------------------------------------------------------|
| Document Type | Engineering Master Blueprint — DOC-02 of 04                                              |
| Project       | OmniRAG v1.0                                                                             |
| Domain        | Knowledge Management / Organizational Memory / RAG Systems                               |
| Tech Domain   | Node.js + TypeScript + Neo4j + MongoDB + Redis + LangGraph.js + Groq                     |
| Status        | Blueprint Freeze — Fill before Phase 1 begins                                            |
| Pairs With    | Vibe Coding Rules (DOC-01) · Engineering Journal (DOC-03) · Technical Deep Dive (DOC-04) |

> *This document defines WHAT you are building and HOW before a single
> line of code is written. Every decision here is a locked contract.
> When an AI tool or your own impulse suggests something different, come
> back here first.*
>
> **Table of Contents**

## Part 01 Product Blueprint

> 1.1 Project Overview
>
> 1.2 Vision, Scope & Non-Goals
>
> 1.3 Competitor Analysis & Market Gap
>
> 1.4 User Personas
>
> 1.5 Goals, Objectives & Success Metrics

## Part 02 Technical Blueprint

> 2.1 Architecture Design
>
> 2.2 Tech Stack — Every Technology with Reason
>
> 2.3 Database Design
>
> 2.4 API Design & Contracts
>
> 2.5 Security Architecture
>
> 2.6 Scalability & Failure Recovery
>
> 2.7 Data Flow Architecture

## Part 03 Engineering Blueprint

> 3.1 Folder Structure
>
> 3.2 Coding Standards & Conventions
>
> 3.3 Git Workflow & Standards

## Part 04 Execution Blueprint — All 13 Phases

> 4.1 Development Philosophy
>
> 4.2 Phase-by-Phase Build Order
>
> 4.3 Weekly Milestone Plan

## Part 05 DevOps & Deployment Blueprint

> 5.1 Docker & Environment Strategy
>
> 5.2 CI/CD Pipeline
>
> 5.3 Infrastructure, Monitoring & Runbook

## Part 06 Demo & Presentation Blueprint

> 6.1 Demo Storyline & Script
>
> 6.2 Demo Environment & Backup Plan
>
> 6.3 Interview Prep

## Part 07 Appendices (Fill During Build)

> 7.1 Environment Variables Reference
>
> 7.2 Decision Log
>
> 7.3 Tech Debt & Future Roadmap
>
> 7.4 Local Setup Guide

## Part 08 AI / ML Blueprint

> 8.1 AI Component Inventory
>
> 8.2 RAG Architecture
>
> 8.3 Model Evaluation Strategy
>
> 8.4 Synthetic Data Strategy
>
> 8.5 Hallucination Guard & Confidence Safety
>
> **PART 01 — Product Blueprint**
>
> **ℹ** *Defines WHAT you are building and WHY. Fill completely before
> Part 2. OmniRAG serves two user groups — students and engineering
> teams — because both face the same underlying problem: knowledge
> fragmented across sources, people, and time that nobody can find or
> connect.*
>
### 1.1 Project Overview

**Project Name**

OmniRAG — Organizational Memory Operating System

**One-Line Tagline**

A temporal knowledge graph that connects everything a team or study
group produces — GitHub activity, Slack decisions, uploaded documents —
into a permanently queryable intelligence layer that never forgets and
never loses context.

> **WHY:** This tagline covers the three sources (GitHub, Slack, files),
> the core technology (temporal knowledge graph), both user groups
> (team, study group), and the key value proposition (never forgets) in
> one sentence. This is your 10-second answer to "what does OmniRAG do?"

**Problem Statement**

> **⚠** *Rule: No solution language. Describe the pain as if OmniRAG
> does not exist. Done when: real pain described, no mention of the
> solution, under 3 sentences.*

Knowledge dies constantly in both study groups and engineering teams. A
decision made in a Slack thread six months ago, an architecture choice
explained in a document nobody saved, a bug fixed by someone who has
since graduated or left — all of it disappears from accessible memory
within weeks. People repeat the same mistakes, rediscover the same
solutions, and spend hours searching for things that were already known.

> **WHY:** This problem statement covers both user groups without naming
> the solution once. Students rediscovering solved problems and
> engineers losing institutional knowledge are the same pain at
> different scales.

**Why This Problem Matters**

For engineering teams, the cost is measurable — new engineers take 3 to
6 months to reach full productivity, and most of that time is spent
learning things that are already documented somewhere inaccessible. For
students, the cost is academic performance and collaboration quality.
Every university study group and every software team has this problem.
Tools like Confluence, Notion, and Google Drive exist but they require
humans to manually organise and tag everything — which never happens
consistently. The gap is a system that connects knowledge automatically,
without manual curation, and makes it queryable in plain language.

**Target Users**

Primary Group A — Engineering teams running software projects. They have
GitHub repositories with years of commit history, Slack channels with
hundreds of decisions buried in threads, and documents scattered across
Google Drive, Notion, and email. Secondary Group A — SREs and backend
engineers who need to find why a decision was made, who made it, and
whether it is still relevant.

Primary Group B — University study groups and individual students. They
upload lecture notes, textbooks, past exam papers, and YouTube
transcripts. They ask questions in plain language and need cited answers
they can trust.

The system works identically for both groups because the underlying
problem is identical — connecting fragmented knowledge into something
queryable. Group A uses the GitHub and Slack connectors more. Group B
uses the file upload connector more.

**Core Goal**

Make every piece of knowledge a team or study group has ever produced
permanently findable, connectable, and queryable — with clear citations,
honest confidence scores, and a record of when things changed and why.

**Why This Matters Now**

RAG systems are being built everywhere but almost all of them are simple
vector search over documents — they find similar text but cannot answer
"why was this decided", "who knows most about this", "has this changed
since last year", or "does this contradict something else". The temporal
knowledge graph approach in OmniRAG represents the next generation of
RAG — causally connected, time-aware, and contradiction-detecting.
Building this as a fresher demonstrates you understand where the field
is going, not just where it has been.

### 1.2 Vision, Scope & Non-Goals

**In Scope — v1 Must Have**

> **ℹ** *These are the features that MUST exist for OmniRAG to work as
> described. Missing any of these breaks the core value proposition.*

- GitHub webhook connector — ingests push events, PR events, issue
  events, and review comments in real time

- Slack Bolt SDK connector — ingests messages, threads, and reactions in
  real time

- Local file upload connector — accepts PDF (via pdf-parse) and DOCX
  (via mammoth) uploads

- Redis Streams ingestion queue — ordered, acknowledged, replayable
  consumer group processing

- Unified event schema normalization — every source converted to the
  same internal format before touching the graph

- Privacy classifier on Ollama locally — sensitive content classified
  before ingestion, never sent to external API

- Three-stage entity resolution — Stage 1 Jaro-Winkler lexical, Stage 2
  Transformers.js embedding similarity, Stage 3 Neo4j graph neighborhood

- Merge undo — every entity merge is a reversible graph event

- Temporal knowledge graph in Neo4j — every node and relationship
  carries valid_from and valid_until timestamps

- Contradiction detection — three typed categories: direct factual,
  temporal, cross-source ownership

- Decision provenance tracking — every decision node carries who made
  it, when, what source, and current status

- Hybrid retrieval — BM25 full-text search parallel with Transformers.js
  vector search, fused via Reciprocal Rank Fusion

- Neo4j graph expansion — top retrieval results expanded 1 to 2 hops to
  find causally connected knowledge

- Temporal filtering — outdated nodes ranked lower for current-state
  queries

- Query-time hallucination guard — every generated claim
  cross-referenced against source nodes before returning

- Graph-derived confidence scoring — source_count, recency,
  contradiction_count, verification_status

- Five-step prompt chain with self-reflection — LLM checks its own
  answer before returning

- LangGraph.js coordinator with three specialist agents — Graph
  Traversal, Causal Inference, Synthesis

- Six named tools for agent tool calling — LLM decides sequence, not
  hardcoded

- Semantic drift detection — compare concept node state at two
  timestamps, narrate what changed

- Knowledge gap detection — repeated unanswered questions, undocumented
  high-traffic concepts

- Expert routing — contribution-weighted expertise scores, not
  self-reported

- Knowledge Transfer Documents — triggered by contributor activity drop,
  compiles full contribution history

- Community verification workflow — AI-generated documents notify top 3
  contributors, require 2 of 3 approvals

- Google OAuth authentication

- react-force-graph knowledge graph visualization with temporal slider

- GitHub Actions CI/CD pipeline

- Render + Vercel deployment

**Out of Scope — v1 Explicitly Not Included**

> **⚠** *Rule R-67: Non-goals listed here are not failures. They are
> honest scope decisions. If an interviewer asks about any of these,
> your answer is: "Deliberately deferred to v2 — the architecture
> supports it but building it in v1 would delay the core graph
> features."*

- Knowledge Spaces multi-tenancy — architecture supports spaceId
  partitioning but not fully built in v1. Single workspace per
  deployment.

- Discord, Notion, Google Drive, email connectors — three sources done
  deeply beats ten sources shallowly

- Socket.io Live Knowledge Rooms — real-time collaborative querying, too
  complex for v1

- GraphQL / Apollo Server — REST is sufficient, GraphQL adds complexity
  without proportional value

- D3.js — replaced by react-force-graph which provides the same
  visualization with far less code

- Prometheus + Grafana — not the core story for OmniRAG unlike
  SentinelAI

- Onboarding Intelligence — overlaps with Knowledge Transfer Documents,
  deferred to v2

- Contribution Graph Analytics dashboard — data is available via query
  endpoints but no dedicated dashboard

- Mobile application

**Long-Term Vision — v2 and Beyond**

v2 adds Knowledge Spaces for multi-tenant team isolation with JWT
space-scoped claims and cross-space entity resolution. Discord and
Notion connectors. Onboarding Intelligence — dependency-ordered concept
paths for new members. Contribution Graph Analytics dashboard showing
single-contributor risk and knowledge orphans. v3 adds enterprise SSO,
Contribution Graph Analytics with risk alerting, and an API for
third-party integrations. The temporal graph schema and module
boundaries are deliberately designed to receive these additions without
structural refactoring.

### 1.3 Competitor Analysis & Market Gap
>
> **ℹ** *OmniRAG is not a Notion competitor or a search tool. The gap it
> fills is the one between "store knowledge" (what Notion, Confluence,
> Google Drive do) and "connect, reason about, and query knowledge
> causally" (what nothing currently does automatically).*

| **Existing Solution**               | **What It Does Well**                                              | **Key Weakness**                                                                                                                                                 | **OmniRAG Advantage**                                                                                                                                                                   |
|-------------------------------------|--------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Notion AI                           | Natural language search over Notion pages, generates summaries     | Only searches Notion — cannot connect GitHub commits, Slack decisions, and documents. No temporal awareness. No causal reasoning. No contradiction detection.    | Connects three sources automatically. Temporal graph knows what was true in 2022 vs now. Finds causal chains no single source contains.                                                 |
| Confluence + Atlassian Intelligence | Enterprise wiki with AI search, integrates with Jira               | Requires manual documentation — humans must write the wiki. Nothing is automatic. No Slack ingestion. No temporal graph.                                         | Automatic ingestion from GitHub and Slack. No manual curation required. Knowledge is extracted from where it actually lives, not where people remember to document it.                  |
| GitHub Copilot / GitHub Search      | Excellent code search, PR and issue search within GitHub           | Siloed within GitHub — cannot connect a GitHub decision to the Slack thread that preceded it or the document that informed it. No cross-source causal reasoning. | Cross-source causal chains — the GitHub PR is connected to the Slack discussion that led to it and the document that justified the technical choice.                                    |
| Google Drive / Docs                 | Document storage and search, collaborative editing                 | Full-text search only — no semantic understanding, no connections between documents, no temporal awareness, no expertise routing.                                | Semantic search with graph expansion — finds related knowledge the query did not explicitly mention. Expert routing identifies who knows most about each topic.                         |
| Guru / Tettra                       | Team knowledge base with verification workflows, Slack integration | Passive systems — humans must create and verify cards manually. No automatic ingestion, no temporal graph, no causal reasoning.                                  | Fully automatic ingestion from GitHub and Slack. Community verification workflow for AI-generated documents mirrors the human verification Guru requires but adds AI-generated content. |
| Perplexity / ChatGPT with files     | General LLM with document upload, good at answering questions      | No persistent memory, no connections between documents across sessions, no temporal awareness, no source graph, no expert routing, no contradiction detection.   | Persistent temporal knowledge graph that grows over time. Every answer cites specific source nodes. Confidence derived from graph properties not LLM self-reporting.                    |

**The Gap OmniRAG Fills**

Every existing tool is either a storage system that humans must curate
(Notion, Confluence, Google Drive) or a retrieval system that finds
similar text without understanding connections (vector search, ChatGPT
with files). The gap is a system that automatically extracts knowledge
from where it actually lives — GitHub, Slack, uploaded files — connects
it causally in a temporal graph, detects when things contradict or
change, and answers questions with citations, honest confidence, and
knowledge of who knows what. No existing tool does all of this
automatically without human curation.

### 1.4 User Personas
>
> **ℹ** *Four personas covering both student and team use cases. Each
> shapes which features matter most and how the demo is framed.*

**Persona 1 — Arjun, Backend Engineer on a 15-person team**

| **Attribute**        | **Detail**                                                                                                                                                                                                                                                                                    |
|----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Role                 | Senior Backend Engineer — owns the payments service, deploys 3-4 times per week, joined the team 8 months ago                                                                                                                                                                                 |
| Pain Points          | Constantly asks why decisions were made and gets "I think someone decided that years ago" as the answer. Spends 30+ minutes per week finding old Slack threads. Has made the same architectural mistake twice because the discussion of why it was wrong lived in a thread that scrolled off. |
| What They Need       | Quick answers to "why was this decided", "who knows most about the auth service", "has this approach been tried before", "what changed in the payments architecture since last year".                                                                                                         |
| How They Use OmniRAG | Connects GitHub and Slack to OmniRAG on day one. Asks questions in the web interface. Gets cited answers with decision provenance. Checks expert routing to find who to ask before writing a Slack message.                                                                                   |

**Persona 2 — Priya, Engineering Manager**

| **Attribute**        | **Detail**                                                                                                                                                                                                         |
|----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Role                 | Engineering Manager — 8 engineers, responsible for knowledge continuity when people leave                                                                                                                          |
| Pain Points          | Every time an engineer leaves, their knowledge walks out with them. Onboarding new engineers takes 3 months of repeated questions. No visibility into which knowledge is dangerously single-contributor.           |
| What They Need       | Knowledge Transfer Documents generated automatically when a contributor goes quiet. Expert routing that identifies who knows what. Gap detection that surfaces undocumented high-traffic concepts.                 |
| How They Use OmniRAG | Monitors the dashboard for Knowledge Transfer Document triggers. Reviews AI-generated documents and approves them in the community verification workflow. Uses expert routing to see knowledge concentration risk. |

**Persona 3 — Divya, Final Year Engineering Student**

| **Attribute**        | **Detail**                                                                                                                                                                                                                                      |
|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Role                 | Final year BTech student — part of a 6-person study group preparing for placements and semester exams                                                                                                                                           |
| Pain Points          | Group members upload notes in different formats to different places. Nobody knows who has the best notes on a topic. Past exam papers are saved in different folders. Asking the group a question means waiting for someone to reply.           |
| What They Need       | Upload all notes, textbooks, and past papers once. Ask questions and get answers with citations. Know who in the group has contributed most on each topic.                                                                                      |
| How They Use OmniRAG | Uploads PDFs and DOCX files. Asks questions like "explain dynamic programming from my notes" or "what questions appeared on last year's OS exam". Gets cited answers. Sees which group member uploaded the most relevant content on each topic. |

**Persona 4 — Rohan, FAANG Interviewer Viewing the Project**

| **Attribute**       | **Detail**                                                                                                                                                                                                                                                                        |
|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Role                | Senior Engineer at a top tech company — interviewing candidates for backend/AI roles                                                                                                                                                                                              |
| Pain Points         | Sees hundreds of RAG projects that are just vector search over a PDF. Wants to see something that shows genuine understanding of distributed systems, graph databases, and production AI engineering.                                                                             |
| What They Need      | A project that demonstrates temporal graph design, multi-stage entity resolution, hybrid retrieval with graph expansion, hallucination guards, and LLM agent architecture — all grounded in a real problem.                                                                       |
| What Impresses Them | Knowledge Transfer Documents triggered by activity patterns (shows product thinking), graph-derived confidence over LLM self-reporting (shows AI safety thinking), temporal validity windows (shows systems design depth), three-stage entity resolution (shows algorithm depth). |

### 1.5 Goals, Objectives & Success Metrics
>
> **⚠** *Every metric has a specific number. "Fast queries" is not a
> metric. "p95 retrieval latency under 200ms" is a metric. These numbers
> become your benchmark targets in phase exit criteria and your honest
> limits in the Technical Deep Dive.*

**Functional Goals**

- Ingest events from GitHub, Slack, and file uploads in real time via
  Redis Streams

- Resolve entity identities across sources automatically without manual
  configuration

- Build and maintain a temporal knowledge graph that survives
  contradictions and reversals

- Answer questions in plain language with cited sources and honest
  confidence scores

- Generate Knowledge Transfer Documents automatically when contributors
  go quiet

- Surface knowledge gaps and route questions to the right expert
  automatically

**Non-Functional Goals**

- Simple queries feel fast — streaming starts within 3 seconds, user
  reads while generating

- System works completely free — no paid APIs, all inference local or
  Groq free tier

- Privacy by default — sensitive content never leaves the machine

- Setup from scratch under 5 minutes using docker-compose up

| **Metric / KPI**                             | **Target**                                                                | **How Measured**                                                            | **Failure If**                                               |
|----------------------------------------------|---------------------------------------------------------------------------|-----------------------------------------------------------------------------|--------------------------------------------------------------|
| Entity resolution latency — all three stages | \< 500ms end-to-end                                                       | Benchmark on 1,000 entity pairs with stopwatch in test suite                | Consistently \> 1 second                                     |
| Hybrid retrieval latency p95                 | \< 200ms                                                                  | Prometheus histogram on retrieval calls (or manual timing if no Prometheus) | p95 \> 500ms under normal load                               |
| Simple query first token from Groq           | \< 3 seconds to first streamed token                                      | Measured in chaos engineering / demo run-through                            | Takes \> 8 seconds before any output appears                 |
| Complex query full answer                    | \< 45 seconds end-to-end                                                  | LangGraph.js coordinator measured on benchmark queries                      | Takes \> 90 seconds consistently                             |
| Knowledge Transfer Doc generation            | \< 60 seconds after trigger                                               | Timed in integration test with synthetic contributor data                   | Takes \> 2 minutes                                           |
| RAG hallucination rate                       | \< 8% — claims rejected by hallucination guard                            | Hallucination guard rejection logs over 100 test queries                    | Above 15% rejection rate consistently                        |
| RAG Precision@3                              | \> 0.70 on 50-query test set                                              | Manual relevance judgment on test queries after graph is populated          | Below 0.50 on test evaluation                                |
| Graph-derived confidence accuracy            | Confidence score correlates with answer correctness \> 0.75 Spearman rank | Manual evaluation on 30 queries comparing confidence to actual correctness  | No meaningful correlation between confidence and correctness |
| Entity resolution precision                  | \< 2% false merge rate on 200-pair adversarial test set                   | Test set of similar-but-different names from realistic data                 | False merge rate \> 5% — wrong people merged together        |
| CI/CD pipeline duration                      | \< 6 minutes push to deployed                                             | GitHub Actions workflow duration logs                                       | Pipeline takes \> 12 minutes                                 |

> **PART 02 — Technical Blueprint**
>
> **⚠** *This is the section you paste into every AI session. Every
> technology choice is locked. If an AI suggests something different,
> stop and resolve it against this document — Rule R-68. OmniRAG is
> Node.js + TypeScript throughout — not Python. If an AI suggests Python
> for any module here, that is wrong.*
>
### 2.1 Architecture Design

**Architecture Type**

Modular Monolith with event-driven ingestion pipeline.

> **WHY:** Single Node.js + Express process organised into feature-based
> modules — ingestion, entity_resolution, graph, retrieval, agents,
> intelligence, auth, websocket. Redis Streams handles all async
> ingestion processing. The API layer stays fast by returning
> immediately and handing heavy work to stream consumers.

**Why Modular Monolith — Not Microservices**

Microservices would mean separate deployable services for ingestion,
entity resolution, the graph API, and the agent pipeline. That adds
service discovery, inter-service JWT validation, distributed tracing,
and network failure handling — each a week of work for a solo developer
with no scaling benefit at this scope. The module boundaries in OmniRAG
are already the correct seams to extract services later if needed. The
ingestion pipeline IS event-driven via Redis Streams because webhook
events from GitHub and Slack genuinely need async processing — but this
is a pattern within the monolith, not a separate service.

> **→** *Interview answer: "I chose a modular monolith because at solo
> developer scope, microservices adds operational complexity — service
> discovery, inter-service auth, distributed tracing — without any
> scaling benefit. The module boundaries are already the right seams for
> future extraction. The event-driven ingestion layer handles the actual
> concurrency problem."*

**Why NOT Pure Event-Driven**

Pure event-driven architecture means every operation is a published
event with subscribers — no direct function calls anywhere. This makes
debugging extremely difficult in a graph-heavy system where you need to
trace multi-hop traversals through a call stack. Event-driven is used
where it solves a real problem: high-volume webhook ingestion that must
not block the API. Everything else uses direct function calls for
debuggability and simplicity.

**High-Level System Flow**

> **ℹ** *This is your "walk me through the architecture" answer.
> Memorise this flow.*

Source event arrives (GitHub webhook, Slack event message, file upload)
→ Express route handler validates and acknowledges immediately under
50ms → Event published to Redis Streams consumer group → Stream consumer
normalises to unified event schema → Privacy classifier runs on Ollama
locally — sensitive content excluded → Entity extraction and three-stage
entity resolution against Neo4j → Resolved event written to Neo4j
temporal graph with validity windows → Embedding generated via
Transformers.js stored in MongoDB Atlas Vector Search → Query arrives at
/api/v1/query → Query complexity classified — simple queries bypass
agent pipeline → Hybrid retrieval: BM25 + vector search + Neo4j graph
expansion, fused via RRF → Agent pipeline: LangGraph.js coordinator
assigns to specialists → Five-step prompt chain with self-reflection →
Generated answer passes through hallucination guard → Claims
cross-referenced against source graph nodes → Confidence score derived
from graph properties → Answer streamed token by token to React frontend
via Server-Sent Events → Decision provenance and citations attached.

**Data Flow — One Query Request**

User types "why did we move away from PostgreSQL" → POST /api/v1/query →
QueryClassifier determines this is a CAUSAL type query → Routes to full
LangGraph.js agent pipeline → Graph Traversal Specialist searches Neo4j
for PostgreSQL-related decision nodes → Causal Inference Specialist
traces what decisions came before and after the PostgreSQL nodes →
Synthesis Specialist assembles findings → Five-step chain: extract
relevant nodes → reason about causal chain → synthesise answer →
self-reflect for gaps → format with citations → Hallucination guard
cross-references each claim → Returns answer: "In Q3 2022, the team
decided to move from PostgreSQL to MongoDB \[Slack thread link, commit
SHA\]. The primary reason cited was schema flexibility for varying event
types \[GitHub PR \#147\]. This was reversed in Q1 2023 for the
analytics module which moved back to PostgreSQL for JOIN performance
\[Decision node, document upload\]." with confidence 0.87.

### 2.2 Tech Stack — Every Technology with Reason
>
> **⚠** *Rule R-68: Tech stack locked here. Every choice has a specific
> reason and a rejected alternative. This table is pasted into every AI
> session. Any AI suggestion contradicting this table requires explicit
> resolution before proceeding.*

| **Layer**           | **Technology**                                                | **Why Chosen — Specific Property**                                                                                                                                                                                                                                                                                                                                                                                                                               | **Alternatives Rejected & Why**                                                                                                                                                                                                                       |
|---------------------|---------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Runtime             | Node.js 20 LTS + TypeScript 5                                 | GitHub Octokit and Slack Bolt SDK are both first-class Node.js libraries built by GitHub and Slack respectively. Webhook handling is Node.js's native strength — async event loop handles high-concurrency webhook streams without threading overhead. TypeScript catches type errors across the graph schema, entity schemas, and API contracts at compile time.                                                                                                | Python — GitHub and Slack SDKs are thinner in Python. Go — no LangChain or LangGraph equivalent. Plain JavaScript — no type safety on graph queries is dangerous.                                                                                     |
| API Framework       | Express 4                                                     | Most widely used Node.js web framework — every interviewer knows it. Middleware pattern is exactly right for the auth → rate limit → validation → route handler chain. No magic.                                                                                                                                                                                                                                                                                 | Fastify — marginally faster but less universal. NestJS — too opinionated, decorator-heavy architecture adds abstraction without value for this scope. Hono — newer, less battle-tested.                                                               |
| Graph Database      | Neo4j (AuraDB free tier)                                      | The entire value of OmniRAG lives in the knowledge graph. Multi-hop traversal — finding entities connected to entities connected to a query result — is O(1) per hop in Neo4j's native graph storage regardless of data volume. In PostgreSQL, the same query requires recursive CTEs that become exponentially slow beyond 2 hops. Relationship types (CAUSED, CONTRADICTS, SUPERSEDES, AUTHORED) are first-class schema elements, not foreign key conventions. | PostgreSQL with recursive CTEs — exponentially slow at 3+ hops, no native graph semantics. MongoDB — no graph traversal at all. Amazon Neptune — costs money, AWS lock-in. ArangoDB — less mature, smaller community.                                 |
| Document Database   | MongoDB Atlas (free tier)                                     | Heterogeneous source schemas — a GitHub push event and a Slack message and a PDF upload have completely different shapes. MongoDB's document model handles this naturally. JSONB in PostgreSQL would work but we already have Neo4j for structured relational queries, so keeping MongoDB for document storage avoids a third database type.                                                                                                                     | PostgreSQL — we already have Neo4j for the graph layer. Two databases (MongoDB + Neo4j) is better than three (PostgreSQL + Neo4j + vector DB). Flat files — no query capability.                                                                      |
| Vector Search       | MongoDB Atlas Vector Search                                   | Hybrid retrieval needs vector similarity search for the embedding stage. MongoDB Atlas Vector Search runs inside the same MongoDB instance already handling document storage — zero extra service, zero extra connection pool. HNSW index for fast approximate nearest neighbour.                                                                                                                                                                                | Pinecone — 4th service to run, vendor lock-in on core retrieval. Qdrant — another Docker container, another connection. Weaviate — too heavy, overkill for this scope. pgvector — would require adding PostgreSQL as a 4th database.                  |
| Cache + Streams     | Redis 7 (Upstash free tier)                                   | Three jobs simultaneously: Redis Streams consumer groups for ordered ingestion queue with replay capability, pub/sub for Server-Sent Events broadcasting to React frontend, and query result cache for frequent queries. One service, three roles.                                                                                                                                                                                                               | Kafka — designed for millions of events per second, overkill and much harder to set up. RabbitMQ — AMQP complexity without benefit at this scale. SQS — AWS lock-in, costs money.                                                                     |
| Embeddings          | Transformers.js (all-MiniLM-L6-v2)                            | Runs entirely in Node.js process — zero Python sidecar, zero API cost, zero network latency, works offline. 384-dimensional embeddings sufficient for entity resolution and hybrid retrieval at this scale. Model loads once on startup, subsequent calls are fast.                                                                                                                                                                                              | OpenAI text-embedding-3-small — API cost at ingestion volume, network latency on every embedding. sentence-transformers Python — requires Python subprocess or sidecar. Cohere Embed — costs money.                                                   |
| LLM Provider        | Groq API (LLaMA 3.1 8B for classification, 70B for reasoning) | Free tier with 500 tokens per second — critical for the five-step prompt chain and Knowledge Transfer Document generation within time targets. Groq's speed is a genuine technical advantage not just a budget choice. 30 req/min and 14,400 req/day free tier is sufficient for portfolio demo.                                                                                                                                                                 | OpenAI GPT-4o — variable latency, costs money. Anthropic Claude — costs money. Ollama for reasoning — too slow for multi-step chains, used only for privacy classifier where speed is not critical.                                                   |
| Local LLM           | Ollama (llama3)                                               | Privacy classifier runs locally — sensitive content never sent to external API. Offline fallback when Groq rate limit hit. Zero cost.                                                                                                                                                                                                                                                                                                                            | Only Groq — single point of failure on external API. Hugging Face Inference API — slower, requires API key.                                                                                                                                           |
| Agent Orchestration | LangGraph.js                                                  | Stateful graph-based coordination — coordinator decides dynamically which specialist to call next based on query type and intermediate results. Handles agent loops (retry when confidence low), conditional branching, and shared state across the five-step prompt chain. LangChain.js is correct for simple linear chains. LangGraph.js is correct when agents make decisions about what to do next.                                                          | LangChain.js sequential chain — fixed order, cannot branch based on what specialists find. AutoGen — less control over tool calling and safety layers. Building from scratch — LangGraph.js handles the state machine correctly, no need to reinvent. |
| File Parsing        | pdf-parse + mammoth                                           | Both are pure npm packages — no Java sidecar, no Docker container, no extra service. pdf-parse handles PDF text extraction. mammoth converts DOCX to clean HTML then to plain text. Both work in the same Node.js process.                                                                                                                                                                                                                                       | Apache Tika — Java sidecar in a Node.js project, adds a service to Docker Compose, complex setup. PDFKit — for creating PDFs not parsing them. Textract AWS — costs money, AWS lock-in.                                                               |
| File Watching       | chokidar                                                      | Cross-platform file system watcher for local file connector. Handles symlinks, macOS FSEvents, Linux inotify, Windows FSEvents. Battle-tested, used by webpack and many major Node.js tools.                                                                                                                                                                                                                                                                     | fs.watch native — known bugs on macOS (misses events), no recursive watching on Linux. Watchman — requires separate installation, overkill.                                                                                                           |
| Auth                | Google OAuth 2.0 + Passport.js + JWT                          | Google OAuth: one button, no password management, no email verification. Passport.js handles the OAuth flow with the Google strategy in ~50 lines. JWT with workspace-scoped claims for contribution tracking and expert routing.                                                                                                                                                                                                                                | Email/password auth — weeks of work for password reset, email verification, rate limiting brute force. Auth0 — costs money. NextAuth — too Next.js specific.                                                                                          |
| Frontend            | React + TypeScript + Tailwind + react-force-graph             | React industry standard. TypeScript for type safety. Tailwind for fast consistent styling. react-force-graph for the temporal knowledge graph visualization — force-directed layout, node click to expand, edge thickness by relationship strength, temporal slider to scrub back in time.                                                                                                                                                                       | Vue — smaller ecosystem. D3.js directly — react-force-graph is D3 under the hood with a React API, much simpler. Cytoscape.js — heavier, more complex API for what is needed here.                                                                    |
| CI/CD               | GitHub Actions                                                | Free for public repos. Native GitHub integration — direct access to commit SHAs, PR metadata, branch names. Every backend interviewer has seen and used GitHub Actions.                                                                                                                                                                                                                                                                                          | CircleCI — costs money. Jenkins — heavyweight, requires its own server. GitLab CI — requires GitLab.                                                                                                                                                  |
| Deployment          | Render (backend) + Vercel (frontend)                          | Both free tiers. Render deploys Docker containers directly. Vercel deploys React with zero config. Both deploy from GitHub on every push.                                                                                                                                                                                                                                                                                                                        | Heroku — removed free tier. Railway — free tier limits. AWS — too complex for portfolio deployment.                                                                                                                                                   |
| Containers          | Docker + Docker Compose                                       | One command starts all 5 services: Node.js API + worker, MongoDB, Neo4j, Redis, Ollama.                                                                                                                                                                                                                                                                                                                                                                          | Podman — less universal. No containers — not reproducible across machines.                                                                                                                                                                            |

### 2.3 Database Design
>
> **⚠** *Rule: Lock before Phase 3 coding begins. The Neo4j schema is
> the hardest part to change later — every entity resolution, retrieval,
> and agent query depends on it. Get it right now.*

**Neo4j — Temporal Knowledge Graph Schema**

> **WHY:** Neo4j is the heart of OmniRAG. Every other database serves
> Neo4j. MongoDB stores raw events and embeddings. Redis caches Neo4j
> query results. All intelligence — entity resolution, causal chains,
> contradiction detection, expert routing — lives in Neo4j.

**Node Labels**

| **Label**     | **What It Represents**                                                                                                           | **Key Properties**                                                                                                                                                                                                                                         | **Created When**                                                                                                 |
|---------------|----------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| Concept       | A topic, technology, system, or idea discussed across sources. e.g. "authentication", "PostgreSQL", "deployment pipeline"        | name: string, aliases: string\[\], valid_from: datetime, valid_until: datetime \| null, confidence_score: float, source_count: int, contradiction_count: int, last_confirmed_at: datetime                                                                  | When entity resolution determines a new concept has been discussed that does not match any existing Concept node |
| Entity        | A person — contributor, author, user. e.g. "Priya Sharma", "ps2024", "priya_s"                                                   | canonical_name: string, known_aliases: string\[\], primary_source: string, contribution_weight: float, expertise_areas: string\[\], last_active_at: datetime, valid_from: datetime                                                                         | When a new contributor identity is first seen and entity resolution cannot merge it with an existing Entity      |
| Decision      | A concrete choice made — architectural, process, or product. e.g. "Move from PostgreSQL to MongoDB", "Use JWT for auth"          | statement: string, decided_at: datetime, decided_by: string (entity id), source_url: string, status: "active"\|"reversed"\|"superseded", reversed_at: datetime \| null, superseded_by: string \| null, valid_from: datetime, valid_until: datetime \| null | When a message or document is classified as DECISION type by the five-type classifier                            |
| Source        | A document, message, commit, or file that contributed knowledge. e.g. "Slack message", "GitHub PR \#147", "lecture_notes_os.pdf" | source_type: "github"\|"slack"\|"file", external_id: string, url: string \| null, author_id: string (entity id), content_preview: string (first 200 chars), ingested_at: datetime, privacy_level: string                                                   | When a new event is ingested and processed through the entity resolution pipeline                                |
| Question      | An unanswered question from Slack or uploaded Q&A. Tracked for knowledge gap detection.                                          | text: string, asked_by: string (entity id), asked_at: datetime, answered: boolean, answer_source_id: string \| null, ask_count: int (how many times asked across all users)                                                                                | When a message is classified as QUESTION type and no SOLUTION linked in the same thread within 24 hours          |
| Contradiction | A detected conflict between two nodes. Created when contradiction detection finds conflicting claims.                            | type: "direct_factual"\|"temporal"\|"cross_source_ownership", description: string, detected_at: datetime, resolved: boolean, resolution_notes: string \| null                                                                                              | When contradiction detection engine identifies conflicting properties across two nodes                           |

**Relationship Types**

| **Relationship** | **Direction**                                    | **Properties**                                                                     | **Meaning**                                                                      |
|------------------|--------------------------------------------------|------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| MENTIONED_IN     | Concept → Source                                 | relevance_score: float, mention_count: int, first_mentioned_at: datetime           | This concept was discussed in this source document or message                    |
| AUTHORED         | Entity → Source                                  | authored_at: datetime, source_type: string                                         | This person created this source document or message                              |
| DECIDED          | Entity → Decision                                | decided_at: datetime, confidence: float                                            | This person made this decision (extracted by classifier)                         |
| CAUSED           | Decision → Concept                               | established_at: datetime, causal_evidence: string, confidence: float               | This decision caused changes to this concept — causal chain link                 |
| SUPERSEDES       | Decision → Decision                              | superseded_at: datetime, reason: string                                            | This newer decision replaces the older one — temporal decision chain             |
| CONTRADICTS      | Concept → Contradiction, Contradiction → Concept | detected_at: datetime, contradiction_type: string                                  | This concept is involved in a detected contradiction                             |
| EXPERTISE_IN     | Entity → Concept                                 | contribution_score: float, last_contribution_at: datetime, contribution_count: int | This entity has contributed knowledge about this concept — drives expert routing |
| REFERENCES       | Source → Source                                  | reference_type: string, established_at: datetime                                   | This source explicitly references another source — cross-document linking        |
| ANSWERS          | Source → Question                                | answered_at: datetime, confidence: float                                           | This source contains an answer to this question — resolves knowledge gap         |
| ALIAS_OF         | Entity → Entity                                  | resolved_at: datetime, resolution_stage: string, merge_confidence: float           | These two entity nodes were resolved to be the same person                       |

**Temporal Validity Rules**

> **ℹ** *This is the most important design decision in the entire
> schema. Every node that can change over time carries valid_from and
> valid_until. This is what makes OmniRAG time-aware.*

When a Decision is reversed: set valid_until on the existing Decision
node to the reversal timestamp. Create a new Decision node with
valid_from at the reversal timestamp and a SUPERSEDES relationship
pointing to the old node. The old decision is preserved — it is still
queryable for "what did we believe in 2022".

When a Concept changes significantly: update the existing node's
properties and set last_confirmed_at. If the change is a contradiction,
create a Contradiction node and link both versions.

Query pattern for past state: MATCH (n:Concept) WHERE n.valid_from \<=
\$timestamp AND (n.valid_until IS NULL OR n.valid_until \> \$timestamp)
— this retrieves the graph state at any past timestamp without
snapshots.

Why not snapshots: storing full graph snapshots at every change point
would require gigabytes of storage for a large team. Validity windows on
individual nodes means the full history is stored in O(n changes) space
not O(n changes × graph size).

**Neo4j Indexes**

| **Index**                                       | **On**                        | **Query It Serves**                                                                             | **Why**                                                         |
|-------------------------------------------------|-------------------------------|-------------------------------------------------------------------------------------------------|-----------------------------------------------------------------|
| BTREE on Concept.name                           | Concept(name)                 | Entity resolution Stage 1 — lexical lookup by name                                              | Every ingested event looks up existing concepts by name first   |
| FULLTEXT on Concept.name + Concept.aliases      | Concept(name, aliases)        | BM25 full-text search in hybrid retrieval                                                       | Exact technical term search — "JWT", "PostgreSQL", error codes  |
| BTREE on Entity.canonical_name                  | Entity(canonical_name)        | Entity resolution Stage 1 — person lookup                                                       |                                                                 |
| BTREE on Decision.status + Decision.decided_at  | Decision(status, decided_at)  | Fetch active decisions sorted by recency — dashboard and drift detection                        | Composite covers both filter and sort in one scan               |
| BTREE on Source.external_id                     | Source(external_id)           | Deduplication — prevent same GitHub commit or Slack message ingested twice                      | Unique constraint on this index enforces exactly-once ingestion |
| BTREE on Question.answered + Question.ask_count | Question(answered, ask_count) | Knowledge gap detection — unanswered questions sorted by frequency                              |                                                                 |
| BTREE on Entity.last_active_at                  | Entity(last_active_at)        | Knowledge Transfer Document trigger — find contributors who went quiet                          |                                                                 |
| RANGE on all valid_from, valid_until            | All temporal nodes            | Past-state queries — WHERE valid_from \<= \$ts AND (valid_until IS NULL OR valid_until \> \$ts) | Without this index, temporal queries become full graph scans    |

**MongoDB — Document Storage Schema**

**Collection: raw_events**

Every ingested event stored in its original form before normalization.
Never deleted — provides replay capability if Neo4j needs rebuilding.

| **Field**         | **Type**     | **Description**                                                                                 |
|-------------------|--------------|-------------------------------------------------------------------------------------------------|
| \_id              | ObjectId     | MongoDB auto-generated ID                                                                       |
| source_type       | string       | "github" \| "slack" \| "file"                                                                   |
| external_id       | string       | GitHub event ID, Slack message ts, or file hash — used for deduplication                        |
| raw_payload       | object       | Complete original event payload — GitHub webhook JSON, Slack event JSON, or extracted file text |
| normalized_event  | object       | Unified schema version — same structure regardless of source                                    |
| privacy_level     | string       | "public_knowledge" \| "internal_knowledge" \| "sensitive_personal" \| "hr_matter"               |
| processing_status | string       | "pending" \| "processed" \| "failed" \| "excluded_private"                                      |
| neo4j_node_ids    | string\[\]   | IDs of Neo4j nodes created from this event — for traceability                                   |
| ingested_at       | Date         |                                                                                                 |
| processed_at      | Date \| null |                                                                                                 |

**Collection: embeddings**

Transformers.js embeddings for all ingested content. Separate from
raw_events for query performance. The embedding is over the normalized
content not the raw payload.

| **Field**       | **Type**      | **Description**                                                               |
|-----------------|---------------|-------------------------------------------------------------------------------|
| \_id            | ObjectId      |                                                                               |
| raw_event_id    | ObjectId      | Reference to raw_events — join when retrieving full content                   |
| neo4j_node_id   | string        | Which Neo4j node this embedding represents                                    |
| node_type       | string        | "Concept" \| "Decision" \| "Source" \| "Entity"                               |
| content_text    | string        | The text that was embedded — stored for retrieval display                     |
| embedding       | number\[384\] | Transformers.js all-MiniLM-L6-v2 vector — stored as Atlas Vector Search field |
| embedding_model | string        | "all-MiniLM-L6-v2" — locked, never change without re-embedding all            |
| created_at      | Date          |                                                                               |

MongoDB Atlas Vector Search index on embedding field: type HNSW,
dimensions 384, similarity cosine. This is the vector search stage of
hybrid retrieval.

**Collection: generated_documents**

AI-generated documents — Knowledge Transfer Documents, gap reports,
drift summaries. Stored separately from raw events because they are
outputs not inputs.

| **Field**             | **Type**     | **Description**                                                                          |
|-----------------------|--------------|------------------------------------------------------------------------------------------|
| \_id                  | ObjectId     |                                                                                          |
| doc_type              | string       | "knowledge_transfer" \| "gap_report" \| "drift_summary" \| "onboarding_path"             |
| subject_entity_id     | string       | Neo4j Entity node ID of the person this document is about (for KTDs)                     |
| content               | string       | Full generated document text                                                             |
| trust_tier            | string       | "ai_draft" \| "community_verified"                                                       |
| verification_requests | object\[\]   | Array of { entity_id, notified_at, approved_at \| null } — tracks community verification |
| approvals_required    | number       | 2 — always 2 of 3 approvals needed                                                       |
| approvals_received    | number       | Current approval count                                                                   |
| trigger               | string       | What triggered generation — "activity_drop" \| "gap_threshold" \| "manual"               |
| generated_at          | Date         |                                                                                          |
| verified_at           | Date \| null |                                                                                          |

### 2.4 API Design & Contracts
>
> **⚠** *Rule R-27: API contracts locked before frontend touches
> anything. Rule R-28: Every response uses the standard envelope. Rule
> R-29: Versioned from day one — /api/v1/ throughout.*

**Base URL & Versioning**

Local: http://localhost:3001/api/v1/

Production: https://omnirag-api.onrender.com/api/v1/

Server-Sent Events: /api/v1/query/stream (for streaming query responses
token by token)

**Standard Response Envelope**

| **Field** | **Type**       | **Always Present** | **Description**                                         |
|-----------|----------------|--------------------|---------------------------------------------------------|
| success   | boolean        | Yes                | true for 2xx, false for all errors                      |
| data      | object \| null | Yes                | Response payload on success, null on error              |
| error     | object \| null | Yes                | null on success. { code, message, fields } on error     |
| meta      | object         | Yes                | { version: "v1", request_id: uuid, timestamp: ISO8601 } |

**API Endpoints**

| **Method** | **Path**                 | **Auth**             | **Request**                                                                  | **Success Response**                                                             | **Error Codes**                    | **Rate Limit** |
|------------|--------------------------|----------------------|------------------------------------------------------------------------------|----------------------------------------------------------------------------------|------------------------------------|----------------|
| POST       | /auth/google             | None                 | Body: { code: string }                                                       | 200: { token, refresh_token, user }                                              | INVALID_OAUTH_CODE                 | 20/min         |
| POST       | /auth/refresh            | None                 | Body: { refresh_token }                                                      | 200: { token, refresh_token }                                                    | TOKEN_EXPIRED                      | 30/min         |
| GET        | /workspace/status        | JWT                  | None                                                                         | 200: { entity_count, decision_count, source_count, gap_count, last_ingested_at } | UNAUTHORIZED                       | 60/min         |
| POST       | /ingest/github/webhook   | GitHub HMAC          | GitHub webhook payload                                                       | 202: { event_id, queued: true }                                                  | INVALID_SIGNATURE                  | 500/min        |
| POST       | /ingest/slack/webhook    | Slack signing secret | Slack Events API payload                                                     | 200: { challenge } or 202: { event_id }                                          | INVALID_SIGNATURE                  | 500/min        |
| POST       | /ingest/files            | JWT                  | Multipart: file (PDF or DOCX, max 10MB)                                      | 202: { file_id, status: "queued" }                                               | UNSUPPORTED_FORMAT, FILE_TOO_LARGE | 20/min         |
| GET        | /ingest/status/:event_id | JWT                  | None                                                                         | 200: { status, neo4j_nodes_created, error_message \| null }                      | NOT_FOUND                          | 100/min        |
| POST       | /query                   | JWT                  | Body: { question: string, filters?: { date_from?, date_to?, source_type? } } | 200: { answer, citations, confidence, query_type, agents_used }                  | VALIDATION_ERROR, GRAPH_EMPTY      | 30/min         |
| GET        | /query/stream            | JWT                  | Query: ?question=...&filters=...                                             | SSE stream: token-by-token answer then final citations JSON                      | UNAUTHORIZED, GRAPH_EMPTY          | 30/min         |
| GET        | /graph/nodes             | JWT                  | Query: ?type=Concept&limit=50&offset=0                                       | 200: { nodes: GraphNode\[\], total }                                             | UNAUTHORIZED                       | 60/min         |
| GET        | /graph/node/:id          | JWT                  | None                                                                         | 200: { node, relationships, sources, confidence_breakdown }                      | NOT_FOUND                          | 100/min        |
| GET        | /graph/history           | JWT                  | Query: ?node_id=...&timestamp=ISO8601                                        | 200: { node_state_at_timestamp, changes_since }                                  | NOT_FOUND                          | 60/min         |
| GET        | /graph/drift/:concept    | JWT                  | Query: ?from=ISO8601&to=ISO8601                                              | 200: { drift_detected: bool, summary, changes: Change\[\] }                      | NOT_FOUND                          | 30/min         |
| GET        | /experts/:concept        | JWT                  | None                                                                         | 200: { experts: Expert\[\], gap_risk: "low"\|"medium"\|"high" }                  | NOT_FOUND                          | 60/min         |
| GET        | /gaps                    | JWT                  | Query: ?limit=20                                                             | 200: { gaps: KnowledgeGap\[\], unanswered_questions: Question\[\] }              | UNAUTHORIZED                       | 60/min         |
| GET        | /documents               | JWT                  | Query: ?type=knowledge_transfer&status=ai_draft                              | 200: { documents: GeneratedDoc\[\] }                                             | UNAUTHORIZED                       | 60/min         |
| POST       | /documents/:id/approve   | JWT                  | None                                                                         | 200: { document, approvals_received, verified: bool }                            | NOT_FOUND, ALREADY_APPROVED        | 20/min         |
| GET        | /health                  | None                 | None                                                                         | 200: { status: "healthy", services: { mongodb, neo4j, redis, ollama } }          | None                               | 200/min        |

**Server-Sent Events — Query Streaming**

GET /api/v1/query/stream sends the answer token by token as the LLM
generates it. This is what makes OmniRAG feel fast even when Groq takes
15 seconds for a complex query.

| **Event Type**      | **Data**                                                                                                              | **When Sent**                                                                 |
|---------------------|-----------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| token               | { text: string }                                                                                                      | Every token as Groq streams it — user reads in real time                      |
| agent_status        | { agent: string, status: "running"\|"complete", summary?: string }                                                    | When LangGraph.js coordinator assigns to a specialist or specialist completes |
| retrieval_context   | { nodes_found: int, graph_hops: int, retrieval_latency_ms: int }                                                      | After hybrid retrieval completes — before LLM generation starts               |
| hallucination_check | { claims_checked: int, claims_rejected: int }                                                                         | After hallucination guard runs on completed answer                            |
| complete            | { answer: string, citations: Citation\[\], confidence: float, confidence_breakdown: object, agents_used: string\[\] } | Final event — complete answer with all metadata                               |
| error               | { code: string, message: string }                                                                                     | If any stage fails — Groq unavailable, graph empty, etc.                      |

### 2.5 Security Architecture

**Authentication Strategy**

Google OAuth 2.0 via Passport.js Google strategy. Flow: user clicks Sign
In with Google → Google returns authorisation code → POST /auth/google →
exchange for Google user profile → create or update user in MongoDB →
issue JWT access token (15 minute expiry) + refresh token (7 day expiry,
stored in Redis). Rule R-53: JWT tokens have expiry and refresh
rotation.

GitHub webhook authentication: HMAC-SHA256 signature validation on every
webhook. X-Hub-Signature-256 header compared against HMAC of raw body
with GITHUB_WEBHOOK_SECRET. Reject immediately if signature invalid.

Slack webhook authentication: Slack signing secret validation.
X-Slack-Signature header compared against signed body. Reject if
invalid. URL verification challenge handled automatically.

**OWASP Top 10 Coverage**

| **Threat**                    | **Mitigation**                                                                                                                                                                                    |
|-------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| A01 Broken Access Control     | JWT middleware on all protected routes. User can only query their workspace — workspace_id claim in JWT. No cross-workspace data access.                                                          |
| A02 Cryptographic Failures    | JWT signed with RS256. Refresh tokens stored hashed in Redis. Webhook secrets in environment variables never in code. HTTPS via Render.                                                           |
| A03 Injection                 | Parameterised Cypher queries throughout — never string concatenation in Neo4j queries. MongoDB queries use driver parameterisation. No eval() anywhere.                                           |
| A04 Insecure Design           | Privacy classifier runs before any content enters the graph — sensitive content excluded at ingestion not after. Hallucination guard prevents LLM output from directly citing non-existent nodes. |
| A05 Security Misconfiguration | CORS explicitly configured — frontend origin only. Security headers via helmet.js: X-Content-Type-Options, X-Frame-Options, CSP. No default credentials.                                          |
| A06 Vulnerable Components     | npm audit runs in CI. Dependabot alerts enabled. Dependencies pinned in package-lock.json.                                                                                                        |
| A07 Authentication Failures   | Rate limiting on /auth/google and /auth/refresh. Expired tokens return 401 TOKEN_EXPIRED. Refresh tokens invalidated on logout.                                                                   |
| A08 Software Integrity        | package-lock.json committed. Docker image built from pinned base image. No external scripts executed at runtime.                                                                                  |
| A09 Logging Failures          | pino structured logging on every request. Errors logged with request_id. No tokens, keys, or raw user content in logs.                                                                            |
| A10 SSRF                      | No user-controlled URL fetching. GitHub webhook URL is a fixed secret. Outbound HTTP only to explicitly allowlisted domains: api.groq.com, slack.com, github.com, accounts.google.com.            |

**Secrets Management**

All secrets in environment variables. .env for local, GitHub Secrets for
CI/CD, Render environment variables for production. .env.example
contains all variable names with descriptions. App validates all
required secrets on startup via a config validation function — refuses
to start with missing values (Rule R-36). Secrets required on startup:
MONGODB_URI, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, REDIS_URL,
GROQ_API_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, JWT_PRIVATE_KEY,
JWT_PUBLIC_KEY, GITHUB_WEBHOOK_SECRET, SLACK_SIGNING_SECRET.

### 2.6 Scalability & Failure Recovery

**Scalability Strategy**

Current architecture handles approximately 200 webhook events per minute
(GitHub + Slack combined) and 30 LLM requests per minute (Groq free tier
limit). Scaling signal is Redis Streams consumer lag — when lag exceeds
500 messages, the ingestion pipeline needs more worker processes. At 10x
load: add more Node.js worker processes consuming from the same Redis
Streams consumer group (stateless, scales horizontally). Neo4j AuraDB
free tier (200k nodes, 400k relationships) handles approximately 50,000
ingested events depending on entity overlap before hitting limits.
MongoDB Atlas free tier (512MB) handles approximately 100,000 raw events
at average 5KB per event.

| **Failure Scenario**             | **Detection**                                                         | **Recovery Strategy**                                                                                                                                                                                                     | **RTO Target**           |
|----------------------------------|-----------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------|
| Neo4j connection lost            | GET /health returns neo4j: "unhealthy"                                | Mongoose-style retry with exponential backoff (3 retries). Ingestion worker pauses and retries — Redis Streams messages remain unconsumed until reconnected. Queries return 503 SERVICE_UNAVAILABLE with helpful message. | \< 5 min with auto-retry |
| MongoDB connection lost          | GET /health returns mongodb: "unhealthy"                              | Raw event publishing to Redis Streams stops. API returns 503. Worker retries connection every 5 seconds.                                                                                                                  | \< 3 min with retry      |
| Redis connection lost            | Ingestion queue stops. Cache misses. SSE broadcasting fails.          | API falls back to direct Neo4j queries (no cache). Ingestion events queue in-memory (max 100) then drop. Alert fires. SSE clients reconnect automatically.                                                                | \< 2 min with fallback   |
| Groq API rate limit (30/min)     | SSE stream returns error event with RATE_LIMIT code                   | Retry after 60 seconds via exponential backoff. If 3 consecutive failures, fall back to Ollama local for the generation step. Quality degrades but system stays functional.                                               | \< 2 min with retry      |
| Groq API fully down              | All LLM calls fail with network error                                 | Ollama llama3 local fallback for all LLM calls. Performance (speed) degrades significantly — Ollama is much slower than Groq. Complex queries may time out. Alert fires.                                                  | \< 1 min with fallback   |
| Transformers.js model not loaded | Entity resolution Stage 2 fails. Hybrid retrieval vector stage fails. | Model preloaded on server startup. If startup load fails, server logs clear error and exits — forces redeploy with correct model file. Never partial startup.                                                             | Redeploy required        |
| Ollama privacy classifier down   | Privacy classifier returns error for all content                      | Fall back to conservative exclusion — if privacy classifier unavailable, exclude all ingested content from graph until classifier recovers. Better to exclude than to expose private content.                             | \< 1 min with fallback   |

### 2.7 Data Flow Architecture
>
> **ℹ** *This section answers "which service reads and writes to which
> database and why" — the most common whiteboard question in system
> design interviews. OmniRAG has three databases serving fundamentally
> different roles. Knowing why each database exists and what it owns is
> critical for defending the architecture.*

**Database Role Summary**

| **Database** | **Role**                                                                          | **Source of Truth For**                                                                                                                          | **Never Used For**                                                                                                           |
|--------------|-----------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| Neo4j        | The knowledge graph — relationships, connections, causal chains, temporal history | Concept nodes, Entity nodes, Decision nodes, all relationships, temporal validity windows, contradiction nodes, expertise scores, question nodes | Raw event storage, embeddings, binary data, generated document text                                                          |
| MongoDB      | Document storage — raw events, embeddings, generated content                      | Raw ingested payloads, Transformers.js embeddings (via Atlas Vector Search), AI-generated document text, ingestion processing status             | Graph traversal, relationship queries, anything requiring JOIN-like operations                                               |
| Redis        | Ephemeral coordination — task queue, cache, pub/sub                               | In-flight task queue (Redis Streams), query result cache (TTL 300s), JWT refresh token blacklist, SSE broadcast channel                          | Persistent storage of any kind — data loss on Redis restart is acceptable because Neo4j and MongoDB are the sources of truth |

**Service → Database Ownership Map**

> **⚠** *Rule: one service owns writes to each data type. Multiple
> services may read. Shared write ownership creates race conditions.*

| **Service**                                                                                   | **Writes To**                                                                                                                                                                                | **Reads From**                                                                                                                                                        | **Why This Ownership**                                                                                                                                                                                         |
|-----------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Express API Server (src/app.ts)                                                               | MongoDB: raw_events (ingestion status updates). Redis: JWT refresh tokens, query result cache writes.                                                                                        | Neo4j: graph queries for API responses. MongoDB: raw event content for citations. Redis: cache reads, JWT validation.                                                 | The API server handles user-facing requests — authentication, queries, file uploads, webhook validation. It does not write to Neo4j directly — all graph writes go through the stream consumer worker.         |
| Redis Streams Consumer Worker (src/ingestion/stream-consumer.ts)                              | Neo4j: ALL graph writes — Concept, Entity, Decision, Source, Question nodes and all relationships. MongoDB: raw_events processing_status and neo4j_node_ids. MongoDB: embeddings collection. | MongoDB: raw_events for content. Neo4j: existing nodes for entity resolution lookups. Ollama: privacy classification.                                                 | The consumer worker is the only writer to Neo4j. This is intentional — single writer to the graph prevents concurrent write conflicts. The consumer processes events sequentially per consumer group.          |
| LangGraph.js Agent Pipeline (src/agents/)                                                     | MongoDB: generated_documents (KTD content, drift summaries). Redis: agent_status pub/sub events for SSE stream.                                                                              | Neo4j: all graph reads for specialist agents via tool calls. MongoDB: embeddings for episodic memory RAG (via Atlas Vector Search). Groq API: LLM reasoning calls.    | Agents are read-heavy — they traverse the graph to find evidence. The only write is storing the generated output (KTDs, postmortems). Agents never write to Neo4j — they read from it.                         |
| Intelligence Features (src/intelligence/)                                                     | MongoDB: generated_documents (KTDs, gap reports). Neo4j: EXPERTISE_IN relationship weight updates only.                                                                                      | Neo4j: Entity nodes for activity monitoring, EXPERTISE_IN for expert routing, Question nodes for gap detection. MongoDB: generated_documents for verification status. | Intelligence features are mostly read-heavy analytics. The one Neo4j write (EXPERTISE_IN weight) is a lightweight relationship property update on an existing relationship — not creating new graph structure. |
| Transformers.js Embedder (src/entity-resolution/stage2-semantic.ts + src/retrieval/vector.ts) | MongoDB: embeddings collection via Atlas Vector Search.                                                                                                                                      | Nothing — produces embeddings from text input.                                                                                                                        | The embedder is a pure computation function. It takes text, returns a vector. The consumer worker calls it and stores the result in MongoDB.                                                                   |

**Data Flow — GitHub Webhook to Knowledge Graph**

The primary ingestion flow. Every GitHub push, PR, issue, and review
event follows this path.

| **Step** | **From**              | **To**                                   | **Data**                                                                                   | **Latency**                         |
|----------|-----------------------|------------------------------------------|--------------------------------------------------------------------------------------------|-------------------------------------|
| 1        | GitHub Actions        | Express POST /ingest/github/webhook      | GitHub webhook payload with X-Hub-Signature-256 header                                     | —                                   |
| 2        | Express middleware    | HMAC validator                           | Validates signature against GITHUB_WEBHOOK_SECRET. Rejects immediately if invalid.         | \< 5ms                              |
| 3        | Express route handler | Normaliser (src/ingestion/normaliser.ts) | Raw GitHub payload converted to UnifiedEvent schema                                        | \< 10ms                             |
| 4        | Express route handler | MongoDB raw_events (INSERT)              | UnifiedEvent stored with status "pending". external_id checked for duplicates.             | \< 20ms                             |
| 5        | Express route handler | Redis Streams XADD (omnirag:events)      | raw_event MongoDB \_id published to stream. 202 Accepted returned to GitHub.               | \< 5ms. Total API response: \< 50ms |
| 6        | Redis Streams         | Consumer Worker XREADGROUP               | Worker picks up event from consumer group "omnirag-workers"                                | \< 100ms — polling interval         |
| 7        | Consumer Worker       | Ollama (privacy classifier)              | Content text sent for privacy classification. If sensitive: mark excluded, XACK, stop.     | 200-500ms — local Ollama inference  |
| 8        | Consumer Worker       | Transformers.js (in-process)             | Embed the content text. No API call — local inference.                                     | \< 100ms warm, \< 200ms cold        |
| 9        | Consumer Worker       | Entity resolution pipeline (stages 1-3)  | Identify Concept, Entity, Decision in the event. Resolve against existing Neo4j nodes.     | \< 500ms all three stages           |
| 10       | Consumer Worker       | Neo4j (Cypher MERGE/CREATE)              | Write Concept/Entity/Decision/Source nodes with temporal properties. Create relationships. | \< 50ms — parameterised Cypher      |
| 11       | Consumer Worker       | MongoDB embeddings (INSERT)              | Store embedding vector linked to Neo4j node_id and MongoDB raw_event \_id.                 | \< 20ms                             |
| 12       | Consumer Worker       | MongoDB raw_events (UPDATE)              | Mark processing_status "processed", store neo4j_node_ids.                                  | \< 10ms                             |
| 13       | Consumer Worker       | Redis Streams XACK                       | Acknowledge message — prevents redelivery.                                                 | \< 5ms                              |
| Total    | —                     | —                                        | GitHub webhook received to Neo4j node created                                              | \< 2 seconds end-to-end             |

**Data Flow — Query to Streamed Answer**

The primary query flow. Every question asked by a user follows this
path.

| **Step**       | **From**                       | **To**                                                     | **Data**                                                                                       | **Latency**                                   |
|----------------|--------------------------------|------------------------------------------------------------|------------------------------------------------------------------------------------------------|-----------------------------------------------|
| 1              | React frontend                 | Express GET /query/stream?question=...                     | Question string + optional filters. JWT validated.                                             | —                                             |
| 2              | Express route                  | Redis cache (GET)                                          | Hash of question + filters checked. Cache hit → return immediately.                            | \< 5ms. If hit: \< 50ms total response.       |
| 3 (cache miss) | Express route                  | QueryTypeClassifier (Groq LLaMA 3.1 8B)                    | Classify query: FACTUAL / CAUSAL / TEMPORAL / EXPERTISE / COMPLEX                              | \< 1 second — fast model                      |
| 4              | Query service                  | BM25 (Neo4j FULLTEXT) + Vector (MongoDB Atlas) in parallel | Two retrieval paths run simultaneously. Results returned independently.                        | \< 200ms for both (p95 target)                |
| 5              | Query service                  | RRF fusion (src/retrieval/rrf.ts)                          | BM25 and vector rankings combined. Pure in-memory computation.                                 | \< 5ms                                        |
| 6              | Query service                  | Neo4j (graph expansion — 1-2 hops)                         | Top 5 RRF nodes expanded via MENTIONED_IN, CAUSED, SUPERSEDES                                  | \< 50ms — BTREE indexed traversal             |
| 7              | Query service (FACTUAL simple) | SSE stream → React                                         | If FACTUAL + high confidence: skip agents, stream answer directly. First token \< 3s.          | \< 3s to first token                          |
| 7 (complex)    | Query service                  | LangGraph.js Coordinator                                   | Full agent pipeline: coordinator assigns specialists. agent_status SSE events emitted.         | Streaming starts \< 3s. Full answer \< 45s.   |
| 8              | Agents                         | Groq LLaMA 3.1 70B                                         | Specialist reasoning. Tokens stream back in real time.                                         | Groq: 500 tok/sec                             |
| 9              | Answer returned                | HallucinationGuard (src/retrieval/hallucination-guard.ts)  | Every factual claim checked against retrieved source node IDs. Uncorroborated claims stripped. | \< 50ms — deterministic TypeScript            |
| 10             | Answer validated               | ConfidenceScorer (src/retrieval/confidence-scorer.ts)      | Confidence derived from source_count, recency, contradiction_count, verification_status.       | \< 30ms — deterministic formula + Neo4j reads |
| 11             | Query service                  | Redis cache (SET, TTL 300s)                                | Validated answer cached by question hash.                                                      | \< 5ms                                        |
| 12             | SSE stream                     | React frontend                                             | complete event: { answer, citations, confidence, confidence_breakdown, agents_used }           | \< 20ms                                       |
| Total          | —                              | —                                                          | Simple FACTUAL query: \< 5 seconds. Complex CAUSAL query: \< 45 seconds.                       | —                                             |

**Database Source of Truth Summary**

| **Data Type**                             | **Source of Truth**                               | **Why Here**                                                                                      | **Also In**                                                       |
|-------------------------------------------|---------------------------------------------------|---------------------------------------------------------------------------------------------------|-------------------------------------------------------------------|
| Knowledge graph — nodes and relationships | Neo4j                                             | Graph traversal, multi-hop queries, temporal validity — native graph database operations          | Not duplicated anywhere                                           |
| Temporal decision history                 | Neo4j — valid_from, valid_until on Decision nodes | Time-aware graph queries — past state reconstruction is a single Cypher WHERE predicate           | Not duplicated                                                    |
| Contributor expertise scores              | Neo4j — EXPERTISE_IN relationship weight property | Score is a property of the relationship between Entity and Concept — naturally lives in the graph | Not duplicated                                                    |
| Raw ingested payloads                     | MongoDB raw_events                                | Arbitrary document shapes (GitHub JSON ≠ Slack JSON ≠ PDF text). Document model correct.          | Not duplicated — provides replay source if Neo4j needs rebuilding |
| Embedding vectors                         | MongoDB embeddings (Atlas Vector Search)          | Atlas Vector Search requires MongoDB. Embeddings linked to Neo4j node IDs for retrieval context.  | Not duplicated                                                    |
| AI-generated document content             | MongoDB generated_documents                       | Long text content — better in MongoDB than as Neo4j node property strings                         | Not duplicated                                                    |
| In-flight ingestion tasks                 | Redis Streams                                     | Redis Streams IS the task queue — ordered, acknowledged, replayable                               | Task ID also in MongoDB raw_events.processing_status              |
| Query result cache                        | Redis (ephemeral)                                 | Fast lookup by question hash. TTL 300s — stale cache is acceptable                                | Source of truth: Neo4j + Groq                                     |
| JWT refresh tokens                        | Redis (ephemeral)                                 | Fast lookup on every authenticated request. 7-day TTL. Blacklist on logout.                       | Not duplicated — session state only                               |

> **PART 03 — Engineering Blueprint**
>
> **ℹ** *TypeScript strict mode throughout. Feature-based folder
> structure — Rule R-15. All database access through repository classes
> — Rule R-48. No file longer than 300 lines — Rule R-16. Dependencies
> flow downward only — routes call services call repositories, never the
> reverse.*
>
### 3.1 Folder Structure
>
> **WHY:** Feature-based folders mean all code for entity_resolution
> lives together — routes, service, repository, types, tests. You never
> need to jump between 4 directories to understand one feature. Rule
> R-15 mandates this.

| **Path**                                                | **Contents**                                                                                                                                                         | **Rule**    |
|---------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------|
| omnirag/                                                | Project root — docker-compose.yml, Makefile, README.md, package.json, tsconfig.json                                                                                  |             |
| omnirag/src/                                            | All TypeScript source code                                                                                                                                           | R-15        |
| omnirag/src/app.ts                                      | Express app factory — registers routers, middleware, error handler. Under 80 lines.                                                                                  | R-39        |
| omnirag/src/server.ts                                   | HTTP server entry point — imports app, binds port, starts stream consumers.                                                                                          |             |
| omnirag/src/config.ts                                   | Config singleton — reads all env vars, validates on import, throws with clear message if missing. All other modules import from here.                                | R-19, R-36  |
| omnirag/src/shared/                                     | Cross-cutting concerns used by multiple features                                                                                                                     |             |
| omnirag/src/shared/types.ts                             | All shared TypeScript interfaces and types — UnifiedEvent, GraphNode, QueryResult, Citation, etc. Single source of truth.                                            | R-33        |
| omnirag/src/shared/constants.ts                         | All named constants — ENTITY_MERGE_THRESHOLD, GRAPH_EXPANSION_HOPS, GROQ_MODEL_FAST, etc. No magic numbers anywhere else.                                            | R-34        |
| omnirag/src/shared/errors.ts                            | Custom error classes — OmniRAGError base, ValidationError, NotFoundError, GraphEmptyError, etc. Standard error codes.                                                | R-41        |
| omnirag/src/shared/logger.ts                            | pino logger configuration. All modules import logger from here — never configure logging twice.                                                                      | R-42        |
| omnirag/src/shared/middleware.ts                        | request-id injection, error handler, CORS, helmet security headers, request logging.                                                                                 |             |
| omnirag/src/database/                                   | Database connection setup and shared utilities                                                                                                                       |             |
| omnirag/src/database/neo4j.ts                           | Neo4j driver singleton — connection pool, session factory. Loaded once on startup.                                                                                   |             |
| omnirag/src/database/mongodb.ts                         | Mongoose connection + all collection models.                                                                                                                         |             |
| omnirag/src/database/redis.ts                           | Redis client singleton — used by cache, streams, pub/sub.                                                                                                            |             |
| omnirag/src/ingestion/                                  | Everything about receiving events from external sources                                                                                                              |             |
| omnirag/src/ingestion/routes.ts                         | Express router — POST /ingest/github/webhook, POST /ingest/slack/webhook, POST /ingest/files. Validates signatures, publishes to Redis Streams. Under 80 lines.      | R-31        |
| omnirag/src/ingestion/normaliser.ts                     | Converts raw source payloads to unified UnifiedEvent schema. Pure functions, no side effects. One function per source type.                                          | R-39        |
| omnirag/src/ingestion/privacy-classifier.ts             | Calls Ollama llama3 locally to classify content privacy level. Four levels. Sensitive content excluded before graph write.                                           |             |
| omnirag/src/ingestion/stream-consumer.ts                | Redis Streams XREADGROUP consumer — processes events from ingestion queue, calls normaliser then entity resolution. Handles acknowledgment and dead letter.          |             |
| omnirag/src/ingestion/deduplication.ts                  | Checks MongoDB raw_events for existing external_id before processing. Prevents same GitHub commit processed twice.                                                   |             |
| omnirag/src/ingestion/test-ingestion.ts                 | Unit tests co-located with source — Rule R-17.                                                                                                                       | R-17        |
| omnirag/src/entity-resolution/                          | Three-stage entity resolution pipeline                                                                                                                               |             |
| omnirag/src/entity-resolution/stage1-lexical.ts         | Jaro-Winkler distance matching. Returns candidates above 0.70 threshold. Pure function — no database calls.                                                          |             |
| omnirag/src/entity-resolution/stage2-semantic.ts        | Cosine similarity of Transformers.js embeddings. Returns candidates above 0.75 threshold.                                                                            |             |
| omnirag/src/entity-resolution/stage3-graph.ts           | Neo4j graph neighborhood analysis — shared neighbor count as confidence signal. Handles cross-system identity resolution.                                            |             |
| omnirag/src/entity-resolution/resolver.ts               | Orchestrates all three stages. Decision logic: auto-merge above 0.85, human review queue 0.60-0.85, new entity below 0.60.                                           |             |
| omnirag/src/entity-resolution/merge-undo.ts             | Records every merge as a reversible event. Undo function restores both nodes with original relationships.                                                            |             |
| omnirag/src/entity-resolution/repository.ts             | Neo4j queries for entity lookup, merge, undo. No business logic.                                                                                                     | R-48        |
| omnirag/src/entity-resolution/test-entity-resolution.ts | Unit tests including adversarial test set — similar-but-different names that must NOT merge.                                                                         | R-17, R-45  |
| omnirag/src/graph/                                      | Temporal knowledge graph write operations                                                                                                                            |             |
| omnirag/src/graph/writer.ts                             | Writes resolved events to Neo4j — creates nodes with temporal properties, creates relationships, detects contradictions.                                             |             |
| omnirag/src/graph/contradiction-detector.ts             | Detects three contradiction types: direct_factual, temporal, cross_source_ownership. Creates Contradiction nodes when found.                                         |             |
| omnirag/src/graph/classifier.ts                         | Five-type message classifier using Groq LLaMA 3.1 8B — DECISION, QUESTION, SOLUTION, CONTEXT, NOISE.                                                                 |             |
| omnirag/src/graph/repository.ts                         | Neo4j queries for graph reading — node lookup, relationship traversal, temporal queries. No business logic.                                                          | R-48        |
| omnirag/src/graph/test-graph.ts                         | Unit tests for temporal query logic and contradiction detection.                                                                                                     | R-17        |
| omnirag/src/retrieval/                                  | Hybrid retrieval pipeline                                                                                                                                            |             |
| omnirag/src/retrieval/bm25.ts                           | BM25 full-text search via Neo4j FULLTEXT index. Returns ranked results with BM25 scores.                                                                             |             |
| omnirag/src/retrieval/vector.ts                         | Vector similarity search via MongoDB Atlas Vector Search. Returns top k results with cosine similarity scores.                                                       |             |
| omnirag/src/retrieval/graph-expansion.ts                | Neo4j graph traversal 1-2 hops from top retrieval results. Adds causally connected nodes to result set.                                                              |             |
| omnirag/src/retrieval/rrf.ts                            | Reciprocal Rank Fusion — fuses BM25 and vector rankings into single ranked list. Pure function.                                                                      |             |
| omnirag/src/retrieval/temporal-filter.ts                | Ranks down outdated nodes for current-state queries. Applies temporal filter based on query type.                                                                    |             |
| omnirag/src/retrieval/hallucination-guard.ts            | Cross-references every claim in generated answer against source nodes. Strips uncorroborated claims. Core AI safety component.                                       | R-90, R-95  |
| omnirag/src/retrieval/confidence-scorer.ts              | Derives confidence score from graph properties — source_count, recency, contradiction_count, verification_status. Never from LLM self-report.                        | R-92        |
| omnirag/src/retrieval/test-retrieval.ts                 | Unit tests including test that hallucination guard strips claims with no source node.                                                                                | R-17, R-102 |
| omnirag/src/agents/                                     | LangGraph.js agent pipeline                                                                                                                                          |             |
| omnirag/src/agents/coordinator.ts                       | LangGraph.js StateGraph — coordinator node, specialist routing, five-step chain, self-reflection step.                                                               |             |
| omnirag/src/agents/graph-traversal-specialist.ts        | Factual queries — direct lookups, relationship traversal, decision history.                                                                                          |             |
| omnirag/src/agents/causal-inference-specialist.ts       | Causal and "why" queries — traces causal chains, identifies decision sequences.                                                                                      |             |
| omnirag/src/agents/synthesis-specialist.ts              | Complex multi-source queries — assembles findings from multiple retrieval results.                                                                                   |             |
| omnirag/src/agents/tools.ts                             | Six named tools: search_knowledge_graph, find_causal_chain, get_decision_history, find_expert, detect_contradictions, get_temporal_state. LLM decides which to call. |             |
| omnirag/src/agents/test-agents.ts                       | Tests that low confidence escalates. Tests that self-reflection step catches incomplete answers.                                                                     | R-102       |
| omnirag/src/intelligence/                               | High-level intelligence features built on top of graph + retrieval                                                                                                   |             |
| omnirag/src/intelligence/drift-detector.ts              | Compares concept node state at two timestamps. Calls Groq to narrate what changed.                                                                                   |             |
| omnirag/src/intelligence/gap-detector.ts                | Queries unanswered Question nodes above ask_count threshold. Identifies undocumented high-traffic concepts.                                                          |             |
| omnirag/src/intelligence/expert-router.ts               | Computes contribution-weighted expertise scores per entity per concept. Returns ranked expert list.                                                                  |             |
| omnirag/src/intelligence/ktd-generator.ts               | Knowledge Transfer Document generator — triggered by contributor activity drop, compiles contribution history via LangChain.js.                                      |             |
| omnirag/src/intelligence/community-verification.ts      | Verification workflow — notify top 3 contributors, track approvals, promote trust tier on 2 of 3 approvals.                                                          |             |
| omnirag/src/auth/                                       | Google OAuth, JWT, Passport.js, rate limiting middleware                                                                                                             |             |
| omnirag/src/websocket/                                  | Server-Sent Events manager — Redis pub/sub bridge for streaming query tokens to React frontend                                                                       |             |
| omnirag/src/query/                                      | Query entry point — classifies query type, routes to retrieval or agent pipeline, assembles final response                                                           |             |
| omnirag/frontend/                                       | React + TypeScript + Tailwind + react-force-graph application                                                                                                        |             |
| omnirag/frontend/src/components/KnowledgeGraph/         | react-force-graph visualization — temporal slider, node click to expand, edge thickness by strength, color by node type                                              |             |
| omnirag/frontend/src/components/QueryInterface/         | Question input, streaming answer display (SSE), citation list, confidence score display, agent status indicator                                                      |             |
| omnirag/frontend/src/components/Dashboard/              | Workspace stats, knowledge gap alerts, Knowledge Transfer Document notifications, expert directory                                                                   |             |
| omnirag/tests/                                          | Integration tests — unit tests live next to source per R-17. E2E tests with seeded Neo4j here.                                                                       | R-17        |
| omnirag/.env.example                                    | All environment variable names with descriptions and placeholder values.                                                                                             | R-51        |
| omnirag/docker-compose.yml                              | 5 services: omnirag-api (Node.js), mongodb, neo4j, redis, ollama                                                                                                     |             |
| omnirag/Makefile                                        | Commands: make dev, make test, make seed, make build, make lint                                                                                                      |             |

### 3.2 Coding Standards & Conventions

**Naming Conventions**

- Files: kebab-case — entity-resolution/stage1-lexical.ts,
  graph/contradiction-detector.ts

- Interfaces and Types: PascalCase with prefix I or T for interfaces —
  IGraphNode, TQueryResult, UnifiedEvent

- Classes: PascalCase — EntityResolver, HallucinationGuard,
  TemporalKnowledgeGraph

- Functions and variables: camelCase — resolveEntity(), mergeConfidence,
  neo4jSession

- Constants: UPPER_SNAKE_CASE in constants.ts — ENTITY_MERGE_THRESHOLD,
  GRAPH_EXPANSION_HOPS

- Express routers: kebab-case filename, variable named router — const
  router = express.Router()

- Cypher query variables: camelCase — MATCH (conceptNode:Concept),
  RETURN conceptNode

- API error codes: UPPER_SNAKE_CASE — VALIDATION_ERROR, GRAPH_EMPTY,
  TOKEN_EXPIRED

**Design Patterns Allowed**

- Repository pattern — all Neo4j and MongoDB access through repository
  modules. Service layer never writes Cypher directly. Rule R-48.

- Singleton pattern — Neo4j driver, MongoDB connection, Transformers.js
  model loaded once. Imported as module-level singleton.

- Strategy pattern for entity resolution stages — each stage is a
  standalone function with the same signature. Coordinator calls them in
  sequence.

- Dependency injection via function parameters — repositories passed to
  service functions as parameters, never imported directly inside
  service logic. Enables testing with mocks.

**Design Patterns FORBIDDEN**

- Direct Cypher string construction with user input — parameterised
  queries always. MATCH (n) WHERE n.name = \$name not WHERE n.name =
  "" + userInput

- Catching bare errors without handling — catch (e) { console.log(e) }
  never committed

- Module-level side effects — no database calls at module import time,
  only in functions

- Circular imports — if A imports B and B imports A, extract shared
  types to shared/types.ts

- Any type in TypeScript — every function parameter and return value has
  an explicit type

**Module Dependency Rules — Rule R-48**

1.  Routes — validate input, call query/ingestion service, return
    response. No business logic. No database calls.

2.  Services (query, ingestion, intelligence) — business logic. Calls
    repositories and agents. No Cypher. No MongoDB queries.

3.  Repositories — database queries only. Returns typed domain objects.
    No business logic. No calls to other repositories.

4.  Agents — LangGraph.js coordination and LLM calls. Calls retrieval
    functions. No direct database access.

5.  Shared utilities — pure functions and constants. No database access.
    Imported by any layer.

### 3.3 Git Workflow & Standards

**Branching Strategy**

main — production-ready code only. Never commit directly. Every commit
on main must pass CI and be deployable.

dev — integration branch. All feature branches merge here via PR. CI
runs on every push.

feature/description — new features. Branch from dev. e.g.
feature/entity-resolution-stage3

fix/description — bug fixes. Branch from dev for non-critical, from main
for hotfixes.

**Commit Message Convention**

Format: type(scope): description — e.g. feat(entity-resolution): add
graph neighborhood stage 3

Types: feat, fix, chore, test, docs, refactor, perf. Scope: module name
from folder structure. Description: present tense, under 72 chars, no
full stop.

**PR Checklist — All Required Before Merge**

- All CI checks pass — ESLint, TypeScript strict compile, Jest unit
  tests, integration tests

- No console.log anywhere — use pino logger

- No Cypher string concatenation anywhere — grep for string
  interpolation in Cypher queries

- New env vars added to .env.example with description

- New feature has unit test AND at least one integration test

- No TypeScript any types introduced

- PR description explains what changed and why

- API changes match locked contract in Section 2.4

- You can explain every line of code in this PR without notes

> **PART 04 — Execution Blueprint**
>
> **⚠** *Rule R-77: Phase N cannot begin until Phase N-1 exit criteria
> are 100% complete. Phase 6 (Core Graph Layer) is the hardest phase —
> the temporal schema and entity resolution must be correct before any
> retrieval or agent work begins. Do not rush Phase 6.*
>
> **Blueprint Completeness Checklist — Required Before Phase 1**

- Problem statement describes real pain for both student and team users
  — no solution language ✓

- All tech stack choices in 2.2 have a specific reason AND a rejected
  alternative ✓

- All Neo4j node labels, relationship types, and indexes documented in
  2.3 ✓

- All MongoDB collections with field schemas documented in 2.3 ✓

- API contracts in 2.4 fully specified with all error codes and rate
  limits ✓

- Non-goals list in 1.2 has at least 3 explicit items ✓

- Success metrics in 1.5 all have specific numbers ✓

- Security threats in 2.5 mapped to mitigations ✓

### 4.1 Development Philosophy

**Development Approach**

Graph layer first, intelligence second. The temporal knowledge graph in
Neo4j is the foundation of every feature in OmniRAG. Entity resolution,
retrieval, agents, Knowledge Transfer Documents — all of it reads from
and writes to Neo4j. If the graph schema is wrong, everything built on
top of it is wrong. Phase 6 is given 2 full weeks because getting it
right is more important than moving fast.

Test the entity resolution pipeline adversarially — Rule R-45. Every
entity resolution test set must include similar-but-different names that
must NOT be merged (Sarah Johnson vs Sarah Jenkins), not just positive
examples of the same person with different names.

**What Gets Built First and Why**

6.  Database connections and schema before any business logic — cannot
    test entity resolution without a real Neo4j schema

7.  Ingestion pipeline before the graph writer — data must flow in
    before the graph can be built

8.  Entity resolution before graph writes — resolving who is who before
    writing connections between them

9.  Retrieval before agents — agents need retrieval as a tool, must work
    independently first

10. Simple queries before LangGraph.js — verify retrieval quality before
    adding agent complexity

11. LangGraph.js agents after retrieval — coordinator calls retrieval as
    a tool

12. Intelligence features after agents — KTD, gap detection, drift use
    the graph and agents as primitives

13. Frontend last — consumes locked API contracts, no guessing about
    what the API returns

### 4.2 Phase-by-Phase Build Order
>
> **PHASE 0 Planning Freeze** *Never code during Phase 0*

**Deliverables**

- Blueprint completeness checklist above — all 8 items checked

- Tech stack locked in 2.2 — every layer justified with rejected
  alternative

- Neo4j node labels, relationships, and indexes in 2.3 — fully
  documented

- MongoDB collections with field schemas in 2.3 — fully documented

- API contracts in 2.4 — all endpoints with request/response/errors

- Security architecture in 2.5 — OWASP coverage documented

- Folder structure in 3.1 — every directory named and described

- docker-compose.yml written with all 5 services — even if they do not
  start yet

**Exit Criteria — All Must Pass Before Next Phase**

- Blueprint completeness checklist all 8 items checked

- Another person could read this blueprint and build the system without
  asking you a question

- You can defend every technology choice in 2.2 with a specific reason
  and a rejected alternative

> **→** *The most expensive mistake in OmniRAG is getting the Neo4j
> schema wrong. Spend extra time in Phase 0 on Section 2.3. Every node
> label, relationship type, and property needs to be right before Phase
> 3 creates them.*
>
> **PHASE 1 Repository Foundation** *Git + Docker + CI skeleton*

**Deliverables**

- Repository with folder structure from 3.1 — empty TypeScript files
  with JSDoc module descriptions

- .gitignore (node_modules, .env, dist), .env.example (all variables
  with descriptions), README skeleton

- Pre-commit hooks — ESLint, TypeScript strict compile, no-secrets
  scanner

- GitHub Actions CI skeleton — runs on every push: lint, type check,
  Jest (even with no tests)

- docker-compose.yml with all 5 services: mongodb, neo4j (4.4 with
  APOC), redis, omnirag-api, ollama

- Multi-stage Dockerfile: dev stage (ts-node), prod stage (compiled JS)

- GET /health returning 200 with { status: "starting" }

- Makefile with make dev, make test, make lint

**Exit Criteria — All Must Pass Before Next Phase**

- docker-compose up starts all 5 services from scratch in under 5
  minutes

- CI runs and passes on a trivial commit

- make dev runs without errors

- Neo4j Browser accessible at localhost:7474 with correct credentials

> **PHASE 2 Backend Skeleton** *Express app + all route stubs + error
> handling*

**Deliverables**

- Express app factory in src/app.ts — registers all routers, middleware,
  error handler

- Config singleton in src/config.ts — validates all env vars on import,
  throws with clear message if missing

- pino structured logger in src/shared/logger.ts — all subsequent
  modules import from here

- helmet.js security headers, CORS middleware (frontend origin only),
  request-id middleware

- Error handler middleware returning standard envelope for all thrown
  errors

- Route stubs for all 18 endpoints in 2.4 — return 501 Not Implemented
  with standard envelope

- TypeScript interfaces for all request and response shapes in
  src/shared/types.ts

- GET /health returns structured status with all 4 service states

**Exit Criteria — All Must Pass Before Next Phase**

- Every endpoint returns standard envelope shape — even 501 stubs

- Invalid JWT returns 401 UNAUTHORIZED — never 500

- Missing required body field returns 400 VALIDATION_ERROR with field
  name

- All CI checks pass including TypeScript strict compile

- Server refuses to start if any required env var is missing — clear
  error message

> **PHASE 3 Database Layer** *MongoDB collections + Neo4j schema +
> Redis + repositories*

**Deliverables**

- MongoDB collections created with Mongoose models — raw_events,
  embeddings, generated_documents

- MongoDB Atlas Vector Search index on embeddings.embedding field —
  HNSW, 384 dimensions, cosine similarity

- Neo4j schema constraints and indexes created via migration script —
  all 8 indexes from 2.3

- Neo4j uniqueness constraint on Source.external_id — prevents duplicate
  ingestion

- Neo4j full-text search index on Concept(name, aliases) — required for
  BM25 retrieval

- Redis connection confirmed with PING. Streams and pub/sub channels
  configured.

- Repository modules for all Neo4j operations — typed Cypher query
  functions, no string concatenation

- Repository modules for MongoDB operations — typed query functions

- Seed script: make seed — creates 3 Concept nodes, 3 Entity nodes, 2
  Decision nodes, 5 Source nodes with valid temporal properties. Enough
  to test retrieval.

- Integration tests for all repository functions — real Neo4j and
  MongoDB connections

**Exit Criteria — All Must Pass Before Next Phase**

- All Neo4j constraints and indexes created correctly — verified via
  Neo4j Browser

- MongoDB Atlas Vector Search index active — verified via Atlas
  dashboard

- Seed script creates correct data — verified via Neo4j Browser Cypher
  queries

- All repository unit tests passing

- Temporal query test passes: querying graph state at a past timestamp
  returns correct nodes

- Baseline Neo4j query latency measured and logged in Engineering
  Journal Part 5.1

> **→** *The Neo4j full-text search index creation syntax is different
> from regular indexes — CALL
> db.index.fulltext.createNodeIndex("conceptSearch", \["Concept"\],
> \["name", "aliases"\]). Test this manually in Neo4j Browser before
> relying on it in the retrieval pipeline.*
>
> **PHASE 4 Auth & Security Layer** *Google OAuth + JWT + rate limiting*

**Deliverables**

- Google OAuth flow via Passport.js Google strategy — POST /auth/google
  exchanges code for user profile

- JWT access token (15 min) + refresh token (7 day, hashed in Redis)
  generation and validation

- JWT middleware on all protected routes — workspace_id claim in payload

- GitHub webhook HMAC-SHA256 signature validation on every webhook
  request

- Slack signing secret validation on every Slack event

- express-rate-limit on all public endpoints — values from Section 2.4

- Auth edge cases tested: expired token (401), tampered token (401),
  wrong rate limit (429)

**Exit Criteria — All Must Pass Before Next Phase**

- Expired JWT returns 401 TOKEN_EXPIRED — never 500

- Invalid GitHub webhook signature returns 401 INVALID_SIGNATURE
  immediately

- Rate limit tested — returns 429 with Retry-After header

- All CI checks pass

> **PHASE 5 Ingestion Pipeline** *GitHub webhook + Slack Bolt + file
> upload + Redis Streams*

**Deliverables**

- GitHub Octokit webhook handler — validates signature, extracts
  push/PR/issue/review events, publishes to Redis Streams XADD

- Slack Bolt SDK event listener — message and reaction events, thread
  hierarchy preserved in payload

- File upload endpoint — pdf-parse for PDF, mammoth for DOCX, text
  extraction, publishes to Redis Streams

- Unified event schema normaliser — one normalise() function per source
  type, all return UnifiedEvent

- Privacy classifier calling Ollama llama3 locally — four privacy
  levels, sensitive content excluded

- Redis Streams consumer group setup — XGROUP CREATE, XREADGROUP
  consumer loop

- Deduplication check — Source.external_id uniqueness constraint
  prevents reprocessing

- Dead letter stream for failed events — events that fail 3 times go to
  omnirag:dead

- Integration test: POST GitHub webhook → Redis Streams → consumer →
  MongoDB raw_events insert

- Integration test: POST file → text extracted → privacy classified →
  Redis Streams published

**Exit Criteria — All Must Pass Before Next Phase**

- GitHub webhook acknowledged under 50ms — processing happens in
  consumer

- Integration test: GitHub push event arrives in MongoDB raw_events
  within 5 seconds

- Privacy classifier correctly excludes test content marked as sensitive

- Dead letter stream receives event after 3 failed processing attempts

- Duplicate GitHub event (same external_id) does not create duplicate
  MongoDB document

> **→** *Test the Redis Streams consumer group acknowledgment logic
> carefully. If a consumer processes an event but crashes before calling
> XACK, the event will be redelivered to another consumer. Your
> processing logic must be idempotent — processing the same event twice
> must produce the same result.*
>
> **PHASE 6 Core Graph Layer** *Entity resolution + temporal graph
> writes + contradiction detection*

**Deliverables**

- Three-stage entity resolution pipeline in
  src/entity-resolution/resolver.ts — Stage 1 Jaro-Winkler, Stage 2
  Transformers.js embedding cosine similarity, Stage 3 Neo4j graph
  neighborhood

- Transformers.js all-MiniLM-L6-v2 model loaded as singleton on server
  startup — model warmup so first call is not slow

- Merge undo system — every merge recorded as reversible event in
  MongoDB, undo function restores both nodes

- Five-type message classifier using Groq LLaMA 3.1 8B — DECISION,
  QUESTION, SOLUTION, CONTEXT, NOISE

- Graph writer — creates/updates Concept, Entity, Decision, Source,
  Question nodes with temporal validity windows

- Decision provenance tracking — decided_at, decided_by, source_url,
  status on every Decision node

- Contradiction detection engine — detects direct_factual, temporal,
  cross_source_ownership types

- Contradiction nodes created with type and description when detected

- EXPERTISE_IN relationship updated on every Entity contribution to a
  Concept — weighted by message type (DECISION scores highest)

- valid_until set on superseded nodes when a Decision is reversed

- Integration test: ingest Slack message classified as DECISION →
  correct Decision node created in Neo4j with valid_from

- Integration test: ingest conflicting Slack messages → Contradiction
  node created linking both Concept nodes

- Entity resolution adversarial test — 200 name pairs, \< 2% false merge
  rate

**Exit Criteria — All Must Pass Before Next Phase**

- Entity resolution adversarial test passes — false merge rate \< 2% on
  200-pair test set

- Temporal query test: querying graph at timestamp T returns only nodes
  valid at T

- Contradiction detection creates Contradiction node when two Sources
  assert conflicting values

- Decision node created with correct valid_from and status "active" for
  DECISION-classified messages

- EXPERTISE_IN relationship weight updated correctly for each
  contribution type

- Transformers.js model warm on startup — first embedding call \< 200ms

- Performance: entity resolution for a single entity under 500ms —
  logged in Journal 5.1

> **→** *This is the most important phase and the most error-prone.
> Budget 2 full weeks. The most common mistake is getting the valid_from
> and valid_until logic wrong on temporal updates. Test every temporal
> scenario manually in Neo4j Browser before writing integration tests.
> Use Neo4j Browser to verify the graph looks correct after each
> integration test — visual inspection catches graph schema mistakes
> that assertions miss.*
>
> **PHASE 7 Retrieval Pipeline** *Hybrid retrieval + RRF + hallucination
> guard + confidence scoring*

**Deliverables**

- BM25 full-text search via Neo4j FULLTEXT index — CALL
  db.index.fulltext.queryNodes("conceptSearch", \$query)

- Vector search via MongoDB Atlas Vector Search — cosine similarity on
  embeddings collection

- RRF fusion in src/retrieval/rrf.ts — combines BM25 and vector
  rankings. Pure function, easy to unit test.

- Graph expansion in src/retrieval/graph-expansion.ts — 1-2 hop Neo4j
  traversal from top RRF results

- Query type classifier — classifies query as FACTUAL, CAUSAL, TEMPORAL,
  EXPERTISE, or COMPLEX

- Temporal filter — outdated nodes ranked lower for FACTUAL queries, all
  nodes included for TEMPORAL queries

- Hallucination guard in src/retrieval/hallucination-guard.ts —
  cross-references every LLM claim against retrieved source nodes

- Graph-derived confidence scorer — source_count × recency_weight × (1 -
  contradiction_penalty) × verification_multiplier

- Simple query bypass — FACTUAL queries with high-confidence single-node
  match skip the agent pipeline

- POST /query endpoint now returns real answers (previously returned
  stub)

- GET /query/stream endpoint returns SSE token stream

- Integration test: query about seeded Decision node returns correct
  citation

- Integration test: hallucination guard strips a fabricated claim from
  test LLM output

**Exit Criteria — All Must Pass Before Next Phase**

- Hybrid retrieval p95 latency \< 200ms on seeded test data — measured
  and logged in Journal 5.1

- Hallucination guard strips at least 1 uncorroborated claim in
  integration test

- Confidence score for a high-quality answer \> 0.80. Confidence for a
  low-source answer \< 0.50.

- SSE streaming endpoint sends first token within 3 seconds on simple
  factual query

- Query type classification correct for 10 test queries of each type

> **→** *Build the hallucination guard before connecting it to the agent
> pipeline. Test it in isolation with mock LLM output containing both
> corroborated and uncorroborated claims. The guard is deterministic —
> it should be 100% testable without a real LLM.*
>
> **PHASE 8 LangGraph.js Agent Pipeline** *Coordinator + 3 specialists +
> tools + five-step chain*

**Deliverables**

- LangGraph.js StateGraph in src/agents/coordinator.ts — QueryState
  interface, coordinator node, specialist routing nodes, self-reflection
  node

- GraphTraversalSpecialist — handles FACTUAL queries, calls
  search_knowledge_graph and get_decision_history tools

- CausalInferenceSpecialist — handles CAUSAL queries, calls
  find_causal_chain tool, traces CAUSED relationships

- SynthesisSpecialist — handles COMPLEX queries, calls multiple tools,
  assembles multi-source answers

- Six named tools in src/agents/tools.ts: search_knowledge_graph,
  find_causal_chain, get_decision_history, find_expert,
  detect_contradictions, get_temporal_state

- Five-step prompt chain: extract_relevant_nodes → reason_about_query →
  synthesise_answer → self_reflect_for_gaps → format_with_citations

- Self-reflection step — LLM checks: "Is this answer complete? Does it
  address the question? Are there gaps?" and if gaps found, loops back
  to extraction

- Agent status events emitted via Redis pub/sub — consumed by SSE stream
  for frontend "Agents thinking..." display

- Groq LLaMA 3.1 70B for reasoning steps, 8B for classification steps

- Ollama fallback when Groq returns 429 or network error

- Tests: complex CAUSAL query routes to CausalInferenceSpecialist.
  Self-reflection loop fires when answer has gaps.

**Exit Criteria — All Must Pass Before Next Phase**

- Complex causal query ("why did we switch databases") produces answer
  with cited Decision nodes and CAUSED relationships

- Self-reflection loop correctly fires when test answer has obvious gaps
  — verified in unit test

- Agent status events arrive at SSE stream in correct order — verified
  in integration test

- Groq fallback to Ollama activates when Groq mock returns 429

- Complex query completes within 45 seconds on seeded test data

> **→** *LangGraph.js StateGraph state mutation is the biggest source of
> bugs in this phase. Every node function must return a new state object
> — never mutate the state in place. Test each node function completely
> in isolation before connecting them in the graph.*
>
> **PHASE 9 Intelligence Features** *Drift detection + gap detection +
> expert routing + KTDs + community verification*

**Deliverables**

- GET /graph/drift/:concept endpoint — compares Concept node state at
  two timestamps, calls Groq to narrate changes

- GET /gaps endpoint — queries unanswered Question nodes with ask_count
  \> 3, returns knowledge gap list

- GET /experts/:concept endpoint — queries EXPERTISE_IN relationships,
  returns contribution-weighted expert list

- Knowledge Transfer Document trigger — Celery-equivalent setInterval
  task checks Entity.last_active_at daily. Triggers KTD generation when
  contributor silent for threshold days.

- KTD generator — LangChain.js chain compiles: contribution history,
  concepts owned, decisions made, questions answered, collaboration map

- Community verification workflow — POST /documents/:id/approve tracks
  approvals, promotes trust_tier to "community_verified" on 2 of 3

- Notification system — top 3 contributors (by EXPERTISE_IN weight on
  document subject) notified of new AI-draft document needing review

- Integration test: contributor activity drops → KTD generated and
  stored in MongoDB generated_documents

- Integration test: 2 approvals on AI-draft document → trust_tier
  promoted to community_verified

**Exit Criteria — All Must Pass Before Next Phase**

- GET /gaps returns correct unanswered questions from seeded test data

- GET /experts/:concept returns experts ranked correctly by EXPERTISE_IN
  contribution weight

- GET /graph/drift returns drift detected when two different states
  seeded at different timestamps

- KTD generation integration test passes — correct content compiled from
  seeded contributor data

- Community verification workflow promotes trust_tier correctly after 2
  approvals

> **PHASE 10 Caching & Optimization** *Redis cache + query routing +
> Neo4j index tuning*

**Deliverables**

- Redis cache for query results — cache key is hash of question +
  filters, TTL 300 seconds

- Cache invalidation on new ingestion — when new content added to graph,
  clear related cache keys

- Query routing optimisation — single-concept FACTUAL queries skip agent
  pipeline and go directly to retrieval

- Neo4j query profiling — run PROFILE on all repository queries,
  identify missing indexes

- Add any missing indexes discovered in profiling

- Transformers.js embedding batch processing — embed multiple texts in
  single call where possible

- N+1 query detection — audit all retrieval paths for multiple
  sequential single-node lookups

- Cache hit rate logging — log hits/misses per query type in pino
  structured logs

**Exit Criteria — All Must Pass Before Next Phase**

- Cache hit rate \> 30% on repeated demo queries — verified in
  integration test

- Repeated identical query returns in \< 50ms from cache

- Neo4j PROFILE shows no "DB Hits" on queries that should use indexes

- No N+1 queries in retrieval pipeline under load test

- Performance improvements vs Phase 7 baseline logged in Journal 5.1

> **PHASE 11 DevOps & Observability** *GitHub Actions CI/CD + Render +
> Vercel + health checks*

**Deliverables**

- GitHub Actions 4-stage pipeline: lint+typecheck+test → integration
  tests → Docker build+push → Render deploy

- Integration test stage spins up MongoDB and Neo4j as GitHub Actions
  services

- Docker multi-stage build verified — prod image contains no dev
  dependencies

- Render deployment configured — Docker image from Docker Hub, all env
  vars set

- Vercel deployment configured — React frontend from frontend/ directory

- Structured logging audit — every key operation has a pino log with
  request_id

- Error messages in production scrubbed — no stack traces, no internal
  paths

- HTTPS confirmed on both Render and Vercel deployments

- Security hardening — OWASP checklist from 2.5 verified, npm audit
  clean

**Exit Criteria — All Must Pass Before Next Phase**

- Full CI/CD pipeline runs end-to-end on a test push to main

- Render deployment accessible at production URL with all services
  healthy

- GET /health on production returns all services healthy

- Zero npm audit critical or high vulnerabilities

- No stack traces in production API error responses

> **PHASE 12 Demo Preparation & Documentation** *Demo dataset +
> react-force-graph + README + demo script*

**Deliverables**

- Demo dataset seeded — 5 Concept nodes, 4 Entity nodes, 3 Decision
  nodes (1 reversed), 10 Source nodes, 2 Contradiction nodes, 2
  unanswered Questions. Covers all feature demos.

- react-force-graph component in frontend — temporal slider implemented,
  node color by type, edge thickness by relationship strength, click to
  expand

- Temporal slider demo — scrub from Q1 to Q4 of demo year, watch a
  Decision node disappear when reversed and reappear when the timeline
  passes its valid_from

- Query interface complete — question input, streaming answer display
  via SSE, citation list, confidence score, agent status indicator

- Knowledge gap notification visible on dashboard

- Knowledge Transfer Document demo — trigger manually, show AI-draft,
  approve as two different users, watch trust_tier change

- Full demo run-through completed end-to-end twice without errors

- README complete — setup in under 5 minutes from scratch

- 5 expected interview questions rehearsed from Part 6.3

**Exit Criteria — All Must Pass Before Next Phase**

- react-force-graph temporal slider works correctly — verified on seeded
  demo data

- Full demo run-through without errors — at least twice

- README runnable by someone not on the project in under 5 minutes

- Part 6 Demo Blueprint all sections complete

- You can answer all 5 interview questions in Part 6.3 without notes

> **→** *The temporal slider is the most visually impressive part of
> OmniRAG. Make sure the demo dataset includes a reversed Decision node
> so you can show a node disappearing and reappearing as the slider
> moves through time. This is the single demonstration that most clearly
> shows why temporal validity windows matter.*
>
### 4.3 Weekly Milestone Plan
>
> **ℹ** *One row per week. "Done When" matches a phase exit criterion
> verbatim. "Risk" names the specific thing most likely to cause a slip
> — not generic risks.*

| **Week** | **Phase**     | **Specific Deliverables**                                                                                                                   | **Done When**                                                                                                     | **Risk**                                                                                                    |
|----------|---------------|---------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| 1        | 0             | Blueprint complete, all 8 checklist items verified, Neo4j schema reviewed thoroughly, docker-compose.yml written                            | Another person could build the system from blueprint without questions                                            | Underestimating Neo4j schema complexity — allow 3 days just for Section 2.3                                 |
| 2        | 1–2           | Repository with folder structure, pre-commit hooks, CI passing, Express skeleton with all 18 route stubs, TypeScript strict compile passing | Every endpoint returns 501 with standard envelope. CI green. TypeScript compiles clean.                           | Neo4j Docker image first pull is slow and large — pre-pull before demo day                                  |
| 3        | 3             | All MongoDB collections with Mongoose models, Neo4j schema constraints and indexes, all repository modules, seed script, integration tests  | Seed script creates correct data. Temporal query test passes. All repository tests passing.                       | Neo4j full-text search index creation syntax — test in Browser first                                        |
| 4        | 4–5           | Google OAuth, JWT, webhook signature validation, GitHub webhook ingestion, Slack ingestion, file upload, Redis Streams consumer             | Integration test: GitHub push event in MongoDB within 5 seconds                                                   | Redis Streams consumer group acknowledgment logic — most common debugging trap in Node.js                   |
| 5        | 6 first half  | Transformers.js model loaded, Stage 1 Jaro-Winkler, Stage 2 embedding similarity, Stage 3 graph neighborhood, adversarial test suite        | Entity resolution adversarial test \< 2% false merge rate                                                         | Transformers.js model download size in Docker — add to Dockerfile pre-download step                         |
| 6        | 6 second half | Graph writer with temporal validity, five-type classifier, contradiction detection, decision provenance, EXPERTISE_IN relationship updates  | Temporal query test passes. Contradiction node created in integration test. Decision provenance correct.          | Getting valid_from / valid_until logic right on Decision reversals — test every case in Neo4j Browser first |
| 7        | 7             | BM25 + vector hybrid retrieval, RRF fusion, graph expansion, hallucination guard, confidence scorer, query streaming via SSE                | p95 retrieval \< 200ms. Hallucination guard strips uncorroborated claim in test. SSE streaming first token \< 3s. | MongoDB Atlas Vector Search index activation delay — can take 15+ minutes after creation                    |
| 8        | 8             | LangGraph.js coordinator + 3 specialists, 6 tools, five-step chain with self-reflection, agent status events to SSE                         | Complex causal query returns cited answer within 45 seconds                                                       | LangGraph.js StateGraph state mutation bugs — test each node in isolation first                             |
| 9        | 9–10          | Drift detection, gap detection, expert routing, KTD generation, community verification workflow, Redis cache, query routing optimisation    | KTD generation integration test passes. GET /gaps returns correct data. Cache hit \> 30% on repeated queries.     | KTD trigger timing logic — test with artificially shortened inactivity threshold                            |
| 10       | 11–12         | GitHub Actions CI/CD, Render + Vercel deployment, react-force-graph with temporal slider, demo dataset, demo run-through                    | Production URL accessible. react-force-graph temporal slider works. Full demo run-through twice without errors.   | react-force-graph temporal slider performance on large graph — test with 50+ nodes before demo              |

> **PART 05 — DevOps & Deployment Blueprint**
>
> **⚠** *OmniRAG has 5 services in Docker Compose — Node.js API,
> MongoDB, Neo4j, Redis, Ollama. The Neo4j and Ollama images are large
> (2-3GB combined). Pre-pull these images before any demo.
> docker-compose up on first run takes 5-10 minutes on a slow
> connection.*
>
### 5.1 Docker & Environment Strategy

**Docker Strategy**

Multi-stage Dockerfile. Stage 1 (builder): Node.js 20 Alpine, installs
all dependencies including devDependencies, compiles TypeScript to
dist/. Stage 2 (production): Node.js 20 Alpine slim, copies only
compiled dist/ and node_modules (production only). Smaller production
image, no TypeScript compiler or test frameworks in production.

Ollama runs as a separate service in Docker Compose. The llama3 model
must be pulled on first startup — Makefile includes make pull-models
which runs ollama pull llama3 inside the Ollama container. This is a
one-time 4GB download. Document in README clearly.

**Environment Differences**

| **Config**      | **Dev**                        | **Staging**              | **Prod**                                                 |
|-----------------|--------------------------------|--------------------------|----------------------------------------------------------|
| Log level       | DEBUG                          | INFO                     | WARNING                                                  |
| Neo4j           | Local Docker Compose container | Neo4j AuraDB free tier   | Neo4j AuraDB free tier                                   |
| MongoDB         | Local Docker Compose container | MongoDB Atlas free tier  | MongoDB Atlas free tier                                  |
| Redis           | Local Docker Compose container | Upstash free tier        | Upstash free tier                                        |
| Ollama          | Local Docker Compose container | Not deployed — Groq only | Not deployed — Groq only (Ollama fallback is local only) |
| CORS            | All localhost origins allowed  | Frontend domain only     | Frontend domain only                                     |
| Rate limits     | Disabled                       | Enforced                 | Enforced                                                 |
| TypeScript      | ts-node with hot reload        | Compiled JS              | Compiled JS                                              |
| Query cache TTL | 60 seconds                     | 300 seconds              | 300 seconds                                              |

> **⚠** *Important: Ollama is only available in local development.
> Staging and production use Groq only. This means the Ollama privacy
> classifier fallback only works locally. In production, if Ollama is
> unavailable (it always is), privacy classification must fall back to
> conservative exclusion — exclude all content with classification
> uncertainty.*
>
### 5.2 CI/CD Pipeline

| **Stage**            | **Trigger**                               | **Steps**                                                                                                                                                             | **Failure Action**                                 | **Target Time** |
|----------------------|-------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|-----------------|
| 1: Quality Gate      | Every push to every branch                | Checkout → Node.js 20 setup → npm ci (cached) → ESLint → TypeScript strict compile → Jest unit tests                                                                  | Block PR merge. Comment on PR with failing check.  | \< 3 min        |
| 2: Integration Tests | Every push to every branch                | Spin up MongoDB and Neo4j as GitHub Actions services → Wait for health checks → Run integration tests (real DB connections) → Verify /health returns 200              | Block PR merge. Log failing test output.           | \< 5 min        |
| 3: Build & Push      | Push to main only (after stages 1+2 pass) | Build Docker multi-stage image → Tag with commit SHA and latest → Push to Docker Hub → Verify image pullable                                                          | Alert. Do not deploy.                              | \< 4 min        |
| 4: Deploy            | After Stage 3 on main                     | Trigger Render deploy via API → Poll until healthy → GET /health must return 200 within 90s → Trigger Vercel frontend deploy → Slack notification: success or failure | Render keeps previous deployment. Alert via Slack. | \< 4 min        |

**Rollback Strategy**

Render keeps the last 3 successful deployments. Rollback via Render
dashboard (one click) or Render CLI. Neo4j AuraDB does not support
point-in-time rollback on free tier — schema migrations must be backward
compatible. New properties are optional (nullable), old properties are
never removed in the same release.

### 5.3 Infrastructure, Monitoring & Runbook

**Infrastructure**

Local: 5 services in Docker Compose. Neo4j Browser at localhost:7474 for
graph inspection. Production: Node.js API on Render free tier (spins
down after inactivity — warn in demo). React frontend on Vercel (no
spin-down). MongoDB Atlas free tier, Neo4j AuraDB free tier, Upstash
Redis free tier.

> **⚠** *Render free tier spins down after 15 minutes of inactivity.
> First request after spin-down takes 30-60 seconds. Warm up the demo
> before the interviewer arrives — make a request 2 minutes beforehand.*

**Runbook — When Things Go Wrong**

| **Symptom**                                      | **First Action**                                                                                     | **Escalation**                                                                            | **Fix**                                                                                                   |
|--------------------------------------------------|------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| All API responses return 503                     | Check Render logs. Look for startup error — most likely missing env var or Neo4j connection failure. | Check Neo4j AuraDB dashboard — is it running? Check env vars in Render dashboard.         | Fix missing env var or Neo4j credentials, trigger redeploy                                                |
| Graph queries return empty results               | GET /health — check Neo4j status. Run make seed locally to verify seed data is present.              | Check if Neo4j AuraDB instance was paused (free tier pauses after 3 days inactivity)      | Resume AuraDB instance from dashboard, run seed script                                                    |
| Groq rate limit causing slow queries             | Check pino logs for 429 responses. Count LLM calls in last minute.                                   | Ollama fallback should activate. If not activating, check OLLAMA_BASE_URL env var.        | In production: wait 60 seconds for Groq reset. Locally: verify Ollama running in Docker                   |
| react-force-graph not loading                    | Check browser console for JavaScript errors. Check if GET /graph/nodes returns data.                 | If graph is empty (first time), run make seed. If Neo4j connection failing, check AuraDB. | Seed data and verify API health                                                                           |
| MongoDB Atlas Vector Search returning no results | Check if Atlas Vector Search index is active — Atlas dashboard → Database → Search Indexes           | Index can take 15-30 minutes to activate after creation                                   | Wait for index activation. Verify index on embeddings collection, field name "embedding", 384 dimensions. |

**Backup Strategy**

MongoDB Atlas: daily automatic backups on free tier, 7-day retention.
Neo4j AuraDB: daily automatic backups on free tier. Model artifacts:
Transformers.js model is an npm package — not backed up, reinstalled on
deployment. Ollama llama3: redownloaded on container restart. No
custom-trained models in OmniRAG — all inference is pre-trained.

> **PART 06 — Demo & Presentation Blueprint**
>
> **ℹ** *The react-force-graph temporal knowledge graph visualization is
> the most visually distinctive part of the OmniRAG demo. No other RAG
> project in a portfolio has a visual, interactive, time-scrubable
> knowledge graph. Lead with it.*
>
### 6.1 Demo Storyline & Script

**Demo Storyline**

The story is not "I built a RAG system". The story is: "Knowledge dies
in teams and study groups every day. Decisions made in Slack are
forgotten. Documents pile up in folders nobody opens. People leave and
take everything they know with them. I built OmniRAG to make
organizational and academic knowledge permanently queryable — and I
built the part that nobody else builds, which is the temporal knowledge
graph that knows when things changed and why."

Structure: Problem (30 seconds) → Architecture overview (60 seconds) →
Live knowledge graph visualization (2 minutes — most visually impressive
part) → Live query demo (2 minutes) → Temporal slider demo (1 minute —
the most technically impressive part) → Knowledge Transfer Document demo
(1 minute) → Expert routing demo (30 seconds) → Failure story from
building it (60 seconds) → Scale discussion (30 seconds).

**Step-by-Step Demo Script**

14. Open the React dashboard. Show the react-force-graph visualization —
    a web of connected nodes. Say: "This is OmniRAG's knowledge graph.
    Every node is a piece of knowledge that was extracted automatically
    from GitHub commits, Slack messages, and uploaded documents. The
    connections between them were inferred, not manually created."

15. Click on a Decision node. Show the expanded panel — source document,
    who decided it, when, confidence score, and related concepts. Say:
    "Every piece of knowledge has a full provenance — who said it, when,
    from which source, and how confident we should be based on how many
    sources agree."

16. Move the temporal slider backward 3 months. Watch a Decision node
    disappear. Say: "This decision was reversed in the period I just
    jumped past. OmniRAG knows what was true at every point in time —
    not just what is true today." Move slider forward — watch the node
    reappear, then disappear at the reversal point.

17. Type "why did we move away from PostgreSQL" in the query interface.
    Show the agent status indicator as specialists run. First token
    streams within 3 seconds. Show the full answer with citation links
    to specific Slack thread and GitHub PR.

18. Type "who knows most about authentication" in the query interface.
    Show expert routing result with contribution-weighted scores. Say:
    "This is not self-reported expertise — it is derived from who
    actually contributed knowledge about authentication across all three
    sources."

19. Go to Documents tab. Show an AI-draft Knowledge Transfer Document
    for a contributor whose activity dropped. Say: "When a team member
    goes quiet — graduation, leaving the company, going on leave —
    OmniRAG generates this document automatically. It compiles
    everything they ever contributed. Two people need to approve it
    before it is trusted."

20. Click Approve on the document as one user. Show approval count
    change. Say: "The community verification workflow means no
    AI-generated document is trusted until real humans have validated
    it."

21. Show the Knowledge Gaps panel — unanswered questions that appeared
    multiple times. Say: "OmniRAG noticed this question was asked 4
    times with no answer. It surfaced it as a gap and identified the
    expert most likely to answer it."

22. Ask: "How long did it take to set this up?" Answer: "docker-compose
    up and make seed — about 8 minutes from scratch." Show the /health
    endpoint returning all services green.

### 6.2 Demo Environment & Backup Plan

**Demo Dataset**

Seed script creates: 3 services — payment-team, backend-team,
study-group-cs. 5 Concept nodes — "authentication", "PostgreSQL",
"deployment pipeline", "dynamic programming", "operating systems". 4
Entity nodes — 3 engineers and 1 student. 3 Decision nodes including one
that was reversed 3 months ago (essential for temporal slider demo). 10
Source nodes from all three source types. 2 Contradiction nodes. 2
unanswered Question nodes with ask_count of 4. 2 AI-draft Knowledge
Transfer Documents (one pre-approved by 1 person, one fresh draft). All
created with timestamps spread over the past 6 months for realistic
temporal slider demo.

Command: make seed — takes approximately 60 seconds.

**Backup Plans**

- Groq API rate limit hit during demo: Ollama fallback activates
  locally. Query takes 3-4 minutes instead of 20 seconds. Say: "The
  system automatically fell back to the local model — notice it is still
  working, just slower. This is the offline capability."

- Render deployment spinning down: demo locally with docker-compose up.
  Always keep local demo ready. Warm up Render 2 minutes before demo.

- react-force-graph slow on large graph: demo on seeded dataset only (\<
  20 nodes). Never demo on a real populated graph without testing
  performance first.

- Neo4j AuraDB paused (free tier pauses after 3 days): have local Docker
  Compose demo always ready. AuraDB resumes in ~30 seconds from
  dashboard but this is embarrassing live.

- Temporal slider not working visually: have a screenshot of
  before/after states as backup. Explain the temporal query manually.

### 6.3 Interview Prep

**30-Second Pitch**

OmniRAG is a temporal knowledge graph system that automatically connects
GitHub activity, Slack decisions, and uploaded documents into a
permanently queryable intelligence layer. It resolves identities across
sources using a three-stage pipeline, detects when knowledge changes or
contradicts itself, generates answers with cited sources and
graph-derived confidence scores, and creates Knowledge Transfer
Documents automatically when contributors go quiet. The key
differentiator is the temporal graph — every piece of knowledge carries
a valid_from and valid_until timestamp so you can query what the team
believed at any point in the past, not just today.

**Why This Project Stands Out**

- Temporal knowledge graph — not just vector search over documents. The
  graph knows when decisions were made, reversed, and superseded. The
  temporal slider in the demo is something no other RAG portfolio
  project has.

- Three-stage entity resolution — resolving "ps2024", "Priya S", and
  "priya.sharma@company.com" to the same person across GitHub, Slack,
  and documents without manual configuration. The adversarial test set
  (200 similar-but-different name pairs) shows you tested it properly.

- Graph-derived confidence — most RAG systems trust the LLM to
  self-report confidence. OmniRAG derives confidence from source_count,
  recency, contradiction_count, and verification_status — all measurable
  properties of the graph, not the LLM's guess.

- Knowledge Transfer Documents triggered by activity patterns — shows
  product thinking and understanding of the real organizational problem,
  not just the technical one.

- Contradiction detection with typed categories — direct_factual,
  temporal, cross_source_ownership. Shows you thought about failure
  modes in knowledge quality, not just happy path knowledge retrieval.

| **Expected Question**                        | **Prepared Answer**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|----------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Walk me through the architecture.            | Modular monolith with event-driven ingestion. A single Node.js + Express process with feature-based modules. GitHub webhooks, Slack events, and file uploads arrive, get validated and published to Redis Streams consumer groups. A worker process consumes from the stream, runs the privacy classifier on Ollama locally, then the three-stage entity resolution pipeline, then writes to the Neo4j temporal knowledge graph with validity windows. Queries come through the hybrid retrieval pipeline — BM25 and vector search fused via RRF, expanded via Neo4j graph traversal, then through the LangGraph.js agent pipeline for complex queries. Answers are streamed token by token via Server-Sent Events. The react-force-graph frontend visualizes the knowledge graph with a temporal slider.                                                                    |
| Why Neo4j instead of just vector search?     | Vector search finds similar content. Neo4j finds causally connected content. When someone asks "why did we switch databases", the answer requires traversing CAUSED and SUPERSEDES relationships across multiple nodes — a PostgreSQL decision that was informed by a Slack discussion that referenced a benchmark document. Vector search finds text similar to "switching databases" but misses the causal chain. Neo4j traverses it in O(1) per hop regardless of data size. The specific property that locked the decision was that relationship types — CAUSED, CONTRADICTS, SUPERSEDES — are first-class schema elements in Neo4j, not foreign key conventions in a relational database.                                                                                                                                                                               |
| How does entity resolution work?             | Three stages running in sequence with confidence thresholds. Stage 1 — Jaro-Winkler lexical similarity at under 5ms: catches name variations like "Priya" and "priya_s". Auto-merge above 0.88. Stage 2 — cosine similarity of Transformers.js all-MiniLM-L6-v2 embeddings at under 100ms: catches semantic aliases where two names sound like different people but mean the same concept. Stage 3 — Neo4j graph neighborhood at under 200ms: "ps2024" on GitHub and "Priya Sharma" on Slack share 7 common graph neighbors — same PRs, same Slack channels — which raises confidence enough to merge them even though they share zero lexical or semantic similarity. Every merge is a reversible graph event — wrong merges can be undone. I also tested this with an adversarial test set of 200 similar-but-different names to verify the false merge rate was under 2%. |
| What is the temporal validity window system? | Every node in the graph that can change over time carries valid_from and valid_until timestamps. When a decision is reversed, I set valid_until on the old Decision node and create a new one with valid_from at the reversal timestamp and a SUPERSEDES relationship pointing back. The old decision is preserved — it is still queryable. To retrieve the graph state at any past timestamp: MATCH (n) WHERE n.valid_from \<= \$timestamp AND (n.valid_until IS NULL OR n.valid_until \> \$timestamp). This gives you the complete graph state at any point in time without storing full snapshots. The alternative — snapshots — would require storing gigabytes of data. The validity window approach stores only the changes in O(changes) space, not O(changes × graph size).                                                                                          |
| How does the hallucination guard work?       | After the LLM generates an answer, before returning it to the user, I parse the answer into discrete factual claims. For each claim, I check whether there exists a source node in the retrieved graph context that supports it. Any claim I cannot trace to a specific retrieved node gets stripped from the answer. The confidence score is then derived from properties of the remaining supported claims — how many source nodes agree, how recent the most recent source is, whether there are active contradiction nodes on the relevant concepts, and whether the supporting source nodes have been community-verified. The key insight is that the LLM's own confidence score is unreliable — studies show LLMs are frequently most confident when they are wrong. Graph-derived confidence is deterministic and measurable.                                         |

> **PART 07 — Appendices**
>
> **ℹ** *Fill this section as you build. The decision log is your
> interview answer source. Update it the same day you make a decision —
> not at project end.*
>
### 7.1 Environment Variables Reference
>
> **⚠** *Rule R-51: Secrets in environment variables only. Rule R-36:
> App validates all on startup. Update .env.example whenever a new
> variable is added.*

| **Variable**           | **Description**                                             | **Example Value**                                   | **Required** |
|------------------------|-------------------------------------------------------------|-----------------------------------------------------|--------------|
| MONGODB_URI            | MongoDB connection string — Atlas free tier in staging/prod | mongodb+srv://user:pass@cluster.mongodb.net/omnirag | Required     |
| NEO4J_URI              | Neo4j connection string — AuraDB free tier URI              | neo4j+s://xxxxxxxx.databases.neo4j.io               | Required     |
| NEO4J_USERNAME         | Neo4j AuraDB username                                       | neo4j                                               | Required     |
| NEO4J_PASSWORD         | Neo4j AuraDB password                                       | ...                                                 | Required     |
| REDIS_URL              | Redis connection string — Upstash free tier                 | rediss://default:token@host.upstash.io:6379         | Required     |
| GROQ_API_KEY           | Groq API key — free at console.groq.com                     | gsk\_...                                            | Required     |
| GROQ_MODEL_FAST        | LLaMA model for classification tasks                        | llama-3.1-8b-instant                                | Required     |
| GROQ_MODEL_SMART       | LLaMA model for reasoning and generation                    | llama-3.1-70b-versatile                             | Required     |
| OLLAMA_BASE_URL        | Ollama local server — used for privacy classifier           | http://localhost:11434                              | Required     |
| GOOGLE_CLIENT_ID       | Google OAuth 2.0 client ID                                  | 12345.apps.googleusercontent.com                    | Required     |
| GOOGLE_CLIENT_SECRET   | Google OAuth 2.0 client secret                              | GOCSPX-...                                          | Required     |
| JWT_PRIVATE_KEY        | RSA private key for JWT signing (RS256)                     | -----BEGIN RSA PRIVATE KEY-----...                  | Required     |
| JWT_PUBLIC_KEY         | RSA public key for JWT verification                         | -----BEGIN PUBLIC KEY-----...                       | Required     |
| GITHUB_WEBHOOK_SECRET  | HMAC secret for GitHub webhook validation                   | random-32-char-string                               | Required     |
| SLACK_SIGNING_SECRET   | Slack signing secret for event validation                   | ...                                                 | Required     |
| ENTITY_MERGE_THRESHOLD | Auto-merge confidence threshold for entity resolution       | 0.85                                                | Required     |
| GRAPH_EXPANSION_HOPS   | Number of Neo4j hops in graph expansion step                | 2                                                   | Required     |
| KTD_INACTIVITY_DAYS    | Days of contributor inactivity before KTD trigger           | 14                                                  | Required     |
| FRONTEND_URL           | Allowed CORS origin                                         | http://localhost:3000                               | Required     |
| LOG_LEVEL              | Logging verbosity                                           | INFO                                                | Required     |
| PORT                   | Express server port                                         | 3001                                                | Required     |
| NODE_ENV               | Runtime environment — affects CORS, rate limits             | development                                         | Required     |

### 7.2 Decision Log
>
> **ℹ** *Every technology choice, threshold decision, and architectural
> pivot goes here. Fill the same day the decision is made.*

| **Date** | **Decision**                             | **Chosen**                                   | **Rejected**                     | **Reason**                                                                                                                                     |
|----------|------------------------------------------|----------------------------------------------|----------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| Phase 0  | Graph database                           | Neo4j AuraDB                                 | PostgreSQL + recursive CTEs      | Multi-hop traversal is O(1) in Neo4j vs exponentially slow in PostgreSQL. Relationship types are first-class schema elements.                  |
| Phase 0  | Vector search                            | MongoDB Atlas Vector Search                  | Pinecone / Qdrant                | Runs inside existing MongoDB — zero extra service, zero extra connection pool. Sufficient performance at portfolio scale.                      |
| Phase 0  | Embedding model                          | Transformers.js all-MiniLM-L6-v2             | OpenAI text-embedding-3-small    | Zero API cost, zero network latency, works offline, runs in same Node.js process. Critical for entity resolution performance.                  |
| Phase 0  | LLM provider                             | Groq LLaMA 3.1                               | OpenAI GPT-4o                    | Free tier with 500 tok/sec. Speed enables five-step prompt chain within latency targets. Ollama as local fallback.                             |
| Phase 0  | Agent framework                          | LangGraph.js                                 | LangChain.js sequential chain    | LangGraph.js handles stateful graph-based coordination — coordinator decides dynamically. LangChain.js sequential chain is fixed order.        |
| Phase 0  | Architecture                             | Modular Monolith with event-driven ingestion | Microservices                    | Solo developer — microservices adds service discovery, distributed tracing, inter-service auth overhead with no scaling benefit at this scope. |
| Phase 0  | Excluded: Knowledge Spaces multi-tenancy | Single workspace v1                          | Full multi-tenancy               | Architecture supports spaceId partitioning but building it in v1 delays core graph features. Deferred to v2.                                   |
| Phase 0  | Excluded: Socket.io Live Knowledge Rooms | Not in v1                                    | Real-time collaborative querying | Too complex — real-time + graph updates + room management simultaneously. Deferred to v2.                                                      |

Continue adding rows as decisions are made during build — every
threshold value, every library choice, every schema change decision
belongs here.

### 7.3 Tech Debt Log & Future Roadmap

| **ID**   | **Description**                                                                                                     | **Location**                | **Why Deferred**                                                         | **Fix Plan**                                                                                                                  | **Priority** |
|----------|---------------------------------------------------------------------------------------------------------------------|-----------------------------|--------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|--------------|
| DEBT-001 | Knowledge Spaces multi-tenancy — spaceId partitioning on Neo4j graph labels and MongoDB collections not implemented | src/database/, neo4j schema | Core graph features take priority in v1                                  | Add spaceId: string property to all nodes. Partition Neo4j with workspace label prefixes. Add JWT space-scoped claims.        | Medium       |
| DEBT-002 | Discord, Notion, Google Drive connectors — only 3 sources in v1                                                     | src/ingestion/              | Three sources done deeply is stronger than ten sources shallowly         | Add connector per source after v1 proven. Each connector follows the same UnifiedEvent normaliser pattern.                    | Medium       |
| DEBT-003 | Socket.io Live Knowledge Rooms — real-time collaborative querying not built                                         | src/websocket/              | Too complex — real-time + graph updates + room management simultaneously | After core query pipeline stable. Build as progressive enhancement on top of existing SSE stream.                             | Low          |
| DEBT-004 | Contribution Graph Analytics dashboard — data exists, no dedicated UI                                               | frontend/                   | Time — data available via query endpoints but no visualisation built     | Add dedicated analytics view to React dashboard using existing GET /experts and EXPERTISE_IN relationship data.               | Low          |
| DEBT-005 | Onboarding Intelligence — dependency-ordered concept paths for new members                                          | src/intelligence/           | Overlaps with KTD feature in v1                                          | Build on top of expert routing and EXPERTISE_IN graph in v2 after KTD system proven.                                          | Low          |
| DEBT-006 | Prometheus + Grafana observability — not included in v1                                                             | monitoring/                 | Not core story for OmniRAG unlike SentinelAI                             | Add pino-prometheus adapter and basic Grafana dashboard in v2 if SentinelAI observability skills need demonstrating here too. | Low          |

### 7.4 Local Setup Guide
>
> **ℹ** *Done when: a person not on this project can run it from scratch
> in under 5 minutes. Test this with someone else before considering it
> complete.*

**Prerequisites**

- Docker Desktop installed and running

- Git installed

- Make installed (pre-installed on macOS/Linux)

- Groq API key — free at console.groq.com (2 minutes, no credit card)

- Google OAuth credentials — Google Cloud Console → APIs & Services →
  Credentials → Create OAuth 2.0 Client ID → Authorized redirect URI:
  http://localhost:3001/api/v1/auth/google/callback

- MongoDB Atlas free cluster — atlas.mongodb.com (5 minutes). Enable
  Atlas Vector Search. Create database user.

- Neo4j AuraDB free instance — console.neo4j.io (3 minutes). Save the
  connection URI, username, and password.

**Setup Steps**

23. git clone https://github.com/yourname/omnirag && cd omnirag

24. cp .env.example .env — fill in GROQ_API_KEY, GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET, MONGODB_URI, NEO4J_URI, NEO4J_USERNAME,
    NEO4J_PASSWORD. All other values work as defaults.

25. Generate JWT keys: openssl genrsa -out jwt_private.pem 2048 &&
    openssl rsa -in jwt_private.pem -pubout -out jwt_public.pem — paste
    multiline values into .env

26. make dev — starts all 5 Docker services. First run downloads Neo4j
    (1.5GB) and Ollama images (2GB) — takes 5-10 minutes on first run,
    30 seconds thereafter.

27. make pull-models — pulls llama3 model into Ollama container.
    One-time 4GB download. Takes 3-5 minutes.

28. make seed — creates demo data in Neo4j and MongoDB. Takes
    approximately 60 seconds.

29. Verify: GET http://localhost:3001/health → { status: "healthy",
    services: { mongodb: "connected", neo4j: "connected", redis:
    "connected", ollama: "connected" } }

30. Open http://localhost:3000 — React dashboard. Sign in with Google.
    Knowledge graph visualization should show seeded demo nodes.

Total setup time: approximately 15 minutes first run (model downloads),
3 minutes thereafter.

> **PART 08 — AI / ML Blueprint**
>
> **🤖** *OmniRAG uses no trained or fine-tuned ML models — all ML
> inference is pre-trained. The intelligence comes from graph
> architecture, retrieval design, and agent coordination — not model
> training. This makes OmniRAG's AI story fundamentally different from
> SentinelAI's. Where SentinelAI demonstrates trained ML, OmniRAG
> demonstrates advanced RAG engineering, agent architecture, and AI
> safety patterns.*
>
### 8.1 AI Component Inventory
>
> **🤖** *Rule R-93: Every AI component has a defined role, inputs,
> output contract, and non-AI fallback before building. Rule R-95:
> Non-AI fallback must work before the AI version is built.*

| **Component**             | **Type**                                         | **Role**                                                                                                                                                                                                     | **Input**                                                                     | **Output Contract**                                                                                                            | **Non-AI Fallback**                                                                                                                                       |
|---------------------------|--------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| PrivacyClassifier         | Ollama llama3 local                              | Classifies every ingested content item into one of four privacy levels before it touches the graph. Runs locally — sensitive content never sent externally.                                                  | Content text string (up to 1000 chars)                                        | privacy_level: "public_knowledge" \| "internal_knowledge" \| "sensitive_personal" \| "hr_matter"                               | Keyword matching: list of PII-related terms → sensitive_personal. Default: internal_knowledge.                                                            |
| MessageTypeClassifier     | Groq LLaMA 3.1 8B                                | Classifies every ingested message into one of five types. High frequency — runs on every Slack message and GitHub comment ingested.                                                                          | Normalised content text + source_type + metadata                              | message_type: "DECISION" \| "QUESTION" \| "SOLUTION" \| "CONTEXT" \| "NOISE", confidence: float                                | Rule-based: contains "we decided", "going with", "agreed on" → DECISION. Contains "?" → QUESTION. Short, no substance → NOISE.                            |
| TransformersJsEmbedder    | Pre-trained all-MiniLM-L6-v2 via Transformers.js | Generates 384-dimensional semantic embeddings for entity resolution Stage 2 and for MongoDB Atlas Vector Search storage. Runs in Node.js process — zero API cost, zero latency.                              | String (up to 512 tokens — truncated if longer)                               | embedding: Float32Array\[384\] — L2-normalised. embedding_model: "all-MiniLM-L6-v2" always.                                    | N/A — Transformers.js is a local npm package, no external dependency. No fallback needed.                                                                 |
| EntityResolutionEmbedder  | Same TransformersJsEmbedder                      | Used specifically in Stage 2 of entity resolution — embeds candidate entity names and computes cosine similarity to determine if two names refer to the same person.                                         | Two entity name strings                                                       | similarity_score: float 0-1, above_threshold: boolean                                                                          | Fall through to Stage 3 graph neighborhood if embedding similarity is inconclusive.                                                                       |
| QueryTypeClassifier       | Groq LLaMA 3.1 8B (or rule-based)                | Classifies every incoming query to route it to the right pipeline. Simple FACTUAL queries skip agent pipeline. CAUSAL and COMPLEX queries route to full LangGraph.js agents.                                 | Query string                                                                  | query_type: "FACTUAL" \| "CAUSAL" \| "TEMPORAL" \| "EXPERTISE" \| "COMPLEX", complexity_score: float                           | Rule-based: contains "why", "how did" → CAUSAL. Contains "when", "in 2023" → TEMPORAL. Contains "who knows" → EXPERTISE. Short simple question → FACTUAL. |
| GraphTraversalSpecialist  | LangGraph.js node + Groq LLaMA 3.1 70B           | Handles FACTUAL queries — direct concept lookups, decision history, source citation. Calls search_knowledge_graph and get_decision_history tools.                                                            | QueryState with query + retrieved_context                                     | specialist_output: { answer_fragment: string, confidence: float, source_node_ids: string\[\], tools_called: string\[\] }       | Direct Neo4j query on concept name and return top 3 matching nodes with their relationships.                                                              |
| CausalInferenceSpecialist | LangGraph.js node + Groq LLaMA 3.1 70B           | Handles CAUSAL queries — traces CAUSED and SUPERSEDES relationships. Calls find_causal_chain tool. Reasons about decision sequences.                                                                         | QueryState with causal query + graph traversal results                        | specialist_output: { causal_chain: CausalLink\[\], confidence: float, source_node_ids: string\[\] }                            | Return all CAUSED relationships from top matching Decision node without LLM reasoning.                                                                    |
| SynthesisSpecialist       | LangGraph.js node + Groq LLaMA 3.1 70B           | Handles COMPLEX queries requiring multi-source synthesis. Assembles findings from multiple retrieval results into a coherent answer.                                                                         | QueryState with all retrieved context                                         | specialist_output: { synthesised_answer: string, confidence: float, source_node_ids: string\[\], gaps_identified: string\[\] } | Concatenate top 3 retrieval results with source labels. No synthesis.                                                                                     |
| Coordinator               | LangGraph.js StateGraph + Groq LLaMA 3.1 70B     | Entry point for agent pipeline. Reads query type, assigns to correct specialist, manages five-step chain execution, runs self-reflection step.                                                               | Initial QueryState: { query, query_type, retrieved_context }                  | Final QueryState: { answer, citations, confidence, agents_used, self_reflection_triggered: bool }                              | Direct call to SynthesisSpecialist without routing logic.                                                                                                 |
| HallucinationGuard        | Deterministic TypeScript (no LLM)                | Validates every factual claim in the generated answer against retrieved source nodes. Strips claims not traceable to a specific node. This is the safety boundary between LLM output and user-facing answer. | Generated answer text + Set of retrieved source node IDs                      | validated_answer: string (claims stripped), rejected_claims: string\[\], claims_checked: int                                   | N/A — this IS the fallback for LLM hallucinations. It is always deterministic.                                                                            |
| ConfidenceScorer          | Deterministic TypeScript formula (no LLM)        | Derives a confidence score for each answer from graph properties. Never uses LLM self-reported confidence.                                                                                                   | Set of source node IDs referenced in answer + Neo4j properties of those nodes | confidence: float 0-1, confidence_breakdown: { source_count, recency_score, contradiction_penalty, verification_bonus }        | N/A — deterministic formula, no LLM involved.                                                                                                             |
| SelfReflectionStep        | LangGraph.js node + Groq LLaMA 3.1 8B            | Step 4 of the five-step chain. LLM checks its own answer: "Is this complete? Does it address the question? Are there obvious gaps?" If gaps found, loop back to Step 1.                                      | Synthesised answer + original query                                           | self_reflection: { complete: boolean, gaps: string\[\], loop_back: boolean }                                                   | Return complete: true always — skip the reflection step. Adds latency for little gain on simple queries.                                                  |
| KTDGenerator              | LangChain.js chain + Groq LLaMA 3.1 70B          | Generates Knowledge Transfer Document when contributor activity drops. Compiles contribution history, owned concepts, decisions made, questions answered, collaboration patterns.                            | Entity node ID + full contribution history from Neo4j                         | ktd_content: string (structured document, 800-2000 words), generated_at: datetime                                              | Fixed template with contribution data inserted into structured sections. No LLM synthesis.                                                                |
| DriftNarrator             | Groq LLaMA 3.1 70B single call                   | Narrates the semantic drift of a concept — called after the deterministic drift detection identifies changes. Explains what changed and why in plain English.                                                | Concept name + list of detected changes with timestamps                       | drift_narrative: string (200-400 words, plain English explanation)                                                             | Structured diff format: "In Q3 2023, \[property\] changed from \[old_value\] to \[new_value\]". No narrative.                                             |

| **LLM Task**                                          | **Model**               | **Provider** | **Why This Model**                                                                                          | **Fallback**                                                |
|-------------------------------------------------------|-------------------------|--------------|-------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| Message type classification (high frequency)          | llama-3.1-8b-instant    | Groq         | Fast, cheap, good enough for 5-class classification. Runs on every ingested message.                        | Rule-based classifier — decision keywords, question markers |
| Query type classification                             | llama-3.1-8b-instant    | Groq         | Same — simple classification, speed matters                                                                 | Rule-based classifier                                       |
| Agent reasoning — all three specialists + coordinator | llama-3.1-70b-versatile | Groq         | Complex causal reasoning and synthesis requires the larger model. 70B produces better multi-step reasoning. | Ollama llama3 local                                         |
| Self-reflection step                                  | llama-3.1-8b-instant    | Groq         | Self-reflection is essentially a classification — complete/incomplete. 8B is sufficient.                    | Return complete: true — skip reflection                     |
| KTD and drift narration generation                    | llama-3.1-70b-versatile | Groq         | Narrative generation requires coherent long-form output. Quality matters.                                   | Ollama llama3 local                                         |
| Privacy classification                                | llama3 via Ollama       | Local        | Sensitive content MUST NOT leave the machine. Local Ollama is non-negotiable for this task.                 | Keyword matching fallback                                   |

### 8.2 RAG Architecture
>
> **🤖** *OmniRAG implements the most advanced form of RAG in this
> portfolio. Standard RAG: query → vector search → generate. OmniRAG
> RAG: query → BM25 + vector search in parallel → Reciprocal Rank Fusion
> → Neo4j graph expansion → temporal filter → hallucination guard →
> graph-derived confidence. Each stage addresses a failure mode of the
> previous.*

**Document Corpus**

The corpus is the entire Neo4j knowledge graph plus the MongoDB
embeddings collection. It is not static — it grows with every ingested
event. At ingestion time, every normalised event creates or updates
nodes in Neo4j and a corresponding embedding entry in MongoDB. The
corpus is always current. There is no batch indexing step — the graph IS
the index.

Corpus size depends on team/group usage. A 10-person team with active
GitHub and Slack usage generates approximately 200-500 new nodes per
week. A study group uploading lecture notes for a semester generates
50-200 nodes per upload session.

**Chunking Strategy**

Variable chunking based on source type. GitHub commits: the commit
message and diff summary are treated as one chunk per commit — not split
further. Slack messages: each message is one chunk. Thread context is
preserved by including parent message ID in the node metadata — the
graph REPLIED_IN relationship captures thread structure better than text
chunking. Uploaded documents: split into 400-token chunks with 50-token
overlap using a sentence-aware splitter (split at sentence boundaries
within the 400-token window, not mid-sentence). Each chunk becomes a
Source node in Neo4j and an embedding in MongoDB.

> **WHY:** 400-token chunks with 50-token overlap is the industry
> standard for RAG. The 50-token overlap ensures that a concept spanning
> a chunk boundary appears in at least one chunk completely.
> Sentence-aware splitting ensures chunks are coherent text not cut
> mid-sentence.

**Embedding Model — Locked**

Model: sentence-transformers/all-MiniLM-L6-v2 via Transformers.js v3.
Dimensions: 384. Similarity metric: cosine. Loaded as singleton on
server startup. Model version pinned in package.json — never
auto-upgrade.

> **⚠** *Rule R-101: Changing the embedding model requires re-embedding
> the entire corpus. This is a database migration not a config change.
> If all-MiniLM-L6-v2 is ever upgraded, ALL embeddings in MongoDB and
> ALL embedding-based entity resolution scores must be recomputed. Plan
> this as a versioned migration with a transition period.*

**Vector Store**

MongoDB Atlas Vector Search on the embeddings collection. HNSW index
with 384 dimensions, cosine similarity metric. Rejected alternatives:
Pinecone (external service, vendor lock-in), Qdrant (extra Docker
container), Weaviate (too heavy), pgvector (would require adding
PostgreSQL as a 4th database when MongoDB is already handling document
storage).

**Retrieval Strategy — Three Stages**

Stage 1 — Parallel retrieval. BM25 via Neo4j FULLTEXT index and
Transformers.js vector search via MongoDB Atlas Vector Search run
simultaneously. BM25 weights higher for queries containing exact
technical terms (error codes, service names, proper nouns). Vector
search weights higher for conceptual queries. Query type classifier
determines the weighting.

Stage 2 — Reciprocal Rank Fusion. Combines BM25 and vector rankings. RRF
formula: score(d) = sum(1 / (k + rank_in_system)) where k=60. RRF chosen
over score normalisation because BM25 and vector scores are on
incompatible scales — RRF ranks by position not magnitude, which avoids
normalisation errors.

Stage 3 — Neo4j graph expansion. Top 5 RRF results mapped to their
corresponding Neo4j nodes. Traversed 1-2 hops via MENTIONED_IN, CAUSED,
SUPERSEDES, EXPERTISE_IN relationships. Connected nodes added to result
set with lower weight than direct matches. This is what finds causally
connected knowledge that neither BM25 nor vector search alone would
retrieve.

Stage 4 — Temporal filtering. For FACTUAL queries (current state),
outdated nodes (valid_until \< NOW()) ranked down. For TEMPORAL queries
(historical state), all nodes included and ranked by proximity to the
requested timestamp.

k value: top 10 results from each of BM25 and vector search fed to RRF.
Top 5 RRF results expanded via graph. Final context window contains 5-15
nodes depending on graph expansion.

**RAG Quality Metrics — Rule R-97**

| **Metric**                           | **Target**                                                                                        | **How Measured**                                                                      | **Alert If**                                                                        |
|--------------------------------------|---------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| Retrieval Precision@3                | \> 0.70 after corpus has 50+ nodes                                                                | Manual relevance judgment on 30-query test set run monthly                            | Falls below 0.50                                                                    |
| Retrieval latency p95                | \< 200ms for full hybrid retrieval pipeline                                                       | Logged per query in pino structured logs — timing wrapper around retrieval module     | Exceeds 500ms consistently                                                          |
| Hallucination guard rejection rate   | \< 8% of claims stripped                                                                          | HallucinationGuard logs every rejection. Count / total checked over last 100 queries. | Exceeds 15% — LLM prompt or retrieved context quality issue                         |
| Graph-derived confidence correlation | Confidence score \> 0.80 for answers that are subjectively correct, \< 0.60 for answers with gaps | Manual evaluation on 20 queries quarterly                                             | High confidence answers consistently wrong — confidence formula needs recalibration |
| Agent pipeline completion rate       | \> 95% of queries complete without timeout or error                                               | Error rate logged per query type in pino logs                                         | Falls below 90% — Groq availability or timeout issue                                |

### 8.3 Model Evaluation Strategy

Not applicable for standard ML model training — OmniRAG uses only
pre-trained foundation models with no fine-tuning. However, the
following components require quality evaluation:

**Entity Resolution Quality**

Evaluation dataset: hand-crafted adversarial test set of 200 entity name
pairs. 100 pairs that SHOULD merge (same person, different formats). 100
pairs that SHOULD NOT merge (similar names, different people). Split:
all 200 used for evaluation since no training is done — this is a
threshold calibration exercise not a train/test split.

Primary metric: false merge rate (pairs that should not merge but did).
Target: \< 2%.

Baseline: Stage 1 Jaro-Winkler alone without Stages 2 and 3. Expected
baseline false merge rate: ~8%. Three-stage pipeline should reduce this
to \< 2%.

Threshold calibration: run the 200 test pairs through Stage 1 alone,
then Stage 1+2, then all three stages. Plot false merge rate vs true
merge rate at each threshold. Choose threshold at the knee of the curve.
Log the final threshold value and false merge rate in the Engineering
Journal.

**RAG Evaluation**

Manual evaluation set: 30 question-answer pairs created from the seeded
demo data. Each question has a known correct answer traceable to a
specific Neo4j node. For each query: run the full retrieval pipeline,
check whether the correct node appears in the top 3 results
(Precision@3), check whether the generated answer contains the correct
information, check whether the hallucination guard correctly allowed the
correct claims and rejected fabricated ones.

Experiment tracking: no MLflow needed for OmniRAG since no model
training. Evaluation results logged in the Engineering Journal Part 5.1
with date, corpus size at evaluation time, and all metric values. Rerun
evaluation after every significant change to retrieval logic or prompt
templates.

**Drift Detection for AI Quality**

The only "model drift" applicable to OmniRAG is hallucination rate drift
— if the percentage of LLM claims rejected by the hallucination guard
starts increasing, it indicates either the Groq model has changed, the
retrieved context quality has degraded, or the prompt templates need
updating. Track hallucination rejection rate as a rolling 7-day average.
If average exceeds 15%, investigate.

### 8.4 Synthetic Data Strategy

Not applicable for model training — OmniRAG trains no models.

However, the seed script (make seed) creates synthetic knowledge graph
data for development and demo purposes. This is synthetic CORPUS data
not synthetic TRAINING data. The distinction matters:

- Synthetic training data: created to train an ML model. Biases in this
  data directly affect model behaviour. Requires explicit transition
  plan.

- Synthetic corpus data (OmniRAG): created to populate the knowledge
  graph for development and demo. Does not train any model. Can be
  deleted and replaced with real data at any time without affecting
  system behaviour.

Seed script documentation — src/database/seeds/README.md explains every
node created, why each exists, and which feature it demonstrates. The
reversed Decision node is essential for the temporal slider demo. The
Contradiction node demonstrates contradiction detection. Both must be
preserved in the seed script.

### 8.5 Hallucination Guard & Confidence Safety
>
> **🤖** *OmniRAG has no autonomous real-world actions — no
> self-healing, no automated remediation. The safety concern is
> different: preventing the AI from returning false information to
> users. The Hallucination Guard and graph-derived confidence scoring
> are the safety gates. Rule R-90: LLM output that reaches the user must
> pass a deterministic validation layer first.*

**Hallucination Guard Design**

The HallucinationGuard in src/retrieval/hallucination-guard.ts is a
deterministic TypeScript function — no LLM involved. It runs on every
generated answer before it is returned to the user.

31. Claim extraction: parse the generated answer into discrete factual
    claims. Pattern: sentences containing assertion verbs (is, was,
    decided, caused, showed, according to) are treated as factual
    claims.

32. Source node mapping: for each claim, extract the specific Neo4j
    node(s) it references (by concept name, entity name, or decision
    statement).

33. Evidence verification: check whether each referenced node exists in
    the set of nodes retrieved during the retrieval phase. A claim about
    a concept that was NOT in the retrieved context is uncorroborated.

34. Rejection: uncorroborated claims are stripped from the answer text,
    NOT flagged as low-confidence. Stripped entirely. The user never
    sees a claim that cannot be traced to a retrieved source node.

35. Guard output: validated_answer (cleaned text), rejected_claims
    (logged for quality monitoring), claims_checked (total count).

> **WHY:** The distinction between "flag as low confidence" and "strip
> entirely" is important. A low-confidence claim still reaches the user
> and may be acted upon. A stripped claim never reaches the user. For a
> knowledge system where users may make decisions based on answers, the
> safer choice is to strip and let the user ask a more specific question
> rather than to present a hallucinated claim with a warning label.

**Graph-Derived Confidence Scoring**

The ConfidenceScorer in src/retrieval/confidence-scorer.ts is a
deterministic TypeScript formula. Never trusts LLM self-reported
confidence (Rule R-92).

Formula: confidence = source_count_score × recency_score × (1 -
contradiction_penalty) × verification_multiplier

| **Component**           | **Value Range** | **How Computed**                                                                                         | **Why This Signal**                                                                    |
|-------------------------|-----------------|----------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| source_count_score      | 0.4 to 1.0      | min(1.0, 0.4 + (source_count × 0.2)). 1 source = 0.60. 3+ sources = 1.0.                                 | Multiple independent sources agreeing increases confidence. One source could be wrong. |
| recency_score           | 0.5 to 1.0      | Based on age of most recent source: \< 30 days = 1.0, \< 90 days = 0.85, \< 1 year = 0.70, older = 0.50. | Old knowledge may be outdated. Recent sources more likely to reflect current state.    |
| contradiction_penalty   | 0 to 0.4        | If contradiction_count \> 0: penalty = min(0.4, contradiction_count × 0.15).                             | Active contradictions reduce confidence. The answer may be contested.                  |
| verification_multiplier | 1.0 or 1.15     | 1.15 if any supporting source nodes have trust_tier = "community_verified". 1.0 otherwise.               | Human-verified knowledge is more trustworthy than AI-generated knowledge.              |

Confidence breakdown is returned with every answer so users can see
exactly why a score is what it is: { source_count: 3, recency: "2 weeks
ago", contradictions: 0, verified: true }. This is more useful than a
bare number.

**What Happens When Confidence is Low**

Confidence \< 0.50: answer is returned with a prominent low-confidence
indicator in the UI. The breakdown is shown. The user is told which
specific factor drove confidence low ("Only one source found" or "Active
contradiction detected — this topic is contested").

Confidence \< 0.30: answer is still returned but the UI shows a warning
— "OmniRAG found relevant information but has low confidence in this
answer. The knowledge gap panel may show related unanswered questions."

Zero evidence found: hallucination guard has stripped all claims.
Return: "OmniRAG could not find relevant information for this question
in the current knowledge graph. This question has been logged as a
knowledge gap."

> **WHY:** Returning a low-confidence answer is better than returning
> nothing, as long as the confidence is clearly communicated. Users can
> then make informed decisions about whether to trust the answer or seek
> additional verification. The knowledge gap logging means repeated
> unanswered questions surface in the Gaps dashboard for an expert to
> address.
