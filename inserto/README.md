# Inserto

AI-ready resume analyzer and career intelligence platform. Upload or paste a resume and get an overall score,
ATS compatibility checks, skill and keyword extraction, job-description matching, content analysis
(quantification, action verbs, achievements, readability), recruiter-style feedback, prioritized
recommendations, bullet rewrites and role-fit insights.

> Scores are heuristic estimates from text analysis. They reflect common recruiter and ATS conventions,
> not any specific employer's system, and do not predict hiring outcomes.

**Stack:** React 19 · TypeScript · Vite · Tailwind CSS 4 · TanStack Query · React Router · Recharts · Lucide —
Python 3.11 · FastAPI · Pydantic 2 · SQLAlchemy 2 · PostgreSQL 16 (SQLite for local dev) · optional Claude via the Anthropic SDK.

## Run

```bash
cp .env.example .env          # set POSTGRES_PASSWORD and JWT_SECRET
docker compose up --build     # http://localhost:8080
```

Local development:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000     # SQLite at ./inserto.db; Swagger at /api/docs

cd ../frontend
npm install
npm run dev                                   # http://localhost:5173, proxies /api to :8000
```

Tests and checks:

```bash
cd backend && pytest                          # engine + API tests
cd frontend && npm run typecheck && npm run build
```

## Architecture

```
backend/app/
  engine/            Deterministic analysis. Pure functions: no web, DB or AI imports.
    extract.py         PDF (pdfplumber), DOCX (python-docx), TXT -> clean text
    parser.py          contact, sections, roles + dates, education, bullets
    taxonomy.py        120 skills / 14 categories with aliases; 13 role profiles
    skills.py          skill extraction with evidence snippets; keyword ranking
    checks.py          ATS, structure, experience, education, quantification, verbs, achievements, readability, keywords
    matching.py        job-description match, requirement evidence, role fit
    studio.py          bullet rewrites (never invents numbers; inserts [placeholders])
    narrative.py       recruiter lens, recommendations, career insights
    analyzer.py        orchestration, weighting, grade
    result.py          typed AnalysisResult contract (mirrored in frontend/src/lib/types.ts)
  ai/                AIProvider interface + DeterministicProvider + AnthropicProvider
  api/               auth, profile, resumes, analyses/compare/studio/dashboard routes
  models.py          users, resumes, analyses (JSON result column)
frontend/src/
  components/ui      button, card, badge, fields, tabs, dialog, skeleton, empty states
  components/charts  score ring, subscore bars, trend line, category bars, compare bars
  pages/             landing, auth, dashboard, new analysis, job matcher, resumes, history,
                     compare, profile, settings, analysis/{overview,parsed,ats,skills,content,match,studio}
```

### Scoring

| Dimension | Weight | With job description |
|---|---|---|
| Impact (quantification 45%, verbs 30%, achievements 25%) | 28% | 22% |
| ATS compatibility | 20% | 15% |
| Skills & keywords | 15% | 10% |
| Experience (incl. education) | 13% | 10% |
| Structure | 12% | 8% |
| Readability | 12% | 8% |
| Job match | — | 27% |

### AI provider

`app/ai/base.py` defines `AIProvider` with `enhance()` (narrative feedback) and `rewrite_bullet()`.
The deterministic engine always runs first; a provider can only add narrative under `result.ai` and never
changes scores. Set `AI_PROVIDER=anthropic` and `ANTHROPIC_API_KEY` to enable `AnthropicProvider`, which uses
structured outputs constrained to a JSON schema. Provider errors fall back to the deterministic result.
To add another backend, implement `AIProvider` and register it in `app/ai/registry.py`.

## Security and privacy

- Passwords: PBKDF2-SHA256 (390k iterations). Auth: HS256 JWT bearer tokens.
- Uploads: extension allowlist, magic-byte checks, capped reads (5 MB), 10-page PDF limit; encrypted and image-only PDFs rejected.
- Only extracted text is stored, never the original file. All queries are owner-scoped; other users' IDs return 404.
- Deleting a resume or account cascades to all linked analyses.
- The API refuses to start in production with the development JWT secret.
- Before a public deployment: TLS, rate limiting on `/api/auth/*`, Alembic migrations (tables are created on startup today), and a retention policy.

## Known limitations

- Skill detection is taxonomy-based; skills missing from `taxonomy.py` are not found.
- Section/role parsing is heuristic. Unusual layouts (multi-column PDFs, tables) parse less reliably — the ATS tab flags this.
- No OCR for scanned PDFs.
