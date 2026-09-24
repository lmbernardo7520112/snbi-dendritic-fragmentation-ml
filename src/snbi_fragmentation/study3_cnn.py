"""Two preregistered CPU CNNs over already admitted in-memory trajectories.

Imports are lazy. The fit API exposes no epoch, seed, architecture or validation
selection override. All folds use the same seed and final thirty-epoch model.
"""

from copy import deepcopy
import hashlib
import math
import random
import time

from .study3_models import _training_groups, require, scaler_record


TEMPORAL = "TEMPORAL_CNN1D_LBP20"
SPATIOTEMPORAL = "SPATIOTEMPORAL_CNN_SMALL"
CONFIGS = {
    TEMPORAL: {"input_shape": [20, 8], "batch_size": 8, "parameter_count": 5122,
               "parameter_blocks": [1952, 3104, 66],
               "normalization": "TRAIN_GROUP_TIME_MEAN_STD_DDOF0_ZERO_STD_TO_ONE"},
    SPATIOTEMPORAL: {"input_shape": [8, 2, 65, 65], "batch_size": 4,
                    "parameter_count": 2138, "parameter_blocks": [152, 1168, 784, 34],
                    "normalization": "uint8_to_float32_div255"},
}
TRAINING = {
    "seed": 42, "device": "cpu", "threads": 1, "num_workers": 0,
    "epochs": 30, "optimizer": "Adam", "learning_rate": 0.001,
    "weight_decay": 0.0, "betas": [0.9, 0.999], "eps": 1e-8,
    "amsgrad": False, "foreach": None, "maximize": False, "capturable": False,
    "differentiable": False, "fused": None, "loss": "CrossEntropyLoss",
    "reduction": "mean", "shuffle_training": True, "drop_last": False,
    "deterministic_algorithms": True, "augmentation": False,
    "scheduler": False, "early_stopping": False, "epoch_selection": False,
    "architecture_search": False,
}
ARCHITECTURES = {
    TEMPORAL: [
        {"layer": "Conv1d", "in_channels": 20, "out_channels": 32, "kernel_size": 3, "padding": 1},
        {"layer": "ReLU"},
        {"layer": "Conv1d", "in_channels": 32, "out_channels": 32, "kernel_size": 3, "padding": 1},
        {"layer": "ReLU"}, {"layer": "AdaptiveAvgPool1d", "output_size": 1},
        {"layer": "Flatten"}, {"layer": "Linear", "in_features": 32, "out_features": 2},
    ],
    SPATIOTEMPORAL: {
        "shared_spatial_encoder": [
            {"layer": "Conv2d", "in_channels": 2, "out_channels": 8, "kernel_size": 3, "padding": 1},
            {"layer": "ReLU"}, {"layer": "MaxPool2d", "kernel_size": 2, "stride": 2},
            {"layer": "Conv2d", "in_channels": 8, "out_channels": 16, "kernel_size": 3, "padding": 1},
            {"layer": "ReLU"}, {"layer": "AdaptiveAvgPool2d", "output_size": [1, 1]},
            {"layer": "Flatten"},
        ],
        "temporal_head": [
            {"layer": "Conv1d", "in_channels": 16, "out_channels": 16, "kernel_size": 3, "padding": 1},
            {"layer": "ReLU"}, {"layer": "AdaptiveAvgPool1d", "output_size": 1},
            {"layer": "Flatten"}, {"layer": "Linear", "in_features": 16, "out_features": 2},
        ],
    },
}


def method_contract():
    return {"training": deepcopy(TRAINING), "models": deepcopy(CONFIGS),
            "architectures": deepcopy(ARCHITECTURES), "temporal_points": 8,
            "input_channels": ["STRUCTURAL_Y", "RELATIVE_SOLUTE_FIELD_Y"]}


def _seed_cpu():
    import numpy as np
    import torch

    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)


def build_temporal_cnn():
    """Exact 5,122 parameters, deterministic initialization, no data inputs."""
    import torch

    _seed_cpu()
    model = torch.nn.Sequential(
        torch.nn.Conv1d(20, 32, kernel_size=3, padding=1), torch.nn.ReLU(),
        torch.nn.Conv1d(32, 32, kernel_size=3, padding=1), torch.nn.ReLU(),
        torch.nn.AdaptiveAvgPool1d(1), torch.nn.Flatten(), torch.nn.Linear(32, 2),
    ).cpu()
    model._study3_kind = TEMPORAL
    _check_model(model)
    return model


def build_spatiotemporal_cnn():
    """One spatial encoder shared across all eight real selected timepoints."""
    import torch

    _seed_cpu()

    class SharedSpatialTemporal(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.spatial_encoder = torch.nn.Sequential(
                torch.nn.Conv2d(2, 8, kernel_size=3, padding=1), torch.nn.ReLU(),
                torch.nn.MaxPool2d(2),
                torch.nn.Conv2d(8, 16, kernel_size=3, padding=1), torch.nn.ReLU(),
                torch.nn.AdaptiveAvgPool2d((1, 1)), torch.nn.Flatten(),
            )
            self.temporal_head = torch.nn.Sequential(
                torch.nn.Conv1d(16, 16, kernel_size=3, padding=1), torch.nn.ReLU(),
                torch.nn.AdaptiveAvgPool1d(1), torch.nn.Flatten(), torch.nn.Linear(16, 2),
            )
            self._study3_kind = SPATIOTEMPORAL

        def forward(self, values):
            require(values.ndim == 5 and tuple(values.shape[1:]) == (8, 2, 65, 65),
                    "spatiotemporal tensor shape divergence")
            batch = values.shape[0]
            embedded = self.spatial_encoder(values.reshape(batch * 8, 2, 65, 65))
            sequence = embedded.reshape(batch, 8, 16).transpose(1, 2)
            return self.temporal_head(sequence)

    model = SharedSpatialTemporal().cpu()
    _check_model(model)
    return model


def _check_model(model):
    import torch

    kind = getattr(model, "_study3_kind", None)
    require(kind in CONFIGS, "unknown CNN architecture")
    require(sum(p.numel() for p in model.parameters()) == CONFIGS[kind]["parameter_count"],
            "CNN parameter count divergence")
    require(all(p.requires_grad and p.device.type == "cpu" for p in model.parameters()),
            "all CNN parameters must be trainable CPU tensors")
    expected = (["Conv1d", "ReLU", "Conv1d", "ReLU", "AdaptiveAvgPool1d", "Flatten", "Linear"]
                if kind == TEMPORAL else
                ["Conv2d", "ReLU", "MaxPool2d", "Conv2d", "ReLU", "AdaptiveAvgPool2d", "Flatten",
                 "Conv1d", "ReLU", "AdaptiveAvgPool1d", "Flatten", "Linear"])
    leaves = [m for m in model.modules() if not list(m.children())]
    require([type(m).__name__ for m in leaves] == expected, "CNN architecture divergence")
    descriptions = (ARCHITECTURES[kind] if kind == TEMPORAL else
                    ARCHITECTURES[kind]["shared_spatial_encoder"] +
                    ARCHITECTURES[kind]["temporal_head"])
    for module, description in zip(leaves, descriptions):
        for name, expected_value in description.items():
            if name == "layer":
                continue
            observed = getattr(module, name)
            if isinstance(observed, tuple) and type(expected_value) is int:
                expected_value = (expected_value,) * len(observed)
            elif isinstance(expected_value, list):
                expected_value = tuple(expected_value)
            require(observed == expected_value, "CNN layer geometry divergence")
        if isinstance(module, (torch.nn.Conv1d, torch.nn.Conv2d)):
            require(module.groups == 1 and all(v == 1 for v in module.stride + module.dilation)
                    and module.padding_mode == "zeros" and module.bias is not None,
                    "CNN convolution defaults diverged")
        if isinstance(module, torch.nn.ReLU):
            require(module.inplace is False, "CNN activation defaults diverged")
        if isinstance(module, torch.nn.Flatten):
            require(module.start_dim == 1 and module.end_dim == -1, "CNN flatten defaults diverged")
    require(not any(isinstance(m, (torch.nn.Conv3d, torch.nn.GRU, torch.nn.LSTM,
                                  torch.nn.BatchNorm1d, torch.nn.BatchNorm2d,
                                  torch.nn.Dropout)) for m in model.modules()),
            "forbidden CNN module")
    return kind


def _inputs(kind, values, count=None):
    import numpy as np

    require(kind in CONFIGS, "only the two preregistered CNNs are admitted")
    require(isinstance(values, np.ndarray) and len(values.shape) > 1 and len(values) > 0
            and tuple(values.shape[1:]) == tuple(CONFIGS[kind]["input_shape"]),
            "CNN input shape divergence")
    require(count is None or len(values) == count, "CNN input/group mismatch")
    if kind == TEMPORAL:
        require(np.issubdtype(values.dtype, np.floating) and bool(np.isfinite(values).all()),
                "CNN1D requires finite floating LBP20 sequences")
    else:
        require(values.dtype == np.dtype("uint8"), "spatiotemporal input must be native uint8")


def fit_temporal_scaler(values, groups, *, fold):
    """Only explicitly designated fold-TRAIN groups contribute any statistic."""
    _training_groups(groups, fold, lambda event: None)
    _inputs(TEMPORAL, values, len(groups))
    import numpy as np

    source = values.astype(np.float64, copy=False)
    mean, std = source.mean(axis=(0, 2)), source.std(axis=(0, 2), ddof=0)
    std = np.where(std == 0, 1.0, std)
    require(bool(np.isfinite(mean).all()) and bool(np.isfinite(std).all()),
            "nonfinite TRAIN-only CNN scaler")
    return scaler_record(mean, std, groups, observations_per_group=8)


def _tensor(kind, values, scaler):
    import numpy as np
    import torch

    if kind == TEMPORAL:
        require(type(scaler) is dict and scaler.get("training_only") is True,
                "frozen TRAIN-only CNN scaler required")
        mean = np.asarray(scaler["mean"], dtype=np.float64)
        std = np.asarray(scaler["std"], dtype=np.float64)
        require(mean.shape == std.shape == (20,) and bool(np.isfinite(mean).all())
                and bool(np.isfinite(std).all()) and bool((std > 0).all()), "invalid CNN scaler")
        scaled = (values.astype(np.float64, copy=False) - mean[None, :, None]) / std[None, :, None]
        return torch.from_numpy(np.array(scaled, dtype=np.float32, order="C", copy=True))
    return torch.from_numpy(np.array(values, dtype=np.uint8, order="C", copy=True)).to(torch.float32) / 255.0


def _parameter_hash(model):
    digest = hashlib.sha256()
    for name, tensor in model.state_dict().items():
        digest.update(name.encode())
        digest.update(tensor.detach().cpu().numpy().tobytes(order="C"))
    return digest.hexdigest()


def fit_cnn(kind, X, groups, *, fold, on_event):
    """Exactly one thirty-epoch fit; callback refusal precedes scaler/model work."""
    metadata = _training_groups(groups, fold, on_event)
    _inputs(kind, X, len(groups))
    import torch

    on_event({"event": "FIT_START", "family": kind, "condition": kind, "fold": fold})
    scaler = fit_temporal_scaler(X, groups, fold=fold) if kind == TEMPORAL else None
    model = build_temporal_cnn() if kind == TEMPORAL else build_spatiotemporal_cnn()
    model._study3_scaler = deepcopy(scaler)
    initial_hash = _parameter_hash(model)
    generator = torch.Generator(device="cpu").manual_seed(42)
    batch_size = CONFIGS[kind]["batch_size"]

    class GroupDataset(torch.utils.data.Dataset):
        def __len__(self):
            return len(groups)

        def __getitem__(self, index):
            return index, int(groups[index].label)

    loader = torch.utils.data.DataLoader(GroupDataset(), batch_size=batch_size,
                                        shuffle=True, generator=generator,
                                        num_workers=0, drop_last=False)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=0.0,
                                 betas=(0.9, 0.999), eps=1e-8, amsgrad=False,
                                 foreach=None, maximize=False, capturable=False,
                                 differentiable=False, fused=None)
    criterion = torch.nn.CrossEntropyLoss(reduction="mean")
    losses, updates = [], 0
    start = time.perf_counter()
    model.train()
    for epoch in range(1, 31):
        total, seen = 0.0, 0
        for indices, labels in loader:
            values = _tensor(kind, X[indices.tolist()], scaler)
            optimizer.zero_grad(set_to_none=True)
            logits = model(values)
            require(tuple(logits.shape) == (len(labels), 2)
                    and bool(torch.isfinite(logits).all().item()), "nonfinite CNN training logits")
            loss = criterion(logits, labels.to(dtype=torch.long, device="cpu"))
            require(bool(torch.isfinite(loss).item()), "nonfinite CNN loss; no retry")
            loss.backward()
            optimizer.step()
            updates += 1
            seen += len(labels)
            total += float(loss.detach().item()) * len(labels)
        require(seen == len(groups), "CNN epoch group coverage divergence")
        average = total / seen
        require(math.isfinite(average), "nonfinite epoch loss")
        losses.append(average)
        on_event({"event": "FIT_EPOCH_COMPLETE", "family": kind, "condition": kind,
                  "fold": fold, "epoch": epoch, "training_groups_seen": seen})
    elapsed = time.perf_counter() - start
    require(updates == 30 * math.ceil(len(groups) / batch_size), "CNN update budget divergence")
    _check_model(model)
    model.eval()
    metadata.update(family=kind, condition=kind, fit_calls=1, training_runs=1,
                    parameter_count=CONFIGS[kind]["parameter_count"],
                    parameter_blocks=list(CONFIGS[kind]["parameter_blocks"]),
                    epochs=30, epoch_losses=losses, optimizer_updates=updates,
                    runtime_seconds=elapsed, random_seed=42, device="cpu", threads=1,
                    config={**deepcopy(TRAINING), **deepcopy(CONFIGS[kind])},
                    scaler=scaler, initial_parameter_sha256=initial_hash,
                    final_parameter_sha256=_parameter_hash(model),
                    torch_version=str(torch.__version__),
                    convergence="FIXED_EPOCH_BUDGET_COMPLETE",
                    epoch_loss_semantics="group-weighted mean of training batch losses across successive model states",
                    validation_evaluations_during_training=0,
                    dev_evaluations_during_training=0, test_evaluations_during_training=0)
    on_event({"event": "FIT_COMPLETE", "family": kind, "condition": kind, "fold": fold})
    return model, metadata


def predict_cnn(model, X):
    """Final-epoch inference with the frozen TRAIN scaler; no labels or fitting."""
    kind = _check_model(model)
    _inputs(kind, X)
    import torch

    require(hasattr(model, "_study3_scaler"), "a completed Study3 fit is required")
    batch_size = CONFIGS[kind]["batch_size"]
    predicted, logits_rows, probabilities = [], [], []
    model.eval()
    with torch.inference_mode():
        for start in range(0, len(X), batch_size):
            values = _tensor(kind, X[start:start + batch_size], model._study3_scaler)
            logits = model(values)
            require(tuple(logits.shape) == (len(values), 2)
                    and bool(torch.isfinite(logits).all().item()), "invalid CNN prediction")
            predicted.extend(logits.argmax(dim=1).tolist())
            logits_rows.extend(logits.tolist())
            probabilities.extend(torch.softmax(logits, dim=1).tolist())
    return {"predictions": predicted, "logits": logits_rows, "probabilities": probabilities,
            "classes": [0, 1], "decision_scores": None,
            "score_semantics": "FINAL_EPOCH_LOGITS_AND_SOFTMAX"}
