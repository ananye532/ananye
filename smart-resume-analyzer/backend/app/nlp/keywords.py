"""TF-IDF keyword ranking and cosine similarity.

Each sentence or line is treated as a mini-document when learning IDF. With
only two whole documents (one resume, one JD), IDF could do nothing except
separate words that appear in both from words that appear in one. With
sentences as documents, boilerplate words that appear in almost every sentence
get a low IDF, and specific terms get a high one.

Documents are represented as phrases (runs of adjacent content words) and
n-grams never cross a phrase boundary. See preprocessing.phrases_from_doc.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from spacy.language import Language

from .pipeline import get_nlp, has_lemmatizer, has_tagger
from .preprocessing import clean_text, phrases_from_doc, split_chunks
from .skills import skill_token_indices

# Lemmas that act as stop words in a JD context although spaCy doesn't list them.
DOMAIN_STOPWORDS = frozenset(
    {
        "experience", "year", "work", "team", "role", "candidate", "job", "company", "ability",
        "strong", "skill", "skills", "experiences", "years", "requirement", "responsibility", "qualification", "preferred", "plus",
        "etc", "good", "excellent", "knowledge", "understanding", "familiarity", "proficiency",
        "proficient", "opportunity", "new", "great", "able", "solid", "ideal", "key", "day",
    }
)
KEYWORD_POS = frozenset({"NOUN", "PROPN", "ADJ"})
PHRASE_SEP = "|"
NGRAM_MAX = 2

Phrases = list[list[str]]


def _ngrams(phrases: Phrases, n_max: int = NGRAM_MAX) -> list[str]:
    out: list[str] = []
    for p in phrases:
        for n in range(1, n_max + 1):
            out.extend(" ".join(p[i : i + n]) for i in range(len(p) - n + 1))
    return out


def _chunk_phrases(text: str, keep_pos: frozenset[str] | None, nlp: Language | None = None) -> list[Phrases]:
    """Preprocess text into one list of phrases per sentence-like chunk."""
    nlp = nlp or get_nlp()
    if keep_pos is not None and not has_tagger(nlp):
        keep_pos = None  # blank fallback pipeline has no POS tags; filtering would drop every token
    use_lemma = has_lemmatizer(nlp)
    out: list[Phrases] = []
    for doc in nlp.pipe(split_chunks(clean_text(text))):
        phrases = phrases_from_doc(doc, keep_pos, skill_token_indices(doc, nlp), use_lemma)
        phrases = _drop_stopwords(phrases)
        if phrases:
            out.append(phrases)
    return out


def _drop_stopwords(phrases: Phrases) -> Phrases:
    out: Phrases = []
    for p in phrases:
        current: list[str] = []
        for t in p:
            if t in DOMAIN_STOPWORDS:
                if current:
                    out.append(current)
                current = []
            else:
                current.append(t)
        if current:
            out.append(current)
    return out


def _vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        analyzer=lambda phrases: _ngrams(phrases),  # input is already a list of phrases
        sublinear_tf=True,  # 1 + log(tf): ten mentions are not ten times as important as one
        norm="l2",
    )


@dataclass(frozen=True)
class Keyword:
    term: str
    weight: float


def rank_keywords(text: str, top_n: int = 25, nlp: Language | None = None) -> list[Keyword]:
    """Top-N noun/adjective unigrams and bigrams of one document, by TF-IDF summed over its sentences.

    Weights are rescaled so the top keyword is 1.0.
    """
    chunks = _chunk_phrases(text, KEYWORD_POS, nlp)
    if not chunks:
        return []
    vec = _vectorizer()
    matrix = vec.fit_transform(chunks)
    scores = np.asarray(matrix.sum(axis=0)).ravel()
    terms = vec.get_feature_names_out()
    weight = {str(t): float(w) for t, w in zip(terms, scores)}
    top = max(weight.values()) or 1.0

    # A unigram that only ever occurs inside a bigram ("machine" in "machine
    # learning") has the same weight as that bigram and adds no information.
    covered: dict[str, float] = {}
    for term, w in weight.items():
        if " " in term:
            for part in term.split():
                covered[part] = max(covered.get(part, 0.0), w)
    ranked = sorted(
        (t for t in weight if not (" " not in t and covered.get(t, -1.0) >= weight[t] - 1e-9)),
        key=lambda t: (-weight[t], t),
    )
    return [Keyword(t, round(weight[t] / top, 4)) for t in ranked[:top_n]]


def tfidf_cosine(text_a: str, text_b: str) -> float:
    """Cosine similarity of the TF-IDF vectors of two documents, in [0, 1].

    IDF is learned from the sentences of both documents. Each whole document is
    then turned into one vector.
    """
    a, b = _chunk_phrases(text_a, None), _chunk_phrases(text_b, None)
    if not a or not b:
        return 0.0
    vec = _vectorizer().fit(a + b)
    docs = vec.transform([[p for c in a for p in c], [p for c in b for p in c]])
    return round(float(cosine_similarity(docs[0], docs[1])[0, 0]), 4)


def term_set(text: str) -> set[str]:
    """All unigrams and bigrams in the text, built with the same preprocessing as rank_keywords.

    No POS filter here: a JD noun should count as present even if the resume's
    tagger labelled the same word differently.
    """
    return {g for chunk in _chunk_phrases(text, None) for g in _ngrams(chunk)}
