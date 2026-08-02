# Exact level-7 Gundlach pullback on the Frey line

> Geometric status update (2 August 2026): the arithmetic irreducibility
> proved here is upgraded to geometric integrality in
> `EXCEPTIONAL_FIBERS_AUDIT.md`. The original scope statements below are
> retained to document exactly what this earlier certificate proved alone.

Date: 2026-07-25  
Status: **exact specialization and two-good-fiber generic-irreducibility
certificate; not a rational-point result, Branch-I elimination, or
Beal-conjecture proof**

## Source formula and provenance

The author's
[`README-Gundlach-Q5-Inert`](https://members.loria.fr/EMilio/files/README-Gundlach-Q5-Inert)
gives, for \(\ell=7\),

\[
 \Phi_7(X,U,V)=X^{50}+\sum_{i=1}^{50}
 \frac{N_i(U,V)}{D(U,V)^2U^{e_i}}X^{i-1},
\]

with the 50-entry first row of `Tab` supplying \(e_i\).  The exact source is
Enea Milio's
[`PolQ5Gundlach-7.tar.gz`](https://members.loria.fr/EMilio/files/PolQ5Gundlach-7.tar.gz)
archive.  The computation pinned and
verified the archive's 42,342,973 bytes and SHA-256

```text
9A98249312F46FAF91A6F5D549A2C890EE1713D40A5C4CF9310C4B5819C5C226
```

and compared all 51 used extracted files (`DenQ5Gund7` and 50 `NumPhi`
files) member-by-member with that archive.  Their canonical source-hash
manifest has SHA-256

```text
CB9F8AA7B7F33DD34895A201C4261B6636B69F20C8EAFAA393905072E5ECBE38
```

The third-party archive is not copied here; its page and verification recipe
do not state a redistribution license.

## Exact specialization and saturation

Put

\[
 U=\frac95V^2,
 \quad d(V)=D\!\left(\frac95V^2,V\right),
 \quad n_i(V)=N_i\!\left(\frac95V^2,V\right).
\]

Clearing the maximum \(U\)-denominator gives

\[
 F_0(X,V)=d(V)^2U(V)^4X^{50}
  +\sum_{i=1}^{50}n_i(V)U(V)^{4-e_i}X^{i-1}.
\]

Every one of its 51 coefficient blocks has exact \(V\)-adic order 64.
Thus the boundary saturation is

\[
 F_1(X,V)=V^{-64}F_0(X,V)\in\mathbf Q[X,V].
\]

The already certified denominator identity is

\[
 d(V)=cV^{28}Q_{36}(V),\qquad c\in\mathbf Q^\times.
\]

The \(X^{50}\)-coefficient of \(F_1\) is exactly \(6561/625\) times
\((d(V)/V^{28})^2\).  Modulo 101, the gcd of \(d(V)/V^{28}\) with the
\(X^{49}\)-coefficient is 1, with degree 36 preserved.  Hence no factor
supported on the denominator remains common; in fact the complete
\(\mathbf Q[V]\)-content is 1.  Therefore the only polynomial saturation
removed is \(V^{64}\); the common \(Q_{36}\)-valuation is zero.

The global scalar denominator is \(5^{82}\).  After clearing it, the integer
coefficient content is \(2^{48}3^{64}\).  Dividing by this content and choosing
the positive leading sign produces the canonical primitive polynomial
\(F\in\mathbf Z[X,V]\).

## Canonical result

The canonical representation orders \(X\)-blocks from degree 50 to 0 and,
inside each block, records nonzero \(V\)-terms in descending degree as decimal
integers.  Its exact summary is:

| item | value |
|---|---:|
| bidegree \((\deg_X,\deg_V)\) | \((50,100)\) |
| nonzero terms | 4,752 |
| largest coefficient length | 755 decimal digits |
| common boundary factor removed | \(V^{64}\) |
| common \(Q_{36}\) factor removed | none |
| scalar denominator cleared | \(5^{82}\) |
| integer content removed | \(2^{48}3^{64}\) |

The SHA-256 of the canonical `ZXV-DESC-V1` stream is

```text
C8BEB2665A88AC2F8F3172ACE30087ECFA707FCFA45F5363973F9D8CA29C54CC
```

The compact JSON certificate records a separate hash, degree, order, and term
count for every coefficient block, plus a source hash for every published
numerator file.  It is about 50 KB; the multi-megabyte coefficient stream does
not need to be redistributed.

## Cross-language verification

The Python specializer was run normally and with `-OO`, both with the pinned
archive linkage.  Their complete 48,255-byte JSON certificates are byte-for-byte
identical, with file SHA-256

```text
4B95CD50A0F59E6324896987DABD08C8B6BBCF5617EBE81D94C630F3F37EB5AC
```

An independent Node/BigInt implementation does not use rational-polynomial
arithmetic.  It first parses each source file in \(\mathbf Z[x,y]\), substitutes
by multiplying each source coefficient with an independently determined power
of 5, and only then constructs and normalizes \(F\).  It reproduced exactly:

- canonical hash `C8BEB...C54CC`;
- bidegree \((50,100)\);
- \(V^{64}\) saturation;
- scalar denominator \(5^{82}\);
- integer content \(2^{48}3^{64}\);
- 4,752 nonzero terms; and
- 755-digit maximum coefficient length.

## Generic irreducibility over \(\mathbf Q(V)\) and \(K(V)\)

Let

\[
 K=\mathbf Q(\sqrt5),\qquad
 P(X,V)=\Phi_7\!\left(X,\frac95V^2,V\right)\in\mathbf Q(V)[X].
\]

The source formula makes \(P\) monic of degree \(50\) in \(X\).  Exact
archive-linked reconstruction gives the following two square-free good
fibers:

\[
\begin{array}{c|c|c|c|c}
p&V&U&D&\text{degrees of the irreducible factors in }\mathbf F_p[X]\\ \hline
11&4&9&4&25,25\\
659&77&260&482&1,7,7,7,7,7,7,7.
\end{array}
\]

Every displayed factor is supplied explicitly, its product is checked against
the reconstructed fiber, and its irreducibility is verified by the Rabin
criterion.  The two possible-factor-degree sets are

\[
 S_{11}=\{0,25,50\}
\]

and

\[
 S_{659}=\{0,1,7,8,14,15,21,22,28,29,35,36,42,43,49,50\};
\]

hence \(S_{11}\cap S_{659}=\{0,50\}\).

Here is the specialization argument, including the integrality step needed
for that subset-sum conclusion.  Both \(11\) and \(659\) split in \(K\): one
may take square roots of \(5\) equal to \(4\) modulo \(11\) and \(258\)
modulo \(659\).  For either displayed pair \((p,v)\), choose a prime
\(\mathfrak p\mid p\) of \(K\) and put

\[
 R_{p,v}=(\mathcal O_K[V])_{(\mathfrak p,V-v)}.
\]

This is a normal local domain with fraction field \(K(V)\) and residue field
\(\mathbf F_p\).  Since \(p\ne5\) and the displayed values of \(U\) and \(D\)
are nonzero, every coefficient denominator in the source formula is a unit in
\(R_{p,v}\).  Thus \(P\in R_{p,v}[X]\) is monic of degree \(50\).

Suppose \(P=GH\) in \(K(V)[X]\), with \(G,H\) made monic.  The roots of \(G\)
are integral over \(R_{p,v}\), being roots of the monic polynomial \(P\); the
coefficients of \(G\), as elementary symmetric functions of those roots, are
integral over \(R_{p,v}\).  They also lie in its fraction field.  Normality
therefore gives \(G\in R_{p,v}[X]\), and similarly \(H\in R_{p,v}[X]\).
Reduction preserves their \(X\)-degrees because they are monic.  Consequently
\(\deg_XG\) belongs to both \(S_{11}\) and \(S_{659}\), so it is \(0\) or
\(50\).  This proves

\[
 \boxed{P\text{ is irreducible in }K(V)[X]}
\]

and therefore also in \(\mathbf Q(V)[X]\).  Equivalently, the horizontal
degree-\(50\) pullback is irreducible over \(K\).  The canonical primitive
numerator \(F\) is an associate of \(P\) in \(K(V)[X]\); its nonconstant
leading coefficient causes no degree loss here.  At both witness fibers the
clearing/saturation scalar is a local unit, since \(p\notin\{2,3,5\}\) and
\(V,U,D\ne0\).

This is **not** absolute or geometric irreducibility: no assertion is made
over \(\overline K(V)\).  It also does not say that a specialized polynomial
\(P(X,v)\) has no \(K\)-rational root for every \(v\in K\).  In particular,
generic irreducibility does not settle the rational points of the cover, and
it does not analyze the exceptional fibers \(V=0\), \(D=0\), or
\(V=\infty\).

## Minimal release package proposed

The smallest useful addition to the public project is:

1. `specialize_phi7.py` — exact archive-linked producer/verifier;
2. `phi7_specialization_certificate.json` — compact per-block certificate;
3. `specialize_phi7_independent.mjs` — independent BigInt reconstruction; and
4. `two_fiber_factor_certificate.json` — the two explicit finite-field
   factorizations;
5. `verify_two_fiber_certificate.py` — dependency-free product, Rabin, and
   subset-degree verification, with optional source reconstruction; and
6. this short report.

The 42 MB third-party archive should remain external.  The report gives the
source URL and required digest, and the release verifier treats the
archive-linked reconstruction as an optional external-data check.  Without
that external check the compact two-fiber certificate proves its own finite
field products and irreducibility assertions, but does not independently bind
the listed fibers to the published \(\Phi_7\).  Thus the generic-irreducibility
statement is conditional on the pinned source formula and archive linkage.

## What remains open

The generic polynomial is now proved irreducible over \(\mathbf Q(V)\) and
\(K(V)\), conditional on the pinned source linkage.  What remains open is the
arithmetic of its degree-\(50\) cover: its projective normalization and genus,
the exceptional fibers \(V=0,D=0,\infty\), the companion invariant and descent
conditions, all \(K\)-rational lifts, and the Branch-I perfect-power conditions
on those lifts.  Generic irreducibility alone yields no contradiction.
