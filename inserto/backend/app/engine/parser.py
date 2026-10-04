"""Resume text -> structured fields: contact, sections, roles, education, bullets."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from datetime import date

from .lexicon import DEGREE_RANKS

SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "summary": ("summary", "professional summary", "profile", "professional profile", "about", "about me",
                "objective", "career objective", "career summary", "executive summary", "overview"),
    "experience": ("experience", "work experience", "professional experience", "employment",
                   "employment history", "work history", "relevant experience", "career history",
                   "professional background", "industry experience", "work"),
    "education": ("education", "academic background", "academics", "education and training",
                  "education & training", "academic qualifications", "qualifications", "school"),
    "skills": ("skills", "technical skills", "core competencies", "competencies", "technologies",
               "tech stack", "key skills", "skills and tools", "skills & tools", "tools", "expertise",
               "areas of expertise", "skills & technologies", "skills and technologies", "core skills"),
    "projects": ("projects", "personal projects", "selected projects", "key projects", "academic projects",
                 "side projects", "open source"),
    "certifications": ("certifications", "certificates", "licenses", "licenses and certifications",
                       "licenses & certifications", "certifications & licenses", "courses", "training"),
    "awards": ("awards", "honors", "honours", "awards and honors", "awards & honors", "achievements",
               "accomplishments", "recognition"),
    "publications": ("publications", "research", "papers", "talks", "publications & talks"),
    "volunteer": ("volunteer", "volunteering", "volunteer experience", "community", "community involvement"),
    "leadership": ("leadership", "activities", "extracurricular", "extracurricular activities",
                   "leadership & activities", "leadership experience"),
    "languages": ("languages", "language skills"),
    "interests": ("interests", "hobbies", "hobbies and interests", "hobbies & interests"),
}
SECTION_LABELS = {
    "header": "Header", "summary": "Summary", "experience": "Experience", "education": "Education",
    "skills": "Skills", "projects": "Projects", "certifications": "Certifications", "awards": "Awards",
    "publications": "Publications", "volunteer": "Volunteering", "leadership": "Leadership",
    "languages": "Languages", "interests": "Interests",
}
_ALIAS_TO_KEY = {alias: key for key, aliases in SECTION_ALIASES.items() for alias in aliases}

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}
_MONTH = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?"
_DATE = rf"(?:{_MONTH}\s*'?\d{{2,4}}|\d{{1,2}}\s*/\s*\d{{4}}|(?:19|20)\d{{2}})"
_END = rf"(?:{_DATE}|present|current|now|today|ongoing)"
DATE_RANGE = re.compile(rf"(?P<start>{_DATE})\s*(?:-|–|—|to|until|→)\s*(?P<end>{_END})", re.IGNORECASE)
SINGLE_YEAR = re.compile(r"\b(19[5-9]\d|20[0-4]\d)\b")

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"(?:\+?\d{1,3}[\s.-]?)?(?:\(\d{2,4}\)|\d{2,4})[\s.-]?\d{3,4}[\s.-]?\d{3,4}")
URL = re.compile(r"(?:https?://)?(?:www\.)?(?:linkedin\.com/in/[\w-]+|github\.com/[\w-]+|[\w-]+\.(?:dev|io|me|com|net|org|app)(?:/[\w./-]*)?)", re.IGNORECASE)
LOCATION = re.compile(r"\b([A-Z][a-zA-Z.]+(?:\s[A-Z][a-zA-Z.]+)*,\s?(?:[A-Z]{2}|[A-Z][a-z]+(?:\s[A-Z][a-z]+)*))\b")
BULLET_LINE = re.compile(r"^\s*(?:[•*–—>-]|\d{1,2}[.)])\s+")
GPA = re.compile(r"\b(?:gpa|cgpa)\s*[:\-]?\s*(\d(?:\.\d{1,2})?)\s*(?:/\s*(\d(?:\.\d)?))?", re.IGNORECASE)


@dataclass
class Contact:
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    links: list[str] = field(default_factory=list)


@dataclass
class Section:
    key: str
    title: str
    start_line: int
    lines: list[str]


@dataclass
class Role:
    title: str
    company: str | None
    start: str | None
    end: str | None
    start_ym: tuple[int, int] | None
    end_ym: tuple[int, int] | None
    is_current: bool
    duration_months: int | None
    bullets: list[str]


@dataclass
class EducationEntry:
    institution: str | None
    degree: str | None
    degree_level: str | None
    degree_rank: int
    year: int | None
    gpa: str | None


@dataclass
class ParsedResume:
    contact: Contact
    sections: list[Section]
    summary: str | None
    roles: list[Role]
    education: list[EducationEntry]
    skills_listed: list[str]
    certifications: list[str]
    bullets: list[str]
    lines: list[str]
    word_count: int

    def section(self, key: str) -> Section | None:
        return next((s for s in self.sections if s.key == key), None)

    def to_dict(self) -> dict:
        d = asdict(self)
        d.pop("lines")
        for s in d["sections"]:
            s["label"] = SECTION_LABELS.get(s["key"], s["title"])
            s["line_count"] = len(s.pop("lines"))
        for r in d["roles"]:
            r.pop("start_ym")
            r.pop("end_ym")
        return d


def heading_key(line: str) -> str | None:
    stripped = line.strip().strip(":").strip()
    if not stripped or len(stripped) > 45 or len(stripped.split()) > 5:
        return None
    norm = re.sub(r"[^a-z& ]", "", stripped.lower()).strip()
    norm = re.sub(r"\s+", " ", norm)
    return _ALIAS_TO_KEY.get(norm)


def split_sections(lines: list[str]) -> list[Section]:
    sections: list[Section] = [Section("header", "Header", 0, [])]
    for i, line in enumerate(lines):
        key = heading_key(line)
        if key and not any(s.key == key for s in sections):
            sections.append(Section(key, line.strip().strip(":"), i, []))
        elif line.strip():
            sections[-1].lines.append(line)
    return sections


def parse_contact(header_lines: list[str], full_text: str) -> Contact:
    head = "\n".join(header_lines[:8]) or "\n".join(full_text.splitlines()[:8])
    contact = Contact()
    if m := EMAIL.search(full_text):
        contact.email = m.group(0).rstrip(".")
    for m in PHONE.finditer(head):
        digits = re.sub(r"\D", "", m.group(0))
        if 9 <= len(digits) <= 15 and not re.fullmatch(r"(19|20)\d{2}(19|20)\d{2}", digits):
            contact.phone = m.group(0).strip()
            break
    seen: set[str] = set()
    for m in URL.finditer(head):
        url = m.group(0).rstrip(".,")
        if contact.email and url in contact.email:
            continue
        if url.lower() not in seen:
            seen.add(url.lower())
            contact.links.append(url)
    for line in header_lines[:4]:
        cand = line.strip()
        if (cand and 1 < len(cand.split()) <= 4 and not any(ch.isdigit() for ch in cand)
                and "@" not in cand and re.fullmatch(r"[A-Za-zÀ-ɏ.' -]+", cand)
                and not heading_key(cand) and not re.search(r"\b(resume|r\u00e9sum\u00e9|cv|curriculum)\b", cand, re.I)):
            contact.name = cand.title() if cand.isupper() else cand
            break
    for line in header_lines[:6]:
        if contact.email and contact.email in line:
            line = line.replace(contact.email, " ")
        if m := LOCATION.search(line):
            contact.location = m.group(1)
            break
    return contact


def _parse_ym(token: str) -> tuple[int, int] | None:
    t = token.strip().lower().replace("'", "")
    if m := re.match(r"(\d{1,2})\s*/\s*(\d{4})", t):
        return int(m.group(2)), max(1, min(12, int(m.group(1))))
    if m := re.match(r"([a-z]+)\.?\s*(\d{2,4})", t):
        year = int(m.group(2))
        year = year + 2000 if year < 100 else year
        return year, MONTHS.get(m.group(1)[:3], 1)
    if m := re.match(r"(\d{4})", t):
        return int(m.group(1)), 1
    return None


def _months_between(a: tuple[int, int], b: tuple[int, int]) -> int:
    return max(0, (b[0] - a[0]) * 12 + (b[1] - a[1]) + 1)


def is_bullet(line: str) -> bool:
    return bool(BULLET_LINE.match(line))


def strip_bullet(line: str) -> str:
    return BULLET_LINE.sub("", line).strip()


def _split_title_company(header: list[str]) -> tuple[str, str | None]:
    parts = [p for p in header if p]
    if not parts:
        return "Untitled role", None
    first = parts[0]
    for sep in (" at ", " @ ", " | ", " — ", " – ", " - ", ", "):
        if sep in first:
            a, b = first.split(sep, 1)
            return a.strip(" ,|-"), b.strip(" ,|-") or None
    return first.strip(" ,|-"), (parts[1].strip(" ,|-") if len(parts) > 1 else None)


def parse_roles(section: Section | None, today: date) -> list[Role]:
    if not section:
        return []
    roles: list[Role] = []
    header: list[str] = []
    current: Role | None = None
    for raw in section.lines:
        line = raw.strip()
        m = DATE_RANGE.search(line)
        if is_bullet(line) or (current and not m and len(line.split()) > 9):
            if current is None:
                current = Role("Untitled role", None, None, None, None, None, False, None, [])
                roles.append(current)
            if header and current.bullets:  # header lines without a date after bullets: a new role
                title, company = _split_title_company(header)
                current = Role(title, company, None, None, None, None, False, None, [])
                roles.append(current)
            header = []
            current.bullets.append(strip_bullet(line))
            continue
        if m:
            remainder = (line[: m.start()] + line[m.end():]).strip(" ,|()–—-")
            hdr = [h for h in [*header, remainder] if h]
            title, company = _split_title_company(hdr)
            start_ym = _parse_ym(m.group("start"))
            end_raw = m.group("end")
            is_current = end_raw.lower() in {"present", "current", "now", "today", "ongoing"}
            end_ym = (today.year, today.month) if is_current else _parse_ym(end_raw)
            duration = _months_between(start_ym, end_ym) if start_ym and end_ym and end_ym >= start_ym else None
            current = Role(title, company, m.group("start"), end_raw, start_ym, end_ym, is_current, duration, [])
            roles.append(current)
            header = []
        else:
            header.append(line)
            if current and current.bullets and len(header) > 2:
                header = header[-2:]
            elif current and not current.bullets and current.company is None and len(header) == 1:
                current.company = line.strip(" ,|-")
                header = []
    return [r for r in roles if r.bullets or r.start]


def parse_education(section: Section | None) -> list[EducationEntry]:
    if not section:
        return []
    entries: list[EducationEntry] = []
    block: list[str] = []

    def flush() -> None:
        if not block:
            return
        text = " ".join(block)
        low = f" {text.lower()} "
        rank, level, degree = 0, None, None
        for cue, (r, lvl) in DEGREE_RANKS.items():
            if cue in low and r > rank:
                rank, level = r, lvl
        for line in block:
            if any(cue in f" {line.lower()} " for cue in DEGREE_RANKS):
                degree = re.split(r"\s[|\u2022\u00b7]\s|\bc?gpa\b", DATE_RANGE.sub("", line), flags=re.I)[0]
                degree = SINGLE_YEAR.sub("", degree).strip(" ,|-()")
                break
        inst = next((ln for ln in block if re.search(r"universit|college|institut|school|academy|polytechnic", ln, re.I)), None)
        if inst:
            inst = DATE_RANGE.sub("", inst).strip(" ,|-")
            inst = SINGLE_YEAR.sub("", inst).strip(" ,|-")
        years = [int(y) for y in SINGLE_YEAR.findall(text)]
        gpa_m = GPA.search(text)
        gpa = None
        if gpa_m:
            gpa = gpa_m.group(1) + (f"/{gpa_m.group(2)}" if gpa_m.group(2) else "")
        if inst or degree:
            entries.append(EducationEntry(inst, degree, level, rank, max(years) if years else None, gpa))

    for line in section.lines:
        starts_new = re.search(r"universit|college|institut|school|academy", line, re.I) and block and any(
            re.search(r"universit|college|institut|school|academy", b, re.I) for b in block)
        if starts_new:
            flush()
            block = []
        block.append(strip_bullet(line))
    flush()
    return entries


def parse_list_section(section: Section | None) -> list[str]:
    if not section:
        return []
    items: list[str] = []
    for line in section.lines:
        body = strip_bullet(line)
        if ":" in body and len(body.split(":")[0].split()) <= 4:
            body = body.split(":", 1)[1]
        for piece in re.split(r"[,;|•·]", body):
            piece = piece.strip(" .")
            if 1 <= len(piece) <= 40 and len(piece.split()) <= 5:
                items.append(piece)
    return list(dict.fromkeys(items))


def parse(text: str, today: date | None = None) -> ParsedResume:
    today = today or date.today()
    lines = [ln for ln in text.split("\n")]
    sections = split_sections(lines)
    by_key = {s.key: s for s in sections}
    contact = parse_contact(by_key["header"].lines, text)
    summary_sec = by_key.get("summary")
    summary = " ".join(summary_sec.lines).strip() if summary_sec else None
    roles = parse_roles(by_key.get("experience"), today)
    education = parse_education(by_key.get("education"))
    skills_listed = parse_list_section(by_key.get("skills"))
    certs = [strip_bullet(ln) for ln in by_key["certifications"].lines] if "certifications" in by_key else []

    bullets: list[str] = []
    for sec in sections:
        if sec.key in {"experience", "projects", "leadership", "volunteer"}:
            for ln in sec.lines:
                if is_bullet(ln):
                    bullets.append(strip_bullet(ln))
                elif sec.key == "experience" and len(ln.split()) > 9 and not DATE_RANGE.search(ln):
                    # Paragraph-style experience: treat each sentence as a bullet.
                    bullets.extend(s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])", ln) if len(s.split()) >= 3)
    bullets = list(dict.fromkeys(b for b in bullets if b))
    word_count = len(re.findall(r"\b\w[\w'+#.-]*\b", text))
    return ParsedResume(contact, sections, summary, roles, education, skills_listed, certs, bullets, lines, word_count)
