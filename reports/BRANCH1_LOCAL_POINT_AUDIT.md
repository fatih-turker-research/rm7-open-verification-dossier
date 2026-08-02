# Branch-I arithmetic on the RM(7) pullback: local sieve and infinity audit

Date: 2026-08-02  
Status: **exact necessary local restrictions and an exact local-solubility
obstruction to the proposed obstruction; not a proof of C-029, Branch I, or
the Beal conjecture**

## 1. Main outcome

Let

\[
 K=\mathbf Q(\sqrt5),\qquad
 P(X,V)=\Phi_7\!\left(X,\frac95V^2,V\right),
\]

and let `F(X,V)` be the pinned canonical primitive numerator already certified
in the project.  Under Branch I,

\[
 r:=\frac{V}{375}=\frac{B^5}{C^7},\qquad
 1-r=\frac{A^3}{C^7}.
\]

This audit establishes three sharply separated facts.

1. On the unit locus modulo any prime `p` not dividing 15, the two displayed
   perfect-power conditions impose **no first-residue restriction at all**:
   every `r` other than 0 and 1 occurs.
2. Conditional on the existing Frey-to-moduli bridge and pinned Milio source,
   complete split-prime scans at `p=11,29,31` give exact necessary congruence
   restrictions for a `K`-rational root of the first modular equation.
3. At `V=infinity`, the exact Newton data contains a width-one steep edge.
   If `v_q(V)=-7c<0` and `q` does not divide `3*5*281`, that edge gives a
   simple root in `Q_q`.  In particular the first modular equation is
   automatically locally soluble at

   \[
   q=2,7,19,71,79,89,131,
   \]

   the non-`3,5` primes currently forced to divide `C` by the conditional
   project certificates.  Thus those forced divisors cannot by themselves
   close C-029 through the first `Phi_7` equation.

The third item is a negative result for one tempting proof strategy, but it is
mathematically useful: the next computation must incorporate the companion
invariant and the actual moduli/descent conditions, not merely add more first-
equation congruence primes.

## 2. Why the Branch-I ratios are residue-surjective

Let `p` not divide 15 and put `G=F_p^*`, a cyclic group of order `n`.  Fix any
`r` in `F_p` other than 0 and 1, choose a generator `g`, and write

\[
 r=g^R,\qquad 1-r=g^S.
\]

We seek `c=g^k` such that `r*c^7` is a fifth power and `(1-r)*c^7`
is a cube.  In a cyclic group these are exactly the congruences

\[
 R+7k\equiv0\pmod{\gcd(5,n)},\qquad
 S+7k\equiv0\pmod{\gcd(3,n)}.
\]

Multiplication by 7 is invertible modulo both moduli, and the two moduli are
coprime.  The Chinese remainder theorem therefore supplies `k` modulo their
product, which divides `n`.  After choosing fifth and third roots, respectively,
we obtain nonzero `a,b,c` satisfying

\[
 b^5/c^7=r,\quad a^3/c^7=1-r,\quad a^3+b^5=c^7.
\]

Multiplication by the nonzero scalar 375 shows that the unit Branch-I image in
the `V`-line is all of

\[
 \mathbf F_p\setminus\{0,375\}.
\]

The verifier independently checks this by exhaustive exact enumeration for
all three certificate primes.  Consequently a useful restriction here can
only come from the modular cover (or from higher `p`-adic precision), not from
the first reduction of the perfect-power ratios themselves.

## 3. Exact split-prime root sieve

At a split prime `p`, choose a prime of `K` above `p`; its residue field is
`F_p`.  If `U(V)D(V)` is a unit, the published formula makes `P` monic with
integral local coefficients.  A root in `K` is therefore integral and reduces
to a root in `F_p`.  Hence a linear factor of the specialized polynomial is a
necessary condition.

The complete scans give the following result on the locus `p` not dividing
`ABC`, equivalently `V` not congruent to 0 or 375.

| `p` | square roots of 5 | `375 mod p` | allowed `V mod p` | excluded `V mod p` |
|---:|---|---:|---|---|
| 11 | 4, 7 | 1 | 2,3,5,6,8,9,10 | 4,7 |
| 29 | 11, 18 | 27 | 1,3,4,5,6,8,10,11,12,14,15,16,21,24,26 | 2,7,9,13,17,18,19,20,22,23,25,28 |
| 31 | 6, 25 | 3 | 1,2,12,13,14,15,19,20,21,22,26,28,30 | 4,5,6,7,8,9,10,11,16,17,18,23,24,25,27,29 |

Thus, conditional on the bridge, a hypothetical Branch-I solution satisfies,
for each row, the exact disjunction

\[
 p\mid ABC\quad\text{or}\quad V\bmod p\text{ belongs to the allowed set}.
\]

On the simultaneous unit locus the three scans retain

\[
 7\cdot15\cdot13=1365
\]

of the `9*27*29=7047` possible nonboundary CRT classes.  This is a genuine
finite sieve, but without a height bound or a Mordell--Weil sieve it is not a
global exclusion.  The cases `p|B`, `p|A`, and `p|C` lead respectively to
`V=0`, `V=375`, and `V=infinity` modulo `p`, and require separate models.

Each stored degree-50 polynomial is checked directly: monicity, derivative
gcd, the gcd with `X^p-X`, and the gcd with `X^(p^2)-X`.  Optional source mode
reconstructs the canonical integer pullback from all 51 pinned source files
and compares every good stored fiber coefficient-by-coefficient.

## 4. Exact infinity Newton edge

Write

\[
 F(X,V)=\sum_{i=0}^{50}a_i(V)X^i,\qquad d_i=\deg_V a_i.
\]

The source-linked canonical reconstruction gives, in order `i=0,...,50`,

```text
100,99,99,99,98,98,98,98,97,97,97,96,96,96,96,95,95,
95,94,94,94,94,93,93,93,92,92,92,92,91,91,91,90,90,
90,90,89,89,89,88,88,88,88,87,87,87,86,86,86,86,72.
```

The lower hull of `(i,-d_i)` has vertices

\[
 (0,-100),\quad(49,-86),\quad(50,-72),
\]

and slopes `2/7` and `14`.  More importantly for an exact Hensel argument,
the maximum of

\[
 7d_i+98i
\]

is 5404 and occurs only at `i=49,50`.  The corresponding leading
coefficients are

\[
 L_{49}=-3^{86}5^7,\qquad
 L_{50}=3^{60}5^{14}281^2.
\]

Let `V=pi^(-7c)*u`, where `c>0` and `u` is a `q`-adic unit, and put
`X=pi^(-98c)*Y`.  Multiplying by `pi^(5404c)` produces an integral polynomial
whose reduction is

\[
 u^{72}Y^{49}\bigl(L_{49}u^{14}+L_{50}Y\bigr).
\]

For `q` not dividing `L_49*L_50`, its nonzero root

\[
 \overline Y=-\frac{L_{49}}{L_{50}}\,\overline u^{14}
 =\frac{3^{26}}{5^7 281^2}\,\overline u^{14}
\]

is simple: the derivative there is
`L_50*u^72*Y^49`, a unit.  Hensel's lemma therefore gives a root

\[
 X\in\mathbf Q_q,\qquad v_q(X)=-98c.
\]

For a primitive Branch-I triple and `q|C` with `q` not dividing 375, both
`A` and `B` are `q`-adic units, so exactly `v_q(V)=-7v_q(C)`.  The displayed
argument applies to all the audited forced primes.  For the resulting rational
`V` the existing irreducible-`Q36` denominator certificate gives `D(V) != 0`;
also `U(V) != 0`.  Thus `F` and the monic rational polynomial `P` are
nonzero scalar associates at that actual parameter, so the Hensel root is not
an artifact of denominator clearing.  It proves local
solubility only for the first algebraic modular equation.  At level 7 or at
bad reduction it does not by itself prove that the root represents the
required noncuspidal, oriented RM isogeny.

## 5. Exact rational descent reformulation

The remaining `K`-root question can be placed entirely over `Q`.  A root
`X` in `K` with rational `V` is either rational, or can be written uniquely

\[
 X=u+w\sqrt5,\qquad u,w\in\mathbf Q,\quad w\ne0.
\]

For the nonrational case its minimal polynomial is

\[
 M(T)=T^2-2uT+(u^2-5w^2).
\]

Reduce `F(T,V)` modulo `M`.  Define

\[
 P_0=0,\ Q_0=1,\qquad P_1=1,\ Q_1=0,
\]

and recursively

\[
 P_{n+1}=2uP_n+Q_n,\qquad
 Q_{n+1}=-(u^2-5w^2)P_n.
\]

Then `T^n` is congruent to `P_n*T+Q_n` modulo `M`, so the two exact remainder
equations are

\[
 R_1(V,u,w)=\sum_i a_i(V)P_i(u,w)=0,\qquad
 R_0(V,u,w)=\sum_i a_i(V)Q_i(u,w)=0.
\]

Therefore the necessary first-equation locus for C-029 is the union of

\[
 F(u,V)=0
\]

for rational roots and

\[
 R_0(V,u,w)=R_1(V,u,w)=0,\quad w\ne0,
\]

for genuinely quadratic roots.  The Branch-I condition is imposed by the
weighted-projective fiber product

\[
 A^3+B^5=C^7,\qquad VC^7=375B^5,\qquad ABC\ne0,
\]

with weights `(35,21,15)` on `(A,B,C)`.  This is an exact finite-cover/descent
reformulation; it is not asserted to make the rational-point calculation
easy.  It also remains only a necessary locus until the companion invariant,
coarse-moduli exceptions, RM orientation, and Frey-specific descent are
checked.

## 6. Next decisive lemma

The most efficient next target is a **companion-and-boundary lemma**:

> Reconstruct and pin the companion \(\Psi_7\); compute
> \(\Psi_7/(\partial\Phi_7/\partial X)\) on the width-one steep branch; and prove
> whether that branch is cuspidal/non-admissible or gives a genuine oriented
> RM 7-isogeny compatible with the Frey residual character.

If the steep branch is rejected at one already forced `q|C`, it can produce a
new local contradiction.  If it survives, further first-equation local scans
cannot close the route, and the project should construct the projective
normalizations of the rational and quadratic descent loci above, determine
their genera/Jacobians, and run an actual Chabauty or Mordell--Weil sieve.

## 7. Reproduction

Files in this audit:

- `computation/complete_p11_scan.json`, SHA-256
  `AABDB2588519B612CD70325E4DEE839C160B659B79DCA9014EEB9CB967473440`;
- `computation/complete_p29_scan.json`, SHA-256
  `E9C83D812497D91D1254660ADBAAA6BB2C0E745A18D03A2B181E509E6502AA1D`;
- `computation/complete_p31_scan.json`, SHA-256
  `43BF89A3164428FFABF94B32177E47E73D068E9E353BF6260B4114539088CEC3`;
- `computation/verify_branch1_local_certificate.py`, SHA-256
  `8B00BA5E46E57FEB0917D16212A2784A1360A12A82BAFBE804DDEA6AF233267C`.

Commands run successfully in normal and optimized mode:

```text
python -B computation/verify_branch1_local_certificate.py
python -OO -B computation/verify_branch1_local_certificate.py
python -B computation/verify_branch1_local_certificate.py --source PATH/PolQ5Gundlach-7
python -OO -B computation/verify_branch1_local_certificate.py --source PATH/PolQ5Gundlach-7
```

All four runs passed.  Source mode verified the existing 51-member manifest
hash

```text
CB9F8AA7B7F33DD34895A201C4261B6636B69F20C8EAFAA393905072E5ECBE38
```

and bound every good stored finite-field fiber to the reconstructed canonical
pullback.  The third-party source remains external and is not redistributed.
