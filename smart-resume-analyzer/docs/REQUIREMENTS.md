# Requirements

## 1. Purpose

Given a resume (PDF) and a pasted job description (JD), the Smart Resume Analyzer
extracts structured information from both and shows a **transparent, explainable
comparison**: which skills and keywords overlap, which are missing, which resume
sections exist, and concrete suggestions.

It is a writing aid for candidates. It is **not** a hiring predictor. No number it
produces estimates the probability of an interview or an offer.

## 2. Users

| Actor | Goal |
|---|---|
| Candidate | Check how explicitly a resume reflects a specific JD before applying. |
| Career coach | Walk through the comparison with a candidate. |

Recruiter-side ranking of candidates is **out of scope** and must not be built on top
of this system without a fairness review (see `LIMITATIONS.md`).

## 3. Functional requirements

| ID | Feature | Acceptance criteria |
|---|---|---|
| F1 | Resume upload | `POST /api/resumes` accepts one PDF via multipart form. |
| F2 | PDF text extraction | Text is extracted per page with pdfplumber. Image-only (scanned) PDFs are rejected with a clear message, since OCR is out of scope. |
| F3 | Job description input | `POST /api/jobs` accepts title + description text (50 – 20,000 chars). |
| F4 | Skill extraction | Skills are matched against a curated, versioned taxonomy using spaCy `PhraseMatcher`, so aliases such as `JS` → `JavaScript` are handled. Every hit records the matched surface text. |
| F5 | Keyword extraction | The top‑N JD terms (unigrams and bigrams) are ranked by TF‑IDF over lemmatized text. |
| F6 | Section detection | Detects Contact, Summary, Experience, Education, Skills, Projects, Certifications, Awards, Publications, Volunteer, Languages and Interests from heading lines. |
| F7 | Comparison | Reports three separate metrics, each with its formula: skill coverage, keyword coverage, and TF‑IDF cosine similarity. They are **not** combined into a single score. |
| F8 | Missing skills | Lists JD skills absent from the resume, grouped by category. |
| F9 | Suggestions | Rule-based and deterministic. Each suggestion names the rule that produced it. |
| F10 | Report download | `GET /api/analyses/{id}/report?format=md|json` returns an attachment that includes the limitations statement. |

## 4. Non-functional requirements

### Security and privacy
- Upload validation covers the `.pdf` extension, the declared MIME type, the `%PDF-`
  magic bytes, a size cap (default 5 MB), a page cap (default 10), encrypted PDFs and
  unparseable PDFs.
- The original file is never written to disk or to the database. Only the extracted
  text is stored.
- Each user gets a random API key, shown once. Only its SHA‑256 hash is stored. Every
  resource is scoped to its owner, and requests for another user's resource get 404,
  so the API does not reveal that the resource exists.
- `DELETE /api/users/me` hard-deletes the user and, by cascade, all of their data.
- The application never logs document contents.
- Security headers are set: `X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy` and `Cache-Control: no-store` on API responses.
- CORS is restricted to configured origins.

### Explainability
- Every metric is returned with its definition and the raw inputs used to compute it.
- Every extracted skill can be traced to its taxonomy entry and to the matched text.

### Performance
- A typical analysis (2 pages + 1 JD) completes in under 2 s on one CPU core with
  `en_core_web_sm`. This is a design target, not a benchmarked guarantee.

### Testability
- The NLP layer is pure Python, with no FastAPI or DB imports, so it can be unit tested
  in isolation.
- API tests run against SQLite. PostgreSQL is used in Docker.

## 5. Out of scope (v1)
- OCR for scanned resumes
- DOCX upload
- Multi-language support (English only)
- Learned or embedding-based semantic matching (possible v2, see `ARCHITECTURE.md`)
- Password login, OAuth, rate limiting (rate limiting should be added at the reverse proxy for any public deployment)
