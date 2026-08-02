# RM(7) moduli bridge: conditional lemma and exact audit boundary

Date: 25 July 2026  
Status: **the abstract bridge is standard and has a complete proof skeleton
below; its application to the Frey Jacobian remains DEPENDENT on the pinned
RM action, polarization and residual-representation identifications.  It does
not determine a rational point on the degree-50 cover.**

> **Controlling update, 2 August 2026.**  The cover/genus application is now
> proved relative to explicit source inputs in `RM7_COVER_IDENTIFICATION.md`.
> That proof adds the generic \(\mathcal O_K\)-action/Rosati lemma, the
> symmetric inert Gundlach citation, and the missing 50-dimensional
> specialization argument.  Residual reducibility and companion/descent
> questions remain obligations for C-029, not for the genus.  Independent
> regeneration of the source coefficient database remains an upstream
> dependency.

## 1. The bridge actually needed

Let

\[
F=\mathbf Q(\sqrt5),\qquad \mathcal O=\mathcal O_F,\qquad k=F,
\]

and let \((J,\lambda,\iota)\) be a principally polarized abelian surface over
\(k\) with a self-adjoint action
\(\iota:\mathcal O\hookrightarrow\operatorname{End}_k(J)\).  Since \(7\) is
inert in \(F\),

\[
\mathcal O/7\mathcal O\simeq\mathbf F_{49},\qquad
J[7](\bar k)\simeq\mathbf F_{49}^{\,2}
\]

as an \(\mathcal O/7\mathcal O\)-module.

The precise forward implication required by the RM route is:

> If the two-dimensional \(\mathbf F_{49}\)-representation on \(J[7]\) has a
> \(G_k\)-stable \(\mathbf F_{49}\)-line \(H\), then \(H\) is the kernel of a
> \(k\)-rational \(7\)-isogeny preserving RM from \(J\) to a principally
> polarized abelian surface.  Consequently the Hilbert moduli point of \(J\)
> has a \(k\)-rational lift to the inert-level \(Y_0((7))\) cover.

Milio--Robert, Section 4.1, define this cover as parametrizing an RM abelian
surface together with an \(\mathcal O\)-stable maximal isotropic kernel in
\(J[7]\).  Their Proposition 4.3 gives \(7^2+1=50\) geometric kernels when
\(7\) is inert.

Primary source:
[Milio--Robert, *Modular polynomials on Hilbert surfaces*,
Section 4.1 and Proposition 4.3](https://doi.org/10.1016/j.jnt.2020.04.014).

## 2. Proof skeleton

### 2.1 Stable line and field of definition

A \(G_k\)-stable \(\mathbf F_{49}\)-line
\(H\subset J[7](\bar k)\) is an \(\mathcal O\)-stable finite subgroup of
order \(49\).  In characteristic zero the torsion is finite etale.  Galois
stability therefore descends \(H\), the quotient \(J/H\), and the quotient
isogeny to \(k\).  The \(\mathcal O\)-action descends because \(H\) is
\(\mathcal O\)-stable.

The project must still spell out one descent point in the final proof:
`absolutely reducible` must yield a line over the coefficient field
\(\mathbf F_{49}\), not merely over its algebraic closure.  In the proposed
Eisenstein type both distinct characters
\(\psi\) and \(\psi\bar\chi_7\) are already \(\mathbf F_7\)-valued, so the
standard Galois-descent argument should provide this line.  That argument has
not yet been promoted to an unconditional project lemma.

### 2.2 Automatic isotropy

Let \(e_7\) denote the Weil pairing defined by the principal polarization.
Self-adjointness of the RM action gives

\[
e_7(\alpha P,Q)=e_7(P,\alpha Q)
\qquad(\alpha\in\mathcal O).
\]

Choose a generator \(v\) of \(H\) over \(\mathbf F_{49}\).  For
\(\alpha,\beta\in\mathbf F_{49}\),

\[
e_7(\alpha v,\beta v)=e_7(v,\alpha\beta v)
=e_7(\beta v,\alpha v).
\]

Alternation also makes the last pairing the inverse of the first.  Hence its
square is \(1\).  As the pairing takes values in \(\mu_7\) and \(7\) is odd,
the pairing is \(1\).  Thus \(H\) is isotropic.  Its order is
\(\sqrt{\#J[7]}=49\), so it is maximal isotropic.

### 2.3 Principal polarization on the quotient

The polarization \(7\lambda\) descends across the maximal isotropic subgroup
\(H\) to a principal polarization on \(J/H\).  This is exactly the
\(\beta=7\) case of the descent construction in Milio--Robert, Section 4.1.
Thus the quotient object lies on the inert Hilbert Hecke cover used by the
published degree-50 modular polynomial.

## 3. Consequence for the explicit polynomial

For a Branch-I point, the source Gundlach coordinates are rational:

\[
U=\frac95V^2,\qquad V=\frac{375t}{t-1}\in\mathbf Q.
\]

Let \(U'\) be the first Gundlach invariant of the quotient.  A
\(k=\mathbf Q(\sqrt5)\)-rational quotient object gives \(U'\in k\), and the
forward modular relation gives

\[
\Phi_7\!\left(U',\frac95V^2,V\right)=0
\]

whenever the chosen affine invariant chart is defined.  The denominator
certificate in `RM7_ROUTE_FEASIBILITY.md` proves that the source chart
is defined for rational \(V\ne0\), which includes every nontrivial Branch-I
solution.

Because the specialized polynomial has rational coefficients, the existence
of \(U'\in\mathbf Q(\sqrt5)\) implies that it has either

1. a rational linear factor; or
2. an irreducible quadratic factor whose discriminant is \(5\) times a
   rational square.

This is a necessary algebraic test for every putative lift.  It is not a
converse: a root of the coarse invariant equation may still fail the
orientation, polarization, descent, or companion-invariant conditions.

## 4. Application-specific status after the 2 August update

For the normalized cover and genus, the following points are now explicit:

- Pacetti--Villagra Torcomian's integral \(\mathcal O_K\)-action on the actual
  generic new part, together with the absence of an old part and
  \(\operatorname{End}_{K(t)}^0(J_t)=K\), supplies maximality at 7;
  positivity of Rosati supplies self-adjointness;
- Milio--Robert's symmetric inert case and Proposition B.5 identify the
  database variables and retain degree 50; and
- absolute irreducibility plus the 50-dimensional algebra map proves that the
  specialized first invariant still generates the line-cover function field.

The following matters remain open, but they have a different role:

- identifying the residual representation and descending reducibility to a
  \(G_K\)-stable line remain part of the modular-method implication leading
  to C-029;
- cusps, \(\Psi_7\), orientation, and Frey descent remain necessary for
  deciding which \(K\)-points are Diophantine lifts; and
- independent certified regeneration of the source coefficients of
  \(\Phi_7\) remains an upstream trust boundary for C-034.

The congruence \(7\mid C\) concerns reduction at the prime above \(7\); it
does not obstruct the characteristic-zero quotient construction above.
Likewise \(t=1\) is a boundary value modulo auxiliary primes, not an actual
positive Branch-I solution, since \(t-1=-C^7/A^3\ne0\).

## 5. Verdict

No conceptual contradiction was found in the forward RM-isogeny route.  The
route is stronger than a heuristic because a reducible residual
representation supplies the required stable subgroup.  Nevertheless, the
project has not yet eliminated the resulting \(k\)-rational points.  The
decisive arithmetic problem remains the specialized degree-50 cover together
with its Branch-I perfect-power conditions.
