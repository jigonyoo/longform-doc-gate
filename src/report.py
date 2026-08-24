"""Render the document and, separately, the only thing a person has to read."""
from verify import OK

def render_document(tpl, verdicts):
    by = {}
    for v in verdicts:
        by.setdefault(v.claim.section_id, []).append(v)
    out = [f"# {tpl['title']}", ""]
    for spec in tpl["sections"]:
        out.append(f"## {spec['heading']}")
        vs = by.get(spec["id"], [])
        body = [v for v in vs if v.claim.text]
        if not body:
            out += ["> **GAP — nothing in the corpus answers this.** "
                    "Left open on purpose rather than filled with a plausible sentence.", ""]
            continue
        for v in body:
            mark = "" if v.verdict == OK else f" **[{v.verdict}]**"
            cite = v.evidence[0] if v.evidence else "-"
            out.append(f"{v.claim.text}{mark} `[{cite}]`")
        out.append("")
    return "\n".join(out)

def render_queue(verdicts):
    flagged = [v for v in verdicts if v.verdict != OK]
    total = len(verdicts)
    out = ["# Review queue", "",
           f"{len(flagged)} of {total} claims need a person. "
           f"The other {total - len(flagged)} carry a current source and do not.", ""]
    if not flagged:
        out.append("Nothing flagged.")
    for i, v in enumerate(flagged, 1):
        out += [f"## {i}. {v.verdict} — section `{v.claim.section_id}`",
                f"- Claim: {v.claim.text or '(no text produced)'}",
                f"- Why: {v.why}",
                f"- Evidence: {', '.join(v.evidence) if v.evidence else 'none'}", ""]
    return "\n".join(out)

def stats(verdicts):
    c = {}
    for v in verdicts:
        c[v.verdict] = c.get(v.verdict, 0) + 1
    flagged = sum(n for k, n in c.items() if k != OK)
    return {"claims": len(verdicts), "flagged": flagged,
            "must_read": flagged, "counts": c}
