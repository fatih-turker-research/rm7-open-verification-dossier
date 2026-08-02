#!/usr/bin/env python3
"""Exact, standard-library verifier for the discriminant-5 RM(7) route.

This certificate proves only the algebraic identities and denominator-chart
claim recorded in RM7_ROUTE_FEASIBILITY.md.  It does not construct, specialize,
factor, or solve the degree-50 Hilbert modular polynomial Phi_7.

With no arguments the verifier is self-contained.  If the external Gundlach
level-7 archive is supplied with --gundlach-archive, it additionally checks the
archive SHA-256 and derives the embedded primitive Q_36 directly from its
DenQ5Gund7 file, without extracting the archive to disk.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import tarfile
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable


EXPECTED_ARCHIVE_SHA256 = (
    "9A98249312F46FAF91A6F5D549A2C890EE1713D40A5C4CF9310C4B5819C5C226"
)
EXPECTED_Q36_JSON_SHA256 = (
    "2B82A1E94871D8734598ABF4A7B980A938ED06CFF8BAE3F6BEC2E2C6FFFB8656"
)


class CertificateError(RuntimeError):
    """Raised when an exact certificate check fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CertificateError(message)


# ---------------------------------------------------------------------------
# Univariate Q[t] and Q(t), represented with coefficients low degree first.
# ---------------------------------------------------------------------------

QPoly = tuple[Fraction, ...]
ZERO: QPoly = (Fraction(0),)
ONE: QPoly = (Fraction(1),)
T: QPoly = (Fraction(0), Fraction(1))


def ptrim(values: Iterable[Fraction | int]) -> QPoly:
    result = [Fraction(value) for value in values]
    if not result:
        return ZERO
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return tuple(result)


def pconst(value: Fraction | int) -> QPoly:
    return (Fraction(value),)


def padd(left: QPoly, right: QPoly) -> QPoly:
    result = [Fraction(0)] * max(len(left), len(right))
    for index, value in enumerate(left):
        result[index] += value
    for index, value in enumerate(right):
        result[index] += value
    return ptrim(result)


def pneg(poly: QPoly) -> QPoly:
    return tuple(-value for value in poly)


def psub(left: QPoly, right: QPoly) -> QPoly:
    return padd(left, pneg(right))


def pscale(poly: QPoly, scalar: Fraction | int) -> QPoly:
    scalar = Fraction(scalar)
    return ptrim(scalar * value for value in poly)


def pmul(left: QPoly, right: QPoly) -> QPoly:
    result = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, left_value in enumerate(left):
        for j, right_value in enumerate(right):
            result[i + j] += left_value * right_value
    return ptrim(result)


def ppow(poly: QPoly, exponent: int) -> QPoly:
    require(exponent >= 0, "negative Q[t] exponent")
    result = ONE
    base = poly
    power = exponent
    while power:
        if power & 1:
            result = pmul(result, base)
        base = pmul(base, base)
        power >>= 1
    return result


def as_poly(value: QPoly | Fraction | int) -> QPoly:
    return value if isinstance(value, tuple) else pconst(value)


@dataclass(frozen=True)
class Rat:
    """An unreduced rational function in Q(t); equality is by cross product."""

    numerator: QPoly
    denominator: QPoly = ONE

    def __post_init__(self) -> None:
        require(self.denominator != ZERO, "zero rational-function denominator")

    @staticmethod
    def coerce(value: Rat | QPoly | Fraction | int) -> Rat:
        if isinstance(value, Rat):
            return value
        return Rat(as_poly(value))

    def __add__(self, other: Rat | QPoly | Fraction | int) -> Rat:
        other = Rat.coerce(other)
        return Rat(
            padd(
                pmul(self.numerator, other.denominator),
                pmul(other.numerator, self.denominator),
            ),
            pmul(self.denominator, other.denominator),
        )

    __radd__ = __add__

    def __neg__(self) -> Rat:
        return Rat(pneg(self.numerator), self.denominator)

    def __sub__(self, other: Rat | QPoly | Fraction | int) -> Rat:
        return self + (-Rat.coerce(other))

    def __rsub__(self, other: Rat | QPoly | Fraction | int) -> Rat:
        return Rat.coerce(other) - self

    def __mul__(self, other: Rat | QPoly | Fraction | int) -> Rat:
        other = Rat.coerce(other)
        return Rat(
            pmul(self.numerator, other.numerator),
            pmul(self.denominator, other.denominator),
        )

    __rmul__ = __mul__

    def __truediv__(self, other: Rat | QPoly | Fraction | int) -> Rat:
        other = Rat.coerce(other)
        require(other.numerator != ZERO, "division by zero rational function")
        return Rat(
            pmul(self.numerator, other.denominator),
            pmul(self.denominator, other.numerator),
        )

    def __rtruediv__(self, other: Rat | QPoly | Fraction | int) -> Rat:
        return Rat.coerce(other) / self

    def __pow__(self, exponent: int) -> Rat:
        require(exponent >= 0, "negative rational-function exponent")
        return Rat(ppow(self.numerator, exponent), ppow(self.denominator, exponent))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (Rat, tuple, Fraction, int)):
            return NotImplemented
        other_rat = Rat.coerce(other)
        return pmul(self.numerator, other_rat.denominator) == pmul(
            other_rat.numerator, self.denominator
        )


# ---------------------------------------------------------------------------
# Binary forms and normalized transvectants.
# A form is {(x_degree, y_degree): coefficient in Q[t]}.
# ---------------------------------------------------------------------------

BinaryForm = dict[tuple[int, int], QPoly]


def form_add(left: BinaryForm, right: BinaryForm) -> BinaryForm:
    result = dict(left)
    for monomial, coefficient in right.items():
        result[monomial] = padd(result.get(monomial, ZERO), coefficient)
    return {monomial: value for monomial, value in result.items() if value != ZERO}


def form_scale(form: BinaryForm, scalar: Fraction | int) -> BinaryForm:
    result = {monomial: pscale(value, scalar) for monomial, value in form.items()}
    return {monomial: value for monomial, value in result.items() if value != ZERO}


def form_multiply(left: BinaryForm, right: BinaryForm) -> BinaryForm:
    result: BinaryForm = {}
    for (left_x, left_y), left_coefficient in left.items():
        for (right_x, right_y), right_coefficient in right.items():
            monomial = (left_x + right_x, left_y + right_y)
            result[monomial] = padd(
                result.get(monomial, ZERO),
                pmul(left_coefficient, right_coefficient),
            )
    return {monomial: value for monomial, value in result.items() if value != ZERO}


def falling_factorial(value: int, count: int) -> int:
    result = 1
    for offset in range(count):
        result *= value - offset
    return result


def form_derivative(form: BinaryForm, x_count: int, y_count: int) -> BinaryForm:
    result: BinaryForm = {}
    for (x_degree, y_degree), coefficient in form.items():
        if x_degree < x_count or y_degree < y_count:
            continue
        scalar = falling_factorial(x_degree, x_count) * falling_factorial(
            y_degree, y_count
        )
        result[(x_degree - x_count, y_degree - y_count)] = pscale(
            coefficient, scalar
        )
    return result


def form_degree(form: BinaryForm) -> int:
    require(bool(form), "degree requested for zero binary form")
    degrees = {x_degree + y_degree for x_degree, y_degree in form}
    require(len(degrees) == 1, "binary form is not homogeneous")
    return next(iter(degrees))


def transvectant(left: BinaryForm, right: BinaryForm, order: int) -> BinaryForm:
    """Mestre's normalized Ueberschiebung (left,right)_order."""

    left_degree = form_degree(left)
    right_degree = form_degree(right)
    require(order <= min(left_degree, right_degree), "transvectant order too large")
    normalization = Fraction(
        math.factorial(left_degree - order)
        * math.factorial(right_degree - order),
        math.factorial(left_degree) * math.factorial(right_degree),
    )
    result: BinaryForm = {}
    for index in range(order + 1):
        left_derivative = form_derivative(left, order - index, index)
        right_derivative = form_derivative(right, index, order - index)
        scalar = normalization * ((-1) ** index) * math.comb(order, index)
        result = form_add(
            result,
            form_scale(form_multiply(left_derivative, right_derivative), scalar),
        )
    return result


def constant_form_value(form: BinaryForm, name: str) -> QPoly:
    require(set(form).issubset({(0, 0)}), f"{name} is not a scalar invariant")
    return form.get((0, 0), ZERO)


def derive_frey_igusa_invariants() -> tuple[QPoly, QPoly, QPoly, QPoly]:
    """Derive I2,I4,I6,I10 from the Frey sextic, with exact arithmetic."""

    # Homogenization of 5*x^6 - 12*x^5 + 10*t*x^3 + t^2.
    sextic: BinaryForm = {
        (6, 0): pconst(5),
        (5, 1): pconst(-12),
        (3, 3): pscale(T, 10),
        (0, 6): ppow(T, 2),
    }
    quartic_i = transvectant(sextic, sextic, 4)
    delta = transvectant(quartic_i, quartic_i, 2)
    y1 = transvectant(sextic, quartic_i, 4)
    y2 = transvectant(quartic_i, y1, 2)
    y3 = transvectant(quartic_i, y2, 2)

    clebsch_a = constant_form_value(transvectant(sextic, sextic, 6), "A")
    clebsch_b = constant_form_value(
        transvectant(quartic_i, quartic_i, 4), "B"
    )
    clebsch_c = constant_form_value(transvectant(quartic_i, delta, 4), "C")
    clebsch_d = constant_form_value(transvectant(y3, y1, 2), "D")

    i2 = pscale(clebsch_a, -120)
    i4 = padd(
        pscale(ppow(clebsch_a, 2), -720),
        pscale(clebsch_b, 6750),
    )
    i6 = form_polynomial_sum(
        pscale(ppow(clebsch_a, 3), 8640),
        pscale(pmul(clebsch_a, clebsch_b), -108000),
        pscale(clebsch_c, 202500),
    )
    i10 = form_polynomial_sum(
        pscale(ppow(clebsch_a, 5), -62208),
        pscale(pmul(ppow(clebsch_a, 3), clebsch_b), 972000),
        pscale(pmul(ppow(clebsch_a, 2), clebsch_c), 1620000),
        pscale(pmul(clebsch_a, ppow(clebsch_b, 2)), -3037500),
        pscale(pmul(clebsch_b, clebsch_c), -6075000),
        pscale(clebsch_d, -4556250),
    )
    return i2, i4, i6, i10


def form_polynomial_sum(*polynomials: QPoly) -> QPoly:
    result = ZERO
    for polynomial in polynomials:
        result = padd(result, polynomial)
    return result


def verify_invariants_and_moduli_maps() -> None:
    i2, i4, i6, i10 = derive_frey_igusa_invariants()
    expected_i2 = pscale(ppow(T, 2), -600)
    expected_i4 = pscale(ppow(T, 4), 202500)
    expected_i6 = pscale(
        pmul(ppow(T, 5), padd(pscale(T, 79), pconst(96))), -405000
    )
    expected_i10 = pscale(
        pmul(ppow(T, 8), ppow(psub(T, ONE), 2)), 9331200000
    )
    require(
        (i2, i4, i6, i10)
        == (expected_i2, expected_i4, expected_i6, expected_i10),
        "transvectant-derived Igusa-Clebsch tuple differs from the certificate",
    )

    t = Rat(T)
    g = Rat(pconst(Fraction(-3, 10)))
    h = 27 * (t - 1) / (3125 * t)
    weighted_scale = 500 * t**2
    cowan_martin_tuple = (
        24 * g + 6,
        9 * g**2,
        81 * g**3 + 18 * g**2 + 36 * h,
        4 * h**2,
    )
    frey_tuple = tuple(Rat(poly) for poly in (i2, i4, i6, i10))
    weights = (1, 2, 3, 5)
    for index, (frey_invariant, model_invariant, weight) in enumerate(
        zip(frey_tuple, cowan_martin_tuple, weights), start=1
    ):
        require(
            frey_invariant == weighted_scale**weight * model_invariant,
            f"weighted Igusa-to-(g,h) identity {index} failed",
        )

    # Gundlach variables U=J2 and V=J4 in Milio's D=5 database notation.
    u = 253125 * t**2 / (t - 1) ** 2
    v = 375 * t / (t - 1)
    require(g == -u / (6 * v**2), "g=-U/(6V^2) failed")
    require(h == u**2 / v**5, "h=U^2/V^5 failed")
    require(5 * u == 9 * v**2, "the Frey line 5U-9V^2=0 failed")
    require(t == v / (v - 375), "inverse parameter t=V/(V-375) failed")

    # Branch I: q=B^5/A^3, C^7/A^3=1+q and t=-q.
    q = Rat(T)
    branch_t = -q
    v_over_375 = branch_t / (branch_t - 1)
    require(
        v_over_375 == q / (1 + q),
        "V/375=B^5/C^7 branch identity failed",
    )
    require(
        1 - v_over_375 == 1 / (1 + q),
        "1-V/375=A^3/C^7 branch identity failed",
    )

    print("PASS: Frey Igusa-Clebsch invariants derived by exact transvectants")
    print("PASS: weighted map gives g=-3/10 and h=27(t-1)/(3125t)")
    print("PASS: U=(9/5)V^2 and V=375t/(t-1), with the exact Branch-I ratios")


# ---------------------------------------------------------------------------
# Primitive Q_36 obtained from D(9*V^2/5,V) after removing V^28.
# Coefficients are high degree first.  The canonical JSON encoding is hashed.
# ---------------------------------------------------------------------------

Q36_COEFFICIENTS = (
    57855408118596369,
    4159582996205613077697420,
    611244562480503402298887642436605,
    14838701313077169064810745232939451210350,
    647861909207005520686325566349850549643165167300,
    -22858762569563096814554068495934197813411383504916676625,
    222963981456020458027687500737046575020433964374477930988186000,
    -620792024979698123923830514888222520541127734586792355063479567867500,
    520894182218804821622574731881174668532640060656944460643736192384306868125,
    4772720978457955144562659446560580964948310928382925803895252727367582860909375,
    572841623619993907973339509862976143982921866182326003525482772490839425419874165625,
    -1054361059468023276275502185758156964044624485180931943107201933449726067285833342421875,
    14908113901510451835038272786657146750561073347189499134716301446739374292293552408570625000,
    -53920681492162220603128704309278002108639682840935285400224759928333646786094082955708578437500,
    128823255115461026120882302941347426180060288935895320280707335868501615963569989006461634181328125,
    115422047432229512558885391575569037886169768074419180973436324912395785597632658623891224205480078125,
    4343742576635958417379260353879929006606546311749024592418727635085776290093879296020445379225629442187500,
    -12014864835631591448142830817984806590416790320688541176861259143900244056755601903120018374007888839410156250,
    32076791376412861364147110271752920679054324519298898918129526051870075014692585293759654213246587069654419921875,
    -38972688430239593827957008207085872891703096706009662957354695956007665536701267850174697692297137454737739628906250,
    177786629188340113266224916382562169629816451073804695273076169066583880108595596570218043083308742691652834780507812500,
    -335102109076468704229268411999919270518677005599473468943258916549×kh‘éì¶»§q«^tÍÌŒMLMŒNLNLLÎLŒLˆNLŒLÎÍMÍŽNMÎŒMŽNMMÍNÌŒŒÎMLŒÍŒLMLLÌŽMLLÎLMŒŽNMMÌŽÌŒŒŒÎŒŒŒMÌÍŒŒLŒLLÍÍLˆLMŽÎÍÎLŒŒLŽLLLMÍÌŒÍŒÌÍŒŽMLMLÍLNŒÌŒÍNLÌÌNLÌMMÌMMŽÌMMÌNLLŽMNLMÌŒÍŒNŽLNLÍMÍLŒÍÍÎLŽMŽÍLˆLMŒÍLÍLÎMMMÌŒNMLÍMŒÌNNÍŒÍMŽLŽLŒÌLNLLÌÎÍMÍÍÌÌNÌŒŽMNŽÍLMŒÌÍŽLMÍLNLMŒÎLÌMLMÎMŒLMÌNMŒŒMŒLÍÍKˆLNŽŒMLŒMÌNLŒÍŒÎMŒLMŒŽMÍŒMLÍNÍŒMŒŒŒÌŒÎNMLŒLÌLŒMÍMÍÎMLÎNNNLMMÍLMLÎMÍLÌŒNMMÌŒÌMÌÎLÌŒLˆMÌŒÍMÌMNÍLNMŽLLÍÌNLŒÎŒÍMŒNŒŒÌLÌŒNŒMLMMŒNMLŽNLÍŒLNŒLŒLLÍÌLŽNLÎLÍLMŒLÌŒŽÎLMMMŒMÍNÎMÍLÍMLÌLKˆLMLNMÍLLÌÌÎÌLMÍÍŒÌÌLÎNÌMŽLÎLŒLÎMMMŒÌÎÎNÍÍNNLŒÌŽŽLÌÎLŽŒLNLŒMMÎLMŒŽMÍÍLÎLÌŒÎÎŒNMMÎÌLLÍÍLˆNLÎLMMŽÍMÎMÎÍMÎŽÍMŽNNLÍÎNMMŒÌLŒÎLMÌŽÌMNLMÌÎLÌÌŽLMÍŒLMLÎÍMÍÌÎMÌÌÍÌŒŽMÍŽLLLLMÍŒMÌNÍLˆLŒMÍÍŒÌÌŒŒÍÌMNNMÎNNMMŒÎŒMLÍÎLMÌŒNLMMMLÍMLŒMÍMÍÍÍŽMNÍŒŒÌŒMÎÌŒÌÌŒMÍÌÍMŒÎLÌŒNŒMÍLÌMÍÌNLLLÍÍÌÍÍÍLˆMLÌÌMNMLMÍMÌŽMÎLMMÍŽMÎŽLÌLNÌMMÌŽÍMMŒLÍNÌLÌÎMÎMÍÍMŒÍÍŽNÌŽLMNLMŒLMŒMÎLLÌÌMMÌŒÍNMÍNNLÎŽNÌMMŽMŽÍLˆLÌÌÍÌŒÎLÌMNLŒŒLLLLŒLNÌLLLLÌLŽMLÍÌLMÍLŽLÌMMŒÌNLLMNLŒLMLÍÍŽMNMŒÌÌMMŽLMÌŒÌLLMLLLMÍLLMŒÍŒMMŒLˆLNMÍÎLLÎLMNNNMŒÎMÌLLÌNMÌMMŒMMÍÌÌŒŽÌLÎÍŒÍÌŽMŽÎLŽLÎLÍMŒMŽLLŒÍLÌLÌŒMŒÌÍLÌLÍLLNMÌŒÍLLÍMŽLÎMÍÍLˆLÌÎLNLŒMLŒÌÌÌNLÌÎLÌLNŒLÍÎLLŒMŒŽLŒÎLŒŒLMŒMMMŒMLŒMŽLMNLNMŒÍŒLŒÎMÎLLŒLLMLLLMLÍLMÌŒMÍNÌÍLÎMLMÍMLMÌÌŽMLŒNÍKˆÍÌMŒÌŒNŽLÌMŒÌÎÍÍÍÌÌÎMMLÍŽMMŒŒÌNLŽMMŽNMÌÍNÎLŽÌÍÍÌŽŒMŒŽÍŒŒLÎMNÌŽNMLÍLÌLÍŽMLÌNLMÍÍLÌŒLNÌÍŒÎMŽMŽÍKˆMÍLÍÌÌÍÌŽLŒMÍÎMŽMÌŒÌÌŽLÌŽLNMMÎMLÌŒMÌŽŒÎŒLŒMNŒMMŒŒLNNŒLŽMLŽMÎŽNMŒŒÌÍŒÌLÎLLMÍÌLLÍÌÍÌÎNMŒMÌLŽLŒLˆŽLÍÍÍMÎŒÎLŒLÌÌÎLŒŒÌŽŒLÍÍMŽMÍNÌLÍŽŒMÌNÍÍÍLÍMLÍMMNNLŒŒMMLÍŒNMÍŒŒLÌÍŒŒLŒÌLMÌÌÎLNMŽMLNŽÌÌÍÍŒŒNLLŒÌLLŒNÍKŠB‚‚“SÑST—ÑPÕÔ”×ÒQÒÕ×ÓÕÈHÂˆŒÎˆ
ˆ
KMËM‹KLKNKŒŠKˆ
KKKMKËËËKËMŒ‹JKˆ
KŒ‹‹LLKŒ‹K‹ËLKËŒ‹MLËN
Kˆ
KˆÌNˆ
ˆ
KLKKJKˆ
ˆKˆNˆÌˆËˆNKˆKˆŒ‹ˆNˆËˆËˆM‹ˆËˆMˆˆËˆL‹ˆNˆÌˆŒËˆNˆ‹ˆ‹ˆËˆLˆˆˆKˆËˆˆŒˆŒKˆLËˆŒKˆ
Kˆ
KŸB‚‚ˆÈš[š]KYšY[Û[›ÛZX[È™[ÝÈ\ÙHÛÙY™šXÚY[ÈÝÈYÜ™YHš\œÝ‚™YˆœÝš[JÛNˆ\ÝÚ[Kš[YNˆ[
HOˆ\ÝÚ[N‚ˆ™\Ý[HØÛÙY™šXÚY[	Hš[YH›ÜˆÛÙY™šXÚY[[ˆÛWBˆÚ[H[Š™\Ý[
HˆH[™™\Ý[ËLWHOH‚ˆ™\Ý[œÜ

Bˆ™]\›ˆ™\Ý[ÜˆÌB‚‚™YˆœØY
Yˆ\ÝÚ[KšYÚˆ\ÝÚ[Kš[YNˆ[
HOˆ\ÝÚ[N‚ˆ™\Ý[HÌH
ˆX^
[ŠY
K[ŠšYÚ
JBˆ›Üˆ[™^ÛÙY™šXÚY[[ˆ[[Y\˜]JY
N‚ˆ™\Ý[Ú[™^H
ÏHÛÙY™šXÚY[ˆ›Üˆ[™^ÛÙY™šXÚY[[ˆ[[Y\˜]JšYÚ
N‚ˆ™\Ý[Ú[™^H
ÏHÛÙY™šXÚY[ˆ™]\›ˆœÝš[J™\Ý[š[YJB‚‚™YˆœÜÝX˜XÝ
Yˆ\ÝÚ[KšYÚˆ\ÝÚ[Kš[YNˆ[
HOˆ\ÝÚ[N‚ˆ™]\›ˆœØY
YËXÛÙY™šXÚY[›ÜˆÛÙY™šXÚY[[ˆšYÚKš[YJB‚‚™YˆœÛ][\JYˆ\ÝÚ[KšYÚˆ\ÝÚ[Kš[YNˆ[
HOˆ\ÝÚ[N‚ˆ™\Ý[HÌH
ˆ
[ŠY
H
È[ŠšYÚ
HHJBˆ›ÜˆKYÝ˜[YH[ˆ[[Y\˜]JY
N‚ˆ›Üˆ‹šYÚÝ˜[YH[ˆ[[Y\˜]JšYÚ
N‚ˆ™\Ý[ÚH
È—H
ÏHYÝ˜[YH
ˆšYÚÝ˜[YBˆ™]\›ˆœÝš[J™\Ý[š[YJB‚‚™YˆœÙ]›[Ù
ˆ]šY[™ˆ\ÝÚ[K]š\ÛÜŽˆ\ÝÚ[Kš[YNˆ[ŠHOˆ\VÛ\ÝÚ[K\ÝÚ[WN‚ˆ]šY[™HœÝš[J]šY[™š[YJBˆ]š\ÛÜˆHœÝš[J]š\ÛÜ‹š[YJBˆ™\]Z\™J]š\ÛÜˆOHÌK™š[š]KYšY[Û[›ÛZX[]š\Ú[ÛˆžH™\›ÈŠBˆYˆ[Š]šY[™
H[Š]š\ÛÜŠN‚ˆ™]\›ˆÌK]šY[™ˆ][ÝY[HÌH
ˆ
[Š]šY[™
HH[Š]š\ÛÜŠH
ÈJBˆ™[XZ[™\ˆH]šY[™Î—Bˆ[™\œÙWÛXYHÝÊ]š\ÛÜ–ËLWKLKš[YJBˆÚ[H™[XZ[™\ˆOHÌH[™[Š™[XZ[™\ŠHH[Š]š\ÛÜŠN‚ˆYÜ™YWÜÚYH[Š™[XZ[™\ŠHH[Š]š\ÛÜŠBˆØØ[\ˆH™[XZ[™\–ËLWH
ˆ[™\œÙWÛXY	Hš[YBˆ][ÝY[ÙYÜ™YWÜÚYHHØØ[\‚ˆ›Üˆ[™^ÛÙY™šXÚY[[ˆ[[Y\˜]J]š\ÛÜŠN‚ˆ™[XZ[™\–Ú[™^
ÈYÜ™YWÜÚYHOHØØ[\ˆ
ˆÛÙY™šXÚY[ˆ™[XZ[™\ˆHœÝš[J™[XZ[™\‹š[YJBˆ™]\›ˆœÝš[J][ÝY[š[YJK™[XZ[™\‚‚‚™YˆœÜ™[XZ[™\Š]šY[™ˆ\ÝÚ[K]š\ÛÜŽˆ\ÝÚ[Kš[YNˆ[
HOˆ\ÝÚ[N‚ˆ™]\›ˆœÙ]›[Ù
]šY[™]š\ÛÜ‹š[YJVÌWB‚‚™YˆœÛ[ÛšXÊÛNˆ\ÝÚ[Kš[YNˆ[
HOˆ\ÝÚ[N‚ˆÛHHœÝš[JÛKš[YJBˆ™\]Z\™JÛHOHÌKž™\›ÈÛ[›ÛZX[Ø[››Ý™HXYH[ÛšXÈŠBˆ[™\œÙHHÝÊÛVËLWKLKš[YJBˆ™]\›ˆœÝš[JÚ[™\œÙH
ˆÛÙY™šXÚY[›ÜˆÛÙY™šXÚY[[ˆÛWKš[YJB‚‚™YˆœÙØÙ
Yˆ\ÝÚ[KšYÚˆ\ÝÚ[Kš[YNˆ[
HOˆ\ÝÚ[N‚ˆYHœÝš[JYš[YJBˆšYÚHœÝš[JšYÚš[YJBˆÚ[HšYÚOHÌN‚ˆYšYÚHšYÚœÜ™[XZ[™\ŠYšYÚš[YJBˆ™]\›ˆœÛ[ÛšXÊYš[YJB‚‚™YˆœÜÝÛ[Ù
ˆ˜\ÙNˆ\ÝÚ[K^Û™[ˆ[[Ù[\Îˆ\ÝÚ[Kš[YNˆ[ŠHOˆ\ÝÚ[N‚ˆ™\Ý[HÌWBˆ˜\ÙHHœÜ™[XZ[™\Š˜\ÙK[Ù[\Ëš[YJBˆÝÙ\ˆH^Û™[ˆÚ[HÝÙ\Ž‚ˆYˆÝÙ\ˆ	ˆN‚ˆ™\Ý[HœÜ™[XZ[™\ŠœÛ][\J™\Ý[˜\ÙKš[YJK[Ù[\Ëš[YJBˆ˜\ÙHHœÜ™[XZ[™\ŠœÛ][\J˜\ÙK˜\ÙKš[YJK[Ù[\Ëš[YJBˆÝÙ\ˆHBˆ™]\›ˆ™\Ý[‚‚™Yˆ\Ý[˜ÝÜš[YWÙ]š\ÛÜœÊ˜[YNˆ[
HOˆÙ]Ú[N‚ˆ]š\ÛÜœÎˆÙ]Ú[HHÙ]

BˆØ[™Y]HH‚ˆ™[XZ[š[™ÈH˜[YBˆÚ[HØ[™Y]H
ˆØ[™Y]HH™[XZ[š[™Î‚ˆYˆ™[XZ[š[™È	HØ[™Y]HOH‚ˆ]š\ÛÜœË˜Y
Ø[™Y]JBˆÚ[H™[XZ[š[™È	HØ[™Y]HOH‚ˆ™[XZ[š[™ÈËÏHØ[™Y]BˆØ[™Y]H
ÏHBˆYˆ™[XZ[š[™ÈˆN‚ˆ]š\ÛÜœË˜Y
™[XZ[š[™ÊBˆ™]\›ˆ]š\ÛÜœÂ‚‚™YˆœÚ\×Ú\œ™YXÚX›JÛNˆ\ÝÚ[Kš[YNˆ[
HOˆ›ÛÛ‚ˆˆˆ”˜Xš[ˆ\œ™YXÚXš[]H\Ý›ÜˆH[ÛšXÈÛ[›ÛZX[Ý™\ˆ—Üš[YKˆˆˆ‚‚ˆÛHHœÛ[ÛšXÊÛKš[YJBˆYÜ™YHH[ŠÛJHHBˆYˆYÜ™YHH‚ˆ™]\›ˆ˜[ÙBˆÜÛHHÌWBˆ›Üˆ]š\ÛÜˆ[ˆ\Ý[˜ÝÜš[YWÙ]š\ÛÜœÊYÜ™YJN‚ˆœ›Ø™[š]\ÈHœÜÝÛ[Ù
ÜÛKš[YH
Šˆ
YÜ™YHËÈ]š\ÛÜŠKÛKš[YJBˆYˆœÙØÙ
ÛKœÜÝX˜XÝ
œ›Ø™[š]\ËÜÛKš[YJKš[YJHOHÌWN‚ˆ™]\›ˆ˜[ÙBˆš[˜[Ùœ›Ø™[š]\ÈHœÜÝÛ[Ù
ÜÛKš[YJŠ™YÜ™YKÛKš[YJBˆ™]\›ˆœÜÝX˜XÝ
š[˜[Ùœ›Ø™[š]\ËÜÛKš[YJHOHÌB‚‚™YˆÝXœÙ]ÜÝ[\ÊYÜ™Y\Îˆ]\˜X›VÚ[JHOˆÙ]Ú[N‚ˆÝ[\ÈHÌBˆ›ÜˆYÜ™YH[ˆYÜ™Y\Î‚ˆÝ[\ÈHÝ˜[YH
ÈYÜ™YH›Üˆ˜[YH[ˆ\JÝ[\Ê_Bˆ™]\›ˆÝ[\Â‚‚™Yˆ™\šYžWÜLÍ—Ú\œ™YXÚXš[]WØÙ\YšXØ]J
HOˆ›Û™N‚ˆ™\]Z\™J[ŠLÍ—ÐÓÑQ‘’PÒQS•ÊHOHÍË”LÍˆÙ\È›Ý]™HYÜ™YHÍˆŠBˆ™\]Z\™JX]™ØÙ

”LÍ—ÐÓÑQ‘’PÒQS•ÊHOHK”LÍˆ\È›Ýš[Z]]™HŠBˆØ[›ÛšXØ[ÚœÛÛˆHœÛÛ‹™[\ÊLÍ—ÐÓÑQ‘’PÒQS•ËÙ\\˜]ÜœÏJ‹‹ŽˆŠJK™[˜ÛÙJˆ˜\ØÚZH‚ˆ
BˆXÝX[ÙYÙ\ÝH\ÚX‹œÚLMŠØ[›ÛšXØ[ÚœÛÛŠKš^YÙ\Ý

K\\Š
Bˆ™\]Z\™JˆXÝX[ÙYÙ\ÝOHVPÕQÔLÍ—Ò”ÓÓ—ÔÒLM‹ˆˆ”LÍˆÛÙY™šXÚY[YÙ\ÝZ\ÛX]ÚˆØXÝX[ÙYÙ\ÝH‹ˆ
B‚ˆYÜ™YWÜ\][ÛœÎˆ\ÝÝ\VÚ[‹‹—WHH×Bˆ›Üˆš[YK˜XÝÜœ×ÚYÚÝ×ÛÝÈ[ˆSÑST—ÑPÕÔ”×ÒQÒÕ×ÓÕËš][\Ê
N‚ˆ™\]Z\™JLÍ—ÐÓÑQ‘’PÒQS•ÖÌH	Hš[YHOHˆ”LÍˆÜÙ\ÈYÜ™YH[Ù[ÈÜš[Y_HŠBˆ[™\œÙWÛXYHÝÊLÍ—ÐÓÑQ‘’PÒQS•ÖÌH	Hš[YKLKš[YJBˆ[ÛšX×ÜWÚYÚHÂˆÛÙY™šXÚY[
ˆ[™\œÙWÛXY	Hš[YH›ÜˆÛÙY™šXÚY[[ˆLÍ—ÐÓÑQ‘’PÒQS•ÂˆBˆ›ÙXÝÛÝÈHÌWBˆYÜ™Y\Îˆ\ÝÚ[HH×Bˆ›Üˆ˜XÝÜ—ÚYÚ[ˆ˜XÝÜœ×ÚYÚÝ×ÛÝÎ‚ˆ™\]Z\™J˜XÝÜ—ÚYÚÌHOHKˆ››Û›[ÛšXÈ˜XÝÜˆ[Ù[ÈÜš[Y_HŠBˆ˜XÝÜ—ÛÝÈH\Ý
™]™\œÙY
˜XÝÜ—ÚYÚ
JBˆ™\]Z\™JˆœÚ\×Ú\œ™YXÚX›J˜XÝÜ—ÛÝËš[YJKˆˆ˜ÛZ[YY˜XÝÜˆ\È™YXÚX›H[Ù[ÈÜš[Y_H‹ˆ
Bˆ›ÙXÝÛÝÈHœÛ][\J›ÙXÝÛÝË˜XÝÜ—ÛÝËš[YJBˆYÜ™Y\Ë˜\[™
[Š˜XÝÜ—ÚYÚ
HHJBˆ™\]Z\™Jˆ\Ý
™]™\œÙY
›ÙXÝÛÝÊJHOH[ÛšX×ÜWÚYÚˆˆ™˜XÝÜˆ›ÙXÝÙ\È›Ý\]X[[ÛšXÈLÍˆ[Ù[ÈÜš[Y_H‹ˆ
BˆYÜ™YWÜ\][ÛœË˜\[™
\JYÜ™Y\ÊJB‚ˆÛÛ[[Û—ÙYÜ™Y\ÈHÝXœÙ]ÜÝ[\ÊYÜ™YWÜ\][ÛœÖÌJBˆ›Üˆ\][Ûˆ[ˆYÜ™YWÜ\][ÛœÖÌN—N‚ˆÛÛ[[Û—ÙYÜ™Y\È	HÝXœÙ]ÜÝ[\Ê\][ÛŠBˆ™\]Z\™JˆÛÛ[[Û—ÙYÜ™Y\ÈOHÌÍŸKˆˆ™YÜ™YK\ÝXœÙ][\œÙXÝ[ÛˆÙ\È›Ý›Ý™H\œ™YXÚXš[]NˆØÛÛ[[Û—ÙYÜ™Y\ßH‹ˆ
B‚ˆš[
”TÔÎˆLÍˆ\Èš[Z]]™H[™]ÈØ[›ÛšXØ[ÛÙY™šXÚY[\ÚX]Ú\ÈŠBˆš[
”TÔÎˆLÍˆ[ÙŒÈ\È\œ™YXÚX›KY˜XÝÜˆYÜ™Y\ÈÊÌLÊÌMˆŠBˆš[
”TÔÎˆLÍˆ[ÙÌH\È\œ™YXÚX›KY˜XÝÜˆYÜ™Y\È
ÌÌˆŠBˆš[
”TÔÎˆÛÛ[[ÛˆÝXœÙ]YÜ™Y\È\™HÌÍŸNÈØ]\ÜÈ[[XH›Ý™\ÈLÍ‹ÔH\œ™YXÚX›HŠB‚‚ˆÈKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKBˆÈÜ[Û˜[ÛÝ\˜ÙKX\˜Ú]™H[šØYÙK‚ˆÈKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKB‚‚•T“WÑPÕÔˆH™K˜ÛÛ\[JˆŠÞWJJÎ—Š
ÊJO×ˆŠB‚‚™Yˆ\œÙWØš]˜\šX]WÚ[YÙ\—ÜÛ[›ÛZX[
^ˆÝŠHOˆXÝÝ\VÚ[[K[N‚ˆÛÛ\XÝHˆ‹š›Ú[Š^œÜ]

JBˆ™\]Z\™J›ÛÛ
ÛÛ\XÝ
K™[\H[›ÛZ[˜]ÜˆÛ[›ÛZX[ŠBˆ\›\ÎˆXÝÝ\VÚ[[K[HHßBˆ›Üˆ˜]×Ý\›H[ˆÛÛ\XÝœ™\XÙJ‹H‹ŠËHŠKœÜ]
ŠÈŠN‚ˆYˆ›Ý˜]×Ý\›N‚ˆÛÛ[YBˆÚYÛˆHLHYˆ˜]×Ý\›KœÝ\ÝÚ]
‹HŠH[ÙHBˆ\›HH˜]×Ý\›VÌN—HYˆÚYÛˆOHLH[ÙH˜]×Ý\›BˆÛÙY™šXÚY[HÚYÛ‚ˆÙYÜ™YHHˆWÙYÜ™YHHˆ›Üˆ˜XÝÜˆ[ˆ\›KœÜ]
ŠˆŠN‚ˆ˜\šXX›WÛX]ÚHT“WÑPÕÔ‹™[X]Ú
˜XÝÜŠBˆYˆ˜\šXX›WÛX]Ú‚ˆYÜ™YHH[
˜\šXX›WÛX]Ú™Ü›Ý\
ŠHÜˆŒHŠBˆYˆ˜\šXX›WÛX]Ú™Ü›Ý\
JHOHžŽ‚ˆÙYÜ™YH
ÏHYÜ™YBˆ[ÙN‚ˆWÙYÜ™YH
ÏHYÜ™YBˆ[ÙN‚ˆ™\]Z\™J™K™[X]Ú
ˆ—
È‹˜XÝÜŠH\È›Ý›Û™Kˆ˜˜Y\›HÜ˜]×Ý\›_HŠBˆÛÙY™šXÚY[
H[
˜XÝÜŠBˆ[Û›ÛZX[H
ÙYÜ™YKWÙYÜ™YJBˆ\›\ÖÛ[Û›ÛZX[HH\›\Ë™Ù]
[Û›ÛZX[
H
ÈÛÙY™šXÚY[ˆ™]\›ˆÛ[Û›ÛZX[ˆ˜[YH›Üˆ[Û›ÛZX[˜[YH[ˆ\›\Ëš][\Ê
HYˆ˜[Y_B‚‚™Yˆš[Z]]™WÜLÍ—Ùœ›ÛWÙ[›ÛZ[˜]ÜŠ^ˆÝŠHOˆ\VÚ[‹‹—N‚ˆ[›ÛZ[˜]ÜˆH\œÙWØš]˜\šX]WÚ[YÙ\—ÜÛ[›ÛZX[
^
Bˆ™\]Z\™J[Š[›ÛZ[˜]ÜŠHOHÎ[™^XÝY[”MQÝ[™È\›HÛÝ[ŠBˆ™\]Z\™JX^
›ÜˆÈ[ˆ[›ÛZ[˜]ÜŠHOHÌ‹[™^XÝYYYÜ™YHŠBˆ™\]Z\™JX^
H›ÜˆËH[ˆ[›ÛZ[˜]ÜŠHOHÍK[™^XÝYKYYÜ™YHŠB‚ˆ[YØ˜XÚÎˆXÝÚ[œ˜XÝ[Û—HHßBˆ›Üˆ
ÙYÜ™YKWÙYÜ™YJKÛÙY™šXÚY[[ˆ[›ÛZ[˜]Ü‹š][\Ê
N‚ˆ—ÙYÜ™YHHˆ
ˆÙYÜ™YH
ÈWÙYÜ™YBˆ[YØ˜XÚÖÝ—ÙYÜ™YWHH[YØ˜XÚË™Ù]
—ÙYÜ™YKœ˜XÝ[ÛŠ
JH
Èœ˜XÝ[ÛŠˆÛÙY™šXÚY[
ˆ
JŠžÙYÜ™YJKJŠžÙYÜ™YBˆ
Bˆ[YØ˜XÚÈHÙYÜ™YNˆ˜[YH›ÜˆYÜ™YK˜[YH[ˆ[YØ˜XÚËš][\Ê
HYˆ˜[Y_Bˆ™\]Z\™JZ[Š[YØ˜XÚÊHOHŽ™^XÝY‹XYXÈÜ™\ˆŽŠBˆ™\]Z\™JX^
[YØ˜XÚÊHOH™^XÝY[YX˜XÚÈYÜ™YHŠB‚ˆ˜][Û˜[ØÛÙY™šXÚY[ÈHÂˆ[YØ˜XÚË™Ù]
YÜ™YKœ˜XÝ[ÛŠ
JH›ÜˆYÜ™YH[ˆ˜[™ÙJŽJBˆBˆÛÛ[[Û—Ù[›ÛZ[˜]ÜˆHBˆ›ÜˆÛÙY™šXÚY[[ˆ˜][Û˜[ØÛÙY™šXÚY[Î‚ˆÛÛ[[Û—Ù[›ÛZ[˜]ÜˆHX]›ÛJÛÛ[[Û—Ù[›ÛZ[˜]Ü‹ÛÙY™šXÚY[™[›ÛZ[˜]ÜŠBˆ[YÙ\—ØÛÙY™šXÚY[×ÛÝÈHÂˆ[
ÛÙY™šXÚY[
ˆÛÛ[[Û—Ù[›ÛZ[˜]ÜŠH›ÜˆÛÙY™šXÚY[[ˆ˜][Û˜[ØÛÙY™šXÚY[ÂˆBˆÛÛ[HX]™ØÙ

š[YÙ\—ØÛÙY™šXÚY[×ÛÝÊBˆš[Z]]™WÛÝÈHØÛÙY™šXÚY[ËÈÛÛ[›ÜˆÛÙY™šXÚY[[ˆ[YÙ\—ØÛÙY™šXÚY[×ÛÝ×BˆYˆš[Z]]™WÛÝÖËLWH‚ˆš[Z]]™WÛÝÈHËXÛÙY™šXÚY[›ÜˆÛÙY™šXÚY[[ˆš[Z]]™WÛÝ×Bˆ™]\›ˆ\J™]™\œÙY
š[Z]]™WÛÝÊJB‚‚™YˆÚLM—Ùš[J]ˆ]
HOˆÝŽ‚ˆYÙ\ÝH\ÚX‹œÚLMŠ
BˆÚ]]›Ü[Šœ˜ˆŠH\È[™N‚ˆ›Üˆ›ØÚÈ[ˆ]\Š[X™Nˆ[™Kœ™XY
L
ˆL
KˆˆŠN‚ˆYÙ\Ý\]J›ØÚÊBˆ™]\›ˆYÙ\Ýš^YÙ\Ý

K\\Š
B‚‚™Yˆ™\šYžWÙ^\›˜[Ø\˜Ú]™J]ˆ]
HOˆ›Û™N‚ˆ™\]Z\™J]š\×Ùš[J
Kˆ˜\˜Ú]™HÙ\È›Ý^\ÝˆÜ]HŠBˆXÝX[ÙYÙ\ÝHÚLM—Ùš[J]
Bˆ™\]Z\™JˆXÝX[ÙYÙ\ÝOHVPÕQÐTÒU‘WÔÒLM‹ˆˆ‘Ý[™XÚ\˜Ú]™HÒKLMˆZ\ÛX]ÚˆØXÝX[ÙYÙ\ÝH‹ˆ
BˆÚ]\™š[K›Ü[Š][ÙOHœŽ™ÞˆŠH\È\˜Ú]™N‚ˆØ[™Y]\ÈHÂˆY[X™\‚ˆ›ÜˆY[X™\ˆ[ˆ\˜Ú]™K™Ù]Y[X™\œÊ
BˆYˆY[X™\‹š\Ùš[J
H[™Y[X™\‹›˜[YK™[™ÝÚ]
‹Ñ[”MQÝ[™ÈŠBˆBˆ™\]Z\™J[ŠØ[™Y]\ÊHOHK˜\˜Ú]™H]\ÝÛÛZ[ˆ^XÝHÛ™H[”MQÝ[™ÈŠBˆÝ™X[HH\˜Ú]™K™^˜XÝš[JØ[™Y]\ÖÌJBˆ™\]Z\™JÝ™X[H\È›Ý›Û™K˜ÛÝ[›Ý™XY[”MQÝ[™ÈŠBˆ[›ÛZ[˜]Ü—Ý^HÝ™X[Kœ™XY

K™XÛÙJ˜\ØÚZHŠBˆ\š]™YHš[Z]]™WÜLÍ—Ùœ›ÛWÙ[›ÛZ[˜]ÜŠ[›ÛZ[˜]Ü—Ý^
Bˆ™\]Z\™Jˆ\š]™YOHLÍ—ÐÓÑQ‘’PÒQS•Ëˆ˜\˜Ú]™H[›ÛZ[˜]ÜˆÜXÚX[^˜][ÛˆÙ\È›Ý\]X[[X™YYLÍˆ‹ˆ
Bˆš[
ˆ”TÔÎˆ^\›˜[\˜Ú]™HÒKLMˆX]Ú\È
Ü]œÝ]

KœÝÜÚ^™_Hž]\ÊHŠBˆš[
”TÔÎˆ^XÝ
U—Œ‹ÍKŠHÜXÚX[^˜][Ûˆ\ÈÊ•—ŒŽ
”LÍŠŠKÈ[ˆWžŠB‚‚™YˆXZ[Š
HOˆ[‚ˆ\œÙ\ˆH\™Ü\œÙK\™Ý[Y[\œÙ\Š\ØÜš\[ÛW×ÙØ××ÊBˆ\œÙ\‹˜YØ\™Ý[Y[
ˆ‹KYÝ[™XÚX\˜Ú]™H‹ˆ\OT]ˆ[Jˆ›Ü[Û˜[ÛMQÝ[™XÚMË\‹™ÞŽÈ™\šYšY\È]ÈÒKLMˆ[™\š]™\È‚ˆ”LÍˆ\™XÝHœ›ÛH[”MQÝ[™È‚ˆ
Kˆ
Bˆ\™ÜÈH\œÙ\‹œ\œÙWØ\™ÜÊ
B‚ˆžN‚ˆ™\šYžWÚ[˜\šX[×Ø[™Û[Ù[WÛX\Ê
Bˆ™\šYžWÜLÍ—Ú\œ™YXÚXš[]WØÙ\YšXØ]J
BˆYˆ\™ÜË™Ý[™XÚØ\˜Ú]™H\È›Ý›Û™N‚ˆ™\šYžWÙ^\›˜[Ø\˜Ú]™J\™ÜË™Ý[™XÚØ\˜Ú]™JBˆ[ÙN‚ˆš[
”ÒÒTˆ^\›˜[Ý[™XÚ\˜Ú]™H[šØYÙH
\ÙHKYÝ[™XÚX\˜Ú]™HU
HŠBˆ^Ù\Ù\YšXØ]Q\œ›Üˆ\È\œ›ÜŽ‚ˆš[
ˆ‘RSˆÙ\œ›ÜŸHŠBˆ™]\›ˆB‚ˆš[
•‘T’Q’QQˆ^XÝ“MÈ›Ý]HY[]Y\È[™LÍˆ\œ™YXÚXš[]HÙ\YšXØ]HŠBˆš[
ˆ”ÐÓÔNˆ\È™\šYšY\ˆÛÝ™\œÈH“MÈ[™H[™[›ÛZ[˜]ÜˆÛ›NÈ‚ˆHÙ\\˜]HWÍÈÙ\YšXØ]\ÈÛÝ™\ˆÜXÚX[^˜][Ûˆ[™Ù[™\šXÈ˜XÝÜš^˜][Ûˆ‚ˆ
Bˆš[
“ÔSŽˆÛÛ\[š[Û‹ÛÜšY[][Û‹Ù\ØÙ[[™ÛÛ\]HË\˜][Û˜[Ú[]\›Z[˜][ÛˆŠBˆ™]\›ˆ‚‚šYˆ×Û˜[YW×ÈOH—×ÛXZ[—×ÈŽ‚ˆ˜Z\ÙHÞ\Ý[Q^]
XZ[Š
JB