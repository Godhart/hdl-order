# Testing hdl-order 0.3.0

## Quick run

```bash
python -m venv .venv
source .venv/bin/activate
./run-tests.sh
```

or manually:

```bash
pip install -e .
pip install -r requirements-test.txt
pytest -v
```

## Coverage of the suite

The tests exercise:

1. VHDL entity/package/package-body/architecture indexing.
2. VHDL case-insensitive duplicate detection.
3. Architecture duplicate key `(library, entity, architecture)`.
4. SV module/interface/package/program indexing and case sensitivity.
5. Same design-unit name in different libraries.
6. Recursive `.vh`/`.svh` includes.
7. `ifdef`, `ifndef`, `elsif`, `else`, `endif`.
8. `define` and `undef`.
9. `-D NAME` and `-D NAME=VALUE` parsing.
10. Simple macro-expanded `include`.
11. Include lookup through `-I`.
12. Missing include handling.
13. Include-cycle detection.
14. Independent macro context for separate compilation units.
15. Cross-library VHDL compile order A -> B -> A.
16. Headers excluded from compilation units.
17. Explicit TOML compile dependencies.
18. Reports: `--check`, `--symbols`, `--deps`, `--headers`, `--explain`.
19. Output formats: plain, JSON, CSV, ModelSim.
20. CLI exit codes.

One test is deliberately marked `xfail`: macro-generated SV design-unit declarations are
a documented 0.3 limitation. It should show as XFAIL, not FAIL.

## Expected result

A healthy 0.3.0 run should end with all normal tests passing and the documented
limitation reported as XFAIL. If any ordinary test fails, preserve the full pytest
traceback; it should identify whether the failure is in hdl-order itself or in an
assumption about the installed VUnit version.
