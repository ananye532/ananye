"""Skill extraction against a curated taxonomy using spaCy's PhraseMatcher.

Why a taxonomy instead of a learned model? Every match is explainable: it points
to a taxonomy entry and to the exact text that triggered it. The trade-off is
recall, since skills missing from the list are not found. See docs/LIMITATIONS.md.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from functools import lru_cache

from spacy.language import Language
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc
from spacy.util import filter_spans

from .pipeline import get_nlp

TAXONOMY_VERSION = "2026.10-1"


@dataclass(frozen=True)
class SkillEntry:
    category: str
    aliases: tuple[str, ...] = ()  # matched case-insensitively
    cased: tuple[str, ...] = ()  # matched case-sensitively, for ambiguous words ("Go", "Excel", "R")


def _e(category: str, *aliases: str, cased: tuple[str, ...] = ()) -> SkillEntry:
    return SkillEntry(category, tuple(aliases), cased)


PL, WEB, DATA, ML, CLOUD, DEVOPS, DB, TEST, PRACTICE, TOOLS, SOFT = (
    "Programming Languages",
    "Web & Mobile",
    "Data Engineering & Analytics",
    "Machine Learning & AI",
    "Cloud",
    "DevOps & Infrastructure",
    "Databases",
    "Testing & Quality",
    "Practices & Methodologies",
    "Tools",
    "Soft Skills",
)

# canonical name -> entry. The canonical name itself is also matched
# case-insensitively unless the entry has `cased` aliases.
SKILLS: dict[str, SkillEntry] = {
    # Programming languages
    "Python": _e(PL, "python", "python3"),
    "Java": _e(PL, "java"),
    "JavaScript": _e(PL, "javascript", "ecmascript", "es6", cased=("JavaScript", "JS")),
    "TypeScript": _e(PL, "typescript"),
    "C++": _e(PL, "c++", "cpp"),
    "C#": _e(PL, "c#", "c sharp", "csharp"),
    "C": _e(PL, cased=("C",)),
    "Go": _e(PL, "golang", cased=("Go",)),
    "Rust": _e(PL, cased=("Rust",)),
    "Ruby": _e(PL, "ruby"),
    "PHP": _e(PL, "php"),
    "Kotlin": _e(PL, "kotlin"),
    "Swift": _e(PL, cased=("Swift",)),
    "Scala": _e(PL, "scala"),
    "R": _e(PL, cased=("R",)),
    "MATLAB": _e(PL, "matlab"),
    "SQL": _e(PL, "sql"),
    "Bash": _e(PL, "bash", "shell scripting", "shell script"),
    # Web & mobile
    "React": _e(WEB, "react", "react.js", "reactjs"),
    "React Native": _e(WEB, "react native"),
    "Angular": _e(WEB, "angular", "angularjs"),
    "Vue.js": _e(WEB, "vue", "vue.js", "vuejs"),
    "Next.js": _e(WEB, "next.js", "nextjs"),
    "Node.js": _e(WEB, "node.js", "nodejs", cased=("Node.js", "Node")),
    "Express": _e(WEB, "express.js", "expressjs", cased=("Express",)),
    "Django": _e(WEB, "django"),
    "Flask": _e(WEB, "flask"),
    "FastAPI": _e(WEB, "fastapi"),
    "Spring Boot": _e(WEB, "spring boot", "spring framework"),
    ".NET": _e(WEB, ".net", "dotnet", "asp.net"),
    "HTML": _e(WEB, "html", "html5"),
    "CSS": _e(WEB, "css", "css3", "sass", "scss"),
    "Tailwind CSS": _e(WEB, "tailwind", "tailwindcss", "tailwind css"),
    "REST APIs": _e(WEB, "restful", "rest api", "rest apis", "restful api", "restful apis", cased=("REST",)),
    "GraphQL": _e(WEB, "graphql"),
    "gRPC": _e(WEB, "grpc"),
    "Android": _e(WEB, "android"),
    "iOS": _e(WEB, "ios"),
    "Flutter": _e(WEB, "flutter"),
    # Data
    "pandas": _e(DATA, "pandas"),
    "NumPy": _e(DATA, "numpy"),
    "Apache Spark": _e(DATA, "apache spark", "pyspark", cased=("Spark",)),
    "Hadoop": _e(DATA, "hadoop"),
    "Apache Kafka": _e(DATA, "kafka", "apache kafka"),
    "Apache Airflow": _e(DATA, "airflow", "apache airflow"),
    "dbt": _e(DATA, cased=("dbt",)),
    "ETL": _e(DATA, "etl", "elt", "data pipeline", "data pipelines"),
    "Data Warehousing": _e(DATA, "data warehouse", "data warehousing"),
    "Snowflake": _e(DATA, cased=("Snowflake",)),
    "BigQuery": _e(DATA, "bigquery"),
    "Tableau": _e(DATA, "tableau"),
    "Power BI": _e(DATA, "power bi", "powerbi"),
    "Excel": _e(DATA, "microsoft excel", "ms excel", cased=("Excel",)),
    "Statistics": _e(DATA, "statistics", "statistical analysis", "statistical modeling"),
    "A/B Testing": _e(DATA, "a/b testing", "ab testing", "experimentation"),
    "Data Visualization": _e(DATA, "data visualization", "data visualisation"),
    # ML / AI
    "Machine Learning": _e(ML, "machine learning", cased=("Machine Learning", "ML")),
    "Deep Learning": _e(ML, "deep learning"),
    "Natural Language Processing": _e(ML, "natural language processing", "nlp"),
    "Computer Vision": _e(ML, "computer vision"),
    "scikit-learn": _e(ML, "scikit-learn", "sklearn", "scikit learn"),
    "TensorFlow": _e(ML, "tensorflow"),
    "PyTorch": _e(ML, "pytorch"),
    "Keras": _e(ML, "keras"),
    "spaCy": _e(ML, "spacy"),
    "Hugging Face Transformers": _e(ML, "hugging face", "huggingface"),
    "LLMs": _e(ML, "llm", "llms", "large language model", "large language models"),
    "MLOps": _e(ML, "mlops"),
    "XGBoost": _e(ML, "xgboost"),
    # Cloud
    "AWS": _e(CLOUD, "aws", "amazon web services"),
    "Azure": _e(CLOUD, "azure", "microsoft azure"),
    "GCP": _e(CLOUD, "gcp", "google cloud", "google cloud platform"),
    "AWS Lambda": _e(CLOUD, "aws lambda", cased=("Lambda",)),
    "Amazon S3": _e(CLOUD, "amazon s3", cased=("S3",)),
    "Serverless": _e(CLOUD, "serverless"),
    # DevOps
    "Docker": _e(DEVOPS, "docker", "containerization"),
    "Kubernetes": _e(DEVOPS, "kubernetes", "k8s"),
    "Terraform": _e(DEVOPS, "terraform"),
    "Ansible": _e(DEVOPS, "ansible"),
    "CI/CD": _e(DEVOPS, "ci/cd", "ci cd", "continuous integration", "continuous delivery", "continuous deployment"),
    "GitHub Actions": _e(DEVOPS, "github actions"),
    "Jenkins": _e(DEVOPS, "jenkins"),
    "Linux": _e(DEVOPS, "linux", "unix"),
    "Nginx": _e(DEVOPS, "nginx"),
    "Prometheus": _e(DEVOPS, "prometheus"),
    "Grafana": _e(DEVOPS, "grafana"),
    "Microservices": _e(DEVOPS, "microservices", "microservice", "microservice architecture"),
    # Databases
    "PostgreSQL": _e(DB, "postgresql", "postgres", "psql"),
    "MySQL": _e(DB, "mysql"),
    "SQLite": _e(DB, "sqlite"),
    "MongoDB": _e(DB, "mongodb"),
    "Redis": _e(DB, "redis"),
    "Elasticsearch": _e(DB, "elasticsearch", "elastic search", "opensearch"),
    "DynamoDB": _e(DB, "dynamodb"),
    "Cassandra": _e(DB, "cassandra"),
    "SQLAlchemy": _e(DB, "sqlalchemy"),
    # Testing
    "Unit Testing": _e(TEST, "unit testing", "unit tests", "unit test"),
    "pytest": _e(TEST, "pytest"),
    "Jest": _e(TEST, cased=("Jest",)),
    "Selenium": _e(TEST, "selenium"),
    "Cypress": _e(TEST, "cypress"),
    "Test-Driven Development": _e(TEST, "tdd", "test-driven development", "test driven development"),
    # Practices
    "Agile": _e(PRACTICE, "agile"),
    "Scrum": _e(PRACTICE, "scrum"),
    "Kanban": _e(PRACTICE, "kanban"),
    "Code Review": _e(PRACTICE, "code review", "code reviews"),
    "System Design": _e(PRACTICE, "system design", "distributed systems", "software architecture"),
    "Object-Oriented Programming": _e(PRACTICE, "oop", "object-oriented programming", "object oriented programming"),
    "Data Structures & Algorithms": _e(PRACTICE, "data structures", "algorithms"),
    "Security": _e(PRACTICE, "application security", "cybersecurity", "owasp"),
    # Tools
    "Git": _e(TOOLS, "git"),
    "GitHub": _e(TOOLS, "github"),
    "GitLab": _e(TOOLS, "gitlab"),
    "Jira": _e(TOOLS, "jira"),
    "Figma": _e(TOOLS, "figma"),
    # Soft skills
    "Communication": _e(SOFT, "communication", "communication skills", "written communication", "verbal communication"),
    "Leadership": _e(SOFT, "leadership", "led a team", "team lead", "mentoring", "mentored", "mentorship"),
    "Teamwork": _e(SOFT, "teamwork", "collaboration", "collaborative", "cross-functional"),
    "Problem Solving": _e(SOFT, "problem solving", "problem-solving", "troubleshooting"),
    "Project Management": _e(SOFT, "project management", "stakeholder management"),
}


@dataclass
class SkillHit:
    name: str
    category: str
    count: int = 0
    matched_text: set[str] = field(default_factory=set)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category,
            "count": self.count,
            "matched_text": sorted(self.matched_text),
        }


@lru_cache(maxsize=4)
def _matchers(nlp: Language) -> tuple[PhraseMatcher, PhraseMatcher]:
    lower = PhraseMatcher(nlp.vocab, attr="LOWER")
    cased = PhraseMatcher(nlp.vocab, attr="ORTH")
    for name, entry in SKILLS.items():
        insensitive = set(entry.aliases)
        if not entry.cased:
            insensitive.add(name.lower())
        if insensitive:
            lower.add(name, [nlp.make_doc(a) for a in sorted(insensitive)])
        if entry.cased:
            cased.add(name, [nlp.make_doc(a) for a in entry.cased])
    return lower, cased


def extract_skills(text: str, nlp: Language | None = None) -> dict[str, SkillHit]:
    """Return {canonical skill name: SkillHit}.

    Overlapping matches are resolved longest-first, so "React Native" does not
    also count as "React".
    """
    nlp = nlp or get_nlp()
    doc = nlp.make_doc(text)  # tokenization only; matching does not need the tagger
    lower, cased = _matchers(nlp)
    labels: dict[tuple[int, int], str] = {}
    for match_id, start, end in [*lower(doc), *cased(doc)]:
        labels[(start, end)] = nlp.vocab.strings[match_id]
    spans = [doc[start:end] for start, end in labels]

    hits: dict[str, SkillHit] = {}
    for span in filter_spans(spans):
        name = labels[(span.start, span.end)]
        hit = hits.setdefault(name, SkillHit(name, SKILLS[name].category))
        hit.count += 1
        hit.matched_text.add(span.text)
    return hits


def skill_token_indices(doc: Doc, nlp: Language) -> set[int]:
    """Token indices covered by any taxonomy skill match in `doc`."""
    lower, cased = _matchers(nlp)
    return {i for _, s, e in [*lower(doc), *cased(doc)] for i in range(s, e)}


def group_by_category(names: list[str] | set[str]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for n in sorted(names, key=str.lower):
        grouped[SKILLS[n].category].append(n)
    return dict(sorted(grouped.items()))
