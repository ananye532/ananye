"""Loads the spaCy pipeline once per process."""

from __future__ import annotations

import logging
import os
from functools import lru_cache

import spacy
from spacy.language import Language

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("SPACY_MODEL", "en_core_web_sm")


@lru_cache(maxsize=4)
def get_nlp(model: str = DEFAULT_MODEL) -> Language:
    """Return a cached spaCy pipeline.

    The dependency parser is disabled because nothing here needs syntax trees,
    and that roughly halves processing time. If the model is not installed, a
    blank English pipeline is returned instead: tokenization and skill matching
    still work, but lemmas, POS tags and named entities are unavailable, and
    keyword ranking skips its POS filter.
    """
    try:
        return spacy.load(model, disable=["parser"])
    except OSError:
        logger.warning("spaCy model %r not found; falling back to spacy.blank('en')", model)
        return spacy.blank("en")


def has_lemmatizer(nlp: Language) -> bool:
    return "lemmatizer" in nlp.pipe_names


def has_tagger(nlp: Language) -> bool:
    return "tagger" in nlp.pipe_names


def has_ner(nlp: Language) -> bool:
    return "ner" in nlp.pipe_names
