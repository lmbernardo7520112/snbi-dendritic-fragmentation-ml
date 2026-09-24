"""Synthetic domain identities only; no filesystem fixtures."""

from dataclasses import FrozenInstanceError
import unittest

from snbi_fragmentation import study3_domain as core


def rows_for_group(n=4, gid="synthetic-group", label=1, acquisition=core.ACQUISITIONS[0], fold=0):
    return [{"sample_id": f"{gid}-s{i:03d}", "group_id": gid, "acquisition_id": acquisition,
             "frame_index": i, "label": label, "tier": "GOLD" if label else "BACKGROUND",
             "split": "TRAIN", "cv_fold": fold} for i in range(n)]


class Study3DomainTests(unittest.TestCase):
    def test_domain_names_are_explicit(self):
        for name in ("AcquisitionId", "GroupId", "PositiveSiteId", "BackgroundTrackId", "ObservationId",
                     "FrameIndex", "FoldId", "WeakLabel", "TrajectoryObservation", "TrajectoryGroup",
                     "TemporalSelection", "TemporalRepresentation", "RepresentationKind", "Study3FitSpec",
                     "Study3MetricBundle", "Study3Result", "Study3TerminalState"):
            self.assertTrue(hasattr(core, name), name)

    def test_identity_types_reject_noncanonical_inputs(self):
        for constructor, value in ((core.GroupId, ""), (core.ObservationId, " bad "),
                                   (core.AcquisitionId, "new"), (core.FrameIndex, True),
                                   (core.FrameIndex, -1), (core.FoldId, 4), (core.FoldId, False)):
            with self.subTest(constructor=constructor.__name__, value=value), self.assertRaises(ValueError):
                constructor(value)

    def test_group_is_immutable_and_temporally_ordered(self):
        rows = rows_for_group()
        group = core.TrajectoryGroup.from_rows(rows[::-1])
        self.assertEqual([row.frame_index for row in group.observations], [0, 1, 2, 3])
        self.assertEqual((group.n_rows, group.first_frame, group.last_frame, group.cv_fold), (4, 0, 3, 0))
        with self.assertRaises(FrozenInstanceError):
            group.label = 0

    def test_row_admission_rejects_every_nontrain_tier(self):
        for changes in ({"split": "TEST"}, {"split": "DEVELOPMENT"}, {"tier": "SILVER"},
                        {"tier": "UNLABELED"}, {"label": True}, {"label": 0}, {"cv_fold": True}):
            row = rows_for_group(1)[0] | changes
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                core.TrajectoryObservation.from_row(row)

    def test_single_group_cannot_cross_identity_or_fold(self):
        for changes in ({"acquisition_id": core.ACQUISITIONS[1]}, {"label": 0, "tier": "BACKGROUND"},
                        {"group_id": "other"}, {"cv_fold": 1}, {"sample_id": "synthetic-group-s000"}):
            rows = rows_for_group(2)
            rows[1].update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                core.TrajectoryGroup.from_rows(rows)

    def test_temporal_ties_are_ordered_by_sample_id(self):
        rows = rows_for_group(2)
        rows[1]["frame_index"] = 0
        group = core.TrajectoryGroup.from_rows(rows[::-1])
        self.assertEqual([str(row.sample_id) for row in group.observations], [r["sample_id"] for r in rows])

    def test_site_and_background_are_exclusive_weak_entities(self):
        row = rows_for_group(1)[0]
        self.assertEqual(core.TrajectoryObservation.from_row(row | {"site_id": "site"}).site_id, "site")
        with self.assertRaises(ValueError):
            core.TrajectoryObservation.from_row(row | {"background_track_id": "track"})

    def test_subset_validation_rejects_duplicate_groups_and_shared_rows(self):
        group = core.TrajectoryGroup.from_rows(rows_for_group())
        self.assertEqual(core.validate_groups([group]), [group])
        with self.assertRaises(ValueError):
            core.validate_groups([group, group])
        rows = rows_for_group(gid="other")
        rows[0]["sample_id"] = str(group.observations[0].sample_id)
        with self.assertRaises(ValueError):
            core.validate_groups([group, core.TrajectoryGroup.from_rows(rows)])

    def test_fold_spec_rejects_overlap_unknown_model_and_no_fit_control(self):
        kind = core.RepresentationKind.D1_LBP20
        spec = core.Study3FitSpec("D1_LBP20-f0", kind, 0, ("a",), ("b",))
        self.assertEqual(spec.fold, 0)
        for args in (("D1_LBP20-f0", kind, 0, ("a",), ("a",)),
                     ("new-model-f0", "new-model", 0, ("a",), ("b",)),
                     ("ACQUISITION_ONLY-f0", "ACQUISITION_ONLY", 0, ("a",), ("b",))):
            with self.assertRaises(ValueError):
                core.Study3FitSpec(*args)

    def test_result_schema_has_one_prediction_per_group(self):
        metrics = core.Study3MetricBundle(1, 1, 1, 1, 1, 1, ((1, 0), (0, 1)))
        result = core.Study3Result("D1_LBP20", 0, ("a", "b"), (0, 1), metrics)
        self.assertEqual(result.predictions, (0, 1))
        for ids, predictions in ((("a", "a"), (0, 1)), (("a", "b"), (0,)), (("a",), (0,))):
            with self.assertRaises(ValueError):
                core.Study3Result("D1_LBP20", 0, ids, predictions, metrics)

    def test_metric_schema_rejects_confusion_score_mismatch(self):
        with self.assertRaises(ValueError):
            core.Study3MetricBundle(0.9, 1, 1, 1, 1, 1, ((1, 0), (0, 1)))

    def test_selection_schema_rejects_fabricated_rank_or_repeat(self):
        core.TemporalSelection("g", ("s",) * 8, (0,) * 8, (0.0,) * 8,
                               (0,) * 8, (False,) + (True,) * 7)
        with self.assertRaises(ValueError):
            core.TemporalSelection("g", ("s",) * 8, (0,) * 8, (0.0,) * 8,
                                   (1,) * 8, (False,) + (True,) * 7)

    def test_terminal_never_grants_retry_or_access(self):
        core.Study3TerminalState("PRE_SCIENCE_FROZEN", 0, 0)
        core.Study3TerminalState("PASS", 1, 28)
        for kwargs in ({"status": "PASS", "scientific_runs": 1, "distinct_fits": 27},
                       {"status": "PASS", "scientific_runs": 1, "distinct_fits": 28, "test_rows_read": 1},
                       {"status": "BLOCKED", "scientific_runs": 1, "distinct_fits": 0, "retry_count": 1},
                       {"status": "PRE_SCIENCE_FROZEN", "scientific_runs": 0, "distinct_fits": 1}):
            with self.assertRaises(ValueError):
                core.Study3TerminalState(**kwargs)


if __name__ == "__main__":
    unittest.main()
