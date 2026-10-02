from app.nlp.preprocessing import clean_text, lemmatize, split_chunks


def test_clean_text_normalizes_ligatures_bullets_and_spaces():
    raw = "ﬁnance  • Python\r\n\n\n\nNext\x00"
    assert clean_text(raw) == "finance Python\n\nNext"


def test_lemmatize_removes_stopwords_numbers_and_punctuation():
    lemmas = lemmatize("Built 3 scalable APIs, and managed the databases!")
    assert lemmas == ["build", "scalable", "api", "manage", "database"]


def test_split_chunks_on_sentences_and_lines():
    assert split_chunks("One. Two!\nThree") == ["One.", "Two!", "Three"]
