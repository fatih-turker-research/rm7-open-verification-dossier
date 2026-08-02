#!/usr/bin/env python3
"""Exact specialization of Milio's D=5, level-7 Gundlach Phi polynomial.

This is a bounded, standard-library computation.  It parses the 50 published
NumPhi coefficient files, substitutes

    U = (9/5) V^2,

clears the common denominator in the formula from the author's README, and
canonically normalizes the resulting polynomial in Z[X,V].  It does not try
to factor the polynomial or determine rational points.

Only compact hashes and structural metadata are emitted: the large third-
party coefficient database is not copied into the certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import tarfile
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable


ARCHIVE_SHA256 = "9A98249312F46FAF91A6F5D549A2C890EE1713D40A5C4CF9310C4B5819C5C226"
EXPECTED_SOURCE_MANIFEST_SHA256 = "CB9F8AA7B7F33DD34895A201C4261B6636B69F20C8EAFAA393905072E5ECBE38"
EXPECTED_CANONICAL_SHA256 = "C8BEB2665A88AC2F8F3172ACE30087ECFA707FCFA45F5363973F9D8CA29C54CC"

# First row of Tab for l=7 in README-Gundlach-Q5-Inert.  Entry i is the
# exponent of U in the denominator of the coefficient of X^(i-1).
PHI_U_EXPONENTS = (
    2,
    3,
    *([4] * 43),
    3,
    2,
    2,
    1,
    0,
)


class SpecializationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SpecializationError(message)


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


# Sparse Q[V], degree -> coefficient.
Poly = dict[int, Fraction]


def clean(poly: Poly) -> Poly:
    return {degree: coefficient for degree, coefficient in poly.items() if coefficient}


def add(left: Poly, right: Poly) -> Poly:
    if len(left) < len(right):
        left, right = right, left
    result = dict(left)
    for degree, coefficient in right.items():
        value = result.get(degree, Fraction(0)) + coefficient
        if value:
            result[degree] = value
        else:
            result.pop(degree, None)
    return result


def neg(poly: Poly) -> Poly:
    return {degree: -coefficient for degree, coefficient in poly.items()}


def mul(left: Poly, right: Poly) -> Poly:
    if not left or not right:
        return {}
    # Most products in the database are by a scalar or monomial.  Keeping this
    # path explicit avoids unnecessary quadratic loops over dense y-polynomials.
    if len(left) == 1:
        (left_degree, left_coefficient), = left.items()
        return {
            left_degree + right_degree: left_coefficient * right_coefficient
            for right_degree, right_coefficient in right.items()
            if left_coefficient * right_coefficient
        }
    if len(right) == 1:
        return mul(right, left)
    result: Poly = {}
    for left_degree, left_coefficient in left.items():
        for right_degree, right_coefficient in right.items():
            degree = left_degree + right_degree
            result[degree] = result.get(degree, Fraction(0)) + left_coefficient * right_coefficient
    return clean(result)


def power(poly: Poly, exponent: int) -> Poly:
    require(exponent >= 0, "negative exponent")
    result: Poly = {0: Fraction(1)}
    base = poly
    while exponent:
        if exponent & 1:
            result = mul(result, base)
        exponent >>= 1
        if exponent:
            base = mul(base, base)
    return result


def scale(poly: Poly, scalar: Fraction | int) -> Poly:
    scalar = Fraction(scalar)
    if not scalar:
        return {}
    return {degree: scalar * coefficient for degree, coefficient in poly.items()}


def shift(poly: Poly, degree: int) -> Poly:
    require(degree >= 0, "negative polynomial shift")
    return {old_degree + degree: coefficient for old_degree, coefficient in poly.items()}


def order(poly: Poly) -> int:
    require(bool(poly), "zero polynomial has no V-adic order")
    return min(poly)


def degree(poly: Poly) -> int:
    require(bool(poly), "zero polynomial has no degree")
    return max(poly)


@dataclass
class Scanner:
    text: str
    position: int = 0

    def skip_space(self) -> None:
        length = len(self.text)
        while self.position < length and self.text[self.position].isspace():
            self.position += 1

    def peek(self) -> str:
        self.skip_space()
        return self.text[self.position] if self.position < len(self.text) else ""

    def take(self, expected: str | None = None) -> str:
        self.skip_space()
        require(self.position < len(self.text), "unexpected end of expression")
        character = self.text[self.position]
        if expected is not None:
            require(character == expected, f"expected {expected!r}, found {character!r}")
        self.position += 1
        return character

    def integer(self) -> int:
        self.skip_space()
        start = self.position
        length = len(self.text)
        while self.position < length and self.text[self.position].isdigit():
            self.position += 1
        require(self.position > start, f"expected integer at offset {start}")
        return int(self.text[start:self.position])


class PullbackParser:
    """Recursive-descent parser evaluating x=(9/5)V^2 and y=V."""

    def __init__(self, text: str):
        self.scanner = Scanner(text)

    def parse(self) -> Poly:
        result = self.expression()
        require(self.scanner.peek() == "", f"trailing input at offset {self.scanner.position}")
        return result

    def expression(self) -> Poly:
        result = self.term()
        while True:
            token = self.scanner.peek()
            if token == "+":
                self.scanner.take()
                result = add(result, self.term())
            elif token == "-":
                self.scanner.take()
                result = add(result, neg(self.term()))
            else:
                return result

    def term(self) -> Poly:
        result = self.factor()
        while self.scanner.peek() == "*":
            self.scanner.take()
            result = mul(result, self.factor())
        return result

    def factor(self) -> Poly:
        token = self.scanner.peek()
        if token == "+":
            self.scanner.take()
            result = self.factor()
        elif token == "-":
            self.scanner.take()
            result = neg(self.factor())
        elif token == "(":
            self.scanner.take()
            result = self.expression()
            self.scanner.take(")")
        elif token == "x":
            self.scanner.take()
            result = {2: Fraction(9, 5)}
        elif token == "y":
            self.scanner.take()
            result = {1: Fraction(1)}
        elif token.isdigit():
            result = {0: Fraction(self.scanner.integer())}
        else:
            raise SpecializationError(
                f"unexpected token {token!r} at offset {self.scanner.position}"
            )
        if self.scanner.peek() == "^":
            self.scanner.take()
            result = power(result, self.scanner.integer())
        return result


def parse_pullback(text: str) -> Poly:
    return PullbackParser(text).parse()


def canonical_qpoly(poly: Poly) -> tuple[list[int], int, int]:
    """Return primitive Z[V] coefficients, common denominator, and content.

    The coefficient list is high degree first and has positive leading term.
    This normalization is only for a single Q[V] polynomial.
    """
    require(bool(poly), "cannot normalize zero polynomial")
    common_denominator = 1
    for coefficient in poly.values():
        common_denominator = math.lcm(common_denominator, coefficient.denominator)
    low = [
        int(poly.get(k, Fraction(0)) * common_denominator)
        for k in range(order(poly), degree(poly) + 1)
    ]
    content = 0
    for coefficient in low:
        content = math.gcd(content, abs(coefficient))
    require(content > 0, "zero integer content")
    low = [coefficient // content for coefficient in low]
    if low[-1] < 0:
        low = [-coefficient for coefficient in low]
    return list(reversed(low)), common_denominator, content


def qpoly_hash(poly: Poly) -> str:
    primitive_high, _, _ = canonical_qpoly(poly)
    payload = json.dumps(primitive_high, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest().upper()


def divide_by_v_power(poly: Poly, exponent: int) -> Poly:
    require(order(poly) >= exponent, "V-power does not divide polynomial")
    return {degree - exponent: coefficient for degree, coefficient in poly.items()}


def dense_fraction_low(poly: Poly) -> list[Fraction]:
    if not poly:
        return []
    return [poly.get(k, Fraction(0)) for k in range(degree(poly) + 1)]


def trim_low(poly: list[Fraction]) -> list[Fraction]:
    while poly and not poly[-1]:
        poly.pop()
    return poly


def divmod_qpoly(dividend: Poly, divisor: Poly) -> tuple[Poly, Poly]:
    require(bool(divisor), "division by zero polynomial")
    remainder = dense_fraction_low(dividend)
    divisor_low = dense_fraction_low(divisor)
    divisor_degree = len(divisor_low) - 1
    divisor_lead = divisor_low[-1]
    quotient = [Fraction(0)] * max(0, len(remainder) - divisor_degree)
    while remainder and len(remainder) - 1 >= divisor_degree:
        offset = len(remainder) - 1 - divisor_degree
        scalar = remainder[-1] / divisor_lead
        quotient[offset] = scalar
        for index, coefficient in enumerate(divisor_low):
            remainder[index + offset] -= scalar * coefficient
        trim_low(remainder)
    return (
        {k: value for k, value in enumerate(quotient) if value},
        {k: value for k, value in enumerate(remainder) if value},
    )


def fp_trim(poly: list[int], prime: int) -> list[int]:
    result = [coefficient % prime for coefficient in poly]
    while result and result[-1] == 0:
        result.pop()
    return result


def fp_divmod(dividend: list[int], divisor: list[int], prime: int) -> tuple[list[int], list[int]]:
    dividend = fp_trim(dividend, prime)
    divisor = fp_trim(divisor, prime)
    require(bool(divisor), "finite-field division by zero")
    quotient = [0] * max(0, len(dividend) - len(divisor) + 1)
    inverse = pow(divisor[-1], -1, prime)
    while dividend and len(dividend) >= len(divisor):
        offset = len(dividend) - len(divisor)
        scalar = dividend[-1] * inverse % prime
        quotient[offset] = scalar
        for index, coefficient in enumerate(divisor):
            dividend[index + offset] = (
                dividend[index + offset] - scalar * coefficient
            ) % prime
        dividend = fp_trim(dividend, prime)
    return fp_trim(quotient, prime), dividend


def fp_gcd(left: list[int], right: list[int], prime: int) -> list[int]:
    left = fp_trim(left, prime)
    right = fp_trim(right, prime)
    while right:
        _, remainder = fp_divmod(left, right, prime)
        left, right = right, remainder
    if not left:
        return []
    inverse = pow(left[-1], -1, prime)
    return fp_trim([inverse * coefficient for coefficient in left], prime)


def qpoly_mod_prime(poly: Poly, prime: int) -> list[int]:
    require(bool(poly), "cannot reduce zero polynomial")
    result: list[int] = []
    for coefficient in dense_fraction_low(poly):
        require(coefficient.denominator % prime != 0, "bad reduction denominator")
        result.append(
            coefficient.numerator
            * pow(coefficient.denominator, -1, prime)
            % prime
        )
    return fp_trim(result, prime)


def constant_ratio(left: Poly, right: Poly) -> Fraction | None:
    """Return c when left=c*right, otherwise None."""
    if not left or not right or set(left) != set(right):
        return None
    witness_degree = next(iter(right))
    ratio = left[witness_degree] / right[witness_degree]
    return ratio if all(left[k] == ratio * right[k] for k in right) else None


def canonical_global_integer_polynomial(coefficients: dict[int, Poly]) -> tuple[dict[int, dict[int, int]], int, int]:
    """Clear all rational scalar denominators and remove integer content."""
    common_denominator = 1
    for poly in coefficients.values():
        for coefficient in poly.values():
            common_denominator = math.lcm(common_denominator, coefficient.denominator)
    integer_coefficients: dict[int, dict[int, int]] = {}
    content = 0
    for x_degree, poly in coefficients.items():
        target: dict[int, int] = {}
        for v_degree, coefficient in poly.items():
            value = int(coefficient * common_denominator)
            require(Fraction(value, common_denominator) == coefficient, "bad denominator clear")
            if value:
                target[v_degree] = value
                content = math.gcd(content, abs(value))
        integer_coefficients[x_degree] = target
    require(content > 0, "global polynomial is zero")
    for poly in integer_coefficients.values():
        for v_degree in list(poly):
            poly[v_degree] //= content
    leading_poly = integer_coefficients[max(integer_coefficients)]
    leading_value = leading_poly[max(leading_poly)]
    if leading_value < 0:
        for poly in integer_coefficients.values():
            for v_degree in list(poly):
                poly[v_degree] = -poly[v_degree]
    return integer_coefficients, common_denominator, content


def coefficient_bytes(poly: dict[int, int]) -> bytes:
    lines = [b"ZV-DESC-V1\n"]
    if poly:
        for v_degree in sorted(poly, reverse=True):
            lines.append(f"{v_degree}:{poly[v_degree]}\n".encode("ascii"))
    return b"".join(lines)


def global_hash(coefficients: dict[int, dict[int, int]]) -> str:
    digest = hashlib.sha256()
    digest.update(b"ZXV-DESC-V1\n")
    max_x = max(coefficients)
    for x_degree in range(max_x, -1, -1):
        digest.update(f"X:{x_degree}\n".encode("ascii"))
        poly = coefficients.get(x_degree, {})
        for v_degree in sorted(poly, reverse=True):
            digest.update(f"{v_degree}:{poly[v_degree]}\n".encode("ascii"))
        digest.update(b"ENDX\n")
    return digest.hexdigest().upper()


def archive_member_hashes(path: Path) -> dict[str, str]:
    """Hash relevant members in one pass and key them by relative name."""
    relevant: dict[str, str] = {}
    with tarfile.open(path, "r:gz") as archive:
        for member in archive:
            if not member.isfile():
                continue
            relative = member.name.split("PolQ5Gundlach-7/", 1)[-1]
            if relative == "DenQ5Gund7" or re.fullmatch(r"NumPhi/numphi(?:[1-9]|[1-4][0-9]|50)", relative):
                stream = archive.extractfile(member)
                require(stream is not None, f"cannot read archive member {member.name}")
                digest = hashlib.sha256()
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
                relevant[relative] = digest.hexdigest().upper()
    require(len(relevant) == 51, f"expected 51 relevant archive members, got {len(relevant)}")
    return relevant


def specialize(database: Path, archive: Path | None) -> dict[str, object]:
    require(len(PHI_U_EXPONENTS) == 50, "bad Tab exponent count")
    require(database.is_dir(), f"database directory not found: {database}")
    den_path = database / "DenQ5Gund7"
    require(den_path.is_file(), "missing DenQ5Gund7")

    source_hashes: dict[str, str] = {}
    den_text = den_path.read_text(encoding="ascii")
    source_hashes["DenQ5Gund7"] = hashlib.sha256(den_text.encode("ascii")).hexdigest().upper()
    denominator = parse_pullback(den_text)
    require(order(denominator) == 28 and degree(denominator) == 64, "unexpected denominator pullback")

    numerator_pullbacks: list[Poly] = []
    numerator_metadata: list[dict[str, object]] = []
    for index in range(1, 51):
        relative = f"NumPhi/numphi{index}"
        path = database / relative
        require(path.is_file(), f"missing {relative}")
        raw = path.read_bytes()
        source_hashes[relative] = hashlib.sha256(raw).hexdigest().upper()
        text = raw.decode("ascii")
        pulled_back = parse_pullback(text)
        require(bool(pulled_back), f"zero pullback for {relative}")
        numerator_pullbacks.append(pulled_back)
        primitive, local_denominator, local_content = canonical_qpoly(pulled_back)
        numerator_metadata.append(
            {
                "index": index,
                "x_degree_in_phi": index - 1,
                "u_denominator_exponent": PHI_U_EXPONENTS[index - 1],
                "v_order": order(pulled_back),
                "v_degree": degree(pulled_back),
                "nonzero_terms": len(pulled_back),
                "primitive_coefficient_count_dense": len(primitive),
                "pullback_scalar_denominator": str(local_denominator),
                "pullback_integer_content_after_scalar_clear": str(local_content),
                "primitive_dense_high_to_low_sha256": qpoly_hash(pulled_back),
                "source_sha256": source_hashes[relative],
            }
        )

    if archive is not None:
        require(archive.is_file(), f"archive not found: {archive}")
        require(sha256_path(archive) == ARCHIVE_SHA256, "archive SHA-256 mismatch")
        archived = archive_member_hashes(archive)
        require(archived == source_hashes, "extracted database files differ from pinned archive")

    # Multiply Phi by D(V)^2 U(V)^4.  Since U=(9/5)V^2, this gives
    #   D^2 U^4 X^50 + sum N_i U^(4-e_i) X^(i-1).
    u = {2: Fraction(9, 5)}
    coefficients: dict[int, Poly] = {50: mul(mul(denominator, denominator), power(u, 4))}
    for index, (numerator, exponent) in enumerate(zip(numerator_pullbacks, PHI_U_EXPONENTS), start=1):
        coefficients[index - 1] = mul(numerator, power(u, 4 - exponent))

    common_v_order = min(order(poly) for poly in coefficients.values())
    coefficients = {
        x_degree: divide_by_v_power(poly, common_v_order)
        for x_degree, poly in coefficients.items()
    }

    # Saturation by D away from the already removed V factor.  D is a scalar
    # times V^28 Q36; the remaining non-boundary factor is Q36.  Recover it
    # canonically from D/V^28 and test its valuation in every coefficient.
    q36 = divide_by_v_power(denominator, 28)
    q36_valuations: dict[int, int] = {}
    divided_coefficients: dict[int, Poly] = {}
    min_q36_valuation = 10**9
    for x_degree, poly in coefficients.items():
        value = poly
        valuation = 0
        while degree(value) >= degree(q36):
            quotient, remainder = divmod_qpoly(value, q36)
            if remainder:
                break
            value = quotient
            valuation += 1
        q36_valuations[x_degree] = valuation
        min_q36_valuation = min(min_q36_valuation, valuation)
        divided_coefficients[x_degree] = value
    require(min_q36_valuation < 10**9, "failed Q36 valuation")
    if min_q36_valuation:
        # The loop divided each coefficient by its full valuation, so restore
        # any excess beyond the common valuation.
        normalized: dict[int, Poly] = {}
        for x_degree, fully_divided in divided_coefficients.items():
            normalized[x_degree] = mul(
                fully_divided,
                power(q36, q36_valuations[x_degree] - min_q36_valuation),
            )
        coefficients = normalized

    # The X^50 block is a nonzero scalar multiple of Q36^2.  A common
    # Q[V]-content must therefore share a factor with Q36.  The following
    # good-reduction gcd witness proves that the X^49 block shares none.
    leading_ratio = constant_ratio(coefficients[50], mul(q36, q36))
    require(leading_ratio is not None and leading_ratio != 0, "X^50 block is not scalar*Q36^2")
    gcd_prime = 101
    q36_mod = qpoly_mod_prime(q36, gcd_prime)
    x49_mod = qpoly_mod_prime(coefficients[49], gcd_prime)
    require(len(q36_mod) - 1 == 36, "Q36 degree drops modulo gcd witness prime")
    require(fp_gcd(q36_mod, x49_mod, gcd_prime) == [1], "Q36 and X^49 block have nontrivial gcd")

    integers, scalar_denominator, scalar_content = canonical_global_integer_polynomial(coefficients)
    require(scalar_denominator == 5**82, "unexpected global scalar denominator")
    require(scalar_content == 2**48 * 3**64, "unexpected global integer content")
    coefficient_metadata: list[dict[str, object]] = []
    total_terms = 0
    max_digits = 0
    for x_degree in range(50, -1, -1):
        poly = integers[x_degree]
        total_terms += len(poly)
        if poly:
            max_digits = max(max_digits, *(len(str(abs(value))) for value in poly.values()))
            v_order: int | None = min(poly)
            v_degree: int | None = max(poly)
        else:
            v_order = None
            v_degree = None
        coefficient_metadata.append(
            {
                "x_degree": x_degree,
                "v_order": v_order,
                "v_degree": v_degree,
                "nonzero_terms": len(poly),
                "canonical_sparse_sha256": hashlib.sha256(coefficient_bytes(poly)).hexdigest().upper(),
                "q36_valuation_before_common_saturation": q36_valuations[x_degree],
            }
        )

    source_manifest_payload = json.dumps(source_hashes, sort_keys=True, separators=(",", ":")).encode("ascii")
    source_manifest_hash = hashlib.sha256(source_manifest_payload).hexdigest().upper()
    require(source_manifest_hash == EXPECTED_SOURCE_MANIFEST_SHA256, "source member manifest hash mismatch")
    canonical_digest = global_hash(integers)
    require(canonical_digest == EXPECTED_CANONICAL_SHA256, "canonical specialization hash mismatch")
    require(total_terms == 4752, "unexpected canonical nonzero-term count")
    require(max(degree(poly) for poly in coefficients.values()) == 100, "unexpected canonical V-degree")
    require(max_digits == 755, "unexpected maximum coefficient length")
    result: dict[str, object] = {
        "schema": "beal-rm5-phi7-frey-specialization-v1",
        "status": "exact-specialization-only-not-a-factorization-or-rational-point-proof",
        "source": {
            "archive_expected_sha256": ARCHIVE_SHA256,
            "archive_verified_this_run": archive is not None,
            "relevant_member_count": len(source_hashes),
            "relevant_member_hash_manifest_sha256": source_manifest_hash,
        },
        "substitution": {"U": "(9/5)*V^2", "Y_database_variable": "V"},
        "formula": "D(V)^2*U(V)^4*Phi = D(V)^2*U(V)^4*X^50 + sum_i N_i(V)*U(V)^(4-e_i)*X^(i-1)",
        "denominator_pullback": {
            "v_order": order(denominator),
            "v_degree": degree(denominator),
            "nonzero_terms": len(denominator),
            "primitive_dense_high_to_low_sha256": qpoly_hash(denominator),
            "q36_primitive_dense_high_to_low_sha256": qpoly_hash(q36),
            "source_sha256": source_hashes["DenQ5Gund7"],
        },
        "numerator_pullbacks": numerator_metadata,
        "global_normalization": {
            "x_degree": 50,
            "v_degree": max(degree(poly) for poly in coefficients.values()),
            "common_v_factor_removed": common_v_order,
            "common_q36_factor_removed": min_q36_valuation,
            "scalar_denominator_cleared": str(scalar_denominator),
            "scalar_denominator_factorization": "5^82",
            "integer_content_removed": str(scalar_content),
            "integer_content_factorization": "2^48*3^64",
            "polynomial_content_over_QV": "1",
            "polynomial_content_certificate": {
                "x50_block": "nonzero scalar multiple of Q36(V)^2",
                "comparison_scalar": str(leading_ratio),
                "gcd_witness_prime": gcd_prime,
                "gcd_Q36_with_x49_mod_prime": "1",
                "q36_degree_preserved_mod_prime": 36,
            },
            "sign_rule": "coefficient of maximal V-degree in maximal X-degree is positive",
            "canonical_stream_format": "ZXV-DESC-V1; X blocks 50..0; nonzero V terms descending; decimal integers",
            "canonical_stream_sha256": canonical_digest,
            "total_nonzero_terms": total_terms,
            "maximum_decimal_coefficient_digits": max_digits,
            "coefficient_blocks": coefficient_metadata,
        },
        "open_items": [
            "factorization over Q(V) and Q(sqrt(5))(V)",
            "square-free/component/genus analysis",
            "K-rational lift and descent analysis",
            "rational points plus Branch-I perfect-power conditions",
            "independent certification of every third-party database coefficient",
        ],
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path, help="extracted PolQ5Gundlach-7 directory")
    parser.add_argument("--archive", type=Path, help="optional pinned .tar.gz for member-by-member linkage")
    parser.add_argument("--output", type=Path, help="write compact JSON certificate")
    arguments = parser.parse_args()
    try:
        result = specialize(arguments.database, arguments.archive)
    except (OSError, UnicodeError, SpecializationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output:
        arguments.output.write_text(payload, encoding="utf-8", newline="\n")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
