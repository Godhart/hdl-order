# 0.8.0 — 2026-10-08

- Split TWYLT schemas and per-operation business handlers into their own tool files.
- Move genuinely shared wrapper models and analysis helpers to source shared/hdl_common.
- Import shared source via __file__, without building a wrapper-specific package.
- Use TWYLT >=1.1.1 guardrails for declared roots/config/include directories and transport.
- Preserve disabled-policy path semantics, backend installation and CLI behavior.
- Refresh manifest producer example and schemas; retain previous tests and add guarded deployment tests.
