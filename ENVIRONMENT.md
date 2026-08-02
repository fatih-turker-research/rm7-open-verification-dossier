# Execution environment

The release was assembled and rechecked on 2 August 2026 under Windows/PowerShell.

Recorded primary runtimes:

- Python 3.14.6 for the current full verification run;
- Node.js 24.14.0 for the independent BigInt specialization check.

The bundled offline certificate verifiers use only the Python standard library. `verify_package.py` is intended to run under Python 3.11 or newer.

Source-linked reconstruction requires a separately obtained and hash-checked `PolQ5Gundlach-7` archive. No environment file can remove the mathematical dependency on that third-party source or replace independent expert review.

