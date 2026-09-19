"""Synthetic TI3-C contracts; precisely two training calls per complete suite.

Both repeated trainings use fabricated arrays. No fixture comes from a source,
pilot, patch, manifest or published experimental result.
"""

import copy
import importlib.util
import inspect
import json
import math
import unittest
from unittest import mock

from snbi_fragmentation import ti3c_cnn as cnn


NUMERICAL = all(importlib.util.find_spec(name) is not None for name in ("numpy", "torch"))


def samples(split="TRAIN", count=10):
    rows = []
    for index in range(count):
        source = "ESM1" if index % 2 == 0 else "ESM4"
        frame = {("TRAIN", "ESM1"): 73, ("TRAIN", "ESM4"): 98,
                 ("DEVELOPMENT", "ESM1"): 219, ("DEVELOPMENT", "ESM4"): 197,
                 ("FINAL_TEST", "ESM1"): 293, ("FINAL_TEST", "ESM4"): 295}[(split, source)]
        rows.append({"sample_id": f"synthetic-{split}-{index}", "split": split,
                     "source_id": source, "frame_index": frame,
                     "acquisition_id": "bottom_up_anti_parallel" if source == "ESM1" else "top_down_parallel",
                     "baseline_label": index % 2})
    return rows


class InputTrap:
    def __getattr__(self, name):
        raise AssertionError("forbidden input inspected")

    def __len__(self):
        raise AssertionError("forbidden input length examined")


class CNNMetadataTests(unittest.TestCase):
    def test_final_is_denied_before_runtime_or_any_array_access(self):
        with mock.patch.object(cnn, "_runtime") as runtime:
            for split in ("FINAL_TEST", "TRAIN", "DEVELOPMENT"):
                with self.subTest(split=split), self.assertRaises(cnn.CNNContractError):
                    cnn.evaluate_fixed(InputTrap(), InputTrap(), InputTrap(), samples("FINAL_TEST"), split)
            with self.assertRaises(cnn.CNNContractError):
                cnn.train_fixed(InputTrap(), InputTrap(), samples("FINAL_TEST"))
            runtime.assert_not_called()

    def test_dev_cannot_enter_training(self):
        with mock.patch.object(cnn, "_runtime") as runtime, self.assertRaises(cnn.CNNContractError):
            cnn.train_fixed(InputTrap(), InputTrap(), samples("DEVELOPMENT"))
        runtime.assert_not_called()

    def test_unknown_source_frame_acquisition_or_labels_are_denied(self):
        for change in ({"source_id": "ESM2"}, {"source_id": "ESM3"}, {"frame_index": 293},
                       {"frame_index": 73.0}, {"frame_index": True}, {"acquisition_id": "other"},
                       {"baseline_label": True}, {"baseline_label": 2}, {"baseline_label": "POSITIVE"},
                       {"sample_id": ""}):
            data = samples()
            data[0].update(change)
            with self.subTest(change=change), mock.patch.object(cnn, "_runtime") as runtime:
                with self.assertRaises(cnn.CNNContractError):
                    cnn.train_fixed(InputTrap(), InputTrap(), data)
                runtime.assert_not_called()

    def test_duplicate_id_and_single_class_denied(self):
        duplicated = samples()
        duplicated[1]["sample_id"] = duplicated[0]["sample_id"]
        single_class = [{**sample, "baseline_label": 0} for sample in samples()]
        for data in ([], duplicated, single_class):
            with self.assertRaises(cnn.CNNContractError):
                cnn._metadata(data, "TRAIN")

    def test_selection_strictly_compares_dev_only_and_tie_retains_rf(self):
        self.assertEqual(list(inspect.signature(cnn.development_decision).parameters), ["cnn_balanced_accuracy"])
        for value, family in ((0.0, "MULTIMODAL_LBP_RF"), (0.75, "MULTIMODAL_LBP_RF"),
                              (math.nextafter(0.75, 1), "MINIMAL_MULTIMODAL_CNN"),
                              (1.0, "MINIMAL_MULTIMODAL_CNN")):
            result = cnn.development_decision(value)
            self.assertEqual(result["final_model_family_preference"], family)
            self.assertEqual(result["delta_dev_balanced_accuracy"], value - 0.75)
        for invalid in (True, None, "0.8", math.inf, math.nan, -1, 2):
            with self.assertRaises(cnn.CNNContractError):
                cnn.development_decision(invalid)

    def test_metrics_keep_class_order_and_zero_division_convention(self):
        result = cnn.classification_metrics([0, 0, 1, 1], [0, 1, 0, 0])
        self.assertEqual(result["confusion_matrix"], [[1, 1], [2, 0]])
        self.assertEqual(result["balanced_accuracy"], 0.25)
        self.assertEqual(result["precision"], 0.0)
        self.assertEqual(result["recall"], 0.0)
        self.assertEqual(result["f1"], 0.0)
        result = cnn.classification_metrics([0, 1], [0, 0])
        self.assertEqual(result["precision"], 0.0)
        self.assertEqual(result["balanced_accuracy"], 0.5)

    def test_acquisition_diagnostic_uses_train_majority_only_and_no_runtime(self):
        train = samples(count=6)
        for sample, label in zip(train, [1, 0, 1, 0, 0, 1]):
            sample["baseline_label"] = label
        dev = samples("DEVELOPMENT", 4)
        for sample, label in zip(dev, [0, 0, 1, 1]):
            sample["baseline_label"] = label
        final = samples("FINAL_TEST", 2)
        with mock.patch.object(cnn, "_runtime") as runtime:
            result = cnn.acquisition_only_diagnostic(train + dev + final)
            runtime.assert_not_called()
        self.assertEqual(result["majority_class_by_acquisition"],
                         {"bottom_up_anti_parallel": 1, "top_down_parallel": 0})
        self.assertEqual(result["confusion_matrix"], [[1, 1], [1, 1]])
        self.assertEqual(result["balanced_accuracy"], 0.5)
        self.assertEqual(result["sample_order"], [sample["sample_id"] for sample in dev])
        self.assertEqual(result["experimental_opens"], 0)
        self.assertEqual(result["ml_training_calls"], 0)

    def test_acquisition_majority_tie_fails_closed_without_arbitrary_choice(self):
        train = samples(count=4)
        for sample, label in zip(train, [0, 0, 1, 1]):
            sample["baseline_label"] = label
        with self.assertRaises(cnn.CNNContractError) as failure:
            cnn.acquisition_only_diagnostic(train + samples("DEVELOPMENT", 4))
        self.assertEqual(failure.exception.code, "BLOCKED_ACQUISITION_MAJORITY_TIE")


@unittest.skipUnless(NUMERICAL, "optional pinned NumPy/PyTorch CPU runtime unavailable")
class CNNSyntheticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        import torch

        cls.np, cls.torch = np, torch
        cls.train_samples = samples()
        cls.train_labels = np.array([sample["baseline_label"] for sample in cls.train_samples], dtype=np.int64)
        cls.train_inputs = (np.arange(10 * 2 * 65 * 65, dtype=np.uint32).reshape(10, 2, 65, 65) % 251).astype(np.uint8)
        cls.train_inputs.setflags(write=False)
        cls.original = cls.train_inputs.copy()
        cls.dev_samples = samples("DEVELOPMENT", 4)
        cls.dev_labels = np.array([sample["baseline_label"] for sample in cls.dev_samples], dtype=np.int64)
        cls.dev_inputs = np.full((4, 2, 65, 65), 127, dtype=np.uint8)
        cls.dev_inputs.setflags(write=False)
        # Exactly two full synthetic fits. No other test calls train_fixed successfully.
        with mock.patch.object(torch.optim, "Adam", wraps=torch.optim.Adam) as adam:
            with mock.patch.object(torch.utils.data, "DataLoader", wraps=torch.utils.data.DataLoader) as loader:
                cls.model1, cls.report1 = cnn.train_fixed(cls.train_inputs, cls.train_labels, cls.train_samples)
                cls.model2, cls.report2 = cnn.train_fixed(cls.train_inputs, cls.train_labels, cls.train_samples)
                cls.optimizer_calls = adam.call_args_list
                cls.loader_calls = loader.call_args_list

    def test_170_parameter_architecture_forward_shape_and_cpu(self):
        torch = self.torch
        model = cnn.build_model()
        self.assertEqual(type(model).__name__, "MinimalMultimodalCNN")
        self.assertIsInstance(model, torch.nn.Module)
        self.assertEqual(cnn.verify_architecture(model), 170)
        self.assertEqual(sum(p.numel() for p in model.layers[0].parameters()), 152)
        self.assertEqual(sum(p.numel() for p in model.layers[5].parameters()), 18)
        with torch.inference_mode():
            logits = model(torch.zeros((4, 2, 65, 65), dtype=torch.float32))
        self.assertEqual(tuple(logits.shape), (4, 2))
        self.assertEqual(logits.device.type, "cpu")

    def test_parameter_and_layer_argument_drift_stop(self):
        torch = self.torch
        model = cnn.build_model()
        model.layers[5] = torch.nn.Linear(8, 3)
        with self.assertRaises(cnn.CNNContractError) as failure:
            cnn.verify_architecture(model)
        self.assertEqual(failure.exception.code, "BLOCKED_ARCHITECTURE_DIVERGENCE")
        model = cnn.build_model()
        model.layers[1] = torch.nn.ReLU(inplace=True)
        with self.assertRaises(cnn.CNNContractError):
            cnn.verify_architecture(model)

    def test_normalization_is_channel_preserving_float32_division_only(self):
        np, torch = self.np, self.torch
        inputs = np.zeros((2, 2, 65, 65), dtype=np.uint8)
        inputs[:, 0] = 255
        inputs[:, 1] = 128
        inputs.setflags(write=False)
        _, _, actual, _ = cnn._arrays(inputs, np.array([0, 1]), samples(count=2), "TRAIN")
        self.assertEqual(actual.dtype, torch.float32)
        self.assertTrue(bool((actual[:, 0] == 1.0).all().item()))
        self.assertTrue(bool((actual[:, 1] == torch.tensor(128 / 255, dtype=torch.float32)).all().item()))
        self.assertFalse(inputs.flags.writeable)

    def test_native_shape_dtype_and_readonly_are_mandatory(self):
        np = self.np
        invalid_arrays = [self.train_inputs.copy(), self.train_inputs.astype(float),
                          self.train_inputs[:, :1], self.train_inputs[:, :, :64],
                          self.train_inputs.transpose(0, 2, 3, 1), InputTrap()]
        for invalid in invalid_arrays:
            with self.subTest(kind=type(invalid).__name__), self.assertRaises(cnn.CNNContractError):
                cnn._arrays(invalid, self.train_labels, self.train_samples, "TRAIN")
        np.testing.assert_array_equal(self.train_inputs, self.original)

    def test_labels_must_match_metadata_without_coercion_or_reordering(self):
        np = self.np
        for labels in (self.train_labels[::-1], self.train_labels.astype(float),
                       self.train_labels.astype(bool), self.train_labels[:2]):
            with self.assertRaises(cnn.CNNContractError):
                cnn._arrays(self.train_inputs, labels, self.train_samples, "TRAIN")

    def test_two_repeated_synthetic_trainings_are_bitwise_deterministic(self):
        torch = self.torch
        self.assertEqual(self.report1, self.report2)
        for first, second in zip(self.model1.parameters(), self.model2.parameters()):
            self.assertTrue(torch.equal(first, second))
        self.assertEqual(len(self.report1["epoch_losses"]), 10)
        self.assertTrue(all(math.isfinite(loss) for loss in self.report1["epoch_losses"]))
        self.assertEqual(self.report1["epochs_completed"], 10)
        self.assertEqual(self.report1["optimizer_steps"], 20)
        self.assertTrue(torch.are_deterministic_algorithms_enabled())
        self.assertEqual(torch.get_num_threads(), 1)
        self.assertEqual(self.report1["dependency_versions"]["torch"], "2.4.1+cpu")

    def test_frozen_optimizer_and_loader_arguments_have_no_dev_or_tuning_inputs(self):
        self.assertEqual(list(inspect.signature(cnn.train_fixed).parameters), ["train_inputs", "labels", "samples"])
        self.assertEqual(len(self.optimizer_calls), 2)
        self.assertEqual(len(self.loader_calls), 2)
        for call in self.optimizer_calls:
            self.assertEqual(call.kwargs, {"lr": 0.005})
        for call in self.loader_calls:
            self.assertEqual({key: value for key, value in call.kwargs.items() if key != "generator"},
                             {"batch_size": 8, "shuffle": True, "num_workers": 0})
            self.assertEqual(call.kwargs["generator"].initial_seed(), 42)
            self.assertEqual(len(call.args[0]), 10)
        self.assertFalse(self.report1["development_used_during_training"])
        self.assertEqual(self.report1["adam_defaults"]["weight_decay"], 0)
        self.assertEqual(self.report1["adam_defaults"]["betas"], [0.9, 0.999])

    def test_dev_before_train_and_evaluation_before_epoch_ten_are_denied(self):
        model = copy.deepcopy(self.model1)
        with self.assertRaises(cnn.CNNContractError):
            cnn.evaluate_fixed(model, self.dev_inputs, self.dev_labels, self.dev_samples, "DEVELOPMENT")
        model._ti3c_epochs_completed = 9
        with self.assertRaises(cnn.CNNContractError):
            cnn.evaluate_fixed(model, self.train_inputs, self.train_labels, self.train_samples, "TRAIN")

    def test_once_each_evaluation_records_argmax_logits_and_probs_without_weight_changes(self):
        torch = self.torch
        model = copy.deepcopy(self.model1)
        parameters = [p.detach().clone() for p in model.parameters()]
        with mock.patch.object(model, "forward", wraps=model.forward) as forward:
            train = cnn.evaluate_fixed(model, self.train_inputs, self.train_labels, self.train_samples, "TRAIN")
            dev = cnn.evaluate_fixed(model, self.dev_inputs, self.dev_labels, self.dev_samples, "DEVELOPMENT")
            self.assertEqual(forward.call_count, 2)
            with self.assertRaises(cnn.CNNContractError):
                cnn.evaluate_fixed(model, self.dev_inputs, self.dev_labels, self.dev_samples, "DEVELOPMENT")
            self.assertEqual(forward.call_count, 2)
        for before, after in zip(parameters, model.parameters()):
            self.assertTrue(torch.equal(before, after))
        for report, count in ((train, 10), (dev, 4)):
            self.assertEqual(report["sample_count"], count)
            self.assertEqual(len(report["logits_class_order_0_1"]), count)
            for prediction, logits, probabilities in zip(report["predicted_labels"],
                    report["logits_class_order_0_1"], report["probabilities_class_order_0_1"]):
                self.assertEqual(prediction, int(logits[1] > logits[0]))
                self.assertAlmostEqual(sum(probabilities), 1.0, places=6)
            json.dumps(report, allow_nan=False)
        json.dumps(self.report1, allow_nan=False)

    def test_failed_inference_consumes_evaluation_and_cannot_retry(self):
        model = copy.deepcopy(self.model1)
        with mock.patch.object(model, "forward", side_effect=RuntimeError("synthetic inference failure")):
            with self.assertRaises(RuntimeError):
                cnn.evaluate_fixed(model, self.train_inputs, self.train_labels, self.train_samples, "TRAIN")
        with self.assertRaises(cnn.CNNContractError):
            cnn.evaluate_fixed(model, self.train_inputs, self.train_labels, self.train_samples, "TRAIN")

    def test_train_evaluation_reordering_is_denied(self):
        model = copy.deepcopy(self.model1)
        with self.assertRaises(cnn.CNNContractError):
            cnn.evaluate_fixed(model, self.train_inputs[::-1], self.train_labels[::-1],
                               self.train_samples[::-1], "TRAIN")


if __name__ == "__main__":
    unittest.main()
