import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pipeline as P, verify as V, retrieve as R, corpus as C

ROOT = os.path.join(os.path.dirname(__file__), "..")
CORPUS = os.path.join(ROOT, "corpus")
TPL = os.path.join(ROOT, "templates", "quarterly_review.yaml")

def run(mode, region=""):
    return P.build(CORPUS, TPL, region, mode)[3]

class TheTrapIsReal(unittest.TestCase):
    """These assert the problem still exists. If the corpus stops being a trap,
    the rest of the suite proves nothing."""

    def test_superseded_edition_is_longer_than_the_current_one(self):
        c = C.load(CORPUS)
        old = sum(len(s.text) for s in c.sections if s.doc_id == "METH-V1")
        new = sum(len(s.text) for s in c.sections if s.doc_id == "METH-V3")
        self.assertGreater(old, new, "the retired edition must be the longer one")

    def test_naive_retrieval_still_prefers_the_retired_edition(self):
        c = C.load(CORPUS)
        hit = R.naive(c, "how long is discovery and how does it end")
        self.assertEqual(hit.doc_id, "METH-V1")
        self.assertEqual(hit.status, "superseded")

    def test_naive_pass_ships_retired_claims_silently(self):
        vs = run("naive")
        self.assertEqual(sum(1 for v in vs if v.verdict == V.SUPERSEDED), 4)

class TheGateHolds(unittest.TestCase):

    def test_gated_pass_ships_nothing_from_a_retired_edition(self):
        vs = run("gated")
        self.assertEqual(sum(1 for v in vs if v.verdict == V.SUPERSEDED), 0)

    def test_gated_pass_uses_the_current_numbers(self):
        vs = run("gated")
        text = " ".join(v.claim.text for v in vs)
        self.assertIn("two-week", text)
        self.assertNotIn("four-week", text)

    def test_contradiction_between_regions_is_flagged_not_resolved(self):
        vs = run("gated", region="")
        con = [v for v in vs if v.verdict == V.CONTRADICTED]
        self.assertEqual(len(con), 1)
        self.assertIn("60", con[0].why)
        self.assertIn("90", con[0].why)

    def test_naming_a_region_removes_the_contradiction(self):
        vs = run("gated", region="US")
        self.assertEqual(sum(1 for v in vs if v.verdict == V.CONTRADICTED), 0)
        self.assertIn("90 days", " ".join(v.claim.text for v in vs))

    def test_a_question_the_corpus_cannot_answer_is_left_open(self):
        vs = run("gated")
        uns = [v for v in vs if v.verdict == V.UNSUPPORTED]
        self.assertEqual(len(uns), 1)
        self.assertEqual(uns[0].claim.section_id, "pricing")

    def test_similarity_alone_would_have_answered_the_pricing_question(self):
        """The naive path fills the gap with an unrelated sentence. This is the
        reason the coverage floor exists, not a hypothetical."""
        vs = run("naive")
        pricing = [v for v in vs if v.claim.section_id == "pricing"]
        self.assertEqual(len(pricing), 1)
        self.assertIsNotNone(pricing[0].claim.source)
        self.assertEqual(pricing[0].verdict, V.OK)

class TheGateDoesNotOverreach(unittest.TestCase):

    def test_supported_claims_are_not_flagged(self):
        vs = run("gated")
        ok = [v for v in vs if v.verdict == V.OK]
        self.assertGreaterEqual(len(ok), 6)

    def test_every_shipped_claim_carries_a_citation(self):
        vs = run("gated")
        for v in vs:
            if v.verdict == V.OK:
                self.assertTrue(v.evidence, f"claim without evidence: {v.claim.text}")

    def test_coverage_floor_rejects_an_unrelated_section(self):
        c = C.load(CORPUS)
        esc = [s for s in c.sections if s.doc_id == "METH-V3" and s.heading == "Escalation"][0]
        cov = R.coverage("what is the published day rate for a senior consultant", esc)
        self.assertLess(cov, R.MIN_COVERAGE)

if __name__ == "__main__":
    unittest.main()
