# ADR 0008 — hdl-order 0.8.0: wrapper source separation

Accepted 2026-10-08. The installed analyzer remains the CLI/backend dependency.
TWYLT wrapper contracts and business handlers belong to the corresponding tool;
shared input/models and analysis helpers live in shared/hdl_common, resolved via
__file__. No additional wrapper package build/install is required. Remove the
internal twylt_api operation registry from the backend distribution.

Use installed TWYLT >=1.1.1 cooperative guardrails, including file transport.
When enabled, declared roots/config/include directories resolve within workspace;
root trees are preflighted before analysis. Disabled policy keeps cwd semantics.
This preflight is not an OS sandbox of parser-internal or HDL-referenced file I/O.
Backend analysis remains author-owned code; stronger isolation belongs to the OS.

Whole tools/shared source must accompany the launcher. Install hdl-order backend
separately, use distinct processes for different wrapper versions. Updating the
backend producer version changes the manifest fingerprint, so regenerate its example.
Existing CLI/backend tests are retained; one macro-parser xfail remains unchanged.
