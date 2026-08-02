#!/usr/bin/env python3
"""Exact cycle and Riemann--Hurwitz certificate for the RM(7) line cover.

This verifier checks only the finite-field/projective-line calculation.  The
identification of this permutation cover with the normalization of the
published Gundlach pullback is a mathematical dependency documented in
../GENUS8_MONODROMY_AUDIT.md and ../RM7_COVER_IDENTIFICATION.md; it is not
inferred from the cycle computation itself.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


P = 7


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@dataclass(frozen=True, order=True)
class F49:
    """a+b*w in F_7[w]/(w^2-5)."""

    a: int
    b: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "a", self.a % P)
        object.__setattr__(self, "b", self.b % P)

    def __add__(self, other: object) -> "F49":
        other = coerce(other)
        return F49(self.a + other.a, self.b + other.b)

    __radd__ = __add__

    def __neg__(self) -> "F49":
        return F49(-self.a, -self.b)

    def __sub__(self, other: object) -> "F49":
        return self + (-coerce(other))

    def __rsub__(self, other: object) -> "F49":
        return coerce(other) - self

    def __mul__(self, other: object) -> "F49":
        other = coerce(other)
        return F49(self.a * other.a + 5 * self.b * other.b, self.a * other.b + self.b * other.a)

    __rmul__ = __mul__

    def __pow__(self, exponent: int) -> "F49":
        if exponent < 0:
            return self.inverse() ** (-exponent)
        result = F49(1)
        base = self
        while exponent:
            if exponent & 1:
                result *= base
            base *= base
            exponent >>= 1
        return result

    def inverse(self) -> "F49":
        require(self != F49(0), "division by zero")
        norm = (self.a * self.a - 5 * self.b * self.b) % P
        scalar = pow(norm, -1, P)
        return F49(self.a * scalar, -self.b * scalar)

    def __truediv__(self, other: object) -> "F49":
        return self * coerce(other).inverse()


def coerce(value: object) -> F49:
    if isinstance(value, F49):
        return value
    require(isinstance(value, int), f"cannot coerce {type(value)}")
    return F49(value)


Point = F49 | None
Matrix = tuple[F49, F49, F49, F49]


def mobius(matrix: Matrix, point: Point) -> Point:
    a, b, c, d = matrix
    if point is None:
        return None if c == F49(0) else a / c
    denominator = c * point + d
    return None if denominator == F49(0) else (a * point + b) / denominator


def cycles(matrix: Matrix, points: list[Point]) -> list[int]:
    unseen = set(points)
    result: list[int] = []
    while unseen:
        start = min(unseen, key=lambda x: (x is None, x or F49(0)))
        current = start
        length = 0
        while True:
            require(current in unseen, "permutation cycle failed to close")
            unseen.remove(current)
            length += 1
            current = mobius(matrix, current)
            if current == start:
                break
        result.append(length)
    return sorted(result)


def matrix_det(matrix: Matrix) -> F49:
    a, b, c, d = matrix
    return a * d - b * c


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    w = F49(0, 1)
    require(w * w == F49(5), "bad F49 presentation")
    require(all(F49(a, b) ** 48 == F49(1) for a in range(7) for b in range(7) if (a, b) != (0, 0)), "bad F49 multiplicative group")
    points: list[Point] = [F49(a, b) for a in range(7) for b in range(7)] + [None]
    require(len(set(points)) == 50, "P1(F49) must have 50 points")

    # Companion representatives of the projective conjugacy classes supplied
    # by the hypergeometric local monodromy.  1/2 = 4 in F_7.
    trace5 = (w - 1) * 4
    matrices: dict[str, Matrix] = {
        "t=0_order5": (F49(0), F49(-1), F49(1), trace5),
        "t=infinity_order3": (F49(0), F49(-1), F49(1), F49(-1)),
        "t=1_unipotent_order7": (F49(1), F49(1), F49(0), F49(1)),
    }
    for name, matrix in matrices.items():
        require(matrix_det(matrix) == F49(1), f"{name}: determinant is not 1")

    cycle_data = {name: cycles(matrix, points) for name, matrix in matrices.items()}
    require(cycle_data["t=0_order5"] == [5] * 10, "wrong order-5 cycle type")
    require(cycle_data["t=infinity_order3"] == [1, 1] + [3] * 16, "wrong order-3 cycle type")
    require(cycle_data["t=1_unipotent_order7"] == [1] + [7] * 7, "wrong unipotent cycle type")

    # V=375*t/(t-1): t=0, infinity, 1 map to V=0, 375, infinity.
    v_cycles = {
        "V=0": cycle_data["t=0_order5"],
        "V=375": cycle_data["t=infinity_order3"],
        "V=infinity": cycle_data["t=1_unipotent_order7"],
    }
    contributions = {place: sum(length - 1 for length in data) for place, data in v_cycles.items()}
    require(contributions == {"V=0": 40, "V=375": 32, "V=infinity": 42}, "wrong different contributions")
    degree = 50
    total_different = sum(contributions.values())
    twice_genus_minus_two = -2 * degree + total_different
    require(twice_genus_minus_two % 2 == 0, "Riemann--Hurwitz parity failure")
    genus = (twice_genus_minus_two + 2) // 2
    require(genus == 8, "unexpected genus")

    payload = {
        "schema": "rm7-projective-monodromy-genus-v1",
        "field": "F7[w]/(w^2-5)",
        "degree": degree,
        "parameter_change": "V=375*t/(t-1)",
        "cycle_types": {place: data for place, data in v_cycles.items()},
        "different_contributions": contributions,
        "total_different": total_different,
        "riemann_hurwitz": f"2g-2=-2*{degree}+{total_different}={twice_genus_minus_two}",
        "genus": genus,
        "status": "exact permutation calculation; pullback-cover identification is an external theorem dependency",
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    payload["canonical_payload_sha256"] = hashlib.sha256(canonical).hexdigest().upper()
    if args.output:
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print("PASS rm7 projective monodromy genus certificate")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
