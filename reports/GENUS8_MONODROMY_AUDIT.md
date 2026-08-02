# RM(7) pullback: independent ramification and genus audit

Date: 2 August 2026  
Status: **exact boundary and permutation arithmetic; application to the
published modular cover remains DEPENDENT on the named source theorems and
the hash-pinned coefficient database.  This is not a rational-point theorem.**

## 1. Abstract projective-line calculation

Put \(K=\mathbf Q(\sqrt5)\).  Since 7 is inert in \(K\),

\[
\mathcal O_K/7\mathcal O_K\simeq\mathbf F_{49},
\qquad \#\mathbf P^1(\mathbf F_{49})=50.
\]

The two independent standard-library verifiers enumerate all 50 projective
points and check the following permutation types:

\[
5^{10},\qquad 1^2 3^{16},\qquad 1\,7^7.
\]

Their different contributions are \(40,32,42\).  Hence

\[
R=40+32+42=114,
\qquad 2g-2=-2\cdot50+114=14,
\qquad \boxed{g=8}.
\]

One verifier constructs \(\mathbf F_{49}\), projective Mobius actions, cycles,
and the Riemann--Hurwitz sum directly.  The other uses an independent
implementation.  Both run in normal and optimized Python modes.  The
canonical payload hash produced by `verify_rm7_monodromy_genus.py` is

```text
D548DE2CEB8D52FA6C037F23247B3467D4219353A43C66A0B9F22391CCF27870
```

The characteristic-zero hypergeometric monodromy of Pacetti--Villagra
Torcomian is a structural consistency check.  In particular, the matrix at
\(t=1\) is nontrivial unipotent in characteristic zero; it has projective
order 7 only after a nontrivial reduction modulo 7.  This report does not use
an unstated identification of an integral 7-adic lattice to prove that fact
for the pinned cover.  The exact polynomial boundary calculation in Section
3 is the controlling input.

## 2. Identification with the pinned polynomial

The detailed bridge is proved in `RM7_COVER_IDENTIFICATION.md`.  Its essential
steps are:

1. the explicit Frey Jacobian inherits an integral, self-adjoint
   \(\mathcal O_K\)-action, so its 7-torsion lines form a degree-50 finite
   etale cover over the smooth locus;
2. Milio--Robert Proposition 4.3, the symmetric case of Theorem 4.15, and
   Proposition B.5 identify the discriminant-5 inert Gundlach polynomial with
   the product over those 50 line kernels; and
3. after restriction to the Frey line, absolute irreducibility of the pinned
   degree-50 polynomial gives a 50-dimensional field that injects into the
   50-dimensional line algebra, so the two function fields are equal.

The last dimension argument is needed: a generic primitive invariant on the
Hilbert surface need not remain primitive on an arbitrary curve merely by
specialization.

Scalar Tate or quadratic twists disappear projectively.  In the inert
symmetric case \(\beta=\bar\beta=7\), there is no factor-of-two quotient; the
degree remains 50.  Extra automorphisms or target-invariant collisions may
singularize the plane equation, but the equal-function-field argument shows
that they do not alter its normalization.

This identification uses the following named dependencies:

- Pacetti--Villagra Torcomian, Sections 2.2 and 7.1, for the genus-two
  realization, inherited \(\mathcal O_K\)-action, and generic endomorphism
  algebra;
- Milio--Robert, Propositions 4.3, 4.11, and B.5 and Theorem 4.15, for the
  inert symmetric Hilbert correspondence and Gundlach polynomial;
- the project's exact Frey-to-Gundlach map; and
- correctness of the hash-pinned third-party coefficient database.

The first two are cited mathematical inputs.  The coordinate transformation,
absolute irreducibility, and boundary calculations are locally certified.  The
database interpolation itself has not been independently regenerated.  This
is why C-034 remains labelled **DEPENDENT**.

## 3. Exact ramification of the pinned cover

The source-linked exceptional-fibre audit reconstructs all 4,752 terms and
computes normalization data directly from the pinned polynomial:

\[
\begin{array}{c|c|c}
V&\text{normalized cycle type}&\text{different}\\
\hline
0&5^{10}&40\\
Q_{36}(V)=0&1^{50}&0\\
375&1^2 3^{16}&32\\
\infty&1\,7^7&42.
\end{array}
\]

The identified 7-torsion line scheme is finite etale away from
\(t=0,1,\infty\), so these boundary contributions are the complete
characteristic-zero ramification divisor.  Riemann--Hurwitz therefore gives
genus 8.

The width-one infinity edge also gives a \(\mathbf Q\)-rational unramified
place.  Combined with \(\mathbf Q(V)\)-irreducibility, this proves that the
normalization is geometrically integral.

## 4. Reduction-modulo-1009 consistency audit

The following is **finite-field consistency evidence, not a
characteristic-zero lifting proof**.

Reconstructing the pinned polynomial modulo 1009 gives:

- an irreducible bidegree-\((50,100)\) plane polynomial;
- toric arithmetic genus 4522;
- 4,501 ordinary nodes on the large squared-discriminant locus;
- local delta invariant 13 at \(V=375\); and
- the same boundary different \(40+32+42\).

Hence its normalized reduction has

\[
4522-4501-13=8.
\]

The ordinary-node statement is checked inside the finite reduced algebra over
the square-free degree-4501 factor: the common \(X\)-root is unique,
\(F=F_X=F_V=0\), and the Hessian determinant and \(F_{XX}\) are units.  This
explains the squared discriminant geometrically.  It does not, without a
simultaneous-normalization argument, prove persistence of all nodes in
characteristic zero.

Observed dense-coefficient hashes modulo 1009 are:

```text
V:       83B97B859AA5F81B2F0F86BA2A675EFAF515AD2D5E2B8652CF2DE7E1C2267350
H_4501: F0D0080E9740A2BCBA1F3B449AA28CE73450D8EE03FF37A1C6E20639516EE614
V-375:  C7BAA4BAF79B812D74FCC761D45617139963BEE6776404195D7C4D8BED8E44F7
```

The former candidates 4522 and 4509 are invalid as genera of the normalized
characteristic-zero cover.

## 5. Reproduction

Self-contained release checks:

```text
python -B computation/verify_rm7_monodromy_genus.py
python -OO -B computation/verify_rm7_monodromy_genus.py
python -B computation/verify_genus8_monodromy.py
python -OO -B computation/verify_genus8_monodromy.py
```

The source-linked and offline exceptional-fibre checks are:

```text
python -B computation/verify_exceptional_fibers.py --database PATH/PolQ5Gundlach-7
python -B computation/verify_exceptional_fibers_offline.py
python -OO -B computation/verify_exceptional_fibers_offline.py
```

The finite-field node probes remain in the research workspace because they
are consistency experiments, not the controlling certificate.

## 6. Consequence

Genus \(8>1\) gives finiteness of \(Y(K)\) by Faltings, but not an effective
list.  The next arithmetic target is a usable projective model, the companion
\(\Psi_7\), a rigorous Mordell--Weil rank bound, and a complete \(K\)-point
calculation satisfying

\[
\frac{V}{375}=\frac{B^5}{C^7},
\qquad
1-\frac{V}{375}=\frac{A^3}{C^7}.
\]

No Branch-I contradiction or Beal proof follows from the genus calculation
alone.
