"""Two retrievers. The naive one is here so the gated one has something to beat."""
import re
STOP = set("""the a an of to and or is are was were be been for in on by it its with that this at from as how
long does do did each end ends every any what when who which many much there their our your we you i""".split())

def stem(w: str) -> str:
    for suf in ("ies", "es", "ed", "ing", "s"):
        if len(w) > 4 and w.endswith(suf):
            return w[: -len(suf)]
    return w

def toks(s: str):
    return [stem(w) for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP]

def overlap(q, sec):
    qs = set(toks(q))
    return sum(1 for t in toks(sec.text + " " + sec.heading) if t in qs)

def coverage(q, sec):
    """Fraction of the question's content terms the section actually contains.
    A similarity score is not a refusal gate - this is."""
    qs = set(toks(q))
    if not qs:
        return 0.0
    have = set(toks(sec.text + " " + sec.heading))
    return len(qs & have) / len(qs)

MIN_COVERAGE = 0.5

def naive(corpus, question, region=""):
    """Raw overlap, no length normalisation, no status filter, no coverage floor.
    Longer documents win, and superseded editions are longer because they accumulate
    appendices and amendments."""
    ranked = sorted(corpus.sections, key=lambda s: -overlap(question, s))
    return ranked[0] if ranked and overlap(question, ranked[0]) else None

def gated(corpus, question, region=""):
    """Current editions only, region-aware, and every candidate must actually cover
    the question. Returns all admissible sections so contradictions stay visible."""
    cands = []
    for s in corpus.live():
        if region and s.region and s.region != region:
            continue
        cov = coverage(question, s)
        if cov < MIN_COVERAGE:
            continue
        cands.append((cov, overlap(question, s) / (1 + len(toks(s.text)) ** 0.5), s))
    cands.sort(key=lambda x: (-x[0], -x[1]))
    return [s for _, _, s in cands]
