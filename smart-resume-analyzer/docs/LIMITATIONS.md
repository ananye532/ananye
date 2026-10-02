# Limitations of automated resume matching

Read this before interpreting any number this tool produces.

## The metrics do not predict hiring outcomes

Skill coverage, keyword coverage and cosine similarity measure **textual overlap**
between two documents. They have not been validated against interview or hiring
outcomes, and this project makes no claim that they correlate with them. A resume
with 90 % coverage can be rejected, and one with 30 % can be hired.

## Why overlap is a weak signal

1. **Synonyms and paraphrase.** TF‑IDF compares exact (lemmatized) terms. "Led a team
   of five" and "people management" share no words. The skill taxonomy handles some
   aliases (e.g. `k8s` → Kubernetes), but only those it lists.
2. **No understanding of depth.** "Used Python once" and "10 years of Python" both
   count as *Python present*.
3. **Negation and context are ignored.** "No experience with Java" still contains
   "Java".
4. **Taxonomy coverage.** Skills missing from the curated list are invisible to the
   skill extractor. The list reflects the authors' choices and is biased toward
   software and data roles.
5. **PDF extraction is imperfect.** Multi-column layouts, tables, text boxes and
   images can scramble or drop text. Scanned resumes are rejected because OCR is
   not supported.
6. **Two-document TF‑IDF.** With only two documents, IDF can only separate terms that
   appear in both from terms that appear in one. It cannot tell that a word is rare
   in general.
7. **NER errors.** The small spaCy model often mislabels technologies as
   organisations. Entities are displayed but never used for scoring.
8. **English only.**

## Fairness

Keyword-based screening can disadvantage candidates who describe the same work in
different vocabulary. That includes career changers, non-native speakers, people
from different industries or countries, and people with non-traditional education.
Optimising a resume purely for keyword overlap ("keyword stuffing") can also make
it worse for human readers.

**Do not use this tool to rank, filter or reject candidates.** It is designed as a
self-review aid for the person who wrote the resume.

## How to use the output responsibly

- Treat missing skills as prompts. If you have the skill, state it explicitly. If you
  don't, **do not add it**.
- Prefer concrete, quantified evidence over repeating JD keywords.
- Have a human, ideally someone in the target field, review the resume.
