#!/usr/bin/env python3
"""Standard-library verification of the two-fiber RM7 factor certificate.

Without --source this verifies the explicit finite-field factors, their
products, Rabin irreducibility, and the factor-degree subset-sum obstruction.
With --source it additionally re-parses all 50 external numerator files in a
two-component CRT ring and reconstructs both specialized Phi polynomials.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

TAB_PHI = [
    2, 3,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
    4, 4, 4, 4, 4, 4, 4,
    3, 2, 2, 1, 0,
]
if len(TAB_PHI) != 50:
    raise RuntimeError("internal Tab exponent table has wrong length")


class ModParser:
    """Evaluate the restricted GP integer-polynomial syntax modulo m."""

    __slots__ = ("s", "n", "i", "x", "y", "mod")

    def __init__(self, text: str, x: int, y: int, modulus: int):
        self.s, self.n, self.i = text, len(text), 0
        self.x, self.y, self.mod = x, y, modulus

    def skip(self) -> None:
        while self.i < self.n and self.s[self.i].isspace():
            self.i += 1

    def expression(self) -> int:
        out = self.term()
        while True:
            self.skip()
            if self.i >= self.n or self.s[self.i] not in "+-": return out
            op = self.s[self.i]
            self.i += 1
            rhs = self.term()
            out = (out + rhs if op == "+" else out - rhs) % self.mod

    def term(self) -> int:
        out = self.power()
        while True:
            self.skip()
            if self.i >= self.n or self.s[self.i] != "*": return out
            self.i += 1
            out = out * self.power() % self.mod

    def power(self) -> int:
        out = self.atom()
        self.skip()
        if self.i < self.n and self.s[self.i] == "^":
            self.i += 1
            self.skip()
            j = self.i
            while self.i < self.n and self.s[self.i].isdigit(): self.i += 1
            require(j < self.i, f"missing exponent at byte {self.i}")
            out = pow(out, int(self.s[j:self.i]), self.mod)
        return out

    def atom(self) -> int:
        self.skip()
        require(self.i < self.n, "unexpected end of polynomial")
        ch = self.s[self.i]
        if ch == "+": self.i += 1; return self.atom()
        if ch == "-": self.i += 1; return -self.atom() % self.mod
        if ch == "(":
            self.i += 1
            out = self.expression()
            self.skip()
            require(self.i < self.n and self.s[self.i] == ")", f"missing ')' at byte {self.i}")
            self.i += 1
            return out
        if ch == "x": self.i += 1; return self.x
        if ch == "y": self.i += 1; return self.y
        if ch.isdigit():
            j = self.i
            while self.i < self.n and self.s[self.i].isdigit(): self.i += 1
            return int(self.s[j:self.i]) % self.mod
        raise AssertionError(f"unexpected character {ch!r} at byte {self.i}")

    def parse(self) -> int:
        out = self.expression()
        self.skip()
        require(self.i == self.n, f"trailing polynomial input at byte {self.i}")
        return out


def is_prime(n: int) -> bool:
    if n < 2: return False
    if n % 2 == 0: return n == 2
    d = 3
    while d*d <= n:
        if n % d == 0: return False
        d += 2
    return True


def crt(residues: list[int], moduli: list[int]) -> tuple[int, int]:
    x, m = 0, 1
    for a, p in zip(residues, moduli, strict=True):
        require(is_prime(p) and m % p != 0, "CRT moduli must be distinct primes")
        x += m * (((a-x) * pow(m, -1, p)) % p)
        m *= p
    return x % m, m


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest().upper()


def trim(a: list[int]) -> list[int]:
    while len(a) > 1 and a[-1] == 0: a.pop()
    return a


def poly_sub(a: list[int], b: list[int], p: int) -> list[int]:
    return trim([
        ((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % p
        for i in range(max(len(a), len(b)))
    ])


def poly_divmod(a: list[int], b: list[int], p: int) -> tuple[list[int], list[int]]:
    a, b = trim(a[:]), trim(b[:])
    require(b != [0], "polynomial division by zero")
    if len(a) < len(b): return [0], a
    q = [0] * (len(a)-len(b)+1)
    inv = pow(b[-1], -1, p)
    while a != [0] and len(a) >= len(b):
        k, c = len(a)-len(b), a[-1]*inv % p
        q[k] = c
        for j, bj in enumerate(b): a[j+k] = (a[j+k]-c*bj) % p
        trim(a)
    return trim(q), a


def poly_mod(a: list[int], f: list[int], p: int) -> list[int]:
    return poly_divmod(a, f, p)[1]


def poly_mulmod(a: list[int], b: list[int], f: list[int], p: int) -> list[int]:
    c = [0] * (len(a)+len(b)-1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b): c[i+j] = (c[i+j]+ai*bj) % p
    return poly_mod(c, f, p)


def poly_powmod(a: list[int], e: int, f: list[int], p: int) -> list[int]:
    out = [1]
    while e:
        if e & 1: out = poly_mulmod(out, a, f, p)
        a = poly_mulmod(a, a, f, p)
        e >>= 1
    return out


def poly_gcd(a: list[int], b: list[int], p: int) -> list[int]:
    while b != [0]: a, b = b, poly_mod(a, b, p)
    inv = pow(a[-1], -1, p)
    return [z*inv % p for z in a]


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def mul(a: list[int], b: list[int], p: int) -> list[int]:
    c = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            c[i+j] = (c[i+j] + ai*bj) % p
    return trim(c)


def prime_divisors(n: int) -> list[int]:
    ans = []
    q = 2
    while q*q <= n:
        if n % q == 0:
            ans.append(q)
            while n % q == 0: n //= q
        q += 1
    if n > 1: ans.append(n)
    return ans


def rabin_irreducible(f: list[int], p: int) -> bool:
    f = trim([z % p for z in f])
    n = len(f)-1
    require(n >= 1 and f[-1] == 1, "Rabin input must be monic and nonconstant")
    x = [0, 1]
    xred = poly_powmod(x, 1, f, p)
    xp = xred
    states = {0: xred}
    for k in range(1, n+1):
        xp = poly_powmod(xp, p, f, p)
        states[k] = xp
    require(states[n] == xred, f"Frobenius identity failed in degree {n}")
    for q in prime_divisors(n):
        g = poly_gcd(poly_sub(states[n//q], xred, p), f, p)
        require(len(g)-1 == 0, f"Rabin gcd failed for n={n}, q={q}")
    return True


def subset_sums(degrees: list[int]) -> list[int]:
    sums = {0}
    for d in degrees:
        sums |= {x+d for x in list(sums)}
    return sorted(sums)


def reconstruct_from_source(cert: dict, source: Path) -> None:
    items = cert["certificates"]
    primes = [z["p"] for z in items]
    vvals = [z["V"] for z in items]
    uvals = [(9 * pow(5, -1, p) * v*v) % p for p, v in zip(primes, vvals, strict=True)]
    crt_v, modulus = crt(vvals, primes)
    crt_u, modulus2 = crt(uvals, primes)
    require(modulus == modulus2, "CRT modulus mismatch")

    denpath = source / "DenQ5Gund7"
    require(sha256(denpath) == cert["source_denominator_sha256"], "denominator hash mismatch")
    dencrt = ModParser(denpath.read_text("ascii"), crt_u, crt_v, modulus).parse()
    ncrt = []
    for i in range(1, 51):
        path = source / "NumPhi" / f"numphi{i}"
        require(sha256(path) == cert["source_numerator_sha256"][i-1], f"numphi{i} hash mismatch")
        ncrt.append(ModParser(path.read_text("ascii"), crt_u, crt_v, modulus).parse())

    for item in items:
        p, u, d = item["p"], item["U"], item["D"]
        require(u == crt_u % p, f"U mismatch mod {p}")
        require(d == dencrt % p and d != 0, f"D mismatch or zero mod {p}")
        d2inv = pow(d*d % p, -1, p)
        coeffs = [
            (ni % p) * d2inv * pow(pow(u, e, p), -1, p) % p
            for ni, e in zip(ncrt, TAB_PHI, strict=True)
        ] + [1]
        require(coeffs == item["phi_coefficients_low_to_high"], f"Phi coefficient mismatch mod {p}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "certificate",
        type=Path,
        nargs="?",
        default=Path(__file__).resolve().with_name("two_fiber_factor_certificate.json"),
        help="certificate JSON (default: the file beside this verifier)",
    )
    ap.add_argument("--source", type=Path)
    args = ap.parse_args()
    cert = json.loads(args.certificate.read_text(encoding="utf-8"))
    require(cert["schema"] == "rm7-phi-two-fiber-factor-certificate-v1", "schema mismatch")
    require(cert["tab_phi"] == TAB_PHI, "Tab exponent table mismatch")
    require([(z["p"], z["V"]) for z in cert["certificates"]] == [(11, 4), (659, 77)], "target mismatch")

    all_degree_sets = []
    for item in cert["certificates"]:
        p = item["p"]
        require(is_prime(p), f"p={p} is not prime")
        require(pow(5, (p-1)//2, p) == 1, f"p={p} is not split in Q(sqrt(5))")
        expected_u = 9 * pow(5, -1, p) * item["V"] * item["V"] % p
        require(item["U"] == expected_u, f"U=(9/5)V^2 mismatch mod {p}")
        require(item["U"] != 0 and item["D"] != 0, f"bad specialization p={p}")
        f = [z % p for z in item["phi_coefficients_low_to_high"]]
        require(len(f) == 51 and f[-1] == 1, f"Phi is not monic degree 50 mod {p}")
        product = [1]
        degrees = []
        seen = set()
        for factor in item["factors"]:
            g = [z % p for z in factor["coefficients_low_to_high"]]
            require(factor["multiplicity"] == 1, "unexpected multiplicity")
            require(len(g)-1 == factor["degree"] and g[-1] == 1, "bad factor encoding")
            key = tuple(g)
            require(key not in seen, "duplicate factor")
            seen.add(key)
            require(rabin_irreducible(g, p), "irreducibility verification failed")
            product = mul(product, g, p)
            degrees.append(len(g)-1)
        require(product == f, f"factor product mismatch mod {p}")
        require(sum(degrees) == 50, f"degree sum mismatch mod {p}")
        ss = subset_sums(degrees)
        all_degree_sets.append(set(ss))
        print(f"PASS p={p}, V={item['V']}: irreducible factor degrees {degrees}")
        print(f"PASS p={p}: possible generic factor degrees after specialization {ss}")

    intersection = sorted(set.intersection(*all_degree_sets))
    require(intersection == [0, 50], f"unexpected subset-sum intersection {intersection}")
    require(cert["generic_factor_degree_argument"]["intersection"] == intersection, "recorded intersection mismatch")
    print("PASS subset-sum intersection = {0,50}")
    print("PASS: no proper generic factor degree survives both good split specializations")

    if args.source is not None:
        reconstruct_from_source(cert, args.source)
        print("PASS: all 50 archive numerators independently re-parsed and both Phi fibers reconstructed")
    else:
        print("SKIP: archive reconstruction (supply --source PolQ5Gundlach-7)")

    print("LATER CERTIFICATES: normalization and exceptional/projective fibers")
    print("OPEN: companion/descent conditions and complete K-rational point determination")


if __name__ == "__main__":
    main()
