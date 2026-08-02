# Reproduction transcript: RM(7) normalization and local audit

Date: 2 August 2026

Platform used for this addendum:

- Microsoft Windows NT 10.0.26200.0, 64-bit;
- Python 3.14.6;
- standard-library quick verifiers;
- python-flint 0.9.0 only for noncontrolling finite-field node probes.

All commands recorded below exited with status zero. `-OO` runs are included
to ensure that correctness does not depend on Python `assert` statements.

## 1. Exceptional and projective fibres

The full verifier requires the separately obtained, hash-pinned extracted
Milio database; it is not redistributed in this release.

```text
python -B computation/verify_exceptional_fibers.py --database PATH/PolQ5Gundlach-7
python -OO -B computation/verify_exceptional_fibers.py --database PATH/PolQ5Gundlach-7
```

Both modes returned:

```text
PASS: recorded exceptional-fibre certificate matches exact reconstruction
PASS V=0: H10^5 fibre, H10 irreducible, ten geometric e=5 points
PASS D=0: 49 square-free finite points plus one unramified infinity point
PASS V=infinity: seven e=7 points plus one Q-rational e=1 point
PASS V=375: normalized different is 32, not polynomial-discriminant order 58
CONSEQUENCE: existing Q(V)-irreducibility upgrades to geometric integrality
DEPENDENT: genus 8 follows only after identifying the normalization with the cover etale off the three boundary values
```

The archive-linked mode additionally passed:

```text
python -B computation/verify_exceptional_fibers.py --database PATH/PolQ5Gundlach-7 --archive PATH/PolQ5Gundlach-7.tar.gz
```

It verified archive SHA-256
`9A98249312F46FAF91A6F5D549A2C890EE1713D40A5C4CF9310C4B5819C5C226`
and source-member manifest SHA-256
`CB9F8AA7B7F33DD34895A201C4261B6636B69F20C8EAFAA393905072E5ECBE38`.

The compact dependency-free verifier also passed in normal and optimized
modes:

```text
python -B computation/verify_exceptional_fibers_offline.py
python -OO -B computation/verify_exceptional_fibers_offline.py
```

It recomputed the stored hashes, modular products, Rabin irreducibility tests,
Newton arithmetic, cycle degrees, different 114, and the conditional
Riemann--Hurwitz calculation.  It explicitly does not reconstruct \(F\) or
prove linkage to the external Milio database.

## 2. Projective monodromy and genus

Two implementations were run in normal and optimized modes:

```text
python -B computation/verify_genus8_monodromy.py
python -OO -B computation/verify_genus8_monodromy.py
python -B computation/verify_rm7_monodromy_genus.py
python -OO -B computation/verify_rm7_monodromy_genus.py
```

The first implementation returned:

```text
PASS: recorded projective-monodromy certificate matches
PASS: cycle types 5^10, 1^2*3^16, and 1*7^7 on P1(F49)
PASS: exact polynomial boundary contributions agree: 40+32+42=114
DEPENDENT CONCLUSION: the identified projective line cover has genus 8
OPEN: enumerate its K-rational points and verify companion/orientation conditions
```

The second independently enumerated the same 50 projective points and
reproduced canonical payload SHA-256

```text
D548DE2CEB8D52FA6C037F23247B3467D4219353A43C66A0B9F22391CCF27870
```

with

```text
V=0:        5^10,       different 40
V=375:      1^2 3^16,   different 32
V=infinity: 1 7^7,      different 42
2g-2=-2*50+114=14; g=8
```

## 3. Branch-I local certificate

```text
python -B computation/verify_branch1_local_certificate.py
python -OO -B computation/verify_branch1_local_certificate.py
```

Both modes returned:

```text
PASS: Branch-I local certificates verified
  p=11: allowed 7/9; excluded=[4, 7]
  p=29: allowed 15/27; excluded=[2, 7, 9, 13, 17, 18, 19, 20, 22, 23, 25, 28]
  p=31: allowed 13/29; excluded=[4, 5, 6, 7, 8, 9, 10, 11, 16, 17, 18, 23, 24, 25, 27, 29]
  Branch-I unit residue image is full at all three primes
  infinity steep edge: indices 49,50; weights 5404; simple Q_q branch certified
  source linkage: not requested
```

Normal and optimized source-linked modes also passed when invoked with
`--source PATH/PolQ5Gundlach-7`; each stored good fibre was compared
coefficient by coefficient with a fresh reconstruction.

## 4. Release verification

After regenerating `ARTIFACT_HASHES.sha256`, the following commands are the
controlling clean-release checks:

```text
python -B computation/verify_release.py
python -OO -B computation/verify_release.py
python -B computation/verify_release.py --full
```

The full mode additionally reran both explicitly bounded searches; it does not
turn either finite box into a global height bound.

The final archive was also extracted into a new directory and the quick
verifier was run there. Archive name and SHA-256 are recorded in the release
handoff and its `.sha256` sidecar.

## 5. Scope

These computations certify exact finite algebra and the transformation of a
hash-pinned external source. They do not independently regenerate the
upstream modular-polynomial interpolation, enumerate the genus-8
\(K\)-rational points, prove Branch I, solve \((3,5,7)\), or prove the full Beal
conjecture.
