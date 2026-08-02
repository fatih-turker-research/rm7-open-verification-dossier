#!/usr/bin/env python3
"""Verify Branch-I local RM(7) pullback certificates.

This verifier checks three complete split-prime scans and the exact Newton
edge at V=infinity.  With --source it reconstructs the canonical pullback
from the pinned Milio files, binds every stored finite-field fiber to that
source, and independently checks the infinity degree/leading-coefficient
data.

The result is a necessary local sieve and a local-solubility audit.  It is
not a rational-point theorem and does not eliminate Branch I.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path


EXPECTED_SCANS = {
    11: {
        "sha256": "AABDB2588519B612CD70325E4DEE839C160B659B79DCA9014EEB9CB967473440",
        "sqrt5": [4, 7],
        "allowed": [2, 3, 5, 6, 8, 9, 10],
        "excluded": [4, 7],
    },
    29: {
        "sha256": "E9C83D812497D91D1254660ADBAAA6BB2C0E745A18D03A2B181E509E6502AA1D",
        "sqrt5": [11, 18],
        "allowed": [1, 3, 4, 5, 6, 8, 10, 11, 12, 14, 15, 16, 21, 24, 26],
        "excluded": [2, 7, 9, 13, 17, 18, 19, 20, 22, 23, 25, 28],
    },
    31: {
        "sha256": "43BF89A3164428FFABF94B32177E47E73D068E9E353BF6260B4114539088CEC3",
        "sqrt5": [6, 25],
        "allowed": [1, 2, 12, 13, 14, 15, 19, 20, 21, 22, 26, 28, 30],
        "excluded": [4, 5, 6, 7, 8, 9, 10, 11, 16, 17, 18, 23, 24, 25, 27, 29],
    },
}

SOURCE_MANIFEST_SHA256 = "CB9F8AA7B7F33DD34895A201C4261B6636B69F20C8EAFAA393905072E5ECBE38"
V_DEGREES_X0_TO_X50 = [
    100, 99, 99, 99, 98, 98, 98, 98, 97, 97, 97, 96, 96, 96,
    96, 95, 95, 95, 94, 94, 94, 94, 93, 93, 93, 92, 92, 92,
    92, 91, 91, 91, 90, 90, 90, 90, 89, 89, 89, 88, 88, 88,
    88, 87, 87, 87, 86, 86, 86, 86, 72,
]
L49 = -8418174737738920163861301581285423746181953125
L50 = 20429981985896891148023698364161138916015625
FORCED_C_PRIMES_AUDITED = [2, 7, 19, 71, 79, 89, 131]


class Failure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Failure(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def trim(poly: list[int]) -> list[int]:
    poly = poly[:]
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def sub(left: list[int], right: list[int], p: int) -> list[int]:
    size = max(len(left), len(right))
    return trim([
        ((left[i] if i < len(left) else 0) -
         (right[i] if i < len(right) else 0)) % p
        for i in range(size)
    ])


def divmod_poly(dividend: list[int], divisor: list[int], p: int) -> tuple[list[int], list[int]]:
    dividend = trim([value % p for value in dividend])
    divisor = trim([value % p for value in divisor])
    require(divisor != [0], "division by zero polynomial")
    if len(dividend) < len(divisor):
        return [0], dividend
    quotient = [0] * (len(dividend) - len(divisor) + 1)
    inverse = pow(divisor[-1], -1, p)
    while dividend != [0] and len(dividend) >= len(divisor):
        shift = len(dividend) - len(divisor)
        scalar = dividend[-1] * inverse % p
        quotient[shift] = scalar
        for index, coefficient in enumerate(divisor):
            dividend[index + shift] = (
                dividend[index + shift] - scalar * coefficient
            ) % p
        dividend = trim(dividend)
    return trim(quotient), dividend


def mod_poly(poly: list[int], modulus: list[int], p: int) -> list[int]:
    return divmod_poly(poly, modulus, p)[1]


def mulmod(left: list[int], right: list[int], modulus: list[int], p: int) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] = (result[i + j] + a * b) % p
    return mod_poly(result, modulus, p)


def powmod_poly(base: list[int], exponent: int, modulus: list[int], p: int) -> list[int]:
    result = [1]
    while exponent:
        if exponent & 1:
            result = mulmod(result, base, modulus, p)
        base = mulmod(base, base, modulus, p)
        exponent >>= 1
    return result


def gcd_poly(left: list[int], right: list[int], p: int) -> list[int]:
    left, right = trim(left), trim(right)
    while right != [0]:
        left, right = right, mod_poly(left, right, p)
    inverse = pow(left[-1], -1, p)
    return [(value * inverse) % p for value in left]


def derivative(poly: list[int], p: int) -> list[int]:
    return trim([(index * poly[index]) % p for index in range(1, len(poly))])


def frobenius_gcd_degree(poly: list[int], p: int, power: int) -> int:
    xpoly = [0, 1]
    value = xpoly
    for _ in range(power):
        value = powmod_poly(value, p, poly, p)
    return len(gcd_poly(sub(value, xpoly, p), poly, p)) - 1


def reachable_unit_v(p: int) -> set[int]:
    """Brute-force the exact nonzero A,B,C residue image."""
    inverse_375 = pow(375 % p, -1, p)
    del inverse_375  # Its existence is the relevant assertion here.
    image: set[int] = set()
    for a in range(1, p):
        a3 = pow(a, 3, p)
        for b in range(1, p):
            b5 = pow(b, 5, p)
            for c in range(1, p):
                c7 = pow(c, 7, p)
                if (a3 + b5 - c7) % p == 0:
                    image.add(375 * b5 * pow(c7, -1, p) % p)
    return image


def verify_scan(path: Path, p: int, expected: dict[str, object]) -> dict[str, object]:
    require(sha256(path) == expected["sha256"], f"scan SHA mismatch for p={p}")
    data = json.loads(path.read_text(encoding="utf-8"))
    require(data["p"] == p, f"wrong prime in {path}")
    require(data["sqrt5_roots"] == expected["sqrt5"], f"sqrt(5) roots mismatch for p={p}")
    records = {record["V"]: record for record in data["records"]}
    require(set(records) == set(range(p)), f"incomplete V scan for p={p}")
    for v, record in records.items():
        if record["status"] != "ok":
            continue
        poly = record["coefficients_low_to_high"]
        require(len(poly) == 51 and poly[-1] == 1, f"non-monic degree-50 fiber p={p}, V={v}")
        repeated = len(gcd_poly(poly, derivative(poly, p), p)) - 1
        linear = frobenius_gcd_degree(poly, p, 1)
        quadratic = frobenius_gcd_degree(poly, p, 2)
        require(repeated == record["squarefree_gcd_degree"], f"derivative gcd mismatch p={p}, V={v}")
        require(linear == record["linear_factor_total_degree"], f"linear gcd mismatch p={p}, V={v}")
        require(quadratic == record["factors_degree_dividing_2_total_degree"], f"quadratic gcd mismatch p={p}, V={v}")

    boundary = {0, 375 % p}
    unit_values = set(range(p)) - boundary
    reachable = reachable_unit_v(p)
    require(reachable == unit_values, f"Branch-I unit residue image is not full for p={p}")
    allowed = sorted(v for v in unit_values if records[v]["status"] == "ok" and records[v]["linear_factor_total_degree"] > 0)
    excluded = sorted(v for v in unit_values if records[v]["status"] == "ok" and records[v]["linear_factor_total_degree"] == 0)
    bad = sorted(v for v in unit_values if records[v]["status"] != "ok")
    require(allowed == expected["allowed"], f"allowed set mismatch p={p}")
    require(excluded == expected["excluded"], f"excluded set mismatch p={p}")
    require(not bad and set(allowed) | set(excluded) == unit_values, f"uncovered unit values p={p}")
    return {"p": p, "allowed": allowed, "excluded": excluded, "unit_total": len(unit_values)}


def verify_infinity_metadata() -> None:
    require(len(V_DEGREES_X0_TO_X50) == 51, "wrong degree vector length")
    weights = [7 * degree + 98 * x_degree for x_degree, degree in enumerate(V_DEGREES_X0_TO_X50)]
    maximum = max(weights)
    require(maximum == 5404, "unexpected steep-edge weight")
    require([i for i, value in enumerate(weights) if value == maximum] == [49, 50], "steep edge must contain exactly X^49 and X^50")
    require(L49 == -(3**86) * (5**7), "L49 factorization mismatch")
    require(L50 == (3**60) * (5**14) * (281**2), "L50 factorization mismatch")
    require((-L49) * (5**7) * (281**2) == (3**26) * L50, "steep root ratio mismatch")
    for q in FORCED_C_PRIMES_AUDITED:
        require(L49 % q and L50 % q, f"bad steep leading coefficient at q={q}")


def load_specializer(path: Path):
    module_name = "branch1_source_specializer"
    spec = importlib.util.spec_from_file_location(module_name, path)
    require(spec is not None and spec.loader is not None, "cannot load specializer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def reconstruct_source(source: Path, specializer_path: Path) -> dict[int, dict[int, int]]:
    s = load_specializer(specializer_path)
    hashes: dict[str, str] = {}
    den_path = source / "DenQ5Gund7"
    hashes["DenQ5Gund7"] = sha256(den_path)
    denominator = s.parse_pullback(den_path.read_text(encoding="ascii"))
    numerators = []
    for index in range(1, 51):
        relative = f"NumPhi/numphi{index}"
        path = source / relative
        hashes[relative] = sha256(path)
        numerators.append(s.parse_pullback(path.read_text(encoding="ascii")))
    manifest = hashlib.sha256(json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest().upper()
    require(manifest == SOURCE_MANIFEST_SHA256, "source member manifest mismatch")

    u = {2: s.Fraction(9, 5)}
    coefficients = {50: s.mul(s.mul(denominator, denominator), s.power(u, 4))}
    for index, (numerator, exponent) in enumerate(zip(numerators, s.PHI_U_EXPONENTS), start=1):
        coefficients[index - 1] = s.mul(numerator, s.power(u, 4 - exponent))
    common_v_order = min(s.order(poly) for poly in coefficients.values())
    require(common_v_order == 64, "source V-saturation mismatch")
    coefficients = {degree: s.divide_by_v_power(poly, common_v_order) for degree, poly in coefficients.items()}
    integers, scalar_denominator, scalar_content = s.canonical_global_integer_polynomial(coefficients)
    require(scalar_denominator == 5**82, "source scalar denominator mismatch")
    require(scalar_content == 2**48 * 3**64, "source scalar content mismatch")
    degrees = [max(integers[i]) for i in range(51)]
    require(degrees == V_DEGREES_X0_TO_X50, "source infinity degree vector mismatch")
    require(integers[49][86] == L49 and integers[50][72] == L50, "source steep leading coefficients mismatch")
    return integers


def bind_scans_to_source(base: Path, integers: dict[int, dict[int, int]]) -> None:
    for p in EXPECTED_SCANS:
        data = json.loads((base / f"complete_p{p}_scan.json").read_text(encoding="utf-8"))
        for record in data["records"]:
            if record["status"] != "ok":
                continue
            v = record["V"]
            values = []
            for x_degree in range(51):
                value = sum(coefficient * pow(v, v_degree, p) for v_degree, coefficient in integers[x_degree].items()) % p
                values.append(value)
            require(values[50] != 0, f"source leading coefficient vanishes p={p}, V={v}")
            inverse = pow(values[50], -1, p)
            monic = [(value * inverse) % p for value in values]
            require(monic == record["coefficients_low_to_high"], f"source fiber mismatch p={p}, V={v}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--source", type=Path, help="optional extracted pinned PolQ5Gundlach-7 directory")
    parser.add_argument(
        "--specializer",
        type=Path,
        default=Path(__file__).resolve().with_name("specialize_phi7.py"),
    )
    arguments = parser.parse_args()
    try:
        summaries = []
        for p, expected in EXPECTED_SCANS.items():
            summaries.append(verify_scan(arguments.base / f"complete_p{p}_scan.json", p, expected))
        verify_infinity_metadata()
        if arguments.source:
            integers = reconstruct_source(arguments.source, arguments.specializer)
            bind_scans_to_source(arguments.base, integers)
    except (OSError, UnicodeError, ValueError, Failure) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS: Branch-I local certificates verified")
    for summary in summaries:
        print(f"  p={summary['p']}: allowed {len(summary['allowed'])}/{summary['unit_total']}; excluded={summary['excluded']}")
    print("  Branch-I unit residue image is full at all three primes")
    print("  infinity steep edge: indices 49,50; weights 5404; simple Q_q branch certified")
    print(f"  source linkage: {'PASS' if arguments.source else 'not requested'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
