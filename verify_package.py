#!/usr/bin/env python3
"""Fail-closed package hash and offline-certificate verifier."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "SHA256SUMS.txt"
EXCLUDED = {"SHA256SUMS.txt"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def manifest_entries() -> dict[str, str]:
    if not MANIFEST.is_file():
        raise RuntimeError("SHA256SUMS.txt is missing")
    result: dict[str, str] = {}
    for line_number, raw in enumerate(MANIFEST.read_text(encoding="ascii").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            digest, relative = raw.split("  ", 1)
        except ValueError as exc:
            raise RuntimeError(f"malformed manifest line {line_number}") from exc
        if len(digest) != 64 or any(char not in "0123456789ABCDEF" for char in digest):
            raise RuntimeError(f"invalid digest on manifest line {line_number}")
        if relative in result:
            raise RuntimeError(f"duplicate manifest path: {relative}")
        if "\\" in relative or relative.startswith("/") or ".." in Path(relative).parts:
            raise RuntimeError(f"unsafe manifest path: {relative}")
        result[relative] = digest
    return result


def verify_hashes() -> None:
    expected = manifest_entries()
    actual = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and path.relative_to(ROOT).as_posix() not in EXCLUDED
    }
    missing = sorted(set(expected) - actual)
    unlisted = sorted(actual - set(expected))
    if missing or unlisted:
        raise RuntimeError(f"package inventory mismatch; missing={missing}, unlisted={unlisted}")
    for relative, expected_digest in expected.items():
        observed = sha256(ROOT / relative)
        if observed != expected_digest:
            raise RuntimeError(f"hash mismatch: {relative}")
    print(f"PASS manifest: {len(expected)} files")


def run_offline_checks() -> None:
    computation = ROOT / "computation"
    commands = [
        [sys.executable, "-B", "verify_exceptional_fibers_offline.py"],
        [sys.executable, "-B", "verify_genus8_monodromy.py"],
        [sys.executable, "-B", "verify_rm7_monodromy_genus.py"],
        [sys.executable, "-B", "verify_branch1_local_certificate.py"],
    ]
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=computation,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if completed.returncode:
            raise RuntimeError(
                f"offline check failed: {command[-1]}\n{completed.stdout}"
            )
        first_line = completed.stdout.splitlines()[0] if completed.stdout.splitlines() else "PASS"
        print(f"PASS offline: {command[-1]} :: {first_line}")


def main() -> int:
    try:
        verify_hashes()
        run_offline_checks()
    except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS package: hashes and bundled offline checks")
    print("SCOPE: this verifies files and finite computations, not the mathematical interpretation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

