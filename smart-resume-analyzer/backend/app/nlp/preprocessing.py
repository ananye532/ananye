"""Text preprocessing: normalize -> tokenize -> filter -> lemmatize."""

from __future__ import annotations

import re
import unicodedata

from spacy.language import Language
from spacy.tokens import Doc

from .pipeline import get_nlp, has_lemmatizer

# Characters commonly used as bullets in resumes.
_BULLETS = re.compile(r"[•‣◦⁃∙▪●■➢–—]")
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_INLINE_WS = re.compile(r"[ \t ]+")
_MANY_NEWLINES = re.compile(r"\n{3,}")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?;])\s+|\n+")


def clean_text(text: str) -> str:
    """Normalize Unicode and whitespace, keeping line breaks.

    Line breaks are kept because section detection relies on them.
    NFKC folds ligatures such as the single character "ﬁ" into "fi", which PDF
    extraction often produces.
    """
    text = unicodedata.normalize("NFKC", text)
    text = _CONTROL.sub("", text)
    text = _BULLETS.sub(" ", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [_INLINE_WS.sub(" ", line).strip() for line in text.split("\n")]
    return _MANY_NEWLINES.sub("\n\n", "\n".join(lines)).strip()


def split_chunks(text: str) -> list[str]:
    """Split into sentence-like chunks (sentences or lines). Used as mini-documents for IDF."""
    return [c.strip() for c in _SENTENCE_SPLIT.split(text) if c and c.strip()]


def _keep(tok) -> bool:
    return not (tok.is_stop or tok.is_punct or tok.is_space or tok.like_num or tok.like_email or tok.like_url)


def phrases_from_doc(
    doc: Doc,
    keep_pos: frozenset[str] | None = None,
    protected: set[int] | None = None,
    use_lemma: bool = True,
) -> list[list[str]]:
    """Split a processed doc into runs of consecutive content lemmas.

    Removed tokens (stop words, punctuation, numbers, POS outside `keep_pos`)
    act as boundaries. That way an n-gram can only be built from words that
    were actually adjacent: "care about the rest" yields ["care"], ["rest"],
    never the bigram "care rest".

    Tokens whose index is in `protected` (e.g. parts of a known skill) are
    always kept and use their lowercase surface form instead of a lemma, so
    "machine learning" survives even when the tagger calls "learning" a verb.
    """
    protected = protected or set()
    phrases: list[list[str]] = [[]]
    for tok in doc:
        if tok.i in protected:
            phrases[-1].append(tok.lower_)
            continue
        lemma = (tok.lemma_ if use_lemma else tok.text).lower().strip()
        if (
            _keep(tok)
            and (keep_pos is None or tok.pos_ in keep_pos)
            and len(lemma) >= 2
            and any(ch.isalpha() for ch in lemma)
        ):
            phrases[-1].append(lemma)
        elif phrases[-1]:
            phrases.append([])
    return [p for p in phrases if p]


def lemmatize(text: str, nlp: Language | None = None) -> list[str]:
    """Return lowercase lemmas with stop words, punctuation, numbers and whitespace removed.

    Example: "Built scalable APIs using Python" -> ["build", "scalable", "api", "use", "python"]
    """
    nlp = nlp or get_nlp()
    doc = nlp(clean_text(text))
    return [t for phrase in phrases_from_doc(doc, use_lemma=has_lemmatizer(nlp)) for t in phrase]
