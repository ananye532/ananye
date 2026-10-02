# NLP concepts, in plain language

Each section explains one idea, shows a tiny example, and points to the code that
implements it.

---

## 1. Text preprocessing

**Idea:** Raw text from a PDF is messy. It has odd bullet characters, ligatures
(the single character "ﬁ" instead of "f" + "i"), extra spaces and blank lines.
Preprocessing tidies it up so the same word always looks the same.

```
"•  Led the ﬁnance  team"  →  "Led the finance team"
```

**Code:** `app/nlp/preprocessing.py`, function `clean_text`.

---

## 2. Tokenization

**Idea:** Split text into units called *tokens*: words, numbers, punctuation.
This is harder than splitting on spaces. "Node.js" should stay one token, while
"APIs," should become "APIs" and ",".

```
"Built REST APIs, using Node.js."  →  [Built] [REST] [APIs] [,] [using] [Node.js] [.]
```

spaCy's tokenizer has rules and exceptions for English that handle most of this.

**Code:** `nlp(text)` or `nlp.make_doc(text)` from spaCy, used throughout.

---

## 3. Stop words

**Idea:** Words like *the, and, with, is* appear everywhere and carry little
meaning for matching, so they are removed. A resume tool also benefits from removing
*domain* stop words that are everywhere in job ads: *experience, strong, team,
ability*.

**Code:** `token.is_stop` (spaCy's list) plus `DOMAIN_STOPWORDS` in
`app/nlp/keywords.py`.

---

## 4. Lemmatization

**Idea:** Reduce each word to its dictionary form (its *lemma*), so different forms
of the same word count as one.

```
built → build     databases → database     managing → manage
```

This is why a resume saying "managed databases" matches a JD asking for someone to
"manage a database". spaCy picks the lemma using the word's part of speech:
"meeting" as a noun stays "meeting", but as a verb it becomes "meet".

**Code:** `app/nlp/preprocessing.py`, functions `phrases_from_doc` and `lemmatize`.

---

## 5. Named-entity recognition (NER)

**Idea:** A statistical model labels spans of text as entity types: organisations
(ORG), places (GPE), dates (DATE), and so on.

```
"Engineer at Acme Corp, London, 2019–2023"
  → ORG: Acme Corp   GPE: London   DATE: 2019–2023
```

**Where it's appropriate here:** showing the employers, locations and dates found
in the resume, so users can check what was extracted.

**Where it isn't:** scoring. The small English model often calls technologies such
as "Python" or "AWS" organisations. NER output is therefore displayed but never
used in any metric, and entities that are known skills are filtered out.

**Code:** `app/nlp/entities.py`.

---

## 6. Skill extraction

**Idea:** Keep a curated list (a *taxonomy*) of skills, each with its aliases, and
find them in the text.

```
"Deployed to k8s, wrote some JS"  →  Kubernetes (matched "k8s"), JavaScript (matched "JS")
```

spaCy's `PhraseMatcher` does this efficiently over tokens, not raw characters.
"Java" therefore doesn't match inside "JavaScript". Two refinements:

- **Longest match wins.** "React Native" is not also counted as "React".
- **Case-sensitive for ambiguous words.** "Go", "Excel", "REST" and "R" are only
  matched with that exact capitalisation, so "ready to go" or "the rest of the team"
  doesn't count.

Every match records the exact text that triggered it, so you can see *why* a skill
was detected.

**Limitation:** only skills listed in the taxonomy can be found.

**Code:** `app/nlp/skills.py`.

---

## 7. TF‑IDF (Term Frequency – Inverse Document Frequency)

**Idea:** Give each word a weight that answers the question "How characteristic is
this word of this text?"

- **TF (term frequency):** how often the word appears. More mentions means more
  important. A dampened version, 1 + log(count), is used so ten mentions don't
  count ten times as much as one.
- **IDF (inverse document frequency):** how *rare* the word is across a collection
  of documents. A word found everywhere gets a low IDF. A word found in only a few
  places gets a high one.

```
weight(word) = TF(word) × IDF(word)
```

**What counts as a document here?** Each sentence or line. If only the two whole
texts (resume and JD) were used, IDF could do almost nothing. It would only
separate words that appear in both from words that appear in one. With sentences,
words that appear in nearly every sentence get pushed down, and specific terms
stand out.

**Keywords:** the JD's highest-weighted nouns and adjectives, plus two-word phrases
like "machine learning", become its top keywords. A two-word phrase is only formed
from words that were actually next to each other in the text.

**Code:** `app/nlp/keywords.py`, function `rank_keywords`, using scikit-learn's
`TfidfVectorizer`.

---

## 8. Cosine similarity

**Idea:** Turn each document into a list of TF‑IDF weights, one number per
vocabulary term, which works like an arrow in a high-dimensional space. Cosine
similarity measures the angle between the two arrows:

- **1.0**: the arrows point the same way, meaning the same words with the same
  relative emphasis.
- **0.0**: they share no weighted terms at all.

It ignores length, so a long resume isn't penalised just for being long.

```
cos(A, B) = (A · B) / (|A| × |B|)
```

**What it does *not* measure:** whether the person can do the job. Two documents
can use the same words and describe very different levels of skill.

**Code:** `app/nlp/keywords.py`, function `tfidf_cosine`.

---

## 9. Section detection

**Idea:** Resumes have headings such as "Experience" and "Education". A line counts
as a heading if it is short and matches a known pattern, such as "Professional
Experience", "WORK HISTORY:" or "Technical Skills". Each section's body runs until
the next heading.

Contact details are detected with simple patterns (email, phone, LinkedIn, GitHub).
Only *whether* each one is present is returned. The values themselves are never
copied into the results.

**Code:** `app/nlp/sections.py`.

---

## 10. Putting it together: the three metrics

| Metric | Question it answers |
|---|---|
| Skill coverage | Of the taxonomy skills the JD mentions, how many does the resume mention? |
| Keyword coverage | Of the JD's top TF‑IDF terms, how many appear in the resume? |
| Cosine similarity | Overall, how similar is the weighted vocabulary? |

They are shown separately, never averaged into one "match score", because each one
can be high or low for different reasons. A single number would hide those
reasons, and it would invite people to read it as a prediction of being hired,
which it is not. See `LIMITATIONS.md`.
