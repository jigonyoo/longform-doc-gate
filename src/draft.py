"""Drafting is deliberately pluggable. The shipped drafter is extractive and offline
so the whole pipeline is reproducible without an API key. Swap in a model-backed
drafter and the gates in verify.py are unchanged - that is the point of the repo."""
import re
from dataclasses import dataclass

@dataclass
class Claim:
    section_id: str
    text: str
    source: object | None      # Section or None
    alternatives: list         # other admissible sections that also answered

def sentences(text: str):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]

class ExtractiveDrafter:
    """Lifts sentences verbatim from the retrieved section. No paraphrase, so every
    claim is traceable to one sentence in one document."""
    name = "extractive-offline"

    def draft(self, section_spec, sources):
        if not sources:
            return [Claim(section_spec["id"], "", None, [])]
        primary = sources[0] if isinstance(sources, list) else sources
        rest = sources[1:] if isinstance(sources, list) else []
        return [Claim(section_spec["id"], s, primary, rest) for s in sentences(primary.text)]
