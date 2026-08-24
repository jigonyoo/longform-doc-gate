"""Load a corpus of markdown documents with front matter, split into sections."""
import os, re, hashlib
from dataclasses import dataclass, field

FM = re.compile(r"^---\n(.*?)\n---\n", re.S)

@dataclass(frozen=True)
class Section:
    doc_id: str
    doc_title: str
    status: str          # current | superseded
    edition: int
    region: str          # "" means global
    heading: str
    text: str
    line: int

    @property
    def cite(self) -> str:
        return f"{self.doc_id} §{self.heading}"

@dataclass
class Corpus:
    sections: list = field(default_factory=list)

    @property
    def doc_ids(self):
        return sorted({s.doc_id for s in self.sections})

    def live(self):
        return [s for s in self.sections if s.status == "current"]

    def superseded(self):
        return [s for s in self.sections if s.status == "superseded"]


def _front_matter(raw: str) -> tuple[dict, str]:
    m = FM.match(raw)
    if not m:
        return {}, raw
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, raw[m.end():]


def load(path: str) -> Corpus:
    c = Corpus()
    for name in sorted(os.listdir(path)):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(path, name), encoding="utf-8") as fh:
            raw = fh.read()
        meta, body = _front_matter(raw)
        cur_heading, buf, start = None, [], 0
        def flush(h, b, ln):
            if h and b:
                txt = "\n".join(b).strip()
                if txt:
                    c.sections.append(Section(
                        doc_id=meta.get("doc_id", name),
                        doc_title=meta.get("title", name),
                        status=meta.get("status", "current"),
                        edition=int(meta.get("edition", 1)),
                        region=meta.get("region", ""),
                        heading=h, text=txt, line=ln))
        for i, line in enumerate(body.splitlines(), 1):
            if line.startswith("## "):
                flush(cur_heading, buf, start)
                cur_heading, buf, start = line[3:].strip(), [], i
            elif line.startswith("# "):
                continue
            else:
                buf.append(line)
        flush(cur_heading, buf, start)
    return c


def fingerprint(path: str) -> str:
    h = hashlib.sha256()
    for name in sorted(os.listdir(path)):
        if name.endswith(".md"):
            with open(os.path.join(path, name), "rb") as fh:
                h.update(fh.read())
    return h.hexdigest()[:12]
