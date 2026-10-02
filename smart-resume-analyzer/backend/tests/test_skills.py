from app.nlp.skills import SKILLS, extract_skills, group_by_category


def names(text: str) -> set[str]:
    return set(extract_skills(text))


def test_matches_canonical_names_case_insensitively():
    assert {"Python", "PostgreSQL", "Docker"} <= names("python, POSTGRESQL and docker")


def test_aliases_map_to_canonical_name():
    hits = extract_skills("Deployed on k8s with postgres; used sklearn.")
    assert {"Kubernetes", "PostgreSQL", "scikit-learn"} <= set(hits)
    assert hits["Kubernetes"].matched_text == {"k8s"}


def test_symbols_in_skill_names():
    assert {"C++", "C#", "Node.js", "CI/CD", ".NET"} <= names("C++, C#, Node.js, CI/CD and .NET")


def test_longest_match_wins():
    found = names("Built apps in React Native.")
    assert "React Native" in found and "React" not in found


def test_ambiguous_words_require_exact_case():
    assert "Go" in names("Services written in Go.")
    assert "Go" not in names("Ready to go the extra mile.")
    assert "Excel" not in names("I excel at communication.")
    assert "REST APIs" not in names("the rest of the team")
    assert "REST APIs" in names("Designed REST endpoints")


def test_counts_mentions():
    assert extract_skills("Python here. More python there.")["Python"].count == 2


def test_no_false_positives_in_plain_text():
    assert names("I enjoy hiking and cooking on weekends.") == set()


def test_taxonomy_and_grouping():
    assert all(e.aliases or e.cased for e in SKILLS.values())
    assert group_by_category({"Python", "Docker", "Go"}) == {
        "DevOps & Infrastructure": ["Docker"],
        "Programming Languages": ["Go", "Python"],
    }
