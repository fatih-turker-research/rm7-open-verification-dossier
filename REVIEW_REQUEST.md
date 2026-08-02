# Focused independent verification requested

This is an AI-assisted, unverified verification dossier. It is not a theorem, a research publication, a solution of the generalized Fermat equation of signature `(3,5,7)`, a solution of the Beal conjecture, or a prize submission. The uploader cannot independently defend every derivation.

Reviewers are **not** being asked to approve the package or read all of it. Please choose one question. A short report of the first fatal gap, missing hypothesis, convention mismatch, reproducibility failure, or relevant reference is already valuable.

## Five review routes

### Q1 - External polynomial and invariant convention

Start with [`reports/PHI7_PULLBACK_CERTIFICATE.md`](reports/PHI7_PULLBACK_CERTIFICATE.md) and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

Does the hash-pinned `PolQ5Gundlach-7` archive represent the intended inert level-7 Gundlach modular polynomial in the invariant convention used here, and is there an independent way to regenerate or certify it?

### Q2 - Exceptional fibres and normalization

Start with [`reports/EXCEPTIONAL_FIBERS_AUDIT.md`](reports/EXCEPTIONAL_FIBERS_AUDIT.md).

Do the Newton polygons, residual polynomials, normalization steps, and projective-infinity calculation account for every branch above the exceptional fibres, or is any local contribution to the different missing?

### Q3 - Identification of the 50-sheet cover

Start with [`reports/RM7_COVER_IDENTIFICATION.md`](reports/RM7_COVER_IDENTIFICATION.md) and [`reports/RM7_MODULI_BRIDGE_AUDIT.md`](reports/RM7_MODULI_BRIDGE_AUDIT.md).

Does the proposed function-field argument actually identify the restricted degree-50 equation with the RM-stable-line cover on the Frey family, including all required endomorphism, orientation, and field-of-definition hypotheses?

### Q4 - Interior ramification

Start with [`reports/GENUS8_MONODROMY_AUDIT.md`](reports/GENUS8_MONODROMY_AUDIT.md) and [`reports/PROOF_OBLIGATIONS.md`](reports/PROOF_OBLIGATIONS.md).

Is the assertion that there is no additional interior ramification justified by the cited statements and their hypotheses?

### Q5 - Conditional genus calculation

Start with [`reports/GENUS8_MONODROMY_AUDIT.md`](reports/GENUS8_MONODROMY_AUDIT.md).

Assuming Q1-Q4, do degree `50` and the stated different contributions `40 + 32 + 42 = 114` establish genus `8` for the normalization by Riemann-Hurwitz?

## How to respond

Please open a [verification-feedback issue](https://github.com/ftrspor/rm7-open-verification-dossier/issues/new?template=verification-feedback.md) and include:

1. the question number (`Q1`-`Q5`);
2. the exact file, section, formula, or script involved;
3. the finding and the shortest supporting reason or reproducible command;
4. whether the finding is fatal, requires another hypothesis, or is only a clarification.

An issue is a public comment on this repository. Do not include private correspondence or identify another person without that person's permission.
