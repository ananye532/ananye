"""Curated skill taxonomy and role profiles.

Every detected skill traces back to an entry here, so results are explainable.
The trade-off is recall: skills missing from the list are not detected.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

LANG = "Languages"
FRONTEND = "Frontend"
BACKEND = "Backend"
MOBILE = "Mobile"
DATA = "Data & Analytics"
ML = "AI & Machine Learning"
CLOUD = "Cloud & DevOps"
DB = "Databases"
TEST = "Testing & Quality"
SECURITY = "Security"
DESIGN = "Design & Product"
BUSINESS = "Business & Operations"
PRACTICE = "Practices"
SOFT = "Soft Skills"


@dataclass(frozen=True)
class Skill:
    name: str
    category: str
    aliases: tuple[str, ...] = ()  # case-insensitive
    cased: tuple[str, ...] = ()  # case-sensitive, for ambiguous words ("Go", "R")
    soft: bool = False


def _s(name: str, category: str, *aliases: str, cased: tuple[str, ...] = (), soft: bool = False) -> Skill:
    return Skill(name, category, aliases, cased, soft)


SKILLS: tuple[Skill, ...] = (
    # Languages
    _s("Python", LANG, "python", "python3"),
    _s("Java", LANG, "java"),
    _s("JavaScript", LANG, "javascript", "ecmascript", "es6", cased=("JS",)),
    _s("TypeScript", LANG, "typescript", cased=("TS",)),
    _s("C++", LANG, "c++", "cpp"),
    _s("C#", LANG, "c#", "csharp"),
    _s("C", LANG, cased=("C",)),
    _s("Go", LANG, "golang", cased=("Go",)),
    _s("Rust", LANG, cased=("Rust",)),
    _s("Ruby", LANG, "ruby"),
    _s("PHP", LANG, "php"),
    _s("Kotlin", LANG, "kotlin"),
    _s("Swift", LANG, cased=("Swift",)),
    _s("Scala", LANG, "scala"),
    _s("R", LANG, cased=("R",)),
    _s("SQL", LANG, "sql"),
    _s("Bash", LANG, "bash", "shell scripting"),
    _s("HTML", FRONTEND, "html", "html5"),
    _s("CSS", FRONTEND, "css", "css3", "sass", "scss"),
    # Frontend
    _s("React", FRONTEND, "react", "react.js", "reactjs"),
    _s("Next.js", FRONTEND, "next.js", "nextjs"),
    _s("Vue.js", FRONTEND, "vue", "vue.js", "vuejs"),
    _s("Angular", FRONTEND, "angular", "angularjs"),
    _s("Svelte", FRONTEND, "svelte", "sveltekit"),
    _s("Redux", FRONTEND, "redux"),
    _s("Tailwind CSS", FRONTEND, "tailwind", "tailwindcss", "tailwind css"),
    _s("Webpack", FRONTEND, "webpack"),
    _s("Vite", FRONTEND, cased=("Vite",)),
    _s("Accessibility", FRONTEND, "accessibility", "wcag", "a11y"),
    # Backend
    _s("Node.js", BACKEND, "node.js", "nodejs", cased=("Node",)),
    _s("Express", BACKEND, "express.js", "expressjs", cased=("Express",)),
    _s("Django", BACKEND, "django"),
    _s("Flask", BACKEND, "flask"),
    _s("FastAPI", BACKEND, "fastapi"),
    _s("Spring Boot", BACKEND, "spring boot", "spring framework"),
    _s(".NET", BACKEND, ".net", "asp.net", "dotnet"),
    _s("Ruby on Rails", BACKEND, "rails", "ruby on rails"),
    _s("GraphQL", BACKEND, "graphql"),
    _s("REST APIs", BACKEND, "restful", "rest api", "rest apis"),
    _s("gRPC", BACKEND, "grpc"),
    _s("Microservices", BACKEND, "microservices", "microservice"),
    _s("Kafka", BACKEND, "kafka"),
    _s("RabbitMQ", BACKEND, "rabbitmq"),
    _s("Distributed Systems", BACKEND, "distributed systems"),
    _s("System Design", BACKEND, "system design"),
    # Mobile
    _s("iOS", MOBILE, "ios"),
    _s("Android", MOBILE, "android"),
    _s("React Native", MOBILE, "react native"),
    _s("Flutter", MOBILE, "flutter"),
    # Data
    _s("Pandas", DATA, "pandas"),
    _s("NumPy", DATA, "numpy"),
    _s("Spark", DATA, "spark", "pyspark", "apache spark"),
    _s("Airflow", DATA, "airflow"),
    _s("dbt", DATA, cased=("dbt",)),
    _s("ETL", DATA, "etl", "elt", "data pipelines", "data pipeline"),
    _s("Tableau", DATA, "tableau"),
    _s("Power BI", DATA, "power bi", "powerbi"),
    _s("Excel", DATA, cased=("Excel",)),
    _s("Snowflake", DATA, "snowflake"),
    _s("BigQuery", DATA, "bigquery"),
    _s("Data Visualization", DATA, "data visualization", "dashboards", "dashboarding"),
    _s("Statistics", DATA, "statistics", "statistical analysis", "a/b testing", "hypothesis testing"),
    # ML
    _s("Machine Learning", ML, "machine learning", cased=("ML",)),
    _s("Deep Learning", ML, "deep learning"),
    _s("PyTorch", ML, "pytorch"),
    _s("TensorFlow", ML, "tensorflow", "keras"),
    _s("scikit-learn", ML, "scikit-learn", "sklearn"),
    _s("NLP", ML, "nlp", "natural language processing"),
    _s("Computer Vision", ML, "computer vision", "opencv"),
    _s("LLMs", ML, "llm", "llms", "large language models", "generative ai", "genai", "prompt engineering"),
    _s("RAG", ML, "retrieval-augmented generation", cased=("RAG",)),
    _s("MLOps", ML, "mlops"),
    # Cloud & DevOps
    _s("AWS", CLOUD, "aws", "amazon web services", "ec2", "aws lambda"),
    _s("Azure", CLOUD, "azure"),
    _s("GCP", CLOUD, "gcp", "google cloud"),
    _s("Docker", CLOUD, "docker", "containers"),
    _s("Kubernetes", CLOUD, "kubernetes", "k8s"),
    _s("Terraform", CLOUD, "terraform", "infrastructure as code"),
    _s("CI/CD", CLOUD, "ci/cd", "continuous integration", "continuous delivery", "github actions", "jenkins", "gitlab ci"),
    _s("Linux", CLOUD, "linux", "unix"),
    _s("Git", CLOUD, "git", "github", "gitlab"),
    _s("Observability", CLOUD, "observability", "prometheus", "grafana", "datadog", "monitoring"),
    # Databases
    _s("PostgreSQL", DB, "postgresql", "postgres"),
    _s("MySQL", DB, "mysql"),
    _s("MongoDB", DB, "mongodb", "mongo"),
    _s("Redis", DB, "redis"),
    _s("Elasticsearch", DB, "elasticsearch", "opensearch"),
    _s("DynamoDB", DB, "dynamodb"),
    # Testing
    _s("Unit Testing", TEST, "unit testing", "unit tests", "tdd", "test-driven development"),
    _s("Jest", TEST, "jest"),
    _s("Pytest", TEST, "pytest"),
    _s("Cypress", TEST, "cypress"),
    _s("Playwright", TEST, "playwright"),
    _s("Selenium", TEST, "selenium"),
    # Security
    _s("Cybersecurity", SECURITY, "cybersecurity", "information security", "infosec"),
    _s("OAuth", SECURITY, "oauth", "oauth2", "oidc", "sso"),
    _s("Penetration Testing", SECURITY, "penetration testing", "pentesting"),
    # Design & Product
    _s("Figma", DESIGN, "figma"),
    _s("UX Research", DESIGN, "ux research", "user research", "usability testing"),
    _s("UI/UX Design", DESIGN, "ui/ux", "ux design", "ui design", "interaction design", "wireframing", "prototyping"),
    _s("Product Management", DESIGN, "product management", "product roadmap", "roadmapping"),
    _s("Product Strategy", DESIGN, "product strategy", "go-to-market"),
    # Business
    _s("Project Management", BUSINESS, "project management", "pmp"),
    _s("Agile", PRACTICE, "agile", "scrum", "kanban", "sprint planning"),
    _s("Jira", BUSINESS, "jira", "confluence"),
    _s("Salesforce", BUSINESS, "salesforce", "crm"),
    _s("SEO", BUSINESS, "seo", "search engine optimization"),
    _s("Digital Marketing", BUSINESS, "digital marketing", "content marketing", "paid media", "google ads"),
    _s("Financial Modeling", BUSINESS, "financial modeling", "financial analysis", "forecasting", "budgeting"),
    _s("Stakeholder Management", BUSINESS, "stakeholder management", "stakeholders"),
    _s("Data-Driven Decisions", BUSINESS, "kpis", "okrs", "metrics"),
    # Practices
    _s("Code Review", PRACTICE, "code review", "code reviews"),
    _s("Performance Optimization", PRACTICE, "performance optimization", "performance tuning", "latency", "scalability"),
    _s("API Design", PRACTICE, "api design"),
    # Soft skills
    _s("Leadership", SOFT, "leadership", "led", "lead", "mentored", "mentoring", soft=True),
    _s("Communication", SOFT, "communication", "presented", "presentations", "public speaking", soft=True),
    _s("Collaboration", SOFT, "collaboration", "collaborated", "cross-functional", "teamwork", soft=True),
    _s("Problem Solving", SOFT, "problem solving", "problem-solving", "troubleshooting", soft=True),
    _s("Ownership", SOFT, "ownership", "owned", "end-to-end", soft=True),
    _s("Adaptability", SOFT, "adaptability", "fast-paced", soft=True),
)


@dataclass(frozen=True)
class RoleProfile:
    name: str
    core: tuple[str, ...]  # canonical skill names
    nice: tuple[str, ...]
    keywords: tuple[str, ...]


ROLES: tuple[RoleProfile, ...] = (
    RoleProfile(
        "Frontend Engineer",
        ("JavaScript", "TypeScript", "React", "HTML", "CSS"),
        ("Next.js", "Accessibility", "Unit Testing", "Redux", "Tailwind CSS", "Performance Optimization", "Figma"),
        ("component", "ui", "design system", "web performance", "responsive"),
    ),
    RoleProfile(
        "Backend Engineer",
        ("Python", "SQL", "REST APIs", "PostgreSQL", "Docker"),
        ("Go", "Java", "Kubernetes", "Microservices", "Redis", "Kafka", "System Design", "AWS", "Unit Testing"),
        ("api", "service", "scalable", "database", "throughput"),
    ),
    RoleProfile(
        "Full-Stack Engineer",
        ("JavaScript", "TypeScript", "React", "Node.js", "SQL"),
        ("PostgreSQL", "Docker", "AWS", "GraphQL", "Next.js", "CI/CD", "Unit Testing"),
        ("full-stack", "end-to-end", "frontend", "backend"),
    ),
    RoleProfile(
        "Data Scientist",
        ("Python", "SQL", "Statistics", "Machine Learning", "Pandas"),
        ("scikit-learn", "PyTorch", "TensorFlow", "Data Visualization", "Spark", "NLP", "Tableau"),
        ("model", "experiment", "insight", "prediction", "analysis"),
    ),
    RoleProfile(
        "Machine Learning Engineer",
        ("Python", "Machine Learning", "PyTorch", "Docker", "MLOps"),
        ("TensorFlow", "Kubernetes", "LLMs", "RAG", "AWS", "Spark", "Distributed Systems"),
        ("training", "inference", "model", "pipeline", "deployment"),
    ),
    RoleProfile(
        "Data Engineer",
        ("Python", "SQL", "ETL", "Spark", "Airflow"),
        ("Snowflake", "BigQuery", "dbt", "Kafka", "AWS", "Terraform", "Docker"),
        ("pipeline", "warehouse", "ingestion", "batch", "streaming"),
    ),
    RoleProfile(
        "Data Analyst",
        ("SQL", "Excel", "Data Visualization", "Statistics"),
        ("Tableau", "Power BI", "Python", "Pandas", "Data-Driven Decisions", "Communication"),
        ("report", "dashboard", "insight", "trend", "stakeholder"),
    ),
    RoleProfile(
        "DevOps / Platform Engineer",
        ("Linux", "Docker", "Kubernetes", "CI/CD", "Terraform"),
        ("AWS", "GCP", "Azure", "Observability", "Bash", "Python", "Go"),
        ("infrastructure", "reliability", "deployment", "uptime", "incident"),
    ),
    RoleProfile(
        "Mobile Engineer",
        ("Swift", "Kotlin", "iOS", "Android"),
        ("React Native", "Flutter", "Unit Testing", "CI/CD", "REST APIs"),
        ("app", "mobile", "release", "app store"),
    ),
    RoleProfile(
        "Product Manager",
        ("Product Management", "Product Strategy", "Stakeholder Management", "Data-Driven Decisions", "Agile"),
        ("UX Research", "SQL", "Jira", "Communication", "Leadership", "Figma"),
        ("roadmap", "launch", "customer", "requirements", "prioritization"),
    ),
    RoleProfile(
        "Product Designer",
        ("Figma", "UI/UX Design", "UX Research"),
        ("Accessibility", "HTML", "CSS", "Communication", "Collaboration"),
        ("design system", "prototype", "user", "journey", "usability"),
    ),
    RoleProfile(
        "Marketing Specialist",
        ("Digital Marketing", "SEO", "Data-Driven Decisions"),
        ("Salesforce", "Excel", "Communication", "Data Visualization", "Project Management"),
        ("campaign", "conversion", "brand", "audience", "growth"),
    ),
    RoleProfile(
        "Project Manager",
        ("Project Management", "Agile", "Stakeholder Management", "Jira"),
        ("Communication", "Leadership", "Excel", "Financial Modeling"),
        ("delivery", "timeline", "budget", "risk", "scope"),
    ),
)

SKILL_BY_NAME: dict[str, Skill] = {s.name: s for s in SKILLS}
ROLE_BY_NAME: dict[str, RoleProfile] = {r.name.lower(): r for r in ROLES}


def _boundary(term: str) -> str:
    # Symbols like +, #, . are part of skill names (C++, C#, .NET, Node.js), so a plain \b won't do.
    return rf"(?<![\w+#/.-]){re.escape(term)}(?![\w+#/-]|\.\w)"


@lru_cache(maxsize=1)
def compiled_patterns() -> tuple[tuple[Skill, re.Pattern[str], re.Pattern[str] | None], ...]:
    out = []
    for skill in SKILLS:
        insensitive = list(skill.aliases) if skill.cased else [skill.name.lower(), *skill.aliases]
        ipat = (
            re.compile("|".join(_boundary(t) for t in sorted(set(insensitive), key=len, reverse=True)), re.IGNORECASE)
            if insensitive
            else re.compile(r"(?!x)x")
        )
        cpat = re.compile("|".join(_boundary(t) for t in skill.cased)) if skill.cased else None
        out.append((skill, ipat, cpat))
    return tuple(out)


def find_role(name: str | None) -> RoleProfile | None:
    if not name:
        return None
    key = name.strip().lower()
    if key in ROLE_BY_NAME:
        return ROLE_BY_NAME[key]
    for role in ROLES:
        head = role.name.lower().split(" /")[0]
        if head in key or key in head:
            return role
    return None
