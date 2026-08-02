# Exceptional and projective fibres of the level-7 Frey pullback

Date: 2026-08-02  
Status: **exact source-linked local analysis and geometric-integrality upgrade;
genus $8$ remains dependent on a stated moduli/étaleness bridge.  This is not
a Branch-I elimination or a Beal-conjecture proof.**

## 1. Scope and source lock

Let $F(X,V)\in\mathbf Z[X,V]$ be the canonical primitive polynomial obtained
from Milio's first discriminant-5 level-$7$ Gundlach equation after the
substitution

\[
 U=\frac95V^2,
\]

clearing $D(U,V)^2U^4$, removing the common boundary factor $V^{64}$, and
removing scalar content.  This audit reconstructs $F$ from all 51 exact
source files.  It verifies the already pinned hashes

```text
source-member manifest  CB9F8AA7B7F33DD34895A201C4261B6636B69F20C8EAFAA393905072E5ECBE38
canonical F             C8BEB2665A88AC2F8F3172ACE30087ECFA707FCFA45F5363973F9D8CA29C54CC
```

The optional archive-linked run also verifies the external archive digest and
matches every extracted member.  Thus the conclusions below are exact
conclusions about that pinned polynomial.  They retain the project's separate
dependency on the mathematical correctness of the published coefficient
database.

Write

\[
 F(X,V)=\sum_{i=0}^{50}a_i(V)X^i.
\]

All valuations and residual polynomials below are reconstructed directly from
the $4{,}752$ integer terms of $F$.

## 2. Result at a glance

| base value | affine/projective special fibre | points on normalization over \(\overline{\mathbf Q}\) | ramification indices | different |
|---|---|---:|---|---:|
| $V=0$ | $H_{10}(X)^5$ | 10 | $5^{10}$ | 40 |
| $Q_{36}(V)=0$ | 49 simple finite points and one point at $X=\infty$ | 50 per base root | $1^{50}$ | 0 |
| $V=375$ | degrees/multiplicities $1^2,4^6,8^3$ | 18 | $1^2 3^{16}$ | 32 |
| $V=\infty$ | all sheets meet the naive $(\infty,\infty)$ boundary | 8 | $1\,7^7$ | 42 |

The three values corresponding under

\[
 V=\frac{375t}{t-1}
\]

to $t=0,\infty,1$ therefore contribute $40+32+42=114$.  The cycle types
agree exactly with the expected hypergeometric projective-line action.  This
agreement is not used to manufacture the local calculations; it is an
independent structural check.

## 3. The fibre $V=0$

### 3.1 Exact factor and irreducibility

Primitive normalization gives the identity

\[
 \operatorname{prim}_X F(X,0)=H_{10}(X)^5,
\]

where $H_{10}\in\mathbf Z[X]$ is primitive of degree $10$.  The verifier
derives $H_{10}$ as the unique positive-leading exact polynomial fifth root;
it does not ask a factorization library to assert the identity.  Its complete
coefficient vector is in the JSON certificate and has SHA-256

```text
7E0BD03F106D5A46E09DB3ECBF573FD118699FE35E92F063B53DDEF43D67BE70
```

Two complete good reductions give factor degrees

\[
 \begin{array}{c|c|c}
 p&\text{irreducible degrees}&\text{subset degrees}\\ \hline
 11&5,5&\{0,5,10\}\\
 13&2,4,4&\{0,2,4,6,8,10\}.
 \end{array}
\]

The verifier multiplies the displayed finite-field factors, checks every
factor by Rabin's criterion, and obtains subset intersection
$\{0,10\}$.  Gauss's lemma proves that $H_{10}$ is irreducible over
$\mathbf Q$.

### 3.2 Local Newton polygon

Let $\alpha$ be the image of $X$ in
$E=\mathbf Q[X]/(H_{10})$, put $X=\alpha+Z$, and expand

\[
 F(\alpha+Z,V)=\sum_j b_j(V)Z^j
 \quad\text{in }E[V][Z].
\]

Exact polynomial remainders modulo $H_{10}$ give

\[
 \bigl(\operatorname{ord}_V b_0,\ldots,
       \operatorname{ord}_V b_5\bigr)=(1,1,1,1,1,0).
\]

The local edge is consequently

\[
 (0,1)\longrightarrow(5,0),
\]

of primitive slope $-1/5$.  Its endpoint coefficients are nonzero in the
field $E$.  Equivalently, the local degree-five Weierstrass polynomial is
Eisenstein at $V$.  Therefore the degree-ten closed point of the special
fibre lifts to one closed point with the same residue field and ramification
index $5$.  Geometrically there are ten points, each with $e=5$.

Moreover, the coefficient of $VZ^0$ is nonzero.  Hence
$\partial F/\partial V\ne0$ at every one of these geometric points: the
total affine curve is regular there even though its fibre is nonreduced.  The
tame different contribution is

\[
 10(5-1)=40.
\]

Thus saturation by $V^{64}$ removes a vertical clearing-denominator
component, not any horizontal branch of the normalized cover.

## 4. The denominator divisor $Q_{36}(V)=0$

The exact denominator identity is

\[
 D\!\left(\frac95V^2,V\right)=cV^{28}Q_{36}(V),
\qquad c\in\mathbf Q^\times,
\]

with the previously certified irreducible polynomial $Q_{36}$.  In the
$Q_{36}$-adic valuation, the coefficient vector of $F$ satisfies

\[
 v_Q(a_i)=0\quad(0\le i\le49),
 \qquad v_Q(a_{50})=2.
\]

The Newton polygon is

\[
 (0,0)\longrightarrow(49,0)\longrightarrow(50,2).
\]

It accounts for 49 finite roots of valuation zero and one root with
$v_Q(X)=-2$.

The finite degree-49 residual polynomial is proved square-free as follows.
Modulo $23$, $Q_{36}$ is the product of three certified irreducibles of
degrees $7,13,16$.  In each field

\[
 \mathbf F_{23}[V]/(q_d(V)),
\]

the verifier reduces all 51 coefficient blocks, confirms that the fibre has
degree $49$, and computes

\[
 \gcd(F,\partial_XF)=1.
\]

A characteristic-zero common factor over
$\mathbf Q[V]/(Q_{36})$ would survive in every good component, so this is a
valid nonvanishing resultant witness.  The 49 finite geometric points are
therefore simple and unramified.

For the remaining point use $Y=1/X$.  The homogenized local equation begins

\[
 a_{50}(V)+a_{49}(V)Y+\cdots,
\]

where $a_{50}$ has $Q_{36}$-order two and $a_{49}$ is a unit.  The
$Y$-derivative is a unit, so there is one smooth unramified branch with
$Y\asymp Q_{36}^2$, or $X\asymp Q_{36}^{-2}$.  Thus all 50 sheets are
present after projectivizing $X$, and this divisor contributes no different.

The original monic rational-function chart is undefined here.  The argument
proves a statement about the projective closure of the pinned equation; a
companion chart is still required before interpreting every boundary limit as
a Hilbert-moduli point.  For Branch I this does not create a missing parameter:
irreducibility of $Q_{36}$ over $\mathbf Q$ excludes rational, and indeed
quadratic, roots.

## 5. The fibre $V=\infty$

Put $w=1/V$.  After multiplying by $w^{100}$, the exact coefficient
orders are

\[
 v_w(a_i)=\left\lceil\frac{2i}{7}\right\rceil
 \quad(0\le i\le49),
 \qquad v_w(a_{50})=28.
\]

The lower Newton polygon has vertices

\[
 (0,0),\qquad(49,14),\qquad(50,28).
\]

### 5.1 The length-49 edge

The first edge has slope $2/7$.  Its nonzero terms occur at
$i=0,7,\ldots,49$.  The primitive residual polynomial in $T=Z^7$ is

\[
\begin{aligned}
R_7(T)={}&4613203125T^7-382423904078125T^6\\
&+89357517005559862500T^5+67470825277566545625T^4\\
&+24511659357427995375T^3-129503283614995500T^2\\
&+419686804426365T-282429536481.
\end{aligned}
\]

Its coefficient-vector hash is

```text
0C936006C02D53265181722FCC43648CA8ED02EB52F1988472EFE0A2CB1A99DD
```

Rabin's criterion proves its reduction modulo $13$ irreducible.  It is thus
irreducible and separable over $\mathbf Q$.  Newton's theorem gives one
closed point of residue degree $7$ and ramification index $7$, or seven
geometric points with $e=7$.

### 5.2 The length-one edge and a rational place

The second edge has slope $14$ and length one.  With
$Z=w^{14}X$, its nonzero simple residual root is

\[
 Z_0=-\frac{\operatorname{lc}_V(a_{49})}
             {\operatorname{lc}_V(a_{50})}
 =\frac{3^{26}}{5^7\,281^2}
 =\frac{2541865828329}{6168828125}.
\]

Hensel's lemma produces a unique $\mathbf Q[[w]]$-branch with this residue.
It is a $\mathbf Q$-rational, unramified point of the normalization over
$V=\infty$, on which $X$ has pole order $14$.

The complete infinity cycle type is therefore $1\,7^7$, and the different
contribution is

\[
 7(7-1)=42.
\]

### 5.3 Geometric-integrality lemma

Let $L/\mathbf Q(V)$ be the degree-50 function field defined by the already
proved irreducible pullback polynomial.  Let $k_0$ be the algebraic closure
of $\mathbf Q$ inside $L$.  Every nonzero element of $k_0$ has valuation
zero at the rational infinity place just constructed, so reduction embeds
$k_0$ into its residue field $\mathbf Q$.  Hence $k_0=\mathbf Q$.

Because characteristic is zero, $L/\mathbf Q$ is regular.  It follows that
the normalized pullback curve is geometrically integral and, equivalently,
the generic polynomial remains irreducible over
$\overline{\mathbf Q}(V)$.  This removes the earlier
"not geometrically irreducible" caveat, subject to the same pinned-source
dependency as the original $\mathbf Q(V)$-irreducibility proof.

## 6. The additional boundary value $V=375$

Although $V=375$ is not a zero of the published denominator, it is the image
of $t=\infty$ and is essential for interpreting a genus calculation.  Exact
specialization gives

\[
 \operatorname{prim}_X F(X,375)
 =(X-253125)^2H_4(X)^6H_8(X)^3,
\]

with $H_4,H_8$ irreducible; the verifier checks the complete integer product
and Rabin irreducibility modulo $19$.

For $q=V-375$, translation at a root of each factor gives:

| residue-factor degree | fibre multiplicity | orders of translated coefficients $Z^0,\ldots,Z^m$ | lower edge | branches per geometric root |
|---:|---:|---|---|---|
| 1 | 2 | $2,1,0$ | slope $-1$, length 2 | two $e=1$ |
| 4 | 6 | $2,2,2,1,1,1,0$ | slope $-1/3$, length 6 | two $e=3$ |
| 8 | 3 | $1,1,1,0$ | slope $-1/3$, length 3 | one $e=3$ |

For the first two rows, the exact residual quadratic has nonzero discriminant
in the corresponding number field.  The last row has a nonzero binomial
residual.  Thus the cycle type is

\[
 1^2 3^{16}
\]

and the normalized different is

\[
 2\cdot0+4\bigl(2(3-1)\bigr)+8(3-1)=32.
\]

The discriminant of the nonnormal power-basis order has local order $58$:
the three support types contribute $2$, $4\cdot10$, and $8\cdot2$.
Consequently

\[
 58-32=26=2\cdot13
\]

is an index correction.  This explicitly demonstrates why the raw plane-model
discriminant cannot be inserted directly into Riemann--Hurwitz.

## 7. Genus ledger: exact conclusion and dependency

The three boundary cycle types determined directly from $F$ are

\[
 V=0:5^{10},\qquad
 V=375:1^2 3^{16},\qquad
 V=\infty:1\,7^7.
\]

Their total different is

\[
 R_{\rm boundary}=40+32+42=114.
\]

The dependency-separated bridge in `RM7_COVER_IDENTIFICATION.md` identifies
the normalization with the projectivized $J[7]$-line cover, relative to its
named source inputs, and proves that this cover is étale away from
$t=0,1,\infty$.  Thus these are all branch values.  Riemann--Hurwitz for its
geometrically connected degree-50 cover gives

\[
 2g-2=-2\cdot50+114=14,
 \qquad\boxed{g=8}.
\]

This report alone does **not** promote $g=8$ to an unconditional theorem.
The cover bridge requires integral self-adjoint RM, the exact symmetric
Gundlach/database identification, and the specialized degree-50
function-field argument.  Those steps are now written separately, but depend
on named source theorems and on the mathematical correctness of the pinned
database.  Orientation, descent, cusp status, and the companion invariant are
later requirements for C-029, not for the genus.
A separate modular computation indicates that the large squared-discriminant
locus consists of ordinary nodes of the plane model, which is exactly
compatible with genus $8$; lifting that node certificate to characteristic
zero is an alternative route, but it is not part of this certificate.

In particular, the raw polynomial-discriminant estimate $g=4522$ is invalid,
and a partial correction leading to $g=4509$ is also not the controlling
candidate: both count plane-model index singularities as ramification.

## 8. Relevance to Branch I

For the Frey parameter,

\[
 t=-\frac{B^5}{A^3},
 \qquad V=\frac{375t}{t-1}.
\]

- $V=0$ corresponds to $t=0$, hence $B=0$;
- $V=\infty$ corresponds to $t=1$, hence $C=0$;
- $V=375$ corresponds to $t=\infty$, impossible when $A\ne0$; and
- $Q_{36}(V)=0$ has no rational or quadratic parameter.

Thus none of the audited exceptional base values is a missing nonzero Branch-I
solution.  This does not determine the rational points at ordinary finite
values of $V$.

## 9. Reproduction

Files:

- `computation/verify_exceptional_fibers.py` — exact source-linked verifier;
- `computation/verify_exceptional_fibers_offline.py` — dependency-free compact verifier;
- `computation/exceptional_fibers_certificate.json` — compact coefficient, valuation,
  residual, and Newton data.

Their release SHA-256 values are recorded in `ARTIFACT_HASHES.sha256`.

Normal and optimized checks:

```text
python -B computation/verify_exceptional_fibers.py --database PATH/PolQ5Gundlach-7
python -OO -B computation/verify_exceptional_fibers.py --database PATH/PolQ5Gundlach-7
python -B computation/verify_exceptional_fibers_offline.py
python -OO -B computation/verify_exceptional_fibers_offline.py
```

Optional exact linkage to the pinned external archive:

```text
python -B computation/verify_exceptional_fibers.py --database PATH/PolQ5Gundlach-7 --archive PATH/PolQ5Gundlach-7.tar.gz
```

All listed modes pass.  The archive is referenced and hashed, not redistributed.
