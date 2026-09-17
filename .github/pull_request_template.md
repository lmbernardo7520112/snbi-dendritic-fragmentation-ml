## Scope

- [ ] The change belongs to the currently authorized phase.
- [ ] TI-2 execution and TI-3 through TI-8 remain blocked.
- [ ] No raw or derived experimental data is committed.
- [ ] No frame decoding, pixel access, registration, calibration, label, dataset, baseline, or model behavior is introduced.
- [ ] Sandbox failure did not trigger an unsandboxed fallback.

## Evidence

- [ ] Tests pass locally.
- [ ] CI passes.
- [ ] Gate evidence has been updated when applicable.
- [ ] No secret, credential, or absolute local path is present.
- [ ] `/usr/bin/python3 -B scripts/check_repository_data.py` passes locally.
- [ ] `/usr/bin/python3 -B scripts/check_local_bootstrap.py` passes locally when bootstrap files are affected.

## Scientific invariants

- [ ] Source bytes remain immutable.
- [ ] Physical time is not inferred from MP4 playback FPS.
- [ ] Annotated overlays are not model input.
- [ ] Frames are not treated as independent experiments.
