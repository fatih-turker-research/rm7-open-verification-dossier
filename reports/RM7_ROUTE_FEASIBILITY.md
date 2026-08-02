# Discriminant-5 RM(7) route: exact pullback and acceptance boundary

> Status update (2 August 2026): exceptional fibres, geometric integrality and
> the dependency-separated genus-\(8\) calculation are now recorded in
> `EXCEPTIONAL_FIBERS_AUDIT.md`, `RM7_COVER_IDENTIFICATION.md`, and
> `CURRENT_PROGRESS_2026-08-02.md`. Earlier frontier statements below are
> retained as a dated audit trail.

Date: 2026-07-25  
Status: **exact degree-50 pullback and conditional two-good-fiber proof of
generic irreducibility over \(\mathbf Q(V)\) and \(\mathbf Q(\sqrt5)(V)\);
its rational points remain OPEN. This is not a proof of Branch I or of the
Beal conjecture.**

## 1. Outcome

The discriminant-5 Hilbert modular equation at the inert prime \(7\) exists in
explicit downloadable form.  Pulling it back to the Frey family is therefore
an exact computation, not a missing-theory problem.  The pullback should not,
however, be described as intersecting the Frey line with an "isogeny divisor"
on the Hilbert surface.  Generically,

\[
Y_0((7))\longrightarrow Y(1)
\]

is a finite cover of degree \(7^2+1=50\).  Its pullback to the one-parameter
Frey family is a degree-50 cover of the parameter line.  The arithmetic task is
to determine the \(K=\mathbf Q(\sqrt5)\)-rational lifts on that cover.

The exact calculations completed here identify the Frey image as the simple
Gundlach line

\[
\boxed{5U-9V^2=0},
\qquad
U=\frac{253125t^2}{(t-1)^2},
\qquad
V=\frac{375t}{t-1}.
\]

They also prove that the published Gundlach denominator does not vanish at any
rational point of this line with \(V\ne0\).  Thus the denominator chart itself
does not create a hidden rational exceptional parameter in Branch I.

## 2. Exact invariant calculation

For

\[
C_t:\quad y^2=5x^6-12x^5+10tx^3+t^2,
\]

Mestre's normalized transvectants give the Igusa--Clebsch tuple

\[
\begin{aligned}
 I_2&=-600t^2,\\
 I_4&=202500t^4,\\
 I_6&=-405000t^5(79t+96),\\
 I_{10}&=9331200000t^8(t-1)^2.
\end{aligned}
\]

The last expression agrees with the sextic discriminant in this normalization.
The verifier derives all four entries from the sextic; they are not merely
entered as unchecked target values.

Cowan--Martin use the weighted moduli tuple

\[
(I_2:I_4:I_6:I_{10})=
(24g+6:9g^2:81g^3+18g^2+36h:4h^2).
\]

With

\[
g=-\frac3{10},\qquad
h=\frac{27(t-1)}{3125t},\qquad
\lambda=500t^2,
\]

the verifier proves, as identities in \(\mathbf Q(t)\),

\[
I_{2k}=\lambda^k I_{2k}^{\rm CM}
\quad(k=1,2,3,5).
\]

In the notation of Milio's discriminant-5 Gundlach database,

\[
U=J_2=\frac{G_2^5}{H_{10}},\qquad
V=J_4=\frac{H_6G_2^2}{H_{10}},
\]

and the conversion is

\[
g=-\frac{U}{6V^2},\qquad h=\frac{U^2}{V^5}.
\]

Substitution yields the boxed line above and the inverse parameter

\[
t=\frac{V}{V-375}.
\]

The domain exclusions \(t=0,1\) are the singular/boundary fibers of the Frey
family; all rational-function identities in this note are asserted on their
natural common domain.

## 3. Immediate Branch-I arithmetic restriction

Under

\[
A^3+B^5=C^7,\qquad t=-\frac{B^5}{A^3},
\]

one has \(t-1=-C^7/A^3\).  Therefore the same exact map gives

\[
\boxed{\frac{V}{375}=\frac{B^5}{C^7}},
\qquad
\boxed{1-\frac{V}{375}=\frac{A^3}{C^7}}.
\]

These perfect-power conditions must be imposed on every rational point found
on the modular pullback.  They are stronger than treating \(V\) as an
arbitrary rational parameter, but they do not by themselves eliminate Branch
I.

## 4. Exact denominator certificate

Let \(D(U,V)\) be `DenQ5Gund7` in the external level-7 Gundlach archive.  Exact
substitution and primitive normalization give

\[
D\!\left(\frac95V^2,V\right)=cV^{28}Q_{36}(V),
\qquad c\in\mathbf Q^\times,
\]

where \(Q_{36}\in\mathbf Z[V]\) is primitive of degree \(36\).  Its complete
coefficient vector is embedded in the verifier.  The SHA-256 of its canonical
compact JSON encoding (coefficients from degree \(36\) to degree \(0\)) is

```
2B82A1E94871D8734598ABF4A7B980A938ED06CFF8BAE3F6BEC2E2C6FFFB8656
```

The verifier checks complete modular factorizations, including Rabin tests for
the displayed factors:

\[
\begin{array}{c|c|c}
p & \text{degrees of irreducible factors of }Q_{36}\bmod p
  & \text{subset degrees}\\ \hline
23 & 7,13,16 & \{0,7,13,16,20,23,29,36\}\\
31 & 4,32 & \{0,4,32,36\}.
\end{array}
\]

Their subset-degree intersection is \(\{0,36\}\).  Since the leading
coefficient is nonzero modulo both primes and \(Q_{36}\) is primitive, Gauss's
lemma proves that \(Q_{36}\) is irreducible over \(\mathbf Q\).  In particular,
it has no rational root.  Hence \(D(9V^2/5,V)\ne0\) for rational \(V\ne0\); the
remaining factor \(V=0\) is the excluded fiber \(t=0\).

## 5. Exact modular pullback and generic irreducibility

Milio--Robert's modular polynomial describes \(Y_0((7))\) birationally.  With
the database numerator files \(N_i(U,V)\), exponent table \(e_i\), and
denominator \(D(U,V)\), its first equation has the form

\[
\Phi_7(X,U,V)=X^{50}+
\sum_{i=1}^{50}
\frac{N_i(U,V)}{D(U,V)^2U^{e_i}}X^{i-1}.
\]

The exact Frey pullback is therefore

\[
\boxed{\Phi_7\!\left(X,\frac95V^2,V\right)=0}.
\]

Put

\[
P(X,V)=\Phi_7\!\left(X,\frac95V^2,V\right).
\]

The exact archive-linked specializer constructs its canonical primitive
numerator \(F\in\mathbf Z[X,V]\), of bidegree \((50,100)\), after removing the
common boundary factor \(V^{64}\).  The source formula makes \(P\) monic of
degree \(50\) in \(X\).  Two good split fibers have the certified square-free
factor-degree patterns

\[
\begin{array}{c|c|c|c|c}
p&V&U&D&\text{irreducible factor degrees in }\mathbf F_p[X]\\ \hline
11&4&9&4&25,25\\
659&77&260&482&1,7,7,7,7,7,7,7.
\end{array}
\]

Every factor is explicit; the verifier checks its product and applies the
Rabin irreducibility criterion.  The corresponding subset-degree sets are

\[
S_{11}=\{0,25,50\},
\]

\[
S_{659}=\{0,1,7,8,14,15,21,22,28,29,35,36,42,43,49,50\},
\]

whose intersection is \(\{0,50\}\).

For completeness, this subset calculation becomes a characteristic-zero
irreducibility proof as follows.  Both witness primes split in
\(K=\mathbf Q(\sqrt5)\): \(\sqrt5\equiv\pm4\pmod {11}\) and
\(\sqrt5\equiv\pm258\pmod {659}\).  For either \((p,v)\), choose
\(\mathfrak p\mid p\) and set

\[
R_{p,v}=(\mathcal O_K[V])_{(\mathfrak p,V-v)}.
\]

This is a normal local domain with fraction field \(K(V)\) and residue field
\(\mathbf F_p\).  Since \(p\ne5\) and \(U(v)D(v)\ne0\), the coefficient
denominators of \(P\) are units, so \(P\in R_{p,v}[X]\) remains monic of
degree \(50\).  If \(P=GH\) in \(K(V)[X]\), make \(G,H\) monic.  Their
coefficients are integral over \(R_{p,v}\), because they are elementary
symmetric functions of subsets of the roots of the monic polynomial \(P\).
They lie in \(K(V)=\operatorname{Frac}(R_{p,v})\); normality therefore puts
them in \(R_{p,v}\).  Reduction preserves both degrees, so \(\deg_XG\) must
belong to both \(S_{11}\) and \(S_{659}\).  Hence it is \(0\) or \(50\), and

\[
\boxed{P\text{ is irreducible in }K(V)[X],
\text{ and therefore in }\mathbf Q(V)[X].}
\]

The nonconstant \(X\)-leading coefficient of the primitive numerator \(F\)
does not create a loophole: \(F\) and \(P\) are associates in \(K(V)[X]\), and
at both witness fibers their clearing/saturation scalar is a unit because
\(p\notin\{2,3,5\}\) and \(V,U,D\ne0\).

This conclusion is deliberately limited to irreducibility over the two stated
rational-function fields.  It is not absolute/geometric irreducibility over
\(\overline K(V)\), does not exclude a \(K\)-rational root after particular
specializations \(V=v\), and does not cover the exceptional fibers
\(V=0\), \(D=0\), or \(V=\infty\).  Generic irreducibility therefore does not
solve the rational-point problem.

The next computation must construct the projective normalization, determine
its genus and its map to the \(V\)-line, handle all exceptional fibers, and
select and certify a rational-point method.  The companion \(\Psi_7\) equation
must be used to recover the second target invariant away from
\(\partial_X\Phi_7=0\).

For rational \(V\), a \(K\)-rational lift necessarily makes the specialized
degree-50 polynomial in \(X\) have either

1. a rational linear factor; or
2. a quadratic factor over \(\mathbf Q\) whose discriminant is five times a
   rational square.

Equivalently one may set \(X=u+v\sqrt5\), or impose divisibility by

\[
X^2-2uX+(u^2-5v^2).
\]

This is a useful necessary condition, not yet a sufficient moduli statement.
The polynomial is a coarse-invariant equation: extra automorphisms, repeated
roots, \(\partial_X\Phi_7=0\), and the real-multiplication orientation/descent
involution must be checked separately.  Eliminating every such necessary
factor would suffice for exclusion; retaining one does not yet prove that the
required residual character occurs.

## 6. Source artifact and licensing boundary

The exact external data source is Enea Milio's archive:

- database page: [Modular polynomials](https://members.loria.fr/EMilio/modular-polynomials/);
- archive: [PolQ5Gundlach-7.tar.gz](https://members.loria.fr/EMilio/files/PolQ5Gundlach-7.tar.gz);
- author's verification recipe: [README-Gundlach-Q5-Inert](https://members.loria.fr/EMilio/files/README-Gundlach-Q5-Inert);
- observed size: `42342973` bytes;
- observed SHA-256:
  `9A98249312F46FAF91A6F5D549A2C890EE1713D40A5C4CF9310C4B5819C5C226`.

The 42 MB archive is deliberately **not redistributed** in this release.  As
checked on 2026-07-24, neither the database page, the archive, nor its linked
README supplied an explicit redistribution license.  The URL and digest are
provenance, not a grant of permission.  Any redistribution requires permission
or a separately established license.

The mathematical construction and degree statement are in
[Milio--Robert, *Modular polynomials on Hilbert surfaces*](https://doi.org/10.1016/j.jnt.2020.04.014).
The \(D=5\) genus-2 moduli parametrization is in
[Cowan--Martin, *Moduli for rational genus 2 curves with real multiplication for discriminant 5*](https://doi.org/10.5802/jtnb.1286).
A possible independent certified-evaluation route is described by
[Kieffer, *Evaluating modular equations for abelian surfaces*](https://arxiv.org/abs/2010.10094).

The downloadable polynomial files should not be treated as a prize-grade
certificate merely because they parse.  The published computation uses
high-precision evaluation/interpolation and exact reconstruction.  This
release has not yet supplied an independent Fourier-expansion/Sturm-bound or
certified-evaluation proof for every coefficient of \(\Phi_7\).  A final proof
must pin the archive digest, preserve an exact parse transcript, cross-check
independent coordinates or certified evaluations, and handle all exceptional
fibers explicitly.

There is a second, narrower reproducibility boundary.  The compact two-fiber
certificate, when checked without the external archive, proves the displayed
finite-field products and the Rabin/subset-degree assertions internally, but
does not bind those fibers independently to the published \(\Phi_7\).  The
generic-irreducibility theorem above is therefore conditional on the pinned
source formula and archive linkage.  Running the optional source mode re-parses
all 50 numerator files and reconstructs both witness fibers exactly.

## 7. Reproduction and precise OPEN item

The standard-library verifier is
`computation/verify_rm7_route_certificate.py`.
The pullback and two-good-fiber certificates are checked by
`computation/specialize_phi7.py` and
`computation/verify_two_fiber_certificate.py`.

Self-contained check:

```text
python computation/verify_rm7_route_certificate.py
```

Optional exact linkage to a separately downloaded archive:

```text
python computation/verify_rm7_route_certificate.py --gundlach-archive PATH/PolQ5Gundlach-7.tar.gz
```

It verifies:

- the four Frey invariants from normalized transvectants;
- the weighted \(g,h\) scaling;
- the \(U,V\) line and Branch-I perfect-power identities;
- the complete \(Q_{36}\) coefficient hash;
- both finite-field factorizations and each factor's irreducibility;
- the subset-sum/Gauss-lemma proof;
- and, when the archive is supplied, the archive hash and exact denominator
  specialization.

The two-fiber verifier checks the explicit products, Rabin irreducibility of
all factors, and the subset-degree intersection.  With its optional source
argument it also re-parses the pinned denominator and all 50 numerator files
and reconstructs both finite fibers.

**NEXT/OPEN:** the specialized \(\Phi_7\) and its generic irreducibility over
\(\mathbf Q(V)\) and \(K(V)\) are now certified, subject to the stated external
source dependency.  No file in this release computes the projective
normalization and genus, handles every exceptional fiber, proves the correct
\(K/\mathbf Q\) descent condition, or determines the \(K\)-rational points.
Those are the exact next deliverables.  Until they are complete, this route is
a certified reduction, not a Branch-I elimination.
