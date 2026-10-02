# Smart Resume Analyzer

Upload a resume (PDF) and paste a job description. The analyzer extracts skills,
keywords and sections from both and shows a **transparent comparison**: what matches,
what's missing, and concrete, rule-based suggestions. The full analysis can be
downloaded as a Markdown or JSON report.

> **The numbers measure text overlap. They do not predict whether you will be
> interviewed or hired.** Read [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

**Stack:** Python 3.11 · FastAPI · spaCy (`en_core_web_sm`) · scikit-learn ·
pdfplumber · SQLAlchemy 2 · PostgreSQL 16 · React 19 + Vite · Docker Compose

## Documentation

| Doc | Contents |
|---|---|
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | Functional and non-functional requirements, scope |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Components, data model, request flow, design decisions |
| [docs/NLP_CONCEPTS.md](docs/NLP_CONCEPTS.md) | Tokenization, lemmatization, NER, TF-IDF and cosine similarity in plain language |
| [docs/LIMITATIONS.md](docs/LIMITATIONS.md) | What automated matching can't do, and fairness concerns |

## Run with Docker

```bash
cp .env.example .env        # then set POSTGRES_PASSWORD
docker compose up --build
# open http://localhost:8080
```

Only the frontend (nginx, port 8080) is published. The API sits behind it at `/api`.
Swagger UI is available in local development at `http://localhost:8000/docs`.

## Local development

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload            # SQLite by default; set DATABASE_URL for Postgres

# Frontend (separate terminal)
cd frontend
npm install
npm run dev                               # http://localhost:5173, proxies /api to :8000
```

## Tests

```bash
cd backend
pytest                                                                 # SQLite
TEST_DATABASE_URL=postgresql+psycopg2://user:pass@localhost/db pytest  # PostgreSQL
```

There are 39 tests, covering:

- **PDF extraction:** text, pages, line preservation, non-PDF, corrupt, encrypted, image-only and page-limit cases
- **Preprocessing:** normalization, lemmatization, chunking
- **Skill extraction:** aliases, symbols (`C++`, `.NET`), longest match, case-sensitive ambiguous words, false positives
- **Matching:** skill sets, cosine bounds, keyword ranking, bigram boundaries, sections, suggestions, no composite score
- **API endpoints:** auth, upload validation (type, size, magic bytes, pages), job validation, analysis, reports, cross-user isolation, cascade deletes, account deletion

## API

All endpoints except `POST /api/users` and `GET /api/health` require an `X-API-Key` header.

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/users` | Register with an email. Returns an API key **once**. |
| DELETE | `/api/users/me` | Delete the account and all data |
| POST | `/api/resumes` | Upload a PDF (multipart field `file`) |
| GET | `/api/resumes`, `/api/resumes/{id}` | List or get resumes |
| DELETE | `/api/resumes/{id}` | Delete a resume and its analyses |
| POST | `/api/jobs` | `{title, company?, description}` |
| GET, DELETE | `/api/jobs/{id}` | Get or delete a job |
| POST | `/api/analyses` | `{resume_id, job_id}` → full analysis |
| GET | `/api/analyses/{id}` | Fetch an analysis |
| GET | `/api/analyses/{id}/report?format=md\|json` | Download the report |

## Security and privacy

- **Upload checks:** `.pdf` extension, `application/pdf` type, `%PDF-` magic bytes, size cap (5 MB), page cap (10), and rejection of encrypted, corrupt or image-only PDFs. The read is capped, so oversized files are never buffered in full.
- **Storage:** the original file is never stored, only the extracted text and a SHA-256 of the file.
- **API keys:** only the SHA-256 hash is stored.
- **Isolation:** every query is scoped to the owner. Other users' IDs return 404.
- **Deletion:** cascade deletes support the right to erasure (`DELETE /api/users/me`).
- **Logging:** document contents are never logged.
- **Hardening:** security headers and a CSP in nginx. The backend container runs as a non-root user on a read-only filesystem, and the database is not exposed to the host.
- **Before a public deployment:** add TLS, rate limiting at the proxy, OIDC login instead of API keys, a data-retention policy, and Alembic migrations.

## Project layout

```
backend/app/
  api/routes.py        HTTP endpoints
  nlp/                 pure NLP functions (no web or DB imports)
  services/            analysis orchestration and report rendering
  models.py            users, resumes, jobs, analyses
  security.py          auth and upload validation
backend/tests/         pytest suite
frontend/src/          React UI
docs/                  requirements, architecture, NLP explainer, limitations
```
