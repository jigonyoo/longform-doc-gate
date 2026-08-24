"""The gate. Every claim gets one verdict and the evidence behind it."""
import re
from dataclasses import dataclass

OK, SUPERSEDED, CONTRADICTED, UNSUPPORTED = "OK", "SUPERSEDED", "CONTRADICTED", "UNSUPPORTED"
NUM = re.compile(r"\b(\d+)\b|\b(one|two|three|four|five|six|seven|eight|nine|ten|thirty|sixty|ninety)\b", re.I)

@dataclass
class Verdict:
    claim: object
    verdict: str
    why: str
    evidence: list

def numbers(s: str):
    return {(a or b).lower() for a, b in NUM.findall(s)}

def judge(claim):
    if claim.source is None or not claim.text:
        return Verdict(claim, UNSUPPORTED,
                       "no admissible current section answers this question", [])
    if claim.source.status == "superseded":
        return Verdict(claim, SUPERSEDED,
                       f"drawn from {claim.source.doc_id}, which is superseded", [claim.source.cite])
    mine = numbers(claim.text)
    for alt in claim.alternatives:
        if alt.heading != claim.source.heading:
            continue
        theirs = numbers(alt.text)
        if mine and theirs and mine != theirs:
            return Verdict(claim, CONTRADICTED,
                           f"{claim.source.cite} says {sorted(mine)}; {alt.cite} says {sorted(theirs)}",
                           [claim.source.cite, alt.cite])
    return Verdict(claim, OK, "supported by a current source", [claim.source.cite])

def run(claims):
    return [judge(c) for c in claims]
