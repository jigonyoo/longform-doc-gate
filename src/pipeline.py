import os, sys, yaml_lite as yl
import corpus as C, retrieve as R, draft as D, verify as V

def load_template(path):
    with open(path, encoding="utf-8") as fh:
        return yl.load(fh.read())

def build(corpus_dir, template_path, region="US", mode="gated"):
    c = C.load(corpus_dir)
    tpl = load_template(template_path)
    drafter = D.ExtractiveDrafter()
    claims = []
    for spec in tpl["sections"]:
        if mode == "naive":
            src = R.naive(c, spec["question"], region)
            sources = [src] if src else []
        else:
            sources = R.gated(c, spec["question"], region)
        claims += drafter.draft(spec, sources)
    return c, tpl, claims, V.run(claims)
