"""Tiny synthetic-only CNN contract; one real twenty-epoch training run."""

from copy import deepcopy
import importlib.util
import inspect
import json
import math
import unittest
from unittest import mock

from snbi_fragmentation import study2c_cnn as core
from snbi_fragmentation.study2c_models import ModelContractError


CNN_AVAILABLE = all(importlib.util.find_spec(name) is not None for name in ("numpy", "torch"))


def tiny_rows():
    # Four groups, deliberately unequal observation counts; each class totals 2.
    rows = []
    for acquisition_index, acquisition in enumerate(("bottom_up_anti_parallel", "top_down_parallel")):
        for label in (0, 1):
            count = 2 if label else 1
            for index in range(count):
                rows.append({"group_id": f"synthetic-{acquisition_index}-{label}", "label": label,
                             "tier": "GOLD" if label else "BACKGROUND", "split": "TRAIN",
                             "acquisition_id": acquisition})
    return rows, [0.5 if r["label"] else 1.0 for r in rows]


class CNNStaticContractTests(unittest.TestCase):
    def test_training_budget_and_absence_of_adaptive_selection(self):
        self.assertEqual(core.CONFIG["epochs"], 20)
        self.assertEqual(core.CONFIG["batch_size"], 32)
        self.assertEqual(core.CONFIG["learning_rate"], 0.001)
        self.assertEqual(core.CONFIG["weight_decay"], 0.0)
        self.assertEqual(core.CONFIG["num_workers"], 0)
        for key in ("augmentation", "scheduler", "early_stopping", "dev_epoch_selection"):
            self.assertIs(core.CONFIG[key], False)
        json.dumps(core.CONFIG, allow_nan=False)

    def test_predictor_receives_no_labels_or_selection_hook(self):
        self.assertEqual(list(inspect.signature(core.predict_cnn).parameters), ["model", "pairs"])
        self.assertEqual(list(inspect.signature(core.fit_cnn).parameters), ["pairs", "rows", "weights", "progress"])


@unittest.skipUnless(CNN_AVAILABLE, "optional pinned CPU Torch unavailable")
class OneSyntheticCNNTrainingTests(unittest.TestCase):
    """One real fit for the suite, six synthetic pairs, twenty Adam updates."""

    @classmethod
    def setUpClass(cls):
        import numpy as np
        cls.rows, cls.weights = tiny_rows()
        cls.pairs = np.random.default_rng(1301).integers(0, 256, (len(cls.rows), 2, 65, 65), dtype=np.uint8)
        cls.events = []
        cls.model, cls.metadata = core.fit_cnn(cls.pairs, cls.rows, cls.weights, cls.events.append)
        cls.predictions = core.predict_cnn(cls.model, cls.pairs)

    def test_exact_architecture_and_parameter_blocks(self):
        import torch
        model = self.model
        self.assertEqual([type(layer).__name__ for layer in model],
                         ["Conv2d", "ReLU", "MaxPool2d", "Conv2d", "ReLU", "MaxPool2d",
                          "AdaptiveAvgPool2d", "Flatten", "Linear"])
        self.assertEqual((model[0].in_channels, model[0].out_channels), (2, 16))
        self.assertEqual((model[3].in_channels, model[3].out_channels), (16, 32))
        self.assertEqual([sum(p.numel() for p in model[i].parameters()) for i in (0, 3, 8)], [304, 4640, 66])
        self.assertEqual(sum(p.numel() for p in model.parameters()), 5010)
        self.assertTrue(all(p.device.type == "cpu" for p in model.parameters()))
        self.assertEqual(torch.get_num_threads(), 1)
        self.assertTrue(torch.are_deterministic_algorithms_enabled())

    def test_twenty_finite_losses_and_exact_updates_without_dev(self):
        metadata = self.metadata
        self.assertEqual(metadata["fit_calls"], 1)
        self.assertEqual(metadata["training_runs"], 1)
        self.assertEqual(metadata["epochs"], 20)
        self.assertEqual(metadata["optimizer_steps"], 20)
        self.assertEqual(len(metadata["epoch_losses"]), 20)
        self.assertTrue(all(math.isfinite(v) and v >= 0 for v in metadata["epoch_losses"]))
        self.assertEqual(metadata["dev_evaluations_during_training"], 0)
        self.assertEqual(metadata["test_evaluations_during_training"], 0)
        self.assertEqual(metadata["weight_sum_by_class"], {"0": 2.0, "1": 2.0})
        json.dumps(metadata, allow_nan=False)

    def test_progress_contains_each_epoch_once_with_full_synthetic_coverage(self):
        self.assertEqual(len(self.events), 21)
        self.assertEqual(self.events[0]["event"], "CNN_TRAIN_START")
        self.assertEqual([e["epoch"] for e in self.events[1:]], list(range(1, 21)))
        self.assertTrue(all(e["rows_seen"] == 6 for e in self.events[1:]))

    def test_predictions_match_argmax_logits_and_real_softmax(self):
        import numpy as np
        pred = self.predictions
        logits = np.asarray(pred["logits"])
        probability = np.asarray(pred["probabilities"])
        self.assertEqual(logits.shape, (6, 2))
        self.assertEqual(pred["predictions"], logits.argmax(axis=1).tolist())
        expected = np.exp(logits - logits.max(axis=1, keepdims=True))
        expected /= expected.sum(axis=1, keepdims=True)
        np.testing.assert_allclose(probability, expected, atol=1e-7)
        self.assertIsNone(pred["decision_scores"])
        json.dumps(pred, allow_nan=False)

    def test_test_rows_denied_before_new_model_or_training(self):
        rows = deepcopy(self.rows)
        rows[0]["split"] = "TEST"
        with mock.patch.object(core, "build_cnn_model") as builder:
            with self.assertRaisesRegex(ModelContractError, "TEST"):
                core.fit_cnn(self.pairs, rows, self.weights)
            builder.assert_not_called()

    def test_bad_weights_denied_before_new_model(self):
        with mock.patch.object(core, "build_cnn_model") as builder:
            with self.assertRaises(ModelContractError):
                core.fit_cnn(self.pairs, self.rows, [1.0] * 6)
            builder.assert_not_called()

    def test_float_or_wrong_channel_inputs_denied_without_new_model(self):
        import numpy as np
        for pairs in (self.pairs.astype(np.float32) / 255, self.pairs[:, :1], self.pairs[:-1]):
            with mock.patch.object(core, "build_cnn_model") as builder:
                with self.assertRaises(ModelContractError):
                    core.fit_cnn(pairs, self.rows, self.weights)
                builder.assert_not_called()

    def test_prediction_rejects_different_parameter_count(self):
        import torch
        incompatible = torch.nn.Linear(2, 2)
        with self.assertRaisesRegex(ModelContractError, "ARCHITECTURE_DIVERGENCE"):
            core.predict_cnn(incompatible, self.pairs)


if __name__ == "__main__":
    unittest.main()
