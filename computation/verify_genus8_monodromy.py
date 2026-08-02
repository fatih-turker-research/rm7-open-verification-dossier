#!/usr/bin/env python3
"""Verify the degree-50 projective local-monodromy and genus-8 calculation.

The finite-field permutation and Riemann--Hurwitz arithmetic are
self-contained.  The genus conclusion is deliberately labelled dependent on
the cited hypergeometric local-monodromy theorem and on identifying the
normalization of the pinned Phi_7 pullback with the projectivized J[7]-line
cover over P^1 minus {0,1,infinity}.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PRIME = 7
NON_SQUARE = 5
INFINITY = 49


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def pair(value: int) -> tuple[int, int]:
    require(0 <= value < 49, "bad F49 element")
    return value % 7, value // 7


def element(a: int, b: int) -> int:
    return (a % 7) + 7 * (b % 7)


def add(left: int, right: int) -> int:
    a, b = pair(left)
    c, d = pair(right)
    return element(a + c, b + d)


def negate(value: int) -> int:
    a, b = pair(value)
    return element(-a, -b)


def multiply(left: int, right: int) -> int:
    a, b = pair(left)
    c, d = pair(right)
    return element(a * c + NON_SQUARE * b * d, a * d + b * c)


def inverse(value: int) -> int:
    a, b = pair(value)
    norm = (a * a - NON_SQUARE * b * b) % 7
    require(norm != 0, "division by zero in F49")
    inv_norm = pow(norm, -1, 7)
    result = element(a * inv_norm, -b * inv_norm)
    require(multiply(value, result) == 1, "bad F49 inverse")
    return result


def divide(left: int, right: int) -> int:
    return multiply(left, inverse(right))


def mobius(matrix: tuple[int, int, int, int], point: int) -> int:
    a, b, c, d = matrix
    if point == INFINITY:
        return INFINITY if c == 0 else divide(a, c)
    numerator = add(multiply(a, point), b)
    denominator = add(multiply(c, point), d)
    return INFINITY if denominator == 0 else divide(numerator, denominator)


def permutation(matrix: tuple[int, int, int, int]) -> list[int]:
    image = [mobius(matrix, point) for point in range(50)]
    require(sorted(image) == list(range(50)), "matrix does not permute P1(F49)")
    return image


def cycle_lengths(image: list[int]) -> list[int]:
    seen = [False] * len(image)
    lengths = []
    for start in range(len(image)):
        if seen[start]:
            continue
        current = start
        length = 0
        while not seen[current]:
            seen[current] = True
            length += 1
            current = image[current]
        require(current == start, "bad permutation cycle")
        lengths.append(length)
    return sorted(lengths)


def find_nonsplit_order_five() -> tuple[int, int, int, int]:
    # Companion matrices [[0,-d],[1,t]], searched deterministically.
    for determinant in range(1, 49):
        for trace in range(49):
            matrix = (0, negate(determinant), 1, trace)
            if cycle_lengths(permutation(matrix)) == [5] * 10:
                return matrix
    raise VerificationError("no nonsplit order-five matrix found")


def computed_certificate(exceptional: dict) -> dict:
    order_five = find_nonsplit_order_five()
    order_three = (2, 0, 0, 1)  # x -> 2x; 2 has order 3 in F7^*.
    order_seven = (1, 1, 0, 1)  # x -> x+1 in characteristic 7.
    cycles = {
        "t=0_order5": cycle_lengths(permutation(order_five)),
        "t=infinity_order3": cycle_lengths(permutation(order_three)),
        "t=1_order7_unipotent": cycle_lengths(permutation(order_seven)),
    }
    require(cycles["t=0_order5"] == [5] * 10, "bad order-five cycle type")
    require(cycles["t=infinity_order3"] == [1, 1] + [3] * 16, "bad order-three cycle type")
    require(cycles["t=1_order7_unipotent"] == [1] + [7] * 7, "bad unipotent cycle type")

    degree = 50
    contributions = {
        key: degree - len(value)
        for key, value in cycles.items()
    }
    require(contributions == {
        "t=0_order5": 40,
        "t=infinity_order3": 32,
        "t=1_order7_unipotent": 42,
    }, "bad different contributions")
    total = sum(contributions.values())
    genus_numerator = -2 * degree + total + 2
    require(genus_numerator % 2 == 0, "nonintegral Riemann--Hurwitz genus")
    genus = genus_numerator // 2
    require(genus == 8, "unexpected genus")

    # Cross-check the independent exact polynomial-boundary certificate under
    # V=375*t/(t-1): t=0 -> V=0, t=infinity -> V=375, t=1 -> V=infinity.
    require(exceptional["V_equals_0"]["different_contribution"] == 40, "V=0 mismatch")
    require(exceptional["V_equals_375"]["normalized_different_contribution"] == 32, "V=375 mismatch")
    require(exceptional["V_equals_infinity"]["different_contribution"] == 42, "V=infinity mismatch")
    require(exceptional["consequences"]["rational_infinity_place"] is True, "missing rational infinity place")

    return {
        "schema": "beal-rm7-projective-monodromy-genus-v1",
        "status": "genus-8-dependent-on-explicitly-named-cover-identification-and-local-monodromy-inputs",
        "field": "F_49=F_7[w]/(w^2-5)",
        "degree": degree,
        "matrices_as_F49_indices": {
            "nonsplit_order5": list(order_five),
            "split_order3": list(order_three),
            "unipotent_order7": list(order_seven),
        },
        "cycle_lengths": cycles,
        "branch_parameter_map": {
            "formula": "V=375*t/(t-1)",
            "t=0": "V=0",
            "t=infinity": "V=375",
            "t=1": "V=infinity",
        },
        "different_contributions": contributions,
        "total_different": total,
        "riemann_hurwitz": "2g-2=-2*50+114",
        "genus": genus,
        "geometric_connectedness_input": "Q(V)-irreducibility plus the certified Q-rational unramified infinity place implies constant field Q",
        "dependencies": [
            "the Frey rank-two mod-7 local monodromy has orders 5, 3, and nontrivial unipotent order 7 at t=0, infinity, and 1",
            "the projectivized F49-line cover is finite etale away from t=0,1,infinity",
            "the normalization of the pinned Phi_7 pullback is this projective-line cover",
            "the pinned external Phi_7 source represents the intended Hilbert modular polynomial",
        ],
        "scope": "genus and branch-cycle calculation only; no K-rational-point enumeration",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    here = Path(__file__).resolve().parent
    parser.add_argument("certificate", nargs="?", type=Path, default=here / "genus8_monodromy_certificate.json")
    parser.add_argument("--exceptional", type=Path, default=here / "exceptional_fibers_certificate.json")
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args()
    try:
        exceptional = json.loads(args.exceptional.read_text(encoding="utf-8"))
        computed = computed_certificate(exceptional)
        payload = json.dumps(computed, indent=2, sort_keys=True) + "\n"
        if args.write_certificate:
            args.certificate.write_text(payload, encoding="utf-8", newline="\n")
            print(f"WROTE {args.certificate}")
        else:
            recorded = json.loads(args.certificate.read_text(encoding="utf-8"))
            require(recorded == computed, "recorded genus certificate differs")
            print("PASS: recorded projective-monodromy certificate matches")
        print("PASS: cycle types 5^10, 1^2*3^16, and 1*7^7 on P1(F49)")
        print("PASS: exact polynomial boundary contributions agree: 40+32+42=114")
        print("DEPENDENT CONCLUSION: the identified projective line cover has genus 8")
        print("OPEN: enumerate its K-rational points and verify companion/orientation conditions")
        return 0
    except (OSError, ValueError, VerificationError) as exc:
        print(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
