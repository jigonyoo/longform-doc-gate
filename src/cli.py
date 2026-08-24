import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import pipeline as P, report as Rep, corpus as C

def main():
    corpus_dir = os.environ.get("CORPUS", "corpus")
    tpl_path = os.environ.get("TEMPLATE", "templates/quarterly_review.yaml")
    region = os.environ.get("REGION", "")
    outdir = os.environ.get("OUT", "out")
    os.makedirs(outdir, exist_ok=True)

    rows = []
    for mode in ("naive", "gated"):
        c, tpl, claims, verdicts = P.build(corpus_dir, tpl_path, region, mode)
        st = Rep.stats(verdicts)
        rows.append((mode, st))
        open(f"{outdir}/{mode}_document.md", "w", encoding="utf-8").write(
            Rep.render_document(tpl, verdicts))
        open(f"{outdir}/{mode}_review_queue.md", "w", encoding="utf-8").write(
            Rep.render_queue(verdicts))

    print(f"corpus fingerprint: {C.fingerprint(corpus_dir)}   region: {region or 'ALL'}\n")
    print(f"{'':<14}{'claims':>8}{'OK':>6}{'SUPERSEDED':>12}{'CONTRADICTED':>14}{'UNSUPPORTED':>13}{'to review':>11}")
    for mode, st in rows:
        c = st["counts"]
        print(f"{mode:<14}{st['claims']:>8}{c.get('OK',0):>6}{c.get('SUPERSEDED',0):>12}"
              f"{c.get('CONTRADICTED',0):>14}{c.get('UNSUPPORTED',0):>13}{st['must_read']:>11}")
    n, g = rows[0][1], rows[1][1]
    sup = n['counts'].get('SUPERSEDED', 0)
    print(f"\nThe naive pass shipped {sup} claims from a retired edition and said nothing.")
    print(f"Because it says nothing, a person has to read all {n['claims']} claims to find them.")
    print(f"The gated pass hands back {g['must_read']}: "
          f"{g['counts'].get('CONTRADICTED',0)} contradicted, "
          f"{g['counts'].get('UNSUPPORTED',0)} unsupported. The other "
          f"{g['counts'].get('OK',0)} carry a current source and do not need reading.")
    print(f"\nwrote {outdir}/naive_document.md, {outdir}/gated_document.md, "
          f"{outdir}/gated_review_queue.md")

if __name__ == "__main__":
    main()
