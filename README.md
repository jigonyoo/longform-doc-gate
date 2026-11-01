# longform-doc-gate

[![CI](https://github.com/jigonyoo/longform-doc-gate/actions/workflows/ci.yml/badge.svg)](https://github.com/jigonyoo/longform-doc-gate/actions/workflows/ci.yml)

Long-form document generation where the number that matters is **how much of it a person still has to read**.

Point it at a corpus and a section outline. It drafts the document, attaches a source to every
claim, and hands back a short list of the claims a human actually has to look at. Runs offline,
Python standard library only, no API key.

```
make demo    # builds the document twice - once without the gate, once with it
make test    # 12 tests
```

## The measured run

Corpus fingerprint `5015e21b19ba`. Six sections requested, nine claims produced.

|         | claims | OK | SUPERSEDED | CONTRADICTED | UNSUPPORTED | to review |
|---------|-------:|---:|-----------:|-------------:|------------:|----------:|
| naive   |      9 |  5 |      **4** |            0 |           0 |         4 |
| gated   |      9 |  7 |      **0** |        **1** |       **1** |     **2** |

The naive pass shipped **4 claims from a retired edition and said nothing about it**. Because it
says nothing, a person has to read all 9 claims to find them. The gated pass hands back **2**.

## The three failures it is built around

**1. The retired edition is the longer one.** `METH-V1` was replaced in 2026, but it carries four
years of appended FAQs and amendments, so it is 939 characters against the current edition's 518.
Rank by raw overlap and the retired edition wins. The document then states a four-week discovery
and a single reviewer — the 2022 policy — in a deliverable dated 2026, fluently and with no warning.
A test asserts the retired edition is still the longer one, because if that stops being true the
rest of the suite proves nothing.

**2. Two current sources disagree.** The US handbook says unused days carry over 90 days; the EU
handbook says 60. Both are current, so a version gate does not help. The gate returns `CONTRADICTED`
with both citations rather than picking the higher-scoring one. Naming a region resolves it properly;
a test covers both paths.

**3. The corpus cannot answer.** The outline asks for a rate card and no document contains one.
Similarity alone still returns something — the naive pass fills the section with a sentence about
escalation that happens to contain the word "day". The gate leaves the section open and marks it
`GAP`, because an invented sentence and a correct one look identical on the page.

That third case is why the admissibility test is coverage, not similarity. A section must contain
at least half the question's content terms to be admissible. A similarity threshold is not a
refusal gate.

## Where the model goes

Drafting is a plugged-in interface. The shipped `ExtractiveDrafter` lifts sentences verbatim, which
is why this repo runs with no API key and gives the same answer every time. **Swap in a
model-backed drafter and nothing in `verify.py` changes** — the gates operate on claims and sources,
not on how the prose was produced. That separation is the actual subject of this repo. The drafting
half is not where these projects fail.

## Honest limits

- The corpus is synthetic and small. Real knowledge bases are messier and the numbers above would
  have to be re-measured on yours.
- Contradiction detection compares numbers appearing under the same heading. It will not catch two
  sources that disagree in prose without disagreeing in digits.
- Retrieval is token overlap with a crude stemmer, not embeddings. That is enough to demonstrate the
  gates and is not a claim about retrieval quality.
- The extractive drafter cannot summarise or synthesise. It moves sentences.
- `UNSUPPORTED` means *this corpus* cannot answer. It is not a claim that no answer exists.

## Layout

```
corpus/       four documents, two of them a deliberate trap
templates/    the section outline, and the question each section must answer
src/          corpus, retrieve, draft, verify, report, cli
tests/        12 tests - three assert the trap is still a trap
out/          generated documents and the review queue
```
