# Method v1 — limitations addendum

This addendum preserves the scientific result at
`f3c6da78b04299475c7bb85e986eb7435b08bd22`. No scientific reexecution occurred.

1. Terminal E6 synthesis relied partly on an unversioned inline Python driver.
   It is therefore not end-to-end reproducible from a single versioned entry
   point. This remediation neither recreates that driver nor recalculates E6.
2. Roundtrip using a matrix and its own inverse demonstrates algebraic and
   numerical closure, not independent bidirectional registration validation.
3. The frozen grid–mask interaction deterministically reduced 35 candidate
   centres to 15, excluding 20. This materially limited a method requiring
   at least 12 distributed matches at every estimation instant. Grid, mask,
   margins, thresholds and minimum matches remain unchanged.
4. Insufficient evidence from method v1 does not establish registration
   impossibility. TRANSFORM_EXISTENCE=UNDETERMINED and
   METHOD_V1=INSUFFICIENT_EVIDENCE remain unchanged.
5. “27 files” described only closeout commit
   `a1d675f5dbbe3862621aebad2bcb80ab7584858d`. The full PR at that checkpoint
   contained 69 changed files against `f7818c17c18ba9e4306696ea61b427864cf7deb6`.
   This remediation may increase that total.
6. Author approval of the terminal blocked result is not verification of
   physical orientation. Gravity, thermal-gradient and growth vectors in
   native axes and the author's scientific visual review remain pending.

G2_SPATIAL=BLOCKED_METHOD_V1; G3=BLOCKED_DEPENDENCY_G2; E7=PASS_DOCUMENTARY.
Complete metrological uncertainty remains UNRESOLVED. Discretization is MODELLED
under an analytical assumption, not an empirical residual or total uncertainty.
No experimental matrix, ROI or coordinate conversion was produced or changed.
A revised scientific attempt and TI-3–TI-8 require new author authorization.
