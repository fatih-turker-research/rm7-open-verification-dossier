# Proof obligations

> Status refreshed on 2 August 2026. The final addendum records the
> controlling RM(7) frontier; earlier dated analysis is retained for audit.

## P0 — full prize scope

Produce either:

1. a complete proof that every positive solution with \(x,y,z>2\) has a common prime divisor; or
2. one exact positive primitive counterexample.

Anything weaker may be publishable but is not sufficient for the Beal Prize.

## P1 — normalize all signatures

Write a journal-grade reduction proving that any primitive counterexample yields one whose exponents each belong to

\[
\{4\}\cup\{p:p\text{ is an odd prime}\}.
\]

Record precisely which permutations and sign changes are legitimate for positive Beal solutions.

## P2 — complete the \((3,5,7)\) signature

The bounded congruence searches do not solve this obligation. A completion needs a global argument, most plausibly one of:

- a complete descent to finitely many curves plus determination of all relevant rational points;
- a modular/Frey construction with a genuinely bounded lowered level;
- a global reciprocity, Selmer, or Brauer--Manin obstruction eliminating both remaining branches;
- an effective height bound followed by a certified exhaustive computation.

### P2A — Branch-I modular work package

For the genus-2 Frey representation of the \((5,7,3)\) reformulation:

1. prove absolute irreducibility at \(p=7\) in the even-middle-variable case;
2. derive conductor exponents \((2,2)\) with every local hypothesis;
3. reproduce the 14 Hilbert newform orbits at level
   \(3^2(\sqrt5)^2\);
4. certify the exact mod-7 eliminations;
5. invariantly identify and eliminate the three residual forms indexed
   \(3,9,12\) in the authors' computation.

The focused Hilbert-form audit shows that these three survivors are CM forms,
not the two ghost forms at the distinct level \((3)^3(\sqrt5)^3\).  The ghost
forms are excluded in Branch I by the cited Theorem 7.18, but the three CM
survivors remain open. The fingerprint certificate now identifies Magma index
3 invariantly with LMFDB suffix `e`. The assignments \(9\mapsto h\) and
\(12\mapsto l\) are uniquely implied by the reported coefficient fields but
remain conditional until a raw Magma transcript binds those fields to the two
indices. None of these identities is a \(p=7\) elimination; see
`HILBERT_CERTIFICATE_ATTEMPT.md`.

The current M2 audit reduces item 1, conditionally on named local inputs, to
one precise Eisenstein exclusion:

\[
\bar\rho^{\mathrm{ss}}\ne\psi\oplus\psi\bar\chi_7,
\]

with \(\psi\) the unique totally even quadratic character of conductor
\((3)(\sqrt5)\).  The place above 2 does not supply the exclusion.  See
`M2_IRREDUCIBILITY_AUDIT.md` for the dependency-separated derivation and four
legitimate next routes.

The characteristic-7 Cartier--Manin calculation does give one new necessary
condition. For smooth reductions \(t=2,3,4,5,6\pmod7\), the 49-Frobenius
unit-root scalars are \(3,2,5,4,1\), whereas the reducible type has
\(\psi((7))=-1\). Subject to the named representation/comparison inputs this
forces \(t\equiv1\pmod7\), hence \(7\mid C\). Together with the exact
auxiliary-prime coverage it conditionally forces
\(260{,}927{,}370{,}690\mid C\), but this is not a contradiction. The global
Eisenstein/RM-\((7)\)-isogeny exclusion remains P2A's decisive open lemma.

The RM route now has an exact preliminary certificate.  In Gundlach
coordinates the Frey image is

\[
5U=9V^2,\qquad V=\frac{375t}{t-1},
\]

and the chosen published chart denominator has no nonzero rational zero on
this line.

The specialization and generic arithmetic-factorization steps are now
complete **for the hash-pinned source polynomial**.  Exact substitution
\(U=9V^2/5\), denominator clearing, removal of the common boundary factor
\(V^{64}\), and primitive normalization give

\[
F(X,V)\in\mathbf Z[X,V],\qquad
(\deg_XF,\deg_VF)=(50,100),
\]

whose canonical `ZXV-DESC-V1` stream has SHA-256
`C8BEB2665A88AC2F8F3172ACE30087ECFA707FCFA45F5363973F9D8CA29C54CC`.
Normal and `-OO` Python executions and an independent Node/BigInt
reconstruction agree.  This proves the exact transformation and normalization
of the pinned files; it does not independently certify that the third-party
coefficients are the intended mathematical \(\Phi_7\).

After making the pullback monic in \(X\), two good primes that split in
\(K=\mathbf Q(\sqrt5)\) give square-free fiber-factor degrees

\[
(25,25)\quad\text{at }(p,V)=(11,4),
\qquad
(1,7,7,7,7,7,7,7)\quad\text{at }(659,77).
\]

The corresponding subset-degree sets intersect only in \(\{0,50\}\).
Consequently the pinned-source monic pullback is irreducible over both
\(\mathbf Q(V)\) and \(K(V)\).  This is arithmetic function-field
irreducibility, conditional on the pinned source; it is not absolute or
geometric irreducibility and says nothing by itself about exceptional fibers
or special \(K\)-points.

The next obligation is not another good-prime trace sieve or a generic
factorization.  It is to normalize the resulting irreducible cover, compute
its genus and ramification/singularity data, resolve every exceptional,
projective, coarse-moduli and descent fiber, and determine all \(K\)-rational
lifts satisfying

\[
V/375=B^5/C^7,\qquad 1-V/375=A^3/C^7.
\]

The external 42 MB modular-polynomial archive is hash-pinned but not
redistributed because no explicit redistribution license was found.  Its
coefficient construction still needs an independent certified-evaluation or
equivalent completeness check for use in a final computer-assisted proof.
Thus C-029 remains OPEN despite C-030 and C-031.

### P2B — degree-7 classical work package

Audit or independently certify the targeted Hunter--Pohst enumeration behind
Putz's Theorem 3.50, then eliminate the six pure septic fields and the one
exceptional degree-7 field listed in `FRONTIER_AND_STRATEGY.md`.  The exact
certificate proving that the Putz and Dahmen--Siksek exceptional polynomials
define the same field closes only a notation/isomorphism sub-obligation; it
does not establish completeness of the enumeration or eliminate that field.

The incomplete full point lists mentioned for two genus-2 curves are not, by
themselves, P2A or P2B.

## P3 — external dependency audit

For every invoked theorem:

- cite the exact statement and version;
- check all hypotheses against the current variables;
- distinguish peer-reviewed results from working papers;
- reproduce indispensable computer calculations where the source does not supply a checkable certificate.

The Dahmen--Siksek branch theorem is currently classified as a working-paper dependency, not as an independently reproduced theorem in this project.

## P4 — computer-assisted proof obligations

For any finite no-solution theorem, supply:

1. a mathematical coverage lemma mapping every target solution to an enumerated candidate;
2. exact arithmetic only;
3. deterministic source code and environment lock;
4. chunked transcripts and cryptographic hashes;
5. positive and adversarial regression cases;
6. an independent implementation using a different language or library;
7. a short verifier that checks certificates without trusting the search program's control flow;
8. archived source, data, commands, timings, and hardware/software metadata.

## P5 — publication and prize procedure

Before any prize notification:

- the full solution must appear in a respected refereed mathematics publication;
- the mathematical community must have adequate time and access to scrutinize it;
- all AMS Beal Prize procedures then in force must be followed;
- no unpublished manuscript should be sent to AMS, the prize committee, or Mr. Beal as a prize claim.

## P2A controlling update — 2 August 2026

The following former sub-obligations are now closed relative to the pinned
modular-polynomial source:

- normalization at \(V=0\), \(V=375\), \(V=\infty\), and the denominator
  divisor;
- arithmetic and geometric integrality of the degree-50 pullback;
- exact boundary cycle types and different contributions; and
- identification of the modular cover as genus 8, conditional on the named
  Pacetti--Villagra Torcomian and Milio--Robert theorem inputs, the explicit
  degree-50 function-field bridge, and correctness of the pinned coefficient
  database.

The controlling open obligation C-029 is now:

> Determine every \(K=\mathbf Q(\sqrt5)\)-rational point of the genus-8
> normalization whose base coordinate satisfies the two Branch-I
> perfect-power ratios, and prove which of those points, if any, survives the
> companion invariants, cusp exclusions, RM orientation and Frey descent.

This divides into five referee-sized tasks.

1. **P2A-R1 — companion data.** Reconstruct \(\Psi_7\) from the same pinned
   source, produce an independent implementation, and certify the common
   domains and denominator loci.
2. **P2A-R2 — boundary admissibility.** Evaluate the companion invariants on
   the width-one infinity branch. The first \(\Phi_7\) equation is locally
   soluble at the already forced \(C\)-primes, so only a companion,
   orientation or descent condition can turn that branch into a contradiction.
3. **P2A-R3 — usable genus-8 model.** Construct a projective normal model over
   \(K\), with explicit birational maps to the 4,752-term plane equation
   and certified handling of every exceptional chart.
4. **P2A-R4 — Mordell--Weil information.** Determine the Jacobian decomposition
   if available, obtain a rigorous rank bound, and choose a justified
   Chabauty, quadratic-Chabauty, covering or Mordell--Weil-sieve method.
5. **P2A-R5 — point list and Diophantine pullback.** Prove completeness of the
   resulting \(K\)-point list and impose
   \(V/375=B^5/C^7\) and \(1-V/375=A^3/C^7\), followed by all Frey-specific
   moduli/descent checks.

The cyclic-group calculation in `BRANCH1_LOCAL_POINT_AUDIT.md` proves that
ordinary first-residue perfect-power sieves cannot replace R1--R5. Faltings'
theorem gives finiteness after C-034, but no effective list or height bound.
