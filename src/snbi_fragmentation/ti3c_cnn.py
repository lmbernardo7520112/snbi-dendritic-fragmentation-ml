"""Frozen TI3-C CNN on admitted in-memory native TRAIN/DEVELOPMENT patches.

There is no reader, writer, model export or authority activation here. The
runner authenticates the unchanged sample manifest and consumes its exclusive
receipt before admitting experimental arrays. Optional runtime imports are lazy
so dependency-free governance collection never imports PyTorch.
"""

import math
import random
import sys

from .ti3_dataset import ACQUISITIONS, FRAME_SPLITS


TORCH_VERSION = "2.4.1+cpu"
NUMPY_VERSION = "1.26.4"
PARAMETER_COUNT = 170
RF_REFERENCE_BALANCED_ACCURACY = 0.75
CHANNEL_ORDER = ["STRUCTURAL_LUMINANCE", "RELATIVE_SOLUTE_FIELD_LUMINANCE"]
TRAINING_CONTRACT = {
    "python_seed": 42, "numpy_seed": 42, "torch_seed": 42,
    "device": "cpu", "deterministic_algorithms": True, "num_threads": 1,
    "epochs": 10, "batch_size": 8, "shuffle": True,
    "generator_seed": 42, "num_workers": 0, "loss": "CrossEntropyLoss",
    "optimizer": "Adam", "learning_rate": 0.005, "weight_decay": 0.0,
    "scheduler": None, "early_stopping": False, "augmentation": "NONE",
    "normalization": "FLOAT32_NATIVE_UINT8_DIVIDED_BY_255",
}
ARCHITECTURE = [
    {"type": "Conv2d", "in_channels": 2, "out_channels": 8,
     "kernel_size": 3, "padding": 1, "bias": True},
    {"type": "ReLU"}, {"type": "MaxPool2d", "kernel_size": 2, "stride": 2},
    {"type": "AdaptiveAvgPool2d", "output_size": [1, 1]},
    {"type": "Flatten"}, {"type": "Linear", "in_features": 8, "out_features": 2,
                          "bias": True},
]


class CNNContractError(ValueError):
    """A contract failure is terminal for the scientific runner."""

    def __init__(self, code, message):
        self.code = code
        super().__init__(f"{code}: {message}")


def _require(condition, code, message):
    if not condition:
        raise CNNContractError(code, message)


def _runtime():
    import numpy as np
    import torch

    _require(sys.version_info[:2] == (3, 12) and np.__version__ == NUMPY_VERSION
             and torch.__version__ == TORCH_VERSION and torch.version.cuda is None,
             "BLOCKED_DEPENDENCY_DIVERGENCE", "Python 3.12 and exact CPU runtime required")
    return np, torch


def validate_runtime():
    """Validate versions without initializing a model or training."""
    np, torch = _runtime()
    return {"python": ".".join(str(value) for value in sys.version_info[:3]),
            "numpy": np.__version__, "torch": torch.__version__,
            "torch_cuda_build": torch.version.cuda, "device": "cpu"}


def _metadata(samples, split):
    # Check metadata before importing numerical libraries or touching arrays.
    _require(split in ("TRAIN", "DEVELOPMENT"), "FORBIDDEN_INPUT", "FINAL_TEST is prohibited")
    _require(type(samples) is list and samples, "INPUT_CONTRACT", "sample metadata required")
    ids, labels = set(), []
    for sample in samples:
        _require(type(sample) is dict and sample.get("split") == split,
                 "FORBIDDEN_INPUT", "sample split differs or is forbidden")
        source, frame = sample.get("source_id"), sample.get("frame_index")
        _require(type(source) is str and source in ("ESM1", "ESM4") and type(frame) is int
                 and FRAME_SPLITS.get((source, frame)) == split,
                 "FORBIDDEN_INPUT", "only the five authorized structural pairs are admitted")
        _require(sample.get("acquisition_id") == ACQUISITIONS[source],
                 "INPUT_CONTRACT", "acquisition provenance differs")
        sample_id, label = sample.get("sample_id"), sample.get("baseline_label")
        _require(type(sample_id) is str and sample_id and sample_id not in ids,
                 "INPUT_CONTRACT", "sample identifiers must be unique and explicit")
        _require(type(label) is int and label in (0, 1), "INPUT_CONTRACT", "binary weak label required")
        ids.add(sample_id)
        labels.append(label)
    _require(set(labels) == {0, 1}, "INPUT_CONTRACT", "both weak-label classes required")
    return labels


def _arrays(inputs, labels, samples, split):
    expected = _metadata(samples, split)
    np, torch = _runtime()
    _require(isinstance(inputs, np.ndarray) and inputs.dtype == np.dtype("uint8")
             and inputs.shape == (len(samples), 2, 65, 65) and not inputs.flags.writeable,
             "INPUT_CONTRACT", "readonly native uint8 N-by-2-by-65-by-65 inputs required")
    _require(isinstance(labels, np.ndarray) and labels.dtype.kind in "iu"
             and labels.shape == (len(samples),) and np.array_equal(labels, np.array(expected)),
             "INPUT_CONTRACT", "integer labels must match the frozen sample order")
    # A copy both preserves callers' readonly bytes and prevents tensor aliasing.
    tensor = torch.tensor(inputs, dtype=torch.float32, device="cpu") / 255.0
    targets = torch.tensor(labels, dtype=torch.long, device="cpu")
    return np, torch, tensor, targets


def build_model():
    """Construct the exact nn.Module lazily, without a module-level torch import."""
    _, torch = _runtime()

    class MinimalMultimodalCNN(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.layers = torch.nn.Sequential(
                torch.nn.Conv2d(2, 8, kernel_size=3, padding=1),
                torch.nn.ReLU(),
                torch.nn.MaxPool2d(kernel_size=2, stride=2),
                torch.nn.AdaptiveAvgPool2d((1, 1)),
                torch.nn.Flatten(),
                torch.nn.Linear(8, 2),
            )

        def forward(self, inputs):
            return self.layers(inputs)

    model = MinimalMultimodalCNN().to(device="cpu")
    verify_architecture(model)
    return model


def verify_architecture(model):
    _, torch = _runtime()
    count = sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
    _require(count == PARAMETER_COUNT, "BLOCKED_ARCHITECTURE_DIVERGENCE",
             "exactly 170 trainable parameters required")
    layers = list(model.children())
    _require(len(layers) == 1 and type(layers[0]) is torch.nn.Sequential,
             "BLOCKED_ARCHITECTURE_DIVERGENCE", "one fixed sequential stack required")
    layers = list(layers[0])
    expected = (torch.nn.Conv2d, torch.nn.ReLU, torch.nn.MaxPool2d,
                torch.nn.AdaptiveAvgPool2d, torch.nn.Flatten, torch.nn.Linear)
    _require(tuple(type(layer) for layer in layers) == expected,
             "BLOCKED_ARCHITECTURE_DIVERGENCE", "layer sequence differs")
    conv, relu, pool, avg, flatten, linear = layers
    _require((conv.in_channels, conv.out_channels, conv.kernel_size, conv.padding,
              conv.stride, conv.dilation, conv.groups, conv.padding_mode) ==
             (2, 8, (3, 3), (1, 1), (1, 1), (1, 1), 1, "zeros")
             and conv.bias is not None and not relu.inplace
             and (pool.kernel_size, pool.stride, pool.padding, pool.dilation,
                  pool.return_indices, pool.ceil_mode) == (2, 2, 0, 1, False, False)
             and avg.output_size == (1, 1) and flatten.start_dim == 1 and flatten.end_dim == -1
             and (linear.in_features, linear.out_features) == (8, 2) and linear.bias is not None
             and all(parameter.device.type == "cpu" and parameter.requires_grad
                     for parameter in model.parameters()),
             "BLOCKED_ARCHITECTURE_DIVERGENCE", "frozen layer arguments or CPU parameters differ")
    return count


def train_fixed(train_inputs, labels, samples):
    """One ten-epoch fit accepting TRAIN alone; no DEV-dependent branch exists."""
    np, torch, tensor, targets = _arrays(train_inputs, labels, samples, "TRAIN")
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(1)
    model = build_model()
    generator = torch.Generator(device="cpu").manual_seed(42)
    loader = torch.utils.data.DataLoader(
        torch.utils.data.TensorDataset(tensor, targets), batch_size=8, shuffle=True,
        generator=generator, num_workers=0,
    )
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.005)
    _require(optimizer.defaults["weight_decay"] == 0
             and optimizer.defaults["lr"] == 0.005,
             "MODEL_CONTRACT", "frozen Adam settings differ")
    model.train()
    losses, steps = [], 0
    for _ in range(10):
        weighted_loss = 0.0
        for batch_inputs, batch_targets in loader:
            optimizer.zero_grad()
            logits = model(batch_inputs)
            loss = criterion(logits, batch_targets)
            _require(bool(torch.isfinite(loss).item()), "MODEL_CONTRACT", "nonfinite training loss")
            loss.backward()
            optimizer.step()
            weighted_loss += float(loss.item()) * len(batch_targets)
            steps += 1
        losses.append(weighted_loss / len(samples))
    model._ti3c_epochs_completed = 10
    model._ti3c_evaluated_splits = []
    model._ti3c_train_sample_ids = tuple(sample["sample_id"] for sample in samples)
    return model, {
        "train_calls": 1, "epochs_completed": 10, "optimizer_steps": steps,
        "epoch_losses": losses, "epoch_loss_definition": "sample-weighted mean of training minibatch losses",
        "parameter_count": verify_architecture(model), "architecture": ARCHITECTURE,
        "training_contract": dict(TRAINING_CONTRACT),
        "adam_defaults": {key: list(value) if isinstance(value, tuple) else value
                          for key, value in optimizer.defaults.items()},
        "sample_order": [sample["sample_id"] for sample in samples],
        "development_used_during_training": False, "training_sample_count": len(samples),
        "dependency_versions": validate_runtime(),
    }


def classification_metrics(labels, prediction):
    """Binary weak-label reporting with fixed zero-division value zero."""
    _require(type(labels) is list and type(prediction) is list
             and len(labels) == len(prediction) and labels
             and all(type(value) is int and value in (0, 1) for value in labels + prediction)
             and set(labels) == {0, 1}, "METRIC_CONTRACT", "aligned binary labels required")
    tn = sum(actual == 0 and predicted == 0 for actual, predicted in zip(labels, prediction))
    fp = sum(actual == 0 and predicted == 1 for actual, predicted in zip(labels, prediction))
    fn = sum(actual == 1 and predicted == 0 for actual, predicted in zip(labels, prediction))
    tp = sum(actual == 1 and predicted == 1 for actual, predicted in zip(labels, prediction))
    return {
        "balanced_accuracy": 0.5 * (tn / (tn + fp) + tp / (tp + fn)),
        "accuracy": (tn + tp) / len(labels), "precision": tp / (tp + fp) if tp + fp else 0.0,
        "recall": tp / (tp + fn), "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0,
        "confusion_matrix": [[tn, fp], [fn, tp]],
        "confusion_order": "rows=true, columns=predicted; labels=[0,1]",
        "TN": tn, "FP": fp, "FN": fn, "TP": tp, "sample_count": len(labels),
    }


def evaluate_fixed(model, inputs, labels, samples, split):
    """Evaluate TRAIN then DEVELOPMENT once each, strictly after epoch ten."""
    _metadata(samples, split)
    _require(getattr(model, "_ti3c_epochs_completed", None) == 10,
             "MODEL_CONTRACT", "evaluation requires all ten completed epochs")
    expected_previous = [] if split == "TRAIN" else ["TRAIN"]
    _require(getattr(model, "_ti3c_evaluated_splits", None) == expected_previous,
             "FORBIDDEN_EVALUATION", "TRAIN then DEVELOPMENT exactly once required")
    if split == "TRAIN":
        _require(tuple(sample["sample_id"] for sample in samples) == model._ti3c_train_sample_ids,
                 "INPUT_CONTRACT", "descriptive TRAIN evaluation must retain original order")
    else:
        _require(not set(model._ti3c_train_sample_ids).intersection(sample["sample_id"] for sample in samples),
                 "INPUT_CONTRACT", "TRAIN and DEVELOPMENT sample IDs must be disjoint")
    _, torch, tensor, _ = _arrays(inputs, labels, samples, split)
    verify_architecture(model)
    # Consume this evaluation before inference: an error never authorizes retry.
    model._ti3c_evaluated_splits.append(split)
    model.eval()
    with torch.inference_mode():
        logits = model(tensor)
        probabilities = torch.softmax(logits, dim=1)
        prediction = torch.argmax(logits, dim=1)
    _require(tuple(logits.shape) == (len(samples), 2)
             and bool(torch.isfinite(logits).all().item())
             and bool(torch.isfinite(probabilities).all().item())
             and bool(torch.allclose(probabilities.sum(dim=1), torch.ones(len(samples)),
                                     rtol=0.0, atol=1e-6)),
             "MODEL_CONTRACT", "finite binary logits and normalized probabilities required")
    true_labels, predicted_labels = labels.tolist(), prediction.tolist()
    return {
        **classification_metrics(true_labels, predicted_labels),
        "true_labels": true_labels, "predicted_labels": predicted_labels,
        "logits_class_order_0_1": logits.tolist(),
        "probabilities_class_order_0_1": probabilities.tolist(),
        "sample_order": [sample["sample_id"] for sample in samples],
        "decision_rule": "ARGMAX_TWO_LOGITS", "evaluation_calls": 1,
    }


def development_decision(cnn_balanced_accuracy):
    _require(type(cnn_balanced_accuracy) in (int, float) and math.isfinite(cnn_balanced_accuracy)
             and 0 <= cnn_balanced_accuracy <= 1, "METRIC_CONTRACT", "finite balanced accuracy required")
    delta = float(cnn_balanced_accuracy - RF_REFERENCE_BALANCED_ACCURACY)
    return {
        "multimodal_rf_reference_balanced_accuracy": RF_REFERENCE_BALANCED_ACCURACY,
        "cnn_dev_balanced_accuracy": float(cnn_balanced_accuracy),
        "delta_dev_balanced_accuracy": delta,
        "final_model_family_preference": ("MINIMAL_MULTIMODAL_CNN" if delta > 0
                                          else "MULTIMODAL_LBP_RF"),
        "selection_rule": "STRICT_DEV_IMPROVEMENT_OVER_0.75_ELSE_RF",
        "model_family_selection": "COMPLETE",
    }


def acquisition_only_diagnostic(samples):
    """Metadata-only confounding diagnostic; no learned model or pixel access."""
    _require(type(samples) is list and all(type(sample) is dict for sample in samples),
             "INPUT_CONTRACT", "manifest sample records required")
    train = [sample for sample in samples if sample.get("split") == "TRAIN"]
    dev = [sample for sample in samples if sample.get("split") == "DEVELOPMENT"]
    _require(all(sample.get("split") in ("TRAIN", "DEVELOPMENT", "FINAL_TEST") for sample in samples),
             "INPUT_CONTRACT", "unknown split in metadata diagnostic")
    _metadata(train, "TRAIN")
    labels = _metadata(dev, "DEVELOPMENT")
    counts = {acquisition: [0, 0] for acquisition in set(ACQUISITIONS.values())}
    for sample in train:
        counts[sample["acquisition_id"]][sample["baseline_label"]] += 1
    _require(all(zero != one for zero, one in counts.values()),
             "BLOCKED_ACQUISITION_MAJORITY_TIE", "majority must be unique in each acquisition")
    majority = {acquisition: int(one > zero) for acquisition, (zero, one) in counts.items()}
    prediction = [majority[sample["acquisition_id"]] for sample in dev]
    return {**classification_metrics(labels, prediction),
            "diagnostic": "TRAIN_ACQUISITION_MAJORITY_PREDICTS_DEVELOPMENT",
            "training_class_counts_0_1": counts, "majority_class_by_acquisition": majority,
            "sample_order": [sample["sample_id"] for sample in dev],
            "true_labels": labels, "predicted_labels": prediction,
            "experimental_opens": 0, "experimental_bytes": 0, "ml_training_calls": 0,
            "claim": "METADATA_ONLY_CONFOUNDING_DIAGNOSTIC_NOT_MODEL_SELECTION"}
