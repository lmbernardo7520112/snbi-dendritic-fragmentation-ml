"""Exact Study3 CNN architecture and two actual synthetic thirty-epoch fits."""

from copy import deepcopy
import importlib.util
import inspect
import json
import math
from pathlib import Path
import unittest
from unittest import mock

from snbi_fragmentation import study3_cnn as core
from snbi_fragmentation.study3_models import Study3ModelError
from test_study3_models import synthetic_groups


CNN_AVAILABLE = all(importlib.util.find_spec(name) is not None for name in ("numpy", "torch"))


class Study3CNNStaticTests(unittest.TestCase):
    def test_fixed_training_and_exactly_two_architectures(self):
        contract = core.method_contract()
        self.assertEqual(set(contract["models"]), {core.TEMPORAL, core.SPATIOTEMPORAL})
        self.assertEqual(contract["training"]["epochs"], 30)
        self.assertEqual(contract["training"]["seed"], 42)
        self.assertEqual(contract["training"]["learning_rate"], .001)
        self.assertEqual(contract["training"]["weight_decay"], 0)
        self.assertEqual(contract["models"][core.TEMPORAL]["batch_size"], 8)
        self.assertEqual(contract["models"][core.SPATIOTEMPORAL]["batch_size"], 4)
        for key in ("augmentation", "scheduler", "early_stopping", "epoch_selection", "architecture_search"):
            self.assertIs(contract["training"][key], False)
        json.dumps(contract, allow_nan=False)

    def test_fit_has_no_tuning_options_or_validation_hook(self):
        self.assertEqual(list(inspect.signature(core.fit_cnn).parameters),
                         ["kind", "X", "groups", "fold", "on_event"])
        self.assertEqual(list(inspect.signature(core.predict_cnn).parameters), ["model", "X"])


class Study3CNNDocumentCoherenceTests(unittest.TestCase):
    """Preregistered JSON and the executable CNN contract must agree."""

    @classmethod
    def setUpClass(cls):
        path = Path(__file__).absolute().parents[1] / "configs/study3/cnn-contract.json"
        cls.document = json.loads(path.read_text(encoding="utf-8"))
        cls.code = core.method_contract()

    @staticmethod
    def architecture_text(layers):
        rendered = []
        for layer in layers:
            name = layer["layer"]
            if name in {"Conv1d", "Conv2d"}:
                value = (f"{name}({layer['in_channels']},{layer['out_channels']},"
                         f"{layer['kernel_size']},padding={layer['padding']})")
            elif name == "Linear":
                value = f"Linear({layer['in_features']},{layer['out_features']})"
            elif name == "MaxPool2d":
                value = f"MaxPool2d({layer['kernel_size']})"
            elif name == "AdaptiveAvgPool1d":
                value = f"AdaptiveAvgPool1d({layer['output_size']})"
            elif name == "AdaptiveAvgPool2d":
                value = "AdaptiveAvgPool2d((" + ",".join(map(str, layer["output_size"])) + "))"
            else:
                if name not in {"ReLU", "Flatten"}:
                    raise AssertionError("Undeclared architecture layer")
                value = name
            rendered.append(value)
        return rendered

    def test_document_binds_seed_cpu_threads_epochs_and_optimizer(self):
        training = self.code["training"]
        for key in ("seed", "device", "epochs", "optimizer", "learning_rate", "weight_decay", "loss"):
            self.assertEqual(self.document[key], training[key])
        self.assertEqual(self.document["torch_threads"], training["threads"])
        self.assertEqual(self.document["shuffle"], "TRAIN_ONLY")
        self.assertIs(training["shuffle_training"], True)
        self.assertEqual(training["epochs"], 30)
        self.assertEqual(training["seed"], 42)
        self.assertEqual(training["threads"], 1)

    def test_document_binds_both_input_shapes_batches_counts_and_t8(self):
        self.assertEqual(self.code["temporal_points"], 8)
        self.assertEqual(self.code["input_channels"], ["STRUCTURAL_Y", "RELATIVE_SOLUTE_FIELD_Y"])
        for kind in (core.TEMPORAL, core.SPATIOTEMPORAL):
            document, model = self.document[kind], self.code["models"][kind]
            self.assertEqual(document["input_shape"], model["input_shape"])
            self.assertEqual(document["parameters"], model["parameter_count"])
            self.assertEqual(document["parameters"], sum(model["parameter_blocks"]))
            self.assertEqual(document["batch_size"], model["batch_size"])
        self.assertEqual(self.document[core.TEMPORAL]["input_shape"], [20, 8])
        self.assertEqual(self.document[core.SPATIOTEMPORAL]["input_shape"], [8, 2, 65, 65])

    def test_document_binds_temporal_and_shared_spatial_architectures(self):
        self.assertEqual(self.document[core.TEMPORAL]["architecture"],
                         self.architecture_text(self.code["architectures"][core.TEMPORAL]))
        spatial = self.document[core.SPATIOTEMPORAL]
        for block in ("shared_spatial_encoder", "temporal_head"):
            self.assertEqual(spatial[block], self.architecture_text(
                self.code["architectures"][core.SPATIOTEMPORAL][block]))
        self.assertEqual(spatial["sequence"], "B,8,16 -> B,16,8")

    def test_document_binds_fold_local_scaler_and_fixed_pixel_scaling(self):
        temporal = self.document[core.TEMPORAL]
        self.assertEqual(temporal["normalization"],
                         "TRAIN-fold mean/std per feature over groups*timepoints; ddof=0; zero std->1")
        self.assertEqual(self.code["models"][core.TEMPORAL]["normalization"],
                         "TRAIN_GROUP_TIME_MEAN_STD_DDOF0_ZERO_STD_TO_ONE")
        self.assertEqual(temporal["persist_scaler"], ["mean", "std", "sha256"])
        self.assertEqual(self.document[core.SPATIOTEMPORAL]["scaling"], "uint8->float32/255.0")
        self.assertEqual(self.code["models"][core.SPATIOTEMPORAL]["normalization"],
                         "uint8_to_float32_div255")

    def test_document_prohibitions_match_fixed_no_search_training_and_architectures(self):
        self.assertEqual(set(self.document["prohibited"]),
                         {"BatchNorm", "Dropout", "scheduler", "early_stopping", "augmentation",
                          "additional_seed", "architecture_search", "Conv3d", "GRU", "LSTM",
                          "Transformer", "attention"})
        for flag in ("scheduler", "early_stopping", "augmentation", "architecture_search", "epoch_selection"):
            self.assertIs(self.code["training"][flag], False)
        layers = self.code["architectures"][core.TEMPORAL] + [
            layer for block in self.code["architectures"][core.SPATIOTEMPORAL].values() for layer in block]
        allowed = {"Conv1d", "Conv2d", "ReLU", "MaxPool2d", "AdaptiveAvgPool1d", "AdaptiveAvgPool2d",
                   "Flatten", "Linear"}
        self.assertLessEqual({layer["layer"] for layer in layers}, allowed)


@unittest.skipUnless(CNN_AVAILABLE, "scientific dependencies absent outside strict Study3 profile")
class Study3CNNArchitectureTests(unittest.TestCase):
    def test_temporal_shapes_parameter_blocks_and_deterministic_initialization(self):
        import torch
        first, second = core.build_temporal_cnn(), core.build_temporal_cnn()
        self.assertEqual(tuple(first(torch.zeros(3, 20, 8)).shape), (3, 2))
        self.assertEqual([sum(p.numel() for p in first[i].parameters()) for i in (0, 2, 6)],
                         [1952, 3104, 66])
        self.assertEqual(sum(p.numel() for p in first.parameters()), 5122)
        self.assertTrue(all(torch.equal(a, b) for a, b in zip(first.parameters(), second.parameters())))
        self.assertEqual(torch.get_num_threads(), 1)
        self.assertTrue(torch.are_deterministic_algorithms_enabled())

    def test_spatiotemporal_shapes_and_single_shared_encoder(self):
        import torch
        model = core.build_spatiotemporal_cnn()
        calls = []
        handle = model.spatial_encoder.register_forward_hook(lambda module, args, output: calls.append(
            (tuple(args[0].shape), tuple(output.shape))))
        try:
            self.assertEqual(tuple(model(torch.zeros(2, 8, 2, 65, 65)).shape), (2, 2))
        finally:
            handle.remove()
        self.assertEqual(calls, [((16, 2, 65, 65), (16, 16))])
        blocks = [model.spatial_encoder[0], model.spatial_encoder[3],
                  model.temporal_head[0], model.temporal_head[4]]
        self.assertEqual([sum(p.numel() for p in layer.parameters()) for layer in blocks],
                         [152, 1168, 784, 34])
        self.assertEqual(sum(p.numel() for p in model.parameters()), 2138)

    def test_spatiotemporal_determinism_and_forbidden_layers_absent(self):
        import torch
        first, second = core.build_spatiotemporal_cnn(), core.build_spatiotemporal_cnn()
        self.assertTrue(all(torch.equal(a, b) for a, b in zip(first.parameters(), second.parameters())))
        names = {type(module).__name__ for module in first.modules()}
        self.assertFalse(names & {"Conv3d", "GRU", "LSTM", "Transformer", "MultiheadAttention",
                                  "BatchNorm1d", "BatchNorm2d", "Dropout"})

    def test_same_parameter_count_with_inserted_dropout_is_rejected(self):
        import torch
        model = core.build_temporal_cnn()
        model.add_module("forbidden", torch.nn.Dropout())
        with self.assertRaisesRegex(Study3ModelError, "architecture divergence"):
            core._check_model(model)

    def test_same_parameter_count_with_changed_padding_is_rejected(self):
        model = core.build_temporal_cnn()
        model[0].padding = (0,)
        with self.assertRaisesRegex(Study3ModelError, "geometry divergence"):
            core._check_model(model)


@unittest.skipUnless(CNN_AVAILABLE, "scientific dependencies absent outside strict Study3 profile")
class Study3CNNAdmissionTests(unittest.TestCase):
    def setUp(self):
        import numpy as np
        self.np, self.groups = np, synthetic_groups()
        self.X = np.arange(4 * 20 * 8, dtype=float).reshape(4, 20, 8)

    def test_scaler_uses_group_and_time_axes_zero_std_becomes_one(self):
        self.X[:, 0, :] = 8
        scaler = core.fit_temporal_scaler(self.X, self.groups, fold=0)
        self.np.testing.assert_array_equal(scaler["mean"], self.X.mean(axis=(0, 2)))
        expected = self.X.std(axis=(0, 2)); expected[0] = 1
        self.np.testing.assert_array_equal(scaler["std"], expected)
        self.assertEqual(scaler["observations_per_group"], 8)
        self.assertEqual(len(scaler["sha256"]), 64)
        self.assertEqual(scaler, core.fit_temporal_scaler(self.X.copy(), self.groups, fold=0))

    def test_validation_cannot_participate_in_scaler(self):
        with self.assertRaisesRegex(Study3ModelError, "validation groups"):
            core.fit_temporal_scaler(self.X, self.groups, fold=1)

    def test_callback_denial_precedes_scaler_or_model_creation(self):
        with mock.patch.object(core, "fit_temporal_scaler") as scaler, \
                mock.patch.object(core, "build_temporal_cnn") as builder:
            with self.assertRaisesRegex(RuntimeError, "fit denied"):
                core.fit_cnn(core.TEMPORAL, self.X, self.groups, fold=0,
                             on_event=mock.Mock(side_effect=RuntimeError("fit denied")))
            scaler.assert_not_called()
            builder.assert_not_called()

    def test_bad_dimensions_dtype_and_nonfinite_values_denied_without_budget_event(self):
        for kind, X in ((core.TEMPORAL, self.X[:, :, :7]),
                        (core.TEMPORAL, self.X.astype("uint8")),
                        (core.TEMPORAL, self.np.full((4, 20, 8), self.np.nan)),
                        (core.SPATIOTEMPORAL, self.np.zeros((4, 8, 2, 65, 65), dtype=float))):
            callback = mock.Mock()
            with self.assertRaises(Study3ModelError):
                core.fit_cnn(kind, X, self.groups, fold=0, on_event=callback)
            callback.assert_not_called()

    def test_fold_validation_denied_before_cnn_initialization(self):
        with mock.patch.object(core, "build_temporal_cnn") as builder:
            with self.assertRaisesRegex(Study3ModelError, "validation groups"):
                core.fit_cnn(core.TEMPORAL, self.X, self.groups, fold=1, on_event=mock.Mock())
            builder.assert_not_called()

    def test_native_spatiotemporal_scaling_has_no_data_dependent_statistics(self):
        values = self.np.array([0, 255], dtype="uint8")
        scaled = core._tensor(core.SPATIOTEMPORAL, values, None)
        self.np.testing.assert_array_equal(scaled.numpy(), [0., 1.])


@unittest.skipUnless(CNN_AVAILABLE, "scientific dependencies absent outside strict Study3 profile")
class TwoActualSyntheticStudy3CNNFitsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        cls.groups, cls.fits, cls.events, cls.inputs = synthetic_groups(), {}, {}, {}
        cls.inputs[core.TEMPORAL] = np.random.default_rng(310).normal(size=(4, 20, 8))
        cls.inputs[core.SPATIOTEMPORAL] = np.random.default_rng(311).integers(
            0, 256, (4, 8, 2, 65, 65), dtype=np.uint8)
        for kind, values in cls.inputs.items():
            cls.events[kind] = []
            cls.fits[kind] = core.fit_cnn(kind, values, cls.groups, fold=0,
                                        on_event=cls.events[kind].append)

    def test_exact_thirty_epochs_one_fit_and_thirty_updates_each(self):
        for kind, (_, report) in self.fits.items():
            self.assertEqual(report["fit_calls"], 1)
            self.assertEqual(report["epochs"], 30)
            self.assertEqual(report["optimizer_updates"], 30)
            self.assertEqual(len(report["epoch_losses"]), 30)
            self.assertTrue(all(math.isfinite(v) and v >= 0 for v in report["epoch_losses"]))
            self.assertEqual(report["validation_evaluations_during_training"], 0)
            self.assertEqual(report["dev_evaluations_during_training"], 0)
            self.assertEqual(report["test_evaluations_during_training"], 0)
            self.assertNotEqual(report["initial_parameter_sha256"], report["final_parameter_sha256"])
            json.dumps(report, allow_nan=False)

    def test_fit_callback_counts_and_full_group_coverage_every_epoch(self):
        for events in self.events.values():
            self.assertEqual([e["event"] for e in events].count("FIT_START"), 1)
            self.assertEqual([e["event"] for e in events].count("FIT_COMPLETE"), 1)
            epochs = events[1:-1]
            self.assertEqual([e["epoch"] for e in epochs], list(range(1, 31)))
            self.assertTrue(all(e["training_groups_seen"] == 4 for e in epochs))

    def test_predictions_are_final_argmax_and_actual_softmax(self):
        import numpy as np
        for kind, (model, _) in self.fits.items():
            result = core.predict_cnn(model, self.inputs[kind])
            logits = np.asarray(result["logits"])
            self.assertEqual(logits.shape, (4, 2))
            self.assertEqual(result["predictions"], logits.argmax(axis=1).tolist())
            probabilities = np.exp(logits - logits.max(axis=1, keepdims=True))
            probabilities /= probabilities.sum(axis=1, keepdims=True)
            np.testing.assert_allclose(result["probabilities"], probabilities, atol=1e-7)
            json.dumps(result, allow_nan=False)

    def test_prediction_never_updates_training_scaler(self):
        import numpy as np
        model, report = self.fits[core.TEMPORAL]
        before = deepcopy(model._study3_scaler)
        core.predict_cnn(model, np.full((2, 20, 8), 12345., dtype=float))
        self.assertEqual(model._study3_scaler, before)
        self.assertEqual(report["scaler"], before)
        self.assertIsNone(self.fits[core.SPATIOTEMPORAL][1]["scaler"])


if __name__ == "__main__":
    unittest.main()
