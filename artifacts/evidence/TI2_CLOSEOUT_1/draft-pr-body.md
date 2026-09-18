## Result and scope

TI-2 attempted reproducible registration between ESM2/3→ESM1 and ESM5/6→ESM4,
canonical ROI and spatial calibration. Method v1 did not obtain enough
correspondences at every required estimation instant. This PR preserves that
terminal result and reconciles its documentation; it does not rerun science.

- TI2_EXECUTION: `TERMINAL_BLOCKED_PENDING_CLOSEOUT`
- METHOD_V1: `INSUFFICIENT_EVIDENCE`
- G2-SPATIAL: `BLOCKED_METHOD_V1`
- TRANSFORM_EXISTENCE: `UNDETERMINED`
- G3: `BLOCKED_DEPENDENCY_G2`
- E7: `PASS_DOCUMENTARY`
- TI3_PLUS_AUTHORIZED: `false`

## Commits and custody

- `7e2223dd84346beebbccefe51afcead66a02d339` — recovery and contracts
- `5e1c4dc2406e1b6fbcf71bd8d86d6d842f3af3ad` — governed runtime and controls
- `f3c6da78b04299475c7bb85e986eb7435b08bd22` — TI2_EXECUTION_RESULT_COMMIT
- `{{TI2_CLOSEOUT_COMMIT}}` — documentary closeout

Exactly 30 pilot frames were decoded from the MP4s without additional loss,
preserving the videos' native resolution and pixel format. Headerless `.raw`
pixel buffers are not raw detector data. No mass extraction, extra frame or
experimental binary is versioned. Source and frame hashes from execution are
preserved. Closeout opened no experimental file or pixel and did not inspect
reserved quartiles.

## E0–E7

| Stage | Result |
|---|---|
| E0 | PASS: custody, scope, tools and RED contracts |
| E1 | PASS: exactly 30 bounded decoded frames |
| E2 | PARTIAL: geometry audit; physical orientation remains unverified |
| E3 | BLOCKED_METHOD_V1 before transformation-class selection |
| E4 | BLOCKED_DEPENDENCY; quartile pixels remain unanalysed |
| E5 | BLOCKED_DEPENDENCY; no certified shared ROI |
| E6 | Nominal scale documented; metrological uncertainty unresolved |
| E7 | PASS_DOCUMENTARY |

No experimental matrix, inverse or ROI was certified. Excluding the margin
removed 20/35 grid candidates; the method's insufficiency does not prove that
a valid transformation does not exist. No thresholds were relaxed.

## Documentary reconciliation

- `elapsed_from_first_frame_s = 1.18 × frame_index`.
- ESM1–3: `experimental_time_s = -25.96 + 1.18 × frame_index`.
- ESM4–6: `experimental_time_s = -34.22 + 1.18 × frame_index`.
- Experimental zero: solidification-front entry into the field of view.
- Historical `physical_time_s` values remain unchanged as deprecated elapsed
  aliases; the two explicit times are added and tested using Decimal.
- Nominal pixel size is documented as 1.40 µm/px in X and Y, citing the
  author-supplied Gibbs et al. reference, DOI 10.1007/s11837-015-1646-7.
- The historical 500/357 = 1.40056022409 µm/px raster crosscheck is compatible.
  Its interval [1.38888888889, 1.41242937853] is not a confidence interval.
- Complete metrological uncertainty remains UNRESOLVED. No coordinate
  conversion or propagation to unregistered modalities is performed.

No `src/`, matcher, decoder, correspondence, matrix or ROI implementation was
changed by closeout. Primary-text retrieval was not independently performed;
the supplied author authorization is the documentary reconciliation basis.

## Validation

| Profile | Run | Passed | Skipped | Failures | Errors |
|---|---:|---:|---:|---:|---:|
| Historical captured local log | 102 | 102 | 0 | 0 | 0 |
| Historical dependency-free profile, reconfirmed | 102 | 97 | 5 | 0 | 0 |
| Final closeout dependency-free suite | 113 | 108 | 5 | 0 | 0 |

The five optional NumPy/SciPy image-matching tests explicitly skip when the
runtime is absent. The 11 added tests cover deterministic documentary time
and scale semantics. Data, bootstrap, scope, manifest and checksum checks pass.
No dependencies were installed for closeout. Remote CI must be inspected after
this Draft PR is created; local results do not establish remote CI success.

**Green CI, green tests and complete documentation do not approve G2-SPATIAL
or G3.** TI-2R and TI-3–TI-8 were not executed and remain unauthorized. There are
no labels, ledger, ML dataset/splits, baseline, CNN, training or model evaluation.

## Review checklist

- [ ] Review the full closeout authorization and execution-result commit.
- [ ] Check the elapsed/experimental distinction and all ten reference points.
- [ ] Check nominal scale, raster comparison and unresolved metrology separately.
- [ ] Review method-v1 limitations without inferring transformation impossibility.
- [ ] Verify the 30-frame manifest, preserved hashes and zero tracked binaries.
- [ ] Verify exact test/skip counts, guardrails and completed remote CI.
- [ ] Keep this PR open as Draft; no merge or downstream authorization is implied.

Evidence: `artifacts/evidence/TI2_CLOSEOUT_1/closeout-report.md`,
`artifacts/evidence/TI2/execution-report.md`, the G2-SPATIAL/G3 reports,
`tests-final.json` and `artifacts/evidence/TI2/checksums.sha256`.
