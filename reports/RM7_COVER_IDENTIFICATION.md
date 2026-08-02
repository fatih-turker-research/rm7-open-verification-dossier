# Identification of the RM(7) pullback cover

Date: 2 August 2026  
Status: **dependency-separated cover theorem; not a Branch-I elimination, not a
proof of the \((3,5,7)\) equation, and not a proof of the Beal conjecture**

## 1. Statement

Let

\[
K=\mathbf Q(\sqrt5),\qquad
C_t:y^2=5x^6-12x^5+10tx^3+t^2,
\]

and put \(J_t=\operatorname{Jac}(C_t)\).  The exact invariant calculation in
this project gives

\[
5U_G=9V^2,\qquad V=\frac{375t}{t-1}.
\]

Let \(P(X,V)\in\mathbf Q(V)[X]\) be the monic degree-50 equation obtained by
pulling the hash-pinned discriminant-5 inert-level-7 Gundlach polynomial back
to this line, and let \(Y\) be the smooth projective curve with function field
\(\mathbf Q(V)[X]/(P)\).

The database uses the authors' discriminant-5 invariants \((J_2,J_4)\), with
\(J_2=G_2^5/H_{10}\) and \(J_4=H_6G_2^2/H_{10}\).  The project's notation is
\(U_G=J_2\) and \(V=J_4\); the variable \(X\) is the target value \(J'_2\).

Subject to the source dependencies in Section 5, the generic cover \(Y\) is
the pullback of the symmetric inert Hilbert modular correspondence that
classifies the \(\mathcal O_K\)-stable lines in \(J_t[7]\).  It is a
geometrically integral degree-50 cover, finite etale away from
\(t=0,1,\infty\).  The exact normalized boundary data are

\[
\begin{array}{c|c|c|c}
t&V&\text{cycle type}&\text{different}\\
\hline
0&0&5^{10}&40\\
\infty&375&1^2 3^{16}&32\\
1&\infty&1\,7^7&42.
\end{array}
\]

Consequently

\[
2g(Y)-2=-2\cdot50+(40+32+42)=14,
\qquad \boxed{g(Y)=8}.
\]

The theorem determines the normalized cover and its genus.  It does not
determine \(Y(K)\).  Nor does a root of the first modular polynomial by itself
certify the companion invariant, cusp status, orientation, or Frey descent
needed for the Diophantine application.

## 2. The HBAV line cover

Pacetti--Villagra Torcomian construct the displayed genus-two family over
\(K(t)\) from the positive hypergeometric motive.  Their construction gives
the new part an \(\mathcal O_K\)-action; for this quotient there is no old
part, and they state for the generic Jacobian that
\(\operatorname{End}_{K(t)}^0(J_t)=K\).

The asserted full integral \(\mathcal O_K\)-action is already maximal at 7.
The Jacobian also carries its \(K(t)\)-rational canonical principal
polarization.  The associated Rosati involution preserves
\(\operatorname{End}_{K(t)}^0(J_t)=K\) and is positive.  Its restriction to
this totally real field is therefore the identity, so the
\(\mathcal O_K\)-action is self-adjoint.
Since 7 is inert,

\[
\mathcal O_K/7\mathcal O_K\simeq\mathbf F_{49},
\qquad J_t[7]\simeq\mathbf F_{49}^{\,2}
\]

geometrically.  Its rank-one submodules form
\(\mathbf P^1(\mathbf F_{49})\), a set of 50 points.

The discriminant of the sextic is nonzero on
\(U=\mathbf P^1_{\mathbf Q}\setminus\{0,1,\infty\}\), so after base change to
\(K\) the Jacobians form an abelian scheme over \(U_K\).  The generic
\(\mathcal O_K\)-action extends over \(U_K\), and \(J[7]\) and its line scheme
are finite etale there.  Thus the geometric line cover has degree 50 and no
branch point over \(U_{\overline{\mathbf Q}}\); this geometric unramifiedness
descends to the \(\mathbf Q\)-model.

Tate, quadratic, or other scalar twists in the comparison with the
hypergeometric representation multiply every Galois matrix by a scalar.
They therefore disappear after projectivization and do not change this line
cover.

## 3. Why the pinned polynomial is the line cover

Milio--Robert give three ingredients for discriminant 5.

1. Proposition 4.3 counts \(7^2+1=50\) inert RM-stable kernels.
2. The symmetric case of Theorem 4.15 has no factor-of-two enlargement when
   \(\beta=\bar\beta=7\).
3. Proposition B.5 defines the Gundlach polynomial as the product of the
   target first invariant over precisely those kernels; Proposition 4.11 and
   Section 4.3 give the corresponding generic function-field statement.

There is one restriction-to-the-Frey-line issue that must be proved rather
than assumed.  Work over
\(k=\overline{\mathbf Q}(t)=\overline{\mathbf Q}(V)\).  Let \(E\) be the
finite etale \(k\)-algebra of the 50 RM-stable lines.  Evaluation of the target
Gundlach invariant gives an element \(J'_2\in E\) satisfying

\[
P(J'_2,V)=0.
\]

The exact two-fibre certificate proves that \(P\) is irreducible over
\(\mathbf Q(V)\).  The exact width-one rational place at infinity proves that
its constant field is \(\mathbf Q\); hence \(P\) is absolutely irreducible.
Therefore

\[
A=k[X]/(P)
\]

is a field of dimension 50 over \(k\).  Sending \(X\) to \(J'_2\) defines a
unital map \(A\to E\).  A map from a field is injective, and both algebras
have dimension 50, so

\[
A\simeq E.
\]

This equal-degree argument is the missing primitivity check after restriction
to the Frey line.  It also shows that generic collisions of the coarse target
invariant, extra automorphisms, and chart singularities do not create another
component or another function field.  They may affect the chosen plane
equation, but not its normalization.  The companion \(\Psi_7\) is needed to
recover the second target invariant and to test Diophantine admissibility; it
is not needed for this generic function-field identification.

The same argument also gives the arithmetic model needed for C-029.  Put
\(k_K=K(t)=K(V)\), and let \(E_K\) be the finite etale rank-50 algebra of
RM-stable lines.  Both the line scheme and the evaluated invariant
\(J'_2\in E_K\) are defined over \(K(t)\).  The two-fibre certificate proves
that \(P\) is irreducible over \(K(V)\), so
\(A_K=k_K[X]/(P)\) is a degree-50 field.  The \(K(t)\)-defined unital map
\(A_K\to E_K\), \(X\mapsto J'_2\), is injective and is an isomorphism by
equal dimensions.  Thus the identification is not only geometric: it is the
claimed \(K(t)\)-model of the line cover.

## 4. Ramification and geometric connectedness

The line cover is finite etale over \(U\), so every branch point lies over
\(t=0,1,\infty\).  The source-linked exceptional-fibre certificate computes
the normalization of the pinned polynomial at all three points and obtains
different contributions \(40,32,42\).  It also proves that the degree-36
chart-denominator divisor is unramified.

The sum of the differents is 114, and Riemann--Hurwitz gives genus 8.  This
argument uses the exact polynomial boundary calculation as the controlling
ramification input.  The abstract projective local-monodromy cycle check gives
an independent consistency check, but no claim about reduction of a
particular integral 7-adic lattice is needed here.

The rational unramified infinity place, together with irreducibility over
\(\mathbf Q(V)\), forces the constant field to be \(\mathbf Q\).  Thus the
normalization is geometrically integral.  Raw discriminant orders of the
nonnormal plane model are not ramification degrees; the former candidates
4522 and 4509 are invalid.

## 5. Exact dependency boundary

The theorem has four named inputs.

1. The Pacetti--Villagra Torcomian construction of \(C_t\), its inherited
   \(\mathcal O_K\)-action, and its generic endomorphism algebra \(K\).
2. Milio--Robert Proposition 4.3, Proposition 4.11, the symmetric case of
   Theorem 4.15, and Proposition B.5 for the inert degree-50 Gundlach
   correspondence.
3. The project's exact Frey-to-Gundlach map, pullback, absolute
   irreducibility, and normalized boundary calculations.
4. The assertion that the hash-pinned third-party coefficient files are the
   intended published level-7 Gundlach polynomial.

Items 1 and 2 are cited mathematical inputs, not foundations reproved in this
release.  Item 3 is exactly certified.  Item 4 remains an upstream trust
boundary: every byte is hash-pinned, but the original interpolation has not
been independently regenerated.  For that reason C-034 remains labelled
**DEPENDENT**, even though the equal-degree bridge itself is now explicit.

## 6. What remains open

Since \(g(Y)=8>1\), Faltings' theorem implies that \(Y(K)\) is finite.  This
does not provide a list or an effective height bound.  C-029 remains open.
The next decisive work is to:

1. reconstruct and hash-pin the companion \(\Psi_7\);
2. test the width-one infinity point for cusp status, orientation, and Frey
   descent;
3. construct a practical smooth projective model of \(Y/K\), its Jacobian,
   and a rigorous Mordell--Weil rank bound; and
4. enumerate \(Y(K)\), then impose both perfect-power ratios and every
   companion/descent condition.

## Primary references

- A. Pacetti and L. Villagra Torcomian, *On the generalized Fermat equation
  of signature (5,p,3)*, arXiv:2512.17845v1, Sections 2.1, 2.2, and 7.1;
  Section 2.2 invokes GPV Proposition 8.12 for the inherited integral
  \(\mathcal O_K\)-action.
- E. Milio and D. Robert, *Modular polynomials on Hilbert surfaces*, Journal
  of Number Theory 216 (2020), 403--459, especially Propositions 4.3 and
  4.11, Theorem 4.15, and Proposition B.5,
  DOI 10.1016/j.jnt.2020.04.014.
