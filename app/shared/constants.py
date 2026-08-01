"""All named constants used across OmniRAG. No magic numbers elsewhere (R-34)."""

# --- Embeddings (Blueprint 2.3 / 8.2, Rule R-101) ---
# Rule R-101: changing this model is a migration (re-embed the entire
# corpus), not a config change. Every module that produces or indexes
# embeddings (app.database.mongodb, app.database.mongo_repository, and
# Phase 6's sentence-transformers embedder) imports these two values
# from here rather than repeating the literals - a second, silently
# drifted copy of "384" or the model name in another file is exactly
# what this constant existing is meant to prevent.
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSIONS = 384

# --- Entity resolution thresholds (Blueprint 2.3 / 8.1) ---
STAGE1_LEXICAL_THRESHOLD = 0.70
STAGE2_SEMANTIC_THRESHOLD = 0.75
ENTITY_AUTO_MERGE_THRESHOLD = 0.85
ENTITY_REVIEW_QUEUE_LOWER_BOUND = 0.60

# --- Retrieval (Blueprint 8.2) ---
RRF_K = 60
RETRIEVAL_TOP_K_PER_SOURCE = 10
GRAPH_EXPANSION_TOP_N_RESULTS = 5

# --- Confidence scoring (Blueprint 8.5) ---
CONFIDENCE_SOURCE_BASE = 0.4
CONFIDENCE_SOURCE_PER_SOURCE = 0.2
CONFIDENCE_SOURCE_MAX = 1.0
CONFIDENCE_CONTRADICTION_PENALTY_PER = 0.15
CONFIDENCE_CONTRADICTION_PENALTY_MAX = 0.4
CONFIDENCE_VERIFIED_MULTIPLIER = 1.15
CONFIDENCE_UNVERIFIED_MULTIPLIER = 1.0
CONFIDENCE_LOW_THRESHOLD = 0.50
CONFIDENCE_VERY_LOW_THRESHOLD = 0.30

# --- Caching ---
QUERY_CACHE_TTL_SECONDS = 300

# --- Rate limits (requests per minute unless noted) — Blueprint 2.4 ---
RATE_LIMIT_AUTH_GOOGLE = "20/minute"
RATE_LIMIT_AUTH_REFRESH = "30/minute"
RATE_LIMIT_WORKSPACE_STATUS = "60/minute"
RATE_LIMIT_INGEST_WEBHOOK = "500/minute"
RATE_LIMIT_INGEST_FILES = "20/minute"
RATE_LIMIT_INGEST_STATUS = "100/minute"
RATE_LIMIT_QUERY = "30/minute"
RATE_LIMIT_GRAPH_READ = "60/minute"
RATE_LIMIT_GRAPH_NODE = "100/minute"
RATE_LIMIT_GRAPH_DRIFT = "30/minute"
RATE_LIMIT_EXPERTS = "60/minute"
RATE_LIMIT_GAPS = "60/minute"
RATE_LIMIT_DOCUMENTS = "60/minute"
RATE_LIMIT_DOCUMENTS_APPROVE = "20/minute"
RATE_LIMIT_HEALTH = "200/minute"

# --- JWT (Blueprint 2.5) ---
JWT_ACCESS_TOKEN_EXPIRY_MINUTES = 15
JWT_REFRESH_TOKEN_EXPIRY_DAYS = 7

# --- File uploads ---
MAX_UPLOAD_FILE_SIZE_MB = 10
SUPPORTED_UPLOAD_FORMATS = {"pdf", "docx"}

# --- Community verification (Blueprint 2.3) ---
KTD_APPROVALS_REQUIRED = 2
KTD_TOP_CONTRIBUTORS_NOTIFIED = 3

# --- Redis Streams ingestion pipeline (Blueprint 2.7 / Phase 5) ---
# Named here now (Phase 3) even though the consumer worker that reads
# from these is Phase 5 scope, so the stream/group can be created
# idempotently as part of database setup and Rule R-34 (no magic
# strings) holds from the first reference onward, not retrofitted
# later once ingestion code exists.
INGESTION_STREAM_NAME = "omnirag:events"
INGESTION_DEAD_LETTER_STREAM_NAME = "omnirag:dead"
INGESTION_CONSUMER_GROUP = "omnirag-workers"

# --- Redis pub/sub SSE broadcast (Blueprint 2.7 / Phase 8) ---
# Blueprint 2.7 names this channel descriptively ("SSE broadcast
# channel", "agent_status pub/sub events") but never assigns it a
# fixed string the way the ingestion stream/group above are named -
# this constant is that missing fixed name, chosen now (Phase 3) for
# the same reason INGESTION_STREAM_NAME was: Rule R-34 holds from the
# first reference onward. The actual publisher (app/agents/
# coordinator.py, emitting agent_status events) and subscriber
# (app/websocket/, bridging to the SSE response stream) are both
# Phase 8 scope - nothing publishes or subscribes yet. What Phase 3
# delivers is the channel being named and connectivity to Redis pub/
# sub being verified (app.database.redis.verify_pubsub_ready), not a
# working pub/sub feature with no publisher to test it against.
AGENT_STATUS_CHANNEL = "omnirag:agent_status"

# --- API ---
API_VERSION = "v1"
