# Gate G0 evidence bundle

This directory contains reproducible evidence for TI-0 provenance and custody.

## Evidence files

- `source-verification.json`: observed and expected SHA-256 digests and sizes;
- `manifest-validation.json`: deterministic manifest-contract result;
- `scope-audit.json`: proof that TI-1 through TI-8 behavior is absent;
- `test-report.txt`: deterministic unit and integration test transcript;
- `environment.txt`: runtime and platform facts relevant to reproduction;
- `checksums.sha256`: digest of the evidence files;
- `gate-decision.json`: formal automated G0 result and limitations.

Raw experimental and documentary sources are not included. Reproduction
requires authorized local copies matching the canonical manifest.

