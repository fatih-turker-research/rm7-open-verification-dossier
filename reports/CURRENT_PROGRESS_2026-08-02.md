# Current strongest result and acceptance boundary

Date: 2 August 2026  
Project status: **incomplete research result; not a proof of the
\((3,5,7)\) equation, not a proof of the Beal conjecture, and not a prize
submission**

## 1. Exact target

For a hypothetical primitive Branch-I solution

\[
A^3+B^5=C^7,\qquad 30\mid C,\qquad 7\nmid AB,
\]

the Frey family over \(K=\mathbf Q(\sqrt5)\) is

\[
C_t:y^2=5x^6-12x^5+10tx^3+t^2,
\qquad t=-\frac{B^5}{A^3}.
\]

Exact invariant calculations put its Jacobian on the Gundlach line

\[
5U_G=9V^2,\qquad V=\frac{375t}{t-1},
\]

and the Branch-I ratios are

\[
\frac V{375}=\frac{B^5}{C^7},
\qquad
1-\frac V{375}=\frac{A^3}{C^7}.
\]

The first inert-level-7 modular equation pulls back to the certified monic
degree-50 polynomial \(P(X,V)\).  Claim C-029 asks whether this cover has a
\(K\)-rational lift compatible with both ratios and with all
companion/orientation/descent conditions.

## 2. Exact polynomial and normalization results

The canonical primitive numerator
\(F(X,V)\in\mathbf Z[X,V]\) has bidegree \((50,100)\), exactly 4,752 nonzero
terms, and SHA-256

```text
C8BEB2665A88AC2F8F3172ACE30087ECFA707FCFA45F5363973F9D8CA29C54CC
```

Two good-fibre factor-degree witnesses prove that \(P\) is irreducible over
both \(\mathbf Q(V)\) and \(K(V)\), relative to the pinned source.

The source-linked exceptional-fibre calculation gives:

| base value | normalized cycle type | different contribution |
|---|---:|---:|
| \(V=0\) | \(5^{10}\) | 40 |
| \(Q_{36}(V)=0\) | \(1^{50}\) | 0 |
| \(V=375\) | \(1^2 3^{16}\) | 32 |
| \(V=\infty\) | \(1\,7^7\) | 42 |

In particular:

- \(F(X,0)\) is a scalar times \(H_{10}(X)^5\), with \(H_{10}\)
  irreducible;
- the degree-36 denominator divisor has 49 simple finite branches and one
  projective unramified branch;
- at \(V=375\), the normalized different is 32, while the power-basis
  discriminant order is 58 and the index correction is 26; and
- at \(V=\infty\), there are seven points of ramification index 7 and one
  \(\mathbf Q\)-rational unramified point.

That rational place forces the constant field of
\(\mathbf Q(V)[X]/(P)\) to be \(\mathbf Q\).  Therefore the normalization is
geometrically integral.  This closes the earlier geometric-component caveat,
relative to the same pinned polynomial.

## 3. Conditional cover-identification theorem

The hostile cover review exposed and then repaired a missing specialization
step.  The controlling argument is now:

1. Pacetti--Villagra Torcomian's construction gives the generic Frey
   Jacobian an integral \(\mathcal O_K\)-action and endomorphism algebra
   \(K\).  Positivity of the Rosati involution makes that action self-adjoint.
2. Since 7 is inert, \(J[7]\simeq\mathbf F_{49}^2\), and its lines form a
   degree-50 finite etale cover over
   \(\mathbf P^1\setminus\{0,1,\infty\}\).
3. Milio--Robert Proposition 4.3, the symmetric case of Theorem 4.15, and
   Proposition B.5 identify the discriminant-5 inert Gundlach polynomial as
   the product over these 50 kernels.  For \(\beta=\bar\beta=7\), no
   factor-of-two quotient occurs.
4. Over \(\overline{\mathbf Q}(t)\), the absolutely irreducible specialized
   polynomial defines a 50-dimensional field.  Evaluation of the target
   Gundlach invariant injects this field into the 50-dimensional line
   algebra; equal dimensions force an isomorphism.

The fourth step is essential: generic primitivity on a surface does not follow
automatically after restriction to a curve.  The equal-degree argument proves
it here.  Scalar Tate or quadratic twists vanish after projectivization.

Thus, under the named source theorems and the mathematical correctness of the
hash-pinned database, the normalized pinned polynomial is the inert
projective-line cover and is finite etale away from the three boundary values.
The exact boundary different therefore gives

\[
2g-2=-2\cdot50+(40+32+42)=14,
\qquad \boxed{g=8}.
\]

This is recorded as **DEPENDENT**, not unconditional: the external theorems
are cited rather than reproved, and the third-party interpolation that created
the 42 MB coefficient database has not been independently regenerated.  The
pullback, absolute irreducibility, boundary normalization, dimension argument,
and Riemann--Hurwitz arithmetic are exposed for independent checking.

The former candidates \(g=4522\) and \(g=4509\) are retracted.  They counted
index singularities of a nonnormal plane equation as cover ramification.

## 4. Consequence and its limit

Since \(g=8>1\), Faltings' theorem implies that the identified cover has only
finitely many \(K\)-rational points.  It does not enumerate them or supply an
effective height bound, so C-029 remains open.

The special base values cannot encode a nontrivial Branch-I solution:

- \(V=0\) means \(B=0\);
- \(V=375\) means \(A=0\);
- \(V=\infty\) means \(C=0\); and
- irreducibility of \(Q_{36}\) excludes rational and quadratic denominator
  roots.

Ordinary finite \(V\) remains a global rational-point problem.

## 5. Local-sieve audit

For every prime \(p\nmid15\), the two unit perfect-power ratios alone cover
every \(V\in\mathbf F_p\setminus\{0,375\}\).  Complete source-linked root
scans at \(p=11,29,31\) give exact necessary restrictions, but no global
exclusion.

More decisively, the width-one infinity edge has leading coefficients

\[
L_{49}=-3^{86}5^7,
\qquad
L_{50}=3^{60}5^{14}281^2.
\]

If \(v_q(V)=-7c<0\) and \(q\nmid3\cdot5\cdot281\), Hensel's lemma gives a
simple \(\mathbf Q_q\)-root of the first modular equation.  Thus the forced
primes

\[
2,7,19,71,79,89,131
\]

do not yield a contradiction through \(\Phi_7\) alone.  Repeating first-root
congruence scans cannot finish the proof.

## 6. Decisive next work package

The next release should proceed in this order:

1. reconstruct and hash-pin \(\Psi_7\) with an independent implementation;
2. evaluate it at the width-one infinity point and test cusp status,
   admissibility, orientation, and Frey descent;
3. construct a computationally usable smooth projective genus-8 model and
   explicit birational maps over \(K\);
4. obtain a rigorous Mordell--Weil rank bound and enumerate \(Y(K)\) by a
   justified Chabauty, covering, or Mordell--Weil-sieve method; and
5. impose both Branch-I perfect-power ratios and all Frey-specific conditions
   on the complete point list.

Until that list and the companion/descent checks are complete, Branch I is
open.  Even a complete \((3,5,7)\) theorem would be a major partial result, not
a proof of the full Beal conjecture.  The AMS prize procedure additionally
requires a complete work, publication in a respected refereed mathematics
venue, and subsequent community scrutiny; acceptance or an award cannot be
guaranteed in advance.
