# RM(7) Open Verification Dossier

> **Status: AI-assisted, unverified, not peer reviewed, and not a research publication.**
>
> No human mathematical authorship is claimed. The repository uploader has stated that they cannot independently defend all mathematical derivations. The material must not be cited as establishing a theorem, solving the generalized Fermat equation of signature `(3,5,7)`, solving the Beal conjecture, or qualifying for the Beal Prize.

## Purpose

This repository exposes a narrow computational candidate for public checking. It records scripts, certificates, audit notes, and a five-page verification dossier concerning a degree-50 pullback of an inert level-7 Hilbert modular correspondence to a genus-two Frey family.

The package is designed to make errors easier to find. It is not intended to turn unverified AI-generated reasoning into verified human research.

The main document is [`RM7_OPEN_VERIFICATION_DOSSIER.pdf`](RM7_OPEN_VERIFICATION_DOSSIER.pdf).

## Candidate reported by the package

Subject to the stated dependencies, the files report:

- a canonical primitive pullback of bidegree `(50,100)` with 4,752 nonzero terms;
- two-fibre arithmetic irreducibility witnesses;
- normalized boundary cycle types `5^10`, `1^2 3^16`, and `1 7^7`;
- total different `40 + 32 + 42 = 114`;
- a proposed geometric-integrality argument;
- a dependent candidate identification with a 50-sheet RM-stable line cover;
- the candidate Riemann-Hurwitz value `g = 8`.

## What is not established

- The third-party modular-polynomial interpolation has not been independently regenerated.
- No subject-matter expert has validated the mathematical derivations.
- Implementation diversity was produced inside the same AI-assisted workflow and is not independent human replication.
- The complete `K = Q(sqrt(5))` rational-point set is unknown.
- Companion invariants, orientation, descent, and the remaining Diophantine bridge are open.
- Neither the `(3,5,7)` equation nor the Beal conjecture is solved.

## AI-use and responsibility disclosure

OpenAI Codex was used substantively from 24 July through 2 August 2026 for research-direction selection, literature synthesis, derivation, code generation, execution planning, checking, and drafting. GitHub user `ftrspor` directed and authorized the public release and accepts responsibility for posting the artifact, but has expressly stated that they cannot independently provide an expert defence of all derivations.

That limitation is the reason this package is published only as an open verification request. It has not been submitted to a journal, arXiv, Zenodo, the AMS, or the Beal Prize Committee.

See [`STATUS_AND_AI_DISCLOSURE.md`](STATUS_AND_AI_DISCLOSURE.md) for the complete status statement.

## Verify the package

Python 3.11 or newer is recommended. The offline checks use only the Python standard library.

```text
python -B verify_package.py
python -OO -B verify_package.py
```

The package verifier checks every file against `SHA256SUMS.txt`, rejects missing or unlisted files, and runs the four bundled offline certificate checks.

To rebuild the PDF layout, install ReportLab and run:

```text
python -B source/build_rm7_verification_dossier.py
```

The rebuilt file is written under `rebuild/` and is not part of the signed package inventory.

Some source-linked checks require the external `PolQ5Gundlach-7` archive. It is deliberately not redistributed here. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for the exact URL, byte count, and SHA-256 value.

## Independent review requested

Qualified reviewers are asked to focus on five questions:

1. Does the pinned external archive represent the intended inert level-7 Hilbert modular polynomial, and can its interpolation be regenerated independently?
2. Are the Newton-polygon, residual-polynomial, normalization, and projective-infinity calculations complete at every exceptional fibre?
3. Is the proposed function-field bridge to the 50-sheet RM-stable line cover valid after restriction to the Frey line?
4. Is the assertion of no additional interior ramification justified by the cited results and hypotheses?
5. If those points hold, does Riemann-Hurwitz establish genus 8 for the normalization?

## Layout

- `reports/`: claim ledger, proof obligations, dependency analyses, and audit notes.
- `computation/`: exact certificates and Python/Node verification programs.
- `source/`: source used to generate the PDF dossier.
- `SHA256SUMS.txt`: package-level file manifest.

## Licences

- Original code in this package is offered under the MIT License; see `LICENSE-CODE`.
- Original prose and package documentation are offered under CC BY 4.0 to the extent the uploader owns the relevant rights; see `LICENSE-TEXT.md`.
- External papers, databases, names, and cited material remain subject to their own rights. The unlicensed third-party coefficient archive is not included.
