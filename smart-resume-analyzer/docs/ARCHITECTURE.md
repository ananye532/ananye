# Architecture

## 1. System overview

```
 ┌──────────────┐  HTTP (JSON / multipart)  ┌────────────────────────────────────┐
 │ React (Vite) │ ───────────────────────▶  │ FastAPI                            │
 │ served by    │   /api/* proxied by nginx │  api/routes.py   (HTTP, auth, I/O)  │
 │ nginx        │ ◀───────────────────────  │  services/        (orchestration)  │
 └──────────────┘                           │  nlp/             (pure functions) │
                                            └───────────────┬────────────────────┘
                                                            │ SQLAlchemy 2.0
                                                    ┌───────▼────────┐
                                                    │ PostgreSQL 16  │
                                                    └────────────────┘
```

Layering rule: `api → services → nlp`. The `nlp` package has no knowledge of HTTP
or the database, so every algorithm can be unit tested with plain strings.

## 2. Backend modules

| Module | Responsibility |
|---|---|
| `app/config.py` | Settings from environment variables (pydantic-settings) |
| `app/db.py` | Engine, session factory, `get_db` dependency |
| `app/models.py` | ORM tables |
| `app/schemas.py` | Pydantic request and response models |
| `app/security.py` | API-key generation and hashing, auth dependency, upload validation |
| `app/nlp/pipeline.py` | Loads spaCy once. Falls back to a blank English pipeline if the model is missing. |
| `app/nlp/preprocessing.py` | Normalize → tokenize → remove stop words → lemmatize |
| `app/nlp/pdf_extract.py` | PDF bytes → text, using pdfplumber |
| `app/nlp/skills.py` | Taxonomy plus `PhraseMatcher`-based skill extraction |
| `app/nlp/keywords.py` | TF-IDF keyword ranking |
| `app/nlp/sections.py` | Heading-based section detection |
| `app/nlp/entities.py` | spaCy NER (ORG, GPE, DATE). Informational only, never scored. |
| `app/nlp/matching.py` | Skill coverage, keyword coverage, cosine similarity |
| `app/nlp/suggestions.py` | Deterministic improvement rules |
| `app/services/analyzer.py` | Runs the full analysis and returns a JSON-serialisable dict |
| `app/services/report.py` | Renders an analysis as Markdown or JSON |
| `app/api/routes.py` | REST endpoints |

## 3. Data model (PostgreSQL)

```
users (1) ──< resumes (1) ──< analyses >── (1) jobs >── (1) users
```

| Table | Columns | Notes |
|---|---|---|
| `users` | `id UUID PK`, `email VARCHAR(320) UNIQUE`, `api_key_hash CHAR(64) UNIQUE`, `created_at` | Stores only the hash of the key. |
| `resumes` | `id UUID PK`, `user_id FK→users ON DELETE CASCADE`, `filename`, `file_sha256`, `page_count`, `text`, `sections JSONB`, `skills JSONB`, `created_at` | The original file is not stored. `file_sha256` supports deduplication. |
| `jobs` | `id UUID PK`, `user_id FK→users ON DELETE CASCADE`, `title`, `company`, `description`, `skills JSONB`, `created_at` | |
| `analyses` | `id UUID PK`, `user_id FK`, `resume_id FK ON DELETE CASCADE`, `job_id FK ON DELETE CASCADE`, `skill_coverage FLOAT`, `keyword_coverage FLOAT`, `cosine_similarity FLOAT`, `result JSONB`, `taxonomy_version`, `created_at` | The three numeric columns are separate so they can be queried directly. `result` holds the full explainable payload. |

Indexes are on `user_id` in every child table and on `(resume_id, job_id)` in
`analyses`. `JSONB` is used on PostgreSQL. The SQLAlchemy `JSON` type falls back to
`JSON`/`TEXT` on SQLite for tests. Tables are created at startup with
`create_all`. For schema evolution, add Alembic before the first production migration.

## 4. Request flow: create analysis

1. `POST /api/resumes`
   1. Validate the upload: extension, MIME type, size, magic bytes.
   2. Extract text with pdfplumber. Reject PDFs that are encrypted, image-only or over the page limit.
   3. Detect sections and extract skills.
   4. Persist the extracted data and discard the file bytes.
2. `POST /api/jobs`
   1. Validate text length.
   2. Extract skills and persist.
3. `POST /api/analyses {resume_id, job_id}`
   1. Load both records, checking ownership.
   2. `analyzer.analyze()` runs:
      - preprocessing
      - skill diff
      - TF-IDF keywords
      - cosine similarity
      - keyword coverage
      - sections and entities
      - suggestions
   3. Persist and return the result with the definition of every metric.
4. `GET /api/analyses/{id}/report?format=md` returns a downloadable report.

## 5. Key design decisions

| Decision | Why | Trade-off |
|---|---|---|
| Curated skill taxonomy + `PhraseMatcher` instead of a learned skill NER | Deterministic and auditable. Every hit can be explained. | Recall is limited to the taxonomy. Unknown skills are missed. |
| Three separate metrics, no composite score | A single score invites a "hire probability" reading and hides why it is high or low. | Users must read three numbers. |
| TF-IDF with each sentence treated as a document for IDF | No external corpus, no data leakage between users. With sentences as documents, IDF can push down boilerplate terms. | IDF reflects only these two texts, not general English. Explained in `NLP_CONCEPTS.md`. |
| NER is informational only | `en_core_web_sm` often labels tech terms (e.g. "Python") as ORG. | Organisations and dates are shown but never used in scoring. |
| Store text, not files | Smaller attack surface, less personal data held. | The original file cannot be re-rendered. |
| API-key auth | Simple and stateless, enough for a single-tenant demo. | No password reset. Replace with OIDC for multi-tenant production. |

## 6. Deployment

`docker compose up --build` starts three services:

| Service | Image | Role |
|---|---|---|
| `db` | `postgres:16-alpine` | Database with a named volume and a health check |
| `backend` | `python:3.11-slim` | uvicorn. Runs as a non-root user. The spaCy model is baked in at build time. |
| `frontend` | multi-stage `node:20` build → `nginx:alpine` | Serves static files and proxies `/api` to the backend. `client_max_body_size` matches the upload limit. |

## 7. Possible v2

- Sentence-embedding similarity, shown alongside TF-IDF and not replacing it
- OCR fallback using Tesseract
- Taxonomy sourced from ESCO or O*NET instead of the hand-curated list
- Alembic migrations, a rate limiter and audit logging
