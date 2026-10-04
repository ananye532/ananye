"""Word lists used by the content checks."""

STRONG_VERBS: frozenset[str] = frozenset(
    """
    accelerated achieved acquired adapted administered advanced advised advocated analyzed architected
    assembled assessed audited authored automated benchmarked boosted built calculated captured
    championed clarified coached collaborated combined completed composed conceived conceptualized
    conducted consolidated constructed consulted converted coordinated created cultivated customized
    cut debugged decreased defined delivered deployed designed developed devised diagnosed directed
    discovered doubled drove earned eliminated enabled engineered enhanced established evaluated exceeded
    executed expanded expedited facilitated forecasted formulated founded generated grew guided halved
    headed identified implemented improved increased influenced initiated innovated inspected instituted
    integrated introduced invented launched led leveraged lowered maintained managed mapped maximized
    measured mentored migrated minimized modeled modernized monitored motivated negotiated optimized
    orchestrated organized originated outperformed overhauled oversaw partnered performed pioneered
    planned presented prioritized produced programmed promoted proposed prototyped published raised
    rebuilt recommended reconciled recruited redesigned reduced refactored refined reorganized
    resolved restructured revamped reviewed saved scaled secured shipped simplified slashed solved
    spearheaded standardized streamlined strengthened structured supervised surpassed taught tested
    trained transformed tripled troubleshot unified upgraded validated won wrote
    """.split()
)

# Weak openers and their stronger alternatives.
WEAK_PHRASES: dict[str, str] = {
    "responsible for": "Led / Owned / Managed",
    "worked on": "Built / Developed / Delivered",
    "helped": "Contributed to / Enabled / Supported",
    "assisted": "Supported / Partnered on / Enabled",
    "involved in": "Contributed to / Drove",
    "participated in": "Contributed to / Collaborated on",
    "tasked with": "Owned / Delivered",
    "duties included": "Delivered / Owned",
    "handled": "Managed / Resolved / Owned",
    "was in charge of": "Led / Directed",
    "did": "Executed / Delivered",
    "made": "Built / Created",
    "used": "Applied / Leveraged",
    "worked with": "Partnered with / Collaborated with",
}

BUZZWORDS: frozenset[str] = frozenset(
    {
        "synergy",
        "go-getter",
        "team player",
        "hard worker",
        "hardworking",
        "detail-oriented",
        "results-driven",
        "self-starter",
        "think outside the box",
        "best of breed",
        "dynamic",
        "motivated",
        "passionate",
        "guru",
        "ninja",
        "rockstar",
        "proven track record",
        "go-to person",
        "value add",
        "excellent communication skills",
        "strategic thinker",
        "out-of-the-box",
    }
)

FIRST_PERSON = ("i", "me", "my", "mine", "we", "our", "us")

ACHIEVEMENT_CUES: tuple[str, ...] = (
    "increased", "reduced", "improved", "grew", "saved", "cut", "boosted", "achieved", "won",
    "awarded", "exceeded", "launched", "doubled", "tripled", "halved", "accelerated", "decreased",
    "generated", "delivered", "recognized", "promoted", "ranked", "top", "record",
)

DEGREE_RANKS: dict[str, tuple[int, str]] = {
    "phd": (5, "Doctorate"),
    "ph.d": (5, "Doctorate"),
    "doctor": (5, "Doctorate"),
    "mba": (4, "Master's"),
    "master": (4, "Master's"),
    "m.s": (4, "Master's"),
    "msc": (4, "Master's"),
    "m.sc": (4, "Master's"),
    "m.eng": (4, "Master's"),
    "m.tech": (4, "Master's"),
    "ms ": (4, "Master's"),
    "bachelor": (3, "Bachelor's"),
    "b.s": (3, "Bachelor's"),
    "b.a": (3, "Bachelor's"),
    "bsc": (3, "Bachelor's"),
    "b.sc": (3, "Bachelor's"),
    "b.tech": (3, "Bachelor's"),
    "b.e": (3, "Bachelor's"),
    "be ": (3, "Bachelor's"),
    "bs ": (3, "Bachelor's"),
    "ba ": (3, "Bachelor's"),
    "associate": (2, "Associate"),
    "diploma": (1, "Diploma"),
    "certificate": (1, "Certificate"),
    "high school": (1, "High school"),
}

STOPWORDS: frozenset[str] = frozenset(
    """
    a about above after again against all also am an and any are as at be because been before being
    below between both but by can could did do does doing down during each etc few for from further
    had has have having he her here hers herself him himself his how i if in into is it its itself
    just me more most my myself no nor not now of off on once only or other our ours ourselves out
    over own per same she should so some such than that the their theirs them themselves then there
    these they this those through to too under until up very via was we were what when where which
    while who whom why will with within without would you your yours yourself yourselves
    ability able across based candidate candidates company including include includes join looking
    must need new plus preferred required requirements responsibilities role strong team work working
    years year experience well using use strong excellent good great opportunity skills skill qualifications
    hands-on knowledge proficiency proficient familiarity familiar understanding ideal ideally bonus nice
    environment position apply applicants seeking we're you'll you're will equal employer benefits salary
    """.split()
)
