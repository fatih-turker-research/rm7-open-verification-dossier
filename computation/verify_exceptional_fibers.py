#!/usr/bin/env python3
"""Exact audit of the exceptional fibres of the level-7 Frey pullback.

The script reconstructs the canonical bivariate polynomial from the pinned
Milio coefficient files through the existing exact specializer.  It then
checks the fibres V=0 and D=0, the two Newton edges above V=infinity, and the
additional singular fibre V=375 needed to interpret a discriminant/genus
calculation.  Only standard-library arithmetic is used.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPECIALIZER_PATH = HERE / "specialize_phi7.py"
DEFAULT_CERTIFICATE = HERE / "exceptional_fibers_certificate.json"

EXPECTED_SOURCE_MANIFEST = "CB9F8AA7B7F33DD34895A201C4261B6636B69F20C8EAFAA393905072E5ECBE38"
EXPECTED_F_HASH = "C8BEB2665A88AC2F8F3172ACE30087ECFA707FCFA45F5363973F9D8CA29C54CC"

# Monic irreducible-factor witnesses, coefficients low degree first.
H10_FACTORS = {
    11: (
        (6, 6, 6, 6, 5, 1),
        (1, 4, 2, 3, 6, 1),
    ),
    13: (
        (3, 1, 1),
        (4, 1, 2, 4, 1),
        (9, 8, 1, 8, 1),
    ),
}

# The complete factorization of Q36 modulo 23, again low degree first.
Q36_FACTORS_MOD23 = tuple(
    tuple(reversed(factor))
    for factor in (
        (1, 4, 17, 16, 9, 11, 19, 22),
        (1, 9, 9, 15, 7, 7, 3, 5, 7, 14, 22, 4, 0, 5),
        (1, 22, 2, 10, 11, 22, 8, 0, 5, 2, 3, 11, 7, 22, 14, 13, 18),
    )
)

# Exact square-free factors of F(X,375), coefficients low degree first.  They
# are witnesses: the verifier proves their product identity and proves the
# degree-4 and degree-8 factors irreducible modulo 19.
V375_LINEAR = (-253125, 1)
V375_QUARTIC = (
    1347786314725940641513698141598606109619140625,
    -13113508936413963148966286093627929687500,
    33746053533862555163819602089843750,
    4159079991269330058910996875,
    167943143212027895569,
)
V375_OCTIC = (
    631134547519412748138819457275628742485860129502251854715575683198468770573201555098421522416174411773681640625,
    -206165532939057658310660652533546411768523571922156188659620333501679808151952232694020494818687438964843750,
    17313595489944702006645064675640286833286155336776536064608316087398910084002174616791307926177978515625,
    1430187308547470966058678585560544652764637745414222107573407999599586797853401005268096923828125,
    29623201365914399041559905304396435625333356550473887384037583518313745090484619140625000,
    -4106451504743618117172151915929399568503105646183975765639582025196716308593750,
    13143788599609691400854099244168954602226535175458965214189453125,
    -10517674667679063478587963125461080869434285931250,
    26937741611631106201,
)


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def load_specializer():
    spec = importlib.util.spec_from_file_location("phi7_specializer_exceptional", SPECIALIZER_PATH)
    require(spec is not None and spec.loader is not None, "cannot load exact specializer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def trim_int(poly: list[int]) -> list[int]:
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly or [0]


def int_mul(left: list[int] | tuple[int, ...], right: list[int] | tuple[int, ...]) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return trim_int(result)


def int_power(poly: list[int] | tuple[int, ...], exponent: int) -> list[int]:
    result = [1]
    base = list(poly)
    while exponent:
        if exponent & 1:
            result = int_mul(result, base)
        exponent >>= 1
        if exponent:
            base = int_mul(base, base)
    return result


def primitive_int(poly: list[int]) -> tuple[list[int], int]:
    poly = trim_int(poly[:])
    content = 0
    for coefficient in poly:
        content = math.gcd(content, abs(coefficient))
    require(content > 0, "zero polynomial has no primitive part")
    primitive = [coefficient // content for coefficient in poly]
    if primitive[-1] < 0:
        primitive = [-coefficient for coefficient in primitive]
        content = -content
    return primitive, content


def exact_positive_nth_root(value: int, exponent: int) -> int:
    require(value > 0 and exponent > 0, "bad exact root input")
    low, high = 0, 1
    while high**exponent < value:
        high <<= 1
    while high - low > 1:
        middle = (low + high) // 2
        if middle**exponent <= value:
            low = middle
        else:
            high = middle
    require(low**exponent == value, "coefficient is not an exact positive power")
    return low


def exact_polynomial_fifth_root(poly: list[int]) -> list[int]:
    require((len(poly) - 1) % 5 == 0, "degree is not divisible by five")
    degree = (len(poly) - 1) // 5
    lead = exact_positive_nth_root(poly[-1], 5)
    root = [0] * (degree + 1)
    root[degree] = lead
    denominator = 5 * lead**4
    for offset in range(1, degree + 1):
        target_degree = 5 * degree - offset
        current = int_power(root, 5)
        known = current[target_degree] if target_degree < len(current) else 0
        difference = poly[target_degree] - known
        require(difference % denominator == 0, "nonintegral fifth-root coefficient")
        root[degree - offset] = difference // denominator
    require(int_power(root, 5) == poly, "fifth-root reconstruction identity failed")
    return root


def fp_trim(poly: list[int], prime: int) -> list[int]:
    result = [coefficient % prime for coefficient in poly]
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result or [0]


def fp_mul(left: list[int] | tuple[int, ...], right: list[int] | tuple[int, ...], prime: int) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] = (result[i + j] + a * b) % prime
    return fp_trim(result, prime)


def fp_sub(left: list[int], right: list[int], prime: int) -> list[int]:
    return fp_trim(
        [
            (left[i] if i < len(left) else 0) - (right[i] if i < len(right) else 0)
            for i in range(max(len(left), len(right)))
        ],
        prime,
    )


def fp_divmod(dividend: list[int], divisor: list[int], prime: int) -> tuple[list[int], list[int]]:
    dividend = fp_trim(dividend, prime)
    divisor = fp_trim(divisor, prime)
    require(divisor != [0], "finite-field division by zero")
    if len(dividend) < len(divisor):
        return [0], dividend
    quotient = [0] * (len(dividend) - len(divisor) + 1)
    inverse = pow(divisor[-1], -1, prime)
    while dividend != [0] and len(dividend) >= len(divisor):
        offset = len(dividend) - len(divisor)
        scalar = dividend[-1] * inverse % prime
        quotient[offset] = scalar
        for index, coefficient in enumerate(divisor):
            dividend[index + offset] = (dividend[index + offset] - scalar * coefficient) % prime
        dividend = fp_trim(dividend, prime)
    return fp_trim(quotient, prime), dividend


def fp_mod(poly: list[int], modulus: list[int], prime: int) -> list[int]:
    return fp_divmod(poly, modulus, prime)[1]


def fp_mulmod(left: list[int], right: list[int], modulus: list[int], prime: int) -> list[int]:
    return fp_mod(fp_mul(left, right, prime), modulus, prime)


def fp_powmod(base: list[int], exponent: int, modulus: list[int], prime: int) -> list[int]:
    result = [1]
    while exponent:
        if exponent & 1:
            result = fp_mulmod(result, base, modulus, prime)
        base = fp_mulmod(base, base, modulus, prime)
        exponent >>= 1
    return result


def fp_gcd(left: list[int], right: list[int], prime: int) -> list[int]:
    while right != [0]:
        _, remainder = fp_divmod(left, right, prime)
        left, right = right, remainder
    inverse = pow(left[-1], -1, prime)
    return fp_trim([inverse * coefficient for coefficient in left], prime)


def prime_divisors(value: int) -> list[int]:
    result: list[int] = []
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            result.append(divisor)
            while value % divisor == 0:
                value //= divisor
        divisor += 1
    if value > 1:
        result.append(value)
    return result


def rabin_irreducible(poly: list[int] | tuple[int, ...], prime: int) -> bool:
    poly = fp_trim(list(poly), prime)
    degree = len(poly) - 1
    require(degree >= 1 and poly[-1] == 1, "Rabin input must be monic")
    x = [0, 1]
    for divisor in prime_divisors(degree):
        frobenius = fp_powmod(x, prime ** (degree // divisor), poly, prime)
        if fp_gcd(poly, fp_sub(frobenius, x, prime), prime) != [1]:
            return False
    return fp_sub(fp_powmod(x, prime**degree, poly, prime), x, prime) == [0]


def normalized_mod(poly: list[int] | tuple[int, ...], prime: int) -> list[int]:
    reduced = fp_trim(list(poly), prime)
    require(reduced[-1] != 0, "degree drops modulo witness prime")
    inverse = pow(reduced[-1], -1, prime)
    return [coefficient * inverse % prime for coefficient in reduced]


def verify_factor_witness(poly: list[int], prime: int, factors: tuple[tuple[int, ...], ...]) -> list[int]:
    product = [1]
    degrees: list[int] = []
    for factor in factors:
        require(factor[-1] == 1, "factor witness is not monic")
        require(rabin_irreducible(factor, prime), "factor witness is reducible")
        product = fp_mul(product, factor, prime)
        degrees.append(len(factor) - 1)
    require(product == normalized_mod(poly, prime), "modular factor product mismatch")
    return degrees


def subset_sums(degrees: list[int]) -> set[int]:
    result = {0}
    for degree in degrees:
        result |= {value + degree for value in tuple(result)}
    return result


def q_trim(poly: list[Fraction]) -> list[Fraction]:
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly or [Fraction(0)]


def q_divmod(dividend: list[Fraction], divisor: list[Fraction]) -> tuple[list[Fraction], list[Fraction]]:
    dividend = q_trim(dividend[:])
    divisor = q_trim(divisor[:])
    require(divisor != [0], "rational-polynomial division by zero")
    if len(dividend) < len(divisor):
        return [Fraction(0)], dividend
    quotient = [Fraction(0)] * (len(dividend) - len(divisor) + 1)
    while dividend != [0] and len(dividend) >= len(divisor):
        offset = len(dividend) - len(divisor)
        scalar = dividend[-1] / divisor[-1]
        quotient[offset] = scalar
        for index, coefficient in enumerate(divisor):
            dividend[index + offset] -= scalar * coefficient
        dividend = q_trim(dividend)
    return q_trim(quotient), dividend


def q_rem(dividend: list[int] | list[Fraction], divisor: list[int] | tuple[int, ...]) -> list[Fraction]:
    return q_divmod([Fraction(value) for value in dividend], [Fraction(value) for value in divisor])[1]


def q_mulmod(left: list[Fraction], right: list[Fraction], modulus: list[int] | tuple[int, ...]) -> list[Fraction]:
    product = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            product[i + j] += a * b
    return q_rem(product, modulus)


def q_sub(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    return q_trim(
        [
            (left[i] if i < len(left) else 0) - (right[i] if i < len(right) else 0)
            for i in range(max(len(left), len(right)))
        ]
    )


def fraction_poly_canonical(poly: list[Fraction]) -> list[int]:
    poly = q_trim(poly[:])
    common_denominator = 1
    for coefficient in poly:
        common_denominator = math.lcm(common_denominator, coefficient.denominator)
    integers = [int(coefficient * common_denominator) for coefficient in poly]
    primitive, _ = primitive_int(integers)
    return primitive


def vector_hash(values: list[int] | tuple[int, ...]) -> str:
    payload = json.dumps(list(values), separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest().upper()


def translated_residue(
    coefficients: dict[int, dict[int, int]],
    base: int,
    factor: list[int] | tuple[int, ...],
    z_degree: int,
    q_degree: int,
) -> list[Fraction]:
    polynomial = [0] * (51 - z_degree)
    for x_degree in range(z_degree, 51):
        taylor = 0
        for v_degree, coefficient in coefficients[x_degree].items():
            if v_degree >= q_degree:
                taylor += coefficient * math.comb(v_degree, q_degree) * base ** (v_degree - q_degree)
        polynomial[x_degree - z_degree] = math.comb(x_degree, z_degree) * taylor
    return q_rem(polynomial, factor)


def translated_orders(
    coefficients: dict[int, dict[int, int]],
    base: int,
    factor: list[int] | tuple[int, ...],
    maximum_z_degree: int,
    maximum_q_degree: int,
) -> tuple[list[int], list[str], dict[int, list[Fraction]]]:
    orders: list[int] = []
    hashes: list[str] = []
    residues: dict[int, list[Fraction]] = {}
    for z_degree in range(maximum_z_degree + 1):
        found = False
        for q_degree in range(maximum_q_degree + 1):
            remainder = translated_residue(coefficients, base, factor, z_degree, q_degree)
            if remainder != [0]:
                orders.append(q_degree)
                canonical = fraction_poly_canonical(remainder)
                hashes.append(vector_hash(canonical))
                residues[z_degree] = remainder
                found = True
                break
        require(found, "translated coefficient vanished beyond search bound")
    return orders, hashes, residues


class ExtensionField:
    """F_p[z]/(factor), with factor monic and irreducible."""

    def __init__(self, prime: int, factor: tuple[int, ...]):
        self.prime = prime
        self.factor = factor
        self.degree = len(factor) - 1
        require(factor[-1] == 1 and rabin_irreducible(factor, prime), "bad extension modulus")
        self.zero = (0,) * self.degree
        self.one = (1,) + (0,) * (self.degree - 1)

    def reduce(self, values: list[int]) -> tuple[int, ...]:
        values = [value % self.prime for value in values]
        if len(values) < self.degree:
            values += [0] * (self.degree - len(values))
        for index in range(len(values) - 1, self.degree - 1, -1):
            scalar = values[index] % self.prime
         ×m´¶‰žËkºwµç|€‰•¹DÕÕ¹Üˆ(€€€Í½ÕÉ•}¡…Í¡•Íl‰•¹DÕÕ¹Ü‰t€ôÍ¡„ÈÔÙ}Á…Ñ ¡‘•¹}Á…Ñ ¤(€€€‘•¹½µ¥¹…Ñ½È€ôÍÀ¹Á…ÉÍ•}ÁÕ±±‰…¬¡‘•¹}Á…Ñ ¹É•…‘}Ñ•áÐ ‰…Í¥¤ˆ¤¤(€€€¹Õµ•É…Ñ½ÉÌ€ômt(€€€™½È¥¹‘•à¥¸É…¹” Ä°€ÔÄ¤è(€€€€€€€É•±…Ñ¥Ù”€ô˜‰9ÕµA¡¤½¹ÕµÁ¡¥í¥¹‘•áôˆ(€€€€€€€Á…Ñ €ô‘…Ñ…‰…Í”€¼É•±…Ñ¥Ù”(€€€€€€€Í½ÕÉ•}¡…Í¡•ÍmÉ•±…Ñ¥Ù•t€ôÍ¡„ÈÔÙ}Á…Ñ ¡Á…Ñ ¤(€€€€€€€¹Õµ•É…Ñ½ÉÌ¹…ÁÁ•¹¡ÍÀ¹Á…ÉÍ•}ÁÕ±±‰…¬¡Á…Ñ ¹É•…‘}Ñ•áÐ ‰…Í¥¤ˆ¤¤¤(€€€µ…¹¥™•ÍÐ€ô¡…Í¡±¥ˆ¹Í¡„ÈÔØ (€€€€€€€©Í½¸¹‘ÕµÁÌ¡Í½ÕÉ•}¡…Í¡•Ì°Í½ÉÑ}­•åÌõQÉÕ”°Í•Á…É…Ñ½ÉÌô ˆ°ˆ°€ˆèˆ¤¤¹•¹½‘” ‰…Í¥¤ˆ¤(€€€€¤¹¡•á‘¥•ÍÐ ¤¹ÕÁÁ•È ¤(€€€É•ÅÕ¥É”¡µ…¹¥™•ÍÐ€ôôaAQ}M=UI}59%MP°€‰Í½ÕÉ”µµ•µ‰•Èµ…¹¥™•ÍÐµ¥Íµ…Ñ ˆ¤(€€€¥˜…É¡¥Ù”¥Ì¹½Ð9½¹”è(€€€€€€€É•ÅÕ¥É”¡Í¡„ÈÔÙ}Á…Ñ ¡…É¡¥Ù”¤€ôôÍÀ¹I!%Y}M!ÈÔØ°€‰…É¡¥Ù”‘¥•ÍÐµ¥Íµ…Ñ ˆ¤(€€€€€€€É•ÅÕ¥É”¡ÍÀ¹…É¡¥Ù•}µ•µ‰•É}¡…Í¡•Ì¡…É¡¥Ù”¤€ôôÍ½ÕÉ•}¡…Í¡•Ì°€‰…É¡¥Ù”½‘…Ñ…‰…Í”µ¥Íµ…Ñ ˆ¤((€€€Ô€ôìÈèÉ…Ñ¥½¸ ä°€Ô¥ô(€€€É…Ñ¥½¹…°€ôìÔÀèÍÀ¹µÕ°¡ÍÀ¹µÕ°¡‘•¹½µ¥¹…Ñ½È°‘•¹½µ¥¹…Ñ½È¤°ÍÀ¹Á½Ý•È¡Ô°€Ð¤¥ô(€€€™½È¥¹‘•à°€¡¹Õµ•É…Ñ½È°•áÁ½¹•¹Ð¤¥¸•¹Õµ•É…Ñ”¡é¥À¡¹Õµ•É…Ñ½ÉÌ°ÍÀ¹A!%}U}aA=99QL¤°ÍÑ…ÉÐôÄ¤è(€€€€€€€É…Ñ¥½¹…±m¥¹‘•à€´€Åt€ôÍÀ¹µÕ°¡¹Õµ•É…Ñ½È°ÍÀ¹Á½Ý•È¡Ô°€Ð€´•áÁ½¹•¹Ð¤¤(€€€½µµ½¹}Ù}½É‘•È€ôµ¥¸¡ÍÀ¹½É‘•È¡½•™™¥¥•¹Ð¤™½È½•™™¥¥•¹Ð¥¸É…Ñ¥½¹…°¹Ù…±Õ•Ì ¤¤(€€€É•ÅÕ¥É”¡½µµ½¹}Ù}½É‘•È€ôô€ØÐ°€‰Õ¹•áÁ•Ñ•½µµ½¸‰½Õ¹‘…Éä½É‘•Èˆ¤(€€€É…Ñ¥½¹…°€ôì(€€€€€€€‘•É•”èÍÀ¹‘¥Ù¥‘•}‰å}Ù}Á½Ý•È¡½•™™¥¥•¹Ð°½µµ½¹}Ù}½É‘•È¤(€€€€€€€™½È‘•É•”°½•™™¥¥•¹Ð¥¸É…Ñ¥½¹…°¹¥Ñ•µÌ ¤(€€€ô(€€€¥¹Ñ••ÉÌ°‘•¹½µ¥¹…Ñ½É}±•…È°½¹Ñ•¹Ð€ôÍÀ¹…¹½¹¥…±}±½‰…±}¥¹Ñ••É}Á½±å¹½µ¥…°¡É…Ñ¥½¹…°¤(€€€É•ÅÕ¥É”¡ÍÀ¹±½‰…±}¡…Í ¡¥¹Ñ••ÉÌ¤€ôôaAQ}}!M °€‰…¹½¹¥…°¡…Í µ¥Íµ…Ñ ˆ¤(€€€É•ÑÕÉ¸ÍÀ°‘•¹½µ¥¹…Ñ½È°É…Ñ¥½¹…°°¥¹Ñ••ÉÌ°‘•¹½µ¥¹…Ñ½É}±•…È°½¹Ñ•¹Ð°µ…¹¥™•ÍÐ(()‘•˜½µÁÕÑ”¡‘…Ñ…‰…Í”èA…Ñ °…É¡¥Ù”èA…Ñ ð9½¹”¤€´ø‘¥ÑmÍÑÈ°½‰©•Ñtè(€€€ÍÀ°‘•¹½µ¥¹…Ñ½È°É…Ñ¥½¹…°°¥¹Ñ••ÉÌ°‘•¹½µ¥¹…Ñ½É}±•…È°½¹Ñ•¹Ð°µ…¹¥™•ÍÐ€ô‰Õ¥±‘}…¹½¹¥…°¡‘…Ñ…‰…Í”°…É¡¥Ù”¤((€€€€ŒXôÀè•á…Ð™¥™Ñ Á½Ý•È…¹Ñ¡”±½…°9•ÝÑ½¸•‘”¸(€€€™¥‰É•}é•É¼€ôm¥¹Ñ••ÉÍm‘•É••t¹•Ð À°€À¤™½È‘•É•”¥¸É…¹” ÔÄ¥t(€€€ÁÉ¥µ¥Ñ¥Ù•}é•É¼°é•É½}Í…±…È€ôÁÉ¥µ¥Ñ¥Ù•}¥¹Ð¡™¥‰É•}é•É¼¤(€€€ ÄÀ€ô•á…Ñ}Á½±å¹½µ¥…±}™¥™Ñ¡}É½½Ð¡ÁÉ¥µ¥Ñ¥Ù•}é•É¼¤(€€€É•ÅÕ¥É”¡µ…Ñ ¹ © ÄÀ¤€ôô€Ä…¹±•¸¡ ÄÀ¤€ôô€ÄÄ°€‰‰… ÄÀÁÉ¥µ¥Ñ¥Ù”™¥™Ñ É½½Ðˆ¤(€€€¡}‘•É••Ì€ômt(€€€™½ÈÁÉ¥µ”¥¸€ ÄÄ°€ÄÌ¤è(€€€€€€€¡}‘•É••Ì¹…ÁÁ•¹¡Ù•É¥™å}™…Ñ½É}Ý¥Ñ¹•ÍÌ¡ ÄÀ°ÁÉ¥µ”° ÄÁ}Q=IMmÁÉ¥µ•t¤¤(€€€½µµ½¸€ôÍÕ‰Í•Ñ}ÍÕµÌ¡¡}‘•É••ÍlÁt¤€˜ÍÕ‰Í•Ñ}ÍÕµÌ¡¡}‘•É••ÍlÅt¤(€€€É•ÅÕ¥É”¡½µµ½¸€ôôìÀ°€ÄÁô°€‰ ÄÀ¥ÉÉ•‘Õ¥‰¥±¥Ñä‘•É•”½‰ÍÑÉÕÑ¥½¸™…¥±•ˆ¤(€€€é•É½}½É‘•ÉÌ°é•É½}¡…Í¡•Ì°|€ôÑÉ…¹Í±…Ñ•‘}½É‘•ÉÌ¡¥¹Ñ••ÉÌ°€À° ÄÀ°€Ô°€È¤(€€€É•ÅÕ¥É”¡é•É½}½É‘•ÉÌ€ôôlÄ°€Ä°€Ä°€Ä°€Ä°€Át°€‰Õ¹•áÁ•Ñ•XôÀÑÉ…¹Í±…Ñ•½É‘•ÉÌˆ¤((€€€€ŒôÀè•á…ÐÄµ…‘¥ŒÙ…±Õ…Ñ¥½¹Ì…¹„ÍÁ±¥ÐµÁÉ¥µ”ÍÅÕ…É•™É••¹•ÍÌÝ¥Ñ¹•ÍÌ¸(€€€ÄÌÙ}É…Ñ¥½¹…°€ôÍÀ¹‘¥Ù¥‘•}‰å}Ù}Á½Ý•È¡‘•¹½µ¥¹…Ñ½È°€Èà¤(€€€ÄÌÙ}¡¥ °|°|€ôÍÀ¹…¹½¹¥…±}ÅÁ½±ä¡ÄÌÙ}É…Ñ¥½¹…°¤(€€€ÄÌØ€ô±¥ÍÐ¡É•Ù•ÉÍ•¡ÄÌÙ}¡¥ ¤¤(€€€É•ÅÕ¥É”¡Ù•Ñ½É}¡…Í ¡ÄÌÙ}¡¥ ¤€ôô€ˆÉàÉÅäÐàÜÅàÜÌÐÔäá	ÑÝäàÁäÌáÀÙá	ÍÙ	ÉÉÙàØÔØˆ°€‰DÌØ¡…Í µ¥Íµ…Ñ ˆ¤(€€€Å}Ù…±Õ…Ñ¥½¹Ìè±¥ÍÑm¥¹Ñt€ômt(€€€™½È‘•É•”¥¸É…¹” ÔÄ¤è(€€€€€€€Ù…±Õ”€ôÉ…Ñ¥½¹…±m‘•É••t(€€€€€€€Ù…±Õ…Ñ¥½¸€ô€À(€€€€€€€Ý¡¥±”ÍÀ¹‘•É•”¡Ù…±Õ”¤€øôÍÀ¹‘•É•”¡ÄÌÙ}É…Ñ¥½¹…°¤è(€€€€€€€€€€€ÅÕ½Ñ¥•¹Ð°É•µ…¥¹‘•È€ôÍÀ¹‘¥Ùµ½‘}ÅÁ½±ä¡Ù…±Õ”°ÄÌÙ}É…Ñ¥½¹…°¤(€€€€€€€€€€€¥˜É•µ…¥¹‘•Èè(€€€€€€€€€€€€€€€‰É•…¬(€€€€€€€€€€€Ù…±Õ”€ôÅÕ½Ñ¥•¹Ð(€€€€€€€€€€€Ù…±Õ…Ñ¥½¸€¬ô€Ä(€€€€€€€Å}Ù…±Õ…Ñ¥½¹Ì¹…ÁÁ•¹¡Ù…±Õ…Ñ¥½¸¤(€€€É•ÅÕ¥É”¡Å}Ù…±Õ…Ñ¥½¹Ì€ôôlÁt€¨€ÔÀ€¬lÉt°€‰Õ¹•áÁ•Ñ•DÌØ½•™™¥¥•¹ÐÙ…±Õ…Ñ¥½¹Ìˆ¤(€€€Å}‘•É••Ì€ôÙ•É¥™å}™…Ñ½É}Ý¥Ñ¹•ÍÌ¡ÄÌØ°€ÈÌ°DÌÙ}Q=IM}5=ÈÌ¤(€€€É•ÅÕ¥É”¡Å}‘•É••Ì€ôôlÜ°€ÄÌ°€ÄÙt°€‰Õ¹•áÁ•Ñ•DÌØ™…Ñ½È‘•É••Ìµ½‘Õ±¼€ÈÌˆ¤(€€€ÍÅÕ…É•™É••}‘}‘•É••Ìè±¥ÍÑm¥¹Ñt€ômt(€€€™½È™…Ñ½È¥¸DÌÙ}Q=IM}5=ÈÌè(€€€€€€€™¥•±€ôáÑ•¹Í¥½¹¥•± ÈÌ°™…Ñ½È¤(€€€€€€€™¥‰É”€ôm™¥•±¹•Ù…±Õ…Ñ”¡¥¹Ñ••ÉÍm‘•É••t¤™½È‘•É•”¥¸É…¹” ÔÄ¥t(€€€€€€€™¥‰É”€ô•áÑ}ÑÉ¥´¡™¥‰É”°™¥•±¤(€€€€€€€É•ÅÕ¥É”¡±•¸¡™¥‰É”¤€´€Ä€ôô€Ðä°€‰ôÀ™¥¹¥Ñ”™¥‰É”‘½•Ì¹½Ð¡…Ù”‘•É•”€Ðäˆ¤(€€€€€€€‘•É¥Ù…Ñ¥Ù”€ôm™¥•±¹Í…±”¡™¥‰É•m¥¹‘•át°¥¹‘•à¤™½È¥¹‘•à¥¸É…¹” Ä°±•¸¡™¥‰É”¤¥t(€€€€€€€€ô•áÑ}¡™¥‰É”°‘•É¥Ù…Ñ¥Ù”°™¥•±¤(€€€€€€€ÍÅÕ…É•™É••}‘}‘•É••Ì¹…ÁÁ•¹¡±•¸¡¤€´€Ä¤(€€€É•ÅÕ¥É”¡ÍÅÕ…É•™É••}‘}‘•É••Ì€ôôlÀ°€À°€Át°€‰ôÀ™¥¹¥Ñ”™¥‰É”¥Ì¹½ÐÍÅÕ…É•™É•”ˆ¤((€€€€ŒXõ¥¹™¥¹¥Ñä¸€AÕÐÜôÄ½X…¹µÕ±Ñ¥Á±ä‰äÝxÄÀÀ™½ÈÑ¡”™¥ÉÍÐ•‘”¸(€€€Ý}½É‘•ÉÌ€ôlÄÀÀ€´µ…à¡¥¹Ñ••ÉÍm‘•É••t¤™½È‘•É•”¥¸É…¹” ÔÄ¥t(€€€É•ÅÕ¥É” (€€€€€€€Ý}½É‘•ÉÍlèÔÁt€ôômµ…Ñ ¹•¥°¡É…Ñ¥½¸ È€¨‘•É•”°€Ü¤¤™½È‘•É•”¥¸É…¹” ÔÀ¥t(€€€€€€€…¹Ý}½É‘•ÉÍlÔÁt€ôô€Èà°(€€€€€€€€‰Õ¹•áÁ•Ñ•¥¹™¥¹¥Ñä½•™™¥¥•¹ÐÙ…±Õ…Ñ¥½¹Ìˆ°(€€€€¤(€€€¥¹™¥¹¥Ñå}¡Õ±°€ô±½Ý•É}¡Õ±°¡l¡‘•É•”°Ý}½É‘•ÉÍm‘•É••t¤™½È‘•É•”¥¸É…¹” ÔÄ¥t¤(€€€É•ÅÕ¥É”¡¥¹™¥¹¥Ñå}¡Õ±°€ôôl À°€À¤°€ Ðä°€ÄÐ¤°€ ÔÀ°€Èà¥t°€‰Õ¹•áÁ•Ñ•¥¹™¥¹¥Ñä9•ÝÑ½¸Á½±å½¸ˆ¤(€€€É•Í¥‘Õ…±}É…Ü€ôm¥¹Ñ••ÉÍlÜ€¨¥¹‘•áumµ…à¡¥¹Ñ••ÉÍlÜ€¨¥¹‘•át¥t™½È¥¹‘•à¥¸É…¹” à¥t(€€€É•Í¥‘Õ…±}¥¹™¥¹¥Ñä°É•Í¥‘Õ…±}Í…±…È€ôÁÉ¥µ¥Ñ¥Ù•}¥¹Ð¡É•Í¥‘Õ…±}É…Ü¤(€€€É•Í¥‘Õ…±}µ½ÄÌ€ô¹½Éµ…±¥é•‘}µ½¡É•Í¥‘Õ…±}¥¹™¥¹¥Ñä°€ÄÌ¤(€€€É•ÅÕ¥É”¡É…‰¥¹}¥ÉÉ•‘Õ¥‰±”¡É•Í¥‘Õ…±}µ½ÄÌ°€ÄÌ¤°€‰¥¹™¥¹¥ÑäÉ•Í¥‘Õ…°‘•É•”´ÜÁ½±å¹½µ¥…°É•‘Õ¥‰±”µ½€ÄÌˆ¤(€€€±…É•}É½½Ð€ôÉ…Ñ¥½¸ (€€€€€€€€µ¥¹Ñ••ÉÍlÐåumµ…à¡¥¹Ñ••ÉÍlÐåt¥t°(€€€€€€€¥¹Ñ••ÉÍlÔÁumµ…à¡¥¹Ñ••ÉÍlÔÁt¥t°(€€€€¤(€€€É•ÅÕ¥É”¡±…É•}É½½Ð€ôôÉ…Ñ¥½¸ Ì¨¨ÈØ°€Ô¨¨Ü€¨€ÈàÄ¨¨È¤°€‰Õ¹•áÁ•Ñ•É…Ñ¥½¹…°¥¹™¥¹¥Ñä‰É…¹ ˆ¤((€€€€ŒXôÌÜÔèÑ¡¥Ì™¥‰É”¥Ì¹••‘•Ñ¼½ÉÉ•Ð„Á½±å¹½µ¥…°µ‘¥ÍÉ¥µ¥¹…¹Ð•¹ÕÌ(€€€€Œ•ÍÑ¥µ…Ñ”¸€Q¡”™…Ñ½ÉÌ‰•±½Ü…É”¥¹‘•Á•¹‘•¹Ñ±ä¡•­•Ý¥Ñ¹•ÍÍ•Ì¸(€€€™¥‰É•|ÌÜÔ€ôl(€€€€€€€ÍÕ´¡½•™™¥¥•¹Ð€¨€ÌÜÔ¨©Ù}‘•É•”™½ÈÙ}‘•É•”°½•™™¥¥•¹Ð¥¸¥¹Ñ••ÉÍmá}‘•É••t¹¥Ñ•µÌ ¤¤(€€€€€€€™½Èá}‘•É•”¥¸É…¹” ÔÄ¤(€€€t(€€€ÁÉ¥µ¥Ñ¥Ù•|ÌÜÔ°Í…±…É|ÌÜÔ€ôÁÉ¥µ¥Ñ¥Ù•}¥¹Ð¡™¥‰É•|ÌÜÔ¤(€€€•áÁ•Ñ•‘|ÌÜÔ€ô¥¹Ñ}µÕ° (€€€€€€€¥¹Ñ}µÕ°¡¥¹Ñ}Á½Ý•È¡XÌÜÕ}1%9H°€È¤°¥¹Ñ}Á½Ý•È¡XÌÜÕ}EUIQ%°€Ø¤¤°(€€€€€€€¥¹Ñ}Á½Ý•È¡XÌÜÕ}=Q%°€Ì¤°(€€€€¤(€€€É•ÅÕ¥É”¡ÁÉ¥µ¥Ñ¥Ù•|ÌÜÔ€ôô•áÁ•Ñ•‘|ÌÜÔ°€‰XôÌÜÔ™…Ñ½É¥é…Ñ¥½¸¥‘•¹Ñ¥Ñä™…¥±•ˆ¤(€€€™½È™…Ñ½È¥¸€¡XÌÜÕ}EUIQ%°XÌÜÕ}=Q%¤è(€€€€€€€É•ÅÕ¥É”¡É…‰¥¹}¥ÉÉ•‘Õ¥‰±”¡¹½Éµ…±¥é•‘}µ½¡™…Ñ½È°€Ää¤°€Ää¤°€‰XôÌÜÔ™…Ñ½È¥ÌÉ•‘Õ¥‰±”µ½€Ääˆ¤((€€€ØÌÜÕ}‘…Ñ„€ômt(€€€™½È™…Ñ½È°µÕ±Ñ¥Á±¥¥Ñä°•áÁ•Ñ•‘}½É‘•ÉÌ¥¸€ (€€€€€€€€¡XÌÜÕ}1%9H°€È°lÈ°€Ä°€Át¤°(€€€€€€€€¡XÌÜÕ}EUIQ%°€Ø°lÈ°€È°€È°€Ä°€Ä°€Ä°€Át¤°(€€€€€€€€¡XÌÜÕ}=Q%°€Ì°lÄ°€Ä°€Ä°€Át¤°(€€€€¤è(€€€€€€€½É‘•ÉÌ°¡…Í¡•Ì°É•Í¥‘Õ•Ì€ôÑÉ…¹Í±…Ñ•‘}½É‘•ÉÌ (€€€€€€€€€€€¥¹Ñ••ÉÌ°€ÌÜÔ°™…Ñ½È°µÕ±Ñ¥Á±¥¥Ñä°€Ì(€€€€€€€€¤(€€€€€€€É•ÅÕ¥É”¡½É‘•ÉÌ€ôô•áÁ•Ñ•‘}½É‘•ÉÌ°€‰Õ¹•áÁ•Ñ•XôÌÜÔÑÉ…¹Í±…Ñ•½É‘•ÉÌˆ¤(€€€€€€€¥˜µÕ±Ñ¥Á±¥¥Ñä€ôô€Èè(€€€€€€€€€€€‘¥ÍÉ¥µ¥¹…¹Ð€ôÅ}ÍÕˆ (€€€€€€€€€€€€€€€Å}µÕ±µ½¡É•Í¥‘Õ•ÍlÅt°É•Í¥‘Õ•ÍlÅt°™…Ñ½È¤°(€€€€€€€€€€€€€€€lÐ€¨Ù…±Õ”™½ÈÙ…±Õ”¥¸Å}µÕ±µ½¡É•Í¥‘Õ•ÍlÁt°É•Í¥‘Õ•ÍlÉt°™…Ñ½È¥t°(€€€€€€€€€€€€¤(€€€€€€€€€€€É•ÅÕ¥É”¡‘¥ÍÉ¥µ¥¹…¹Ð€„ôlÁt°€‰±¥¹•…ÈµÍÕÁÁ½ÉÐÉ•Í¥‘Õ…°ÅÕ…‘É…Ñ¥Œ¥ÌÉ•Á•…Ñ•ˆ¤(€€€€€€€€€€€‰É…¹¡•Ì°É…µ¥™¥…Ñ¥½¸°‘¥™™•É•¹Ñ}Á•É}É½½Ð€ô€È°€Ä°€À(€€€€€€€•±¥˜µÕ±Ñ¥Á±¥¥Ñä€ôô€Øè(€€€€€€€€€€€‘¥ÍÉ¥µ¥¹…¹Ð€ôÅ}ÍÕˆ (€€€€€€€€€€€€€€€Å}µÕ±µ½¡É•Í¥‘Õ•ÍlÍt°É•Í¥‘Õ•ÍlÍt°™…Ñ½È¤°(€€€€€€€€€€€€€€€lÐ€¨Ù…±Õ”™½ÈÙ…±Õ”¥¸Å}µÕ±µ½¡É•Í¥‘Õ•ÍlÁt°É•Í¥‘Õ•ÍlÙt°™…Ñ½È¥t°(€€€€€€€€€€€€¤(€€€€€€€€€€€É•ÅÕ¥É”¡‘¥ÍÉ¥µ¥¹…¹Ð€„ôlÁt°€‰ÅÕ…ÉÑ¥ŒµÍÕÁÁ½ÉÐÉ•Í¥‘Õ…°ÅÕ…‘É…Ñ¥Œ¥ÌÉ•Á•…Ñ•ˆ¤(€€€€€€€€€€€‰É…¹¡•Ì°É…µ¥™¥…Ñ¥½¸°‘¥™™•É•¹Ñ}Á•É}É½½Ð€ô€È°€Ì°€Ð(€€€€€€€•±Í”è(€€€€€€€€€€€É•ÅÕ¥É”¡É•Í¥‘Õ•ÍlÁt€„ôlÁt…¹É•Í¥‘Õ•ÍlÍt€„ôlÁt°€‰½Ñ¥ŒµÍÕÁÁ½ÉÐ•‘”•¹‘Á½¥¹ÐÙ…¹¥Í¡•Ìˆ¤(€€€€€€€€€€€‰É…¹¡•Ì°É…µ¥™¥…Ñ¥½¸°‘¥™™•É•¹Ñ}Á•É}É½½Ð€ô€Ä°€Ì°€È(€€€€€€€ØÌÜÕ}‘…Ñ„¹…ÁÁ•¹ (€€€€€€€€€€€ì(€€€€€€€€€€€€€€€€‰™…Ñ½É}‘•É•”ˆè±•¸¡™…Ñ½È¤€´€Ä°(€€€€€€€€€€€€€€€€‰™¥‰É•}µÕ±Ñ¥Á±¥¥ÑäˆèµÕ±Ñ¥Á±¥¥Ñä°(€€€€€€€€€€€€€€€€‰ÑÉ…¹Í±…Ñ•‘}½É‘•ÉÍ|Á}Ñ¡É½Õ¡}´ˆè½É‘•ÉÌ°(€€€€€€€€€€€€€€€€‰™¥ÉÍÑ}¹½¹é•É½}É•µ…¥¹‘•É}¡…Í¡•Ìˆè¡…Í¡•Ì°(€€€€€€€€€€€€€€€€‰•½µ•ÑÉ¥}‰É…¹¡•Í}Á•É}™…Ñ½É}É½½Ðˆè‰É…¹¡•Ì°(€€€€€€€€€€€€€€€€‰É…µ¥™¥…Ñ¥½¹}¥¹‘•á}•… ˆèÉ…µ¥™¥…Ñ¥½¸°(€€€€€€€€€€€€€€€€‰‘¥™™•É•¹Ñ}½¹ÑÉ¥‰ÕÑ¥½¹}Á•É}™…Ñ½É}É½½Ðˆè‘¥™™•É•¹Ñ}Á•É}É½½Ð°(€€€€€€€€€€€ô(€€€€€€€€¤(€€€‘¥™™•É•¹Ñ|ÌÜÔ€ôÍÕ´¡¥Ñ•µl‰™…Ñ½É}‘•É•”‰t€¨¥Ñ•µl‰‘¥™™•É•¹Ñ}½¹ÑÉ¥‰ÕÑ¥½¹}Á•É}™…Ñ½É}É½½Ð‰t™½È¥Ñ•´¥¸ØÌÜÕ}‘…Ñ„¤(€€€É•ÅÕ¥É”¡‘¥™™•É•¹Ñ|ÌÜÔ€ôô€ÌÈ°€‰Õ¹•áÁ•Ñ•¹½Éµ…±¥é•‘¥™™•É•¹Ð½¹ÑÉ¥‰ÕÑ¥½¸…ÐXôÌÜÔˆ¤(€€€€Œ½È„ÍÅÕ…É”µ™É•”•‘”É•Í¥‘Õ…°°•Ù•ÉäÁ…¥È½˜É½½ÑÌ½¸Ñ¡…Ð•‘”¡…Ì(€€€€Œ‘¥™™•É•¹”Ù…±Õ…Ñ¥½¸•ÅÕ…°Ñ¼Ñ¡”Á½Í¥Ñ¥Ù”É½½ÐÙ…±Õ…Ñ¥½¸¸€Q¡ÕÌÑ¡”(€€€€ŒÁ½±å¹½µ¥…°µ‘¥ÍÉ¥µ¥¹…¹Ð½É‘•ÉÌÁ•È•½µ•ÑÉ¥ŒÍÕÁÁ½ÉÐÁ½¥¹Ð…É”€È°€ÄÀ°(€€€€Œ…¹€ÈÉ•ÍÁ•Ñ¥Ù•±ä¸(€€€Á½±å¹½µ¥…±}‘¥ÍÉ¥µ¥¹…¹Ñ|ÌÜÔ€ô€Ä€¨€È€¬€Ð€¨€ÄÀ€¬€à€¨€È(€€€É•ÅÕ¥É”¡Á½±å¹½µ¥…±}‘¥ÍÉ¥µ¥¹…¹Ñ|ÌÜÔ€ôô€Ôà°€‰Õ¹•áÁ•Ñ•XôÌÜÔÁ½±å¹½µ¥…°‘¥ÍÉ¥µ¥¹…¹Ð½É‘•Èˆ¤(€€€¥¹‘•á}½ÉÉ•Ñ¥½¹|ÌÜÔ€ôÁ½±å¹½µ¥…±}‘¥ÍÉ¥µ¥¹…¹Ñ|ÌÜÔ€´‘¥™™•É•¹Ñ|ÌÜÔ(€€€É•ÅÕ¥É”¡¥¹‘•á}½ÉÉ•Ñ¥½¹|ÌÜÔ€ôô€ÈØ°€‰Õ¹•áÁ•Ñ•XôÌÜÔ¥¹‘•à½ÉÉ•Ñ¥½¸ˆ¤((€€€É•ÍÕ±Ðè‘¥ÑmÍÑÈ°½‰©•Ñt€ôì(€€€€€€€€‰Í¡•µ„ˆè€‰‰•…°µÉ´Üµ•á•ÁÑ¥½¹…°µ™¥‰É•ÌµØÈˆ°(€€€€€€€€‰Í½ÕÉ”ˆèì(€€€€€€€€€€€€‰µ•µ‰•É}µ…¹¥™•ÍÑ}Í¡„ÈÔØˆèµ…¹¥™•ÍÐ°(€€€€€€€€€€€€‰…¹½¹¥…±}}Í¡„ÈÔØˆèaAQ}}!M °(€€€€€€€€€€€€‰½µµ½¹}Y}™…Ñ½É}É•µ½Ù•ˆè€ØÐ°(€€€€€€€€€€€€‰Í…±…É}‘•¹½µ¥¹…Ñ½É}±•…É•ˆèÍÑÈ¡‘•¹½µ¥¹…Ñ½É}±•…È¤°(€€€€€€€€€€€€‰¥¹Ñ••É}½¹Ñ•¹Ñ}É•µ½Ù•ˆèÍÑÈ¡½¹Ñ•¹Ð¤°(€€€€€€€ô°(€€€€€€€€‰Y}•ÅÕ…±Í|Àˆèì(€€€€€€€€€€€€‰ÁÉ¥µ¥Ñ¥Ù•}™¥‰É•}¥‘•¹Ñ¥Ñäˆè€‰ÁÉ¥µ¥Ñ¥Ù”¡¡`°À¤¤õ ÄÀ¡`¥xÔˆ°(€€€€€€€€€€€€‰™¥‰É•}Í…±…ÈˆèÍÑÈ¡é•É½}Í…±…È¤°(€€€€€€€€€€€€‰ ÄÁ}½•™™¥¥•¹ÑÍ}±½Ý}Ñ½}¡¥ ˆè ÄÀ°(€€€€€€€€€€€€‰ ÄÁ}Í¡„ÈÔØˆèÙ•Ñ½É}¡…Í ¡ ÄÀ¤°(€€€€€€€€€€€€‰¥ÉÉ•‘Õ¥‰¥±¥Ñå}Ý¥Ñ¹•ÍÍ}™…Ñ½É}‘•É••ÌˆèìˆÄÄˆè¡}‘•É••ÍlÁt°€ˆÄÌˆè¡}‘•É••ÍlÅuô°(€€€€€€€€€€€€‰‘•É••}ÍÕ‰Í•Ñ}¥¹Ñ•ÉÍ•Ñ¥½¸ˆèÍ½ÉÑ•¡½µµ½¸¤°(€€€€€€€€€€€€‰ÑÉ…¹Í±…Ñ•‘}½É‘•ÉÍ}hÁ}Ñ¡É½Õ¡}hÔˆèé•É½}½É‘•ÉÌ°(€€€€€€€€€€€€‰™¥ÉÍÑ}¹½¹é•É½}É•µ…¥¹‘•É}¡…Í¡•Ìˆèé•É½}¡…Í¡•Ì°(€€€€€€€€€€€€‰±½…±}¹•ÝÑ½¹}•‘”ˆèmlÀ°€Åt°lÔ°€Áut°(€€€€€€€€€€€€‰±½Í•‘}Á½¥¹ÑÌˆè€Ä°(€€€€€€€€€€€€‰±½Í•‘}Á½¥¹Ñ}É•Í¥‘Õ•}‘•É•”ˆè€ÄÀ°(€€€€€€€€€€€€‰•½µ•ÑÉ¥}Á½¥¹ÑÌˆè€ÄÀ°(€€€€€€€€€€€€‰É…µ¥™¥…Ñ¥½¹}¥¹‘•á}•… ˆè€Ô°(€€€€€€€€€€€€‰‘¥™™•É•¹Ñ}½¹ÑÉ¥‰ÕÑ¥½¸ˆè€ÐÀ°(€€€€€€€ô°(€€€€€€€€‰}•ÅÕ…±Í|Àˆèì(€€€€€€€€€€€€‰DÌÙ}½•™™¥¥•¹ÑÍ}±½Ý}Ñ½}¡¥¡}Í¡„ÈÔØˆèÙ•Ñ½É}¡…Í ¡ÄÌØ¤°(€€€€€€€€€€€€‰DÌÙ}½•™™¥¥•¹Ñ}Ù…±Õ…Ñ¥½¹Í}`Á}Ñ¡É½Õ¡}`ÔÀˆèÅ}Ù…±Õ…Ñ¥½¹Ì°(€€€€€€€€€€€€‰¹•ÝÑ½¹}Ù•ÉÑ¥•ÌˆèmlÀ°€Át°lÐä°€Át°lÔÀ°€Éut°(€€€€€€€€€€€€‰DÌÙ}µ½‘|ÈÍ}™…Ñ½É}‘•É••ÌˆèÅ}‘•É••Ì°(€€€€€€€€€€€€‰™¥¹¥Ñ•}™¥‰É•}‘}‘•É••Í}¥¹}µ½‘|ÈÍ}½µÁ½¹•¹ÑÌˆèÍÅÕ…É•™É••}‘}‘•É••Ì°(€€€€€€€€€€€€‰•½µ•ÑÉ¥}™¥¹¥Ñ•}Á½¥¹ÑÍ}•…¡}‰…Í•}É½½Ðˆè€Ðä°(€€€€€€€€€€€€‰•½µ•ÑÉ¥}¥¹™¥¹¥Ñå}Á½¥¹ÑÍ}•…¡}‰…Í•}É½½Ðˆè€Ä°(€€€€€€€€€€€€‰É…µ¥™¥…Ñ¥½¹}¥¹‘¥•Ìˆè€‰…±°€ÄìÑ¡”¥¹™¥¹¥Ñä‰É…¹ ¡…Ì½É‘}Ä¡`¤ô´Èˆ°(€€€€€€€€€€€€‰‘¥™™•É•¹Ñ}½¹ÑÉ¥‰ÕÑ¥½¸ˆè€À°(€€€€€€€ô°(€€€€€€€€‰Y}•ÅÕ…±Í}¥¹™¥¹¥Ñäˆèì(€€€€€€€€€€€€‰Ý}½É‘•ÉÍ}`Á}Ñ¡É½Õ¡}`ÔÀˆèÝ}½É‘•ÉÌ°(€€€€€€€€€€€€‰¹•ÝÑ½¹}Ù•ÉÑ¥•Ìˆèm±¥ÍÐ¡Á½¥¹Ð¤™½ÈÁ½¥¹Ð¥¸¥¹™¥¹¥Ñå}¡Õ±±t°(€€€€€€€€€€€€‰•‘•}Í±½Á•ÌˆèlˆÈ¼Üˆ°€ˆÄÐ‰t°(€€€€€€€€€€€€‰‘•É••|Ý}É•Í¥‘Õ…±}½•™™¥¥•¹ÑÍ}±½Ý}Ñ½}¡¥ ˆèÉ•Í¥‘Õ…±}¥¹™¥¹¥Ñä°(€€€€€€€€€€€€‰‘•É••|Ý}É•Í¥‘Õ…±}Í¡„ÈÔØˆèÙ•Ñ½É}¡…Í ¡É•Í¥‘Õ…±}¥¹™¥¹¥Ñä¤°(€€€€€€€€€€€€‰‘•É••|Ý}É•Í¥‘Õ…±}É…Ý}Í…±…ÈˆèÍÑÈ¡É•Í¥‘Õ…±}Í…±…È¤°(€€€€€€€€€€€€‰¥ÉÉ•‘Õ¥‰¥±¥Ñå}Ý¥Ñ¹•ÍÍ}ÁÉ¥µ”ˆè€ÄÌ°(€€€€€€€€€€€€‰É…µ¥™¥•‘}±½Í•‘}Á½¥¹Ñ}É•Í¥‘Õ•}‘•É•”ˆè€Ü°(€€€€€€€€€€€€‰É…µ¥™¥•‘}±½Í•‘}Á½¥¹Ñ}”ˆè€Ü°(€€€€€€€€€€€€‰É…Ñ¥½¹…±}Õ¹É…µ¥™¥•‘}‰É…¹¡}±•…‘¥¹}½•™™¥¥•¹ÐˆèÍÑÈ¡±…É•}É½½Ð¤°(€€€€€€€€€€€€‰•½µ•ÑÉ¥}Á½¥¹ÑÌˆè€à°(€€€€€€€€€€€€‰É…µ¥™¥…Ñ¥½¹}¥¹‘¥•ÌˆèlÜ°€Ü°€Ü°€Ü°€Ü°€Ü°€Ü°€Åt°(€€€€€€€€€€€€‰‘¥™™•É•¹Ñ}½¹ÑÉ¥‰ÕÑ¥½¸ˆè€ÐÈ°(€€€€€€€ô°(€€€€€€€€‰Y}•ÅÕ…±Í|ÌÜÔˆèì(€€€€€€€€€€€€‰ÁÉ¥µ¥Ñ¥Ù•}™¥‰É•}™…Ñ½É}‘•É••Í}…¹‘}µÕ±Ñ¥Á±¥¥Ñ¥•ÌˆèmlÄ°€Ét°lÐ°€Ùt°là°€Íut°(€€€€€€€€€€€€‰™¥‰É•}Í…±…ÈˆèÍÑÈ¡Í…±…É|ÌÜÔ¤°(€€€€€€€€€€€€‰±½…±}‘…Ñ„ˆèØÌÜÕ}‘…Ñ„°(€€€€€€€€€€€€‰Á½±å¹½µ¥…±}‘¥ÍÉ¥µ¥¹…¹Ñ}½É‘•ÈˆèÁ½±å¹½µ¥…±}‘¥ÍÉ¥µ¥¹…¹Ñ|ÌÜÔ°(€€€€€€€€€€€€‰¹½Éµ…±¥é•‘}‘¥™™•É•¹Ñ}½¹ÑÉ¥‰ÕÑ¥½¸ˆè€ÌÈ°(€€€€€€€€€€€€‰¥¹‘•á}½ÉÉ•Ñ¥½¹}ÑÝ¥•}‘•±Ñ„ˆè¥¹‘•á}½ÉÉ•Ñ¥½¹|ÌÜÔ°(€€€€€€€ô°(€€€€€€€€‰½¹Í•ÅÕ•¹•Ìˆèì(€€€€€€€€€€€€‰Ñ¡É••}‰½Õ¹‘…Éå}å±•}ÑåÁ•Ìˆèì(€€€€€€€€€€€€€€€€‰XôÀˆè€ˆÕxÄÀˆ°(€€€€€€€€€€€€€€€€‰XôÌÜÔˆè€ˆÅxÈ€ÍxÄØˆ°(€€€€€€€€€€€€€€€€‰Xõ¥¹™¥¹¥Ñäˆè€ˆÄ€ÝxÜˆ°(€€€€€€€€€€€ô°(€€€€€€€€€€€€‰Ñ¡É••}‰½Õ¹‘…Éå}‘¥™™•É•¹Ñ}Ñ½Ñ…°ˆè€ÄÄÐ°(€€€€€€€€€€€€‰É…Ñ¥½¹…±}¥¹™¥¹¥Ñå}Á±…”ˆèQÉÕ”°(€€€€€€€€€€€€‰•½µ•ÑÉ¥}¥¹Ñ•É…±¥Ñå}±•µµ„ˆè€‰D¡X¤µ¥ÉÉ•‘Õ¥‰¥±¥ÑäÁ±ÕÌÑ¡”DµÉ…Ñ¥½¹…°¥¹™¥¹¥ÑäÁ±…”™½É•Ì½¹ÍÑ…¹Ð™¥•±D°¡•¹”•½µ•ÑÉ¥Œ¥¹Ñ•É…±¥Ñä¥¸¡…É…Ñ•É¥ÍÑ¥Œé•É¼ˆ°(€€€€€€€€€€€€‰½¹‘¥Ñ¥½¹…±}•¹ÕÍ}¥™}¹½Éµ…±¥é…Ñ¥½¹}¥Í}•Ñ…±•}½™™}Ñ¡•}Ñ¡É••}‰½Õ¹‘…Éå}Ù…±Õ•Ìˆè€à°(€€€€€€€€€€€€‰•¹ÕÍ|á}‘•Á•¹‘•¹äˆè€‰…ÁÁ±¥…Ñ¥½¸Ñ¼Ñ¡”Á¥¹¹•µ½‘Õ±…È½Ù•ÈÕÍ•ÌÑ¡”Í•Á…É…Ñ•±ä‘½Õµ•¹Ñ•‘•Á•¹‘•¹äµÍ•Á…É…Ñ•½Ù•Èµ¥‘•¹Ñ¥™¥…Ñ¥½¸…¹•Ñ…±•¹•ÍÌÑ¡•½É•´ˆ°(€€€€€€€€€€€€‰É…Ý}Á½±å¹½µ¥…±}‘¥ÍÉ¥µ¥¹…¹Ñ}Ý…É¹¥¹œˆè€‰Ñ¡”Á±…¹”µµ½‘•°‘¥ÍÉ¥µ¥¹…¹Ð½Õ¹ÑÌ¥¹‘•à‘•™•ÑÌ…¹…¹¹½Ð‰”¥¹Í•ÉÑ•‘¥É•Ñ±ä¥¹Ñ¼I¥•µ…¹¸µ!ÕÉÝ¥Ñèˆ°(€€€€€€€ô°(€€€€€€€€‰Í½Á•}‰½Õ¹‘…Éäˆèl(€€€€€€€€€€€€‰Ñ¡¥Ì±½…°•ÉÑ¥™¥…Ñ”‘½•Ì¹½Ð¥ÑÍ•±˜ÁÉ½Ù”Ñ¡”Í•Á…É…Ñ•±ä‘½Õµ•¹Ñ•‘•Á•¹‘•¹äµÍ•Á…É…Ñ•½Ù•Èµ¥‘•¹Ñ¥™¥…Ñ¥½¸…¹•Ñ…±•¹•ÍÌÑ¡•½É•´ˆ°(€€€€€€€€€€€€‰¥¹‘•Á•¹‘•¹ÐÉ••¹•É…Ñ¥½¸½˜Ñ¡”Ñ¡¥ÉµÁ…ÉÑäµ½‘Õ±…ÈµÁ½±å¹½µ¥…°¥¹Ñ•ÉÁ½±…Ñ¥½¸É•µ…¥¹Ì½Á•¸ˆ°(€€€€€€€€€€€€‰½µÁ…¹¥½¸¥¹Ù…É¥…¹ÑÌ°ÕÍÀ…¹½É¥•¹Ñ…Ñ¥½¸…¹‘•Í•¹Ð¡•­Ì°…¹Ñ¡”½µÁ±•Ñ”,µÉ…Ñ¥½¹…°Á½¥¹ÐÍ•ÐÉ•µ…¥¸½Á•¸™½È´ÀÈäˆ°(€€€€€€€€€€€€‰¡…É…Ñ•É¥ÍÑ¥Œµé•É¼±¥™Ñ¥¹œ½˜Ñ¡”µ½‘Õ±¼´ÄÀÀä¹½‘”•ÉÑ¥™¥…Ñ”¥Ì½ÁÑ¥½¹…°½¹Í¥ÍÑ•¹äÝ½É¬°¹½ÐÉ•ÅÕ¥É•‰äÑ¡”½¹ÑÉ½±±¥¹œ•¹ÕÌÁÉ½½˜ˆ°(€€€€€€€t°(€€€ô(€€€É•ÑÕÉ¸É•ÍÕ±Ð(()‘•˜µ…¥¸ ¤€´ø¥¹Ðè(€€€Á…ÉÍ•È€ô…ÉÁ…ÉÍ”¹ÉÕµ•¹ÑA…ÉÍ•È¡‘•ÍÉ¥ÁÑ¥½¸õ}}‘½}|¤(€€€Á…ÉÍ•È¹…‘‘}…ÉÕµ•¹Ð ‰•ÉÑ¥™¥…Ñ”ˆ°¹…ÉÌôˆüˆ°ÑåÁ”õA…Ñ °‘•™…Õ±ÐõU1Q}IQ%%Q¤(€€€Á…ÉÍ•È¹…‘‘}…ÉÕµ•¹Ð (€€€€€€€€ˆ´µ‘…Ñ…‰…Í”ˆ°(€€€€€€€ÑåÁ”õA…Ñ °(€€€€€€€É•ÅÕ¥É•õQÉÕ”°(€€€€€€€¡•±Àô‰Í•Á…É…Ñ•±ä½‰Ñ…¥¹••áÑÉ…Ñ•A½±DÕÕ¹‘±… ´Ü‘¥É•Ñ½Éäˆ°(€€€€¤(€€€Á…ÉÍ•È¹…‘‘}…ÉÕµ•¹Ð ˆ´µ…É¡¥Ù”ˆ°ÑåÁ”õA…Ñ ¤(€€€Á…ÉÍ•È¹…‘‘}…ÉÕµ•¹Ð ˆ´µÝÉ¥Ñ”µ•ÉÑ¥™¥…Ñ”ˆ°…Ñ¥½¸ô‰ÍÑ½É•}ÑÉÕ”ˆ¤(€€€…ÉÕµ•¹ÑÌ€ôÁ…ÉÍ•È¹Á…ÉÍ•}…ÉÌ ¤(€€€ÑÉäè(€€€€€€€½µÁÕÑ•€ô½µÁÕÑ”¡…ÉÕµ•¹ÑÌ¹‘…Ñ…‰…Í”°…ÉÕµ•¹ÑÌ¹…É¡¥Ù”¤(€€€€€€€Á…å±½…€ô©Í½¸¹‘ÕµÁÌ¡½µÁÕÑ•°¥¹‘•¹ÐôÈ°Í½ÉÑ}­•åÌõQÉÕ”¤€¬€‰q¸ˆ(€€€€€€€¥˜…ÉÕµ•¹ÑÌ¹ÝÉ¥Ñ•}•ÉÑ¥™¥…Ñ”è(€€€€€€€€€€€…ÉÕµ•¹ÑÌ¹•ÉÑ¥™¥…Ñ”¹ÝÉ¥Ñ•}Ñ•áÐ¡Á…å±½…°•¹½‘¥¹œô‰ÕÑ˜´àˆ°¹•Ý±¥¹”ô‰q¸ˆ¤(€€€€€€€€€€€ÁÉ¥¹Ð¡˜‰]I=Qí…ÉÕµ•¹ÑÌ¹•ÉÑ¥™¥…Ñ•ôˆ¤(€€€€€€€•±Í”è(€€€€€€€€€€€É•ÅÕ¥É”¡…ÉÕµ•¹ÑÌ¹•ÉÑ¥™¥…Ñ”¹¥Í}™¥±” ¤°˜‰•ÉÑ¥™¥…Ñ”¹½Ð™½Õ¹èí…ÉÕµ•¹ÑÌ¹•ÉÑ¥™¥…Ñ•ôˆ¤(€€€€€€€€€€€É•½É‘•€ô©Í½¸¹±½…‘Ì¡…ÉÕµ•¹ÑÌ¹•ÉÑ¥™¥…Ñ”¹É•…‘}Ñ•áÐ¡•¹½‘¥¹œô‰ÕÑ˜´àˆ¤¤(€€€€€€€€€€€É•ÅÕ¥É”¡É•½É‘•€ôô½µÁÕÑ•°€‰É•½É‘••ÉÑ¥™¥…Ñ”‘¥™™•ÉÌ™É½´•á…ÐÉ•½¹ÍÑÉÕÑ¥½¸ˆ¤(€€€€€€€€€€€ÁÉ¥¹Ð ‰AMLèÉ•½É‘••á•ÁÑ¥½¹…°µ™¥‰É”•ÉÑ¥™¥…Ñ”µ…Ñ¡•Ì•á…ÐÉ•½¹ÍÑÉÕÑ¥½¸ˆ¤(€€€€€€€ÁÉ¥¹Ð ‰AMLXôÀè ÄÁxÔ™¥‰É”° ÄÀ¥ÉÉ•‘Õ¥‰±”°Ñ•¸•½µ•ÑÉ¥Œ”ôÔÁ½¥¹ÑÌˆ¤(€€€€€€€ÁÉ¥¹Ð ‰AMLôÀè€ÐäÍÅÕ…É”µ™É•”™¥¹¥Ñ”Á½¥¹ÑÌÁ±ÕÌ½¹”Õ¹É…µ¥™¥•¥¹™¥¹¥ÑäÁ½¥¹Ðˆ¤(€€€€€€€ÁÉ¥¹Ð ‰AMLXõ¥¹™¥¹¥ÑäèÍ•Ù•¸”ôÜÁ½¥¹ÑÌÁ±ÕÌ½¹”DµÉ…Ñ¥½¹…°”ôÄÁ½¥¹Ðˆ¤(€€€€€€€ÁÉ¥¹Ð ‰AMLXôÌÜÔè¹½Éµ…±¥é•‘¥™™•É•¹Ð¥Ì€ÌÈ°¹½ÐÁ½±å¹½µ¥…°µ‘¥ÍÉ¥µ¥¹…¹Ð½É‘•È€Ôàˆ¤(€€€€€€€ÁÉ¥¹Ð ‰=9MEU9è•á¥ÍÑ¥¹œD¡X¤µ¥ÉÉ•‘Õ¥‰¥±¥ÑäÕÁÉ…‘•ÌÑ¼•½µ•ÑÉ¥Œ¥¹Ñ•É…±¥Ñäˆ¤(€€€€€€€ÁÉ¥¹Ð ‰A99Pè…ÁÁ±¥…Ñ¥½¸Ñ¼Ñ¡”Á¥¹¹•µ½‘Õ±…È½Ù•ÈÕÍ•ÌÑ¡”Í•Á…É…Ñ•±ä‘½Õµ•¹Ñ•½Ù•Èµ¥‘•¹Ñ¥™¥…Ñ¥½¸…¹•Ñ…±•¹•ÍÌÑ¡•½É•´ˆ¤(€€€€€€€É•ÑÕÉ¸€À(€€€•á•ÁÐ€¡Õ‘¥ÑÉÉ½È°=MÉÉ½È°U¹¥½‘•ÉÉ½È°Y…±Õ•ÉÉ½È¤…Ì•áŒè(€€€€€€€ÁÉ¥¹Ð¡˜‰%0èí•áôˆ°™¥±”õÍåÌ¹ÍÑ‘•ÉÈ¤(€€€€€€€É•ÑÕÉ¸€Ä(()¥˜}}¹…µ•}|€ôô€‰}}µ…¥¹}|ˆè(€€€É…¥Í”MåÍÑ•µá¥Ð¡µ…¥¸ ¤¤