"""Exact 5,010-parameter Study2-C CNN, array-only CPU training and inference.

No import-time Torch initialization, source I/O, DEV epoch selection, file
export, scheduler or augmentation. The controller authorizes each one-shot fit
and supplies only the stage's admitted native uint8 pairs.
"""

import math
import random
import time

from .study2c_models import checked_pairs, require, validate_training_rows


CONFIG = {
    "seed": 42, "device": "cpu", "threads": 1, "num_workers": 0,
    "batch_size": 32, "epochs": 20, "shuffle_training": True,
    "input_shape": [2, 65, 65], "input_dtype": "uint8", "normalization": "float32/255.0",
    "parameter_count": 5010, "optimizer": "Adam", "learning_rate": 0.001,
    "weight_decay": 0.0, "betas": [0.9, 0.999], "eps": 1e-8,
    "amsgrad": False, "foreach": None, "maximize": False, "capturable": False,
    "differentiable": False, "fused": None,
    "loss": "CrossEntropyLoss(reduction=none)",
    "batch_objective": "sum(loss_i*weight_i)/sum(weight_i)",
    "deterministic_algorithms": True, "augmentation": False,
    "scheduler": False, "early_stopping": False, "dev_epoch_selection": False,
}
ARCHITECTURE = [
    {"layer": "Conv2d", "in_channels": 2, "out_channels": 16, "kernel_size": 3, "padding": 1},
    {"layer": "ReLU"}, {"layer": "MaxPool2d", "kernel_size": 2, "stride": 2},
    {"layer": "Conv2d", "in_channels": 16, "out_channels": 32, "kernel_size": 3, "padding": 1},
    {"layer": "ReLU"}, {"layer": "MaxPool2d", "kernel_size": 2, "stride": 2},
    {"layer": "AdaptiveAvgPool2d", "output_size": [1, 1]},
    {"layer": "Flatten"}, {"layer": "Linear", "in_features": 32, "out_features": 2},
]


def build_cnn_model():
    """Build the exact architecture and deny divergent parameter counts."""
    import torch

    model = torch.nn.Sequential(
        torch.nn.Conv2d(2, 16, kernel_size=3, padding=1), torch.nn.ReLU(),
        torch.nn.MaxPool2d(2, 2),
        torch.nn.Conv2d(16, 32, kernel_size=3, padding=1), torch.nn.ReLU(),
        torch.nn.MaxPool2d(2, 2), torch.nn.AdaptiveAvgPool2d((1, 1)),
        torch.nn.Flatten(), torch.nn.Linear(32, 2),
    ).cpu()
    require(sum(p.numel() for p in model.parameters() if p.requires_grad) == 5010,
            "BLOCKED_ARCHITECTURE_DIVERGENCE")
    return model


def fit_cnn(pairs, rows, weights, progress=None):
    """Train once for exactly twenty epochs; accepts no development evaluator."""
    checked_pairs(pairs)
    require(len(pairs) == len(rows), "native pair/row count mismatch")
    values, groups = validate_training_rows(rows, weights)
    require(progress is None or callable(progress), "progress must be callable or absent")
    import numpy as np
    import torch

    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    generator = torch.Generator(device="cpu")
    generator.manual_seed(42)
    model = build_cnn_model()

    class ArrayDataset(torch.utils.data.Dataset):
        def __len__(self):
            return len(rows)

        def __getitem__(self, index):
            # Copy only one admitted uint8 pair. No complete float32 corpus is
            # created or persisted; float normalization occurs per minibatch.
            pair = torch.from_numpy(np.array(pairs[index], dtype=np.uint8, copy=True, order="C"))
            return pair, rows[index]["label"], float(values[index])

    loader = torch.utils.data.DataLoader(ArrayDataset(), batch_size=32, shuffle=True,
                                        generator=generator, num_workers=0, drop_last=False)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, betas=(0.9, 0.999),
                                 eps=1e-8, weight_decay=0.0, amsgrad=False,
                                 foreach=None, maximize=False, capturable=False,
                                 differentiable=False, fused=None)
    criterion = torch.nn.CrossEntropyLoss(reduction="none")
    losses, updates = [], 0
    start = time.perf_counter()
    model.train()
    if progress:
        progress({"event": "CNN_TRAIN_START", "epochs": 20, "parameter_count": 5010})
    for epoch in range(1, 21):
        numerator, denominator, rows_seen = 0.0, 0.0, 0
        for native, labels, batch_weights in loader:
            inputs = native.to(dtype=torch.float32, device="cpu") / 255.0
            labels = labels.to(dtype=torch.long, device="cpu")
            batch_weights = batch_weights.to(dtype=torch.float32, device="cpu")
            optimizer.zero_grad(set_to_none=True)
            logits = model(inputs)
            individual = criterion(logits, labels)
            weight_sum = batch_weights.sum()
            weighted_sum = (individual * batch_weights).sum()
            loss = weighted_sum / weight_sum
            require(bool(torch.isfinite(loss).item()) and float(weight_sum.item()) > 0,
                    "nonfinite weighted CNN loss")
            loss.backward()
            optimizer.step()
            updates += 1
            rows_seen += len(labels)
            numerator += float(weighted_sum.detach().item())
            denominator += float(weight_sum.detach().item())
        require(rows_seen == len(rows) and denominator > 0, "CNN epoch coverage divergence")
        average = numerator / denominator
        require(math.isfinite(average), "nonfinite epoch loss")
        losses.append(average)
        if progress:
            progress({"event": "CNN_EPOCH_COMPLETE", "epoch": epoch,
                      "epoch_loss": average, "optimizer_updates": updates, "rows_seen": rows_seen})
    elapsed = time.perf_counter() - start
    require(len(losses) == 20 and updates == 20 * math.ceil(len(rows) / 32), "CNN training budget divergence")
    model.eval()
    metadata = {
        "family": "CNN_V2", "parameter_count": 5010, "parameter_blocks": [304, 4640, 66],
        "fit_calls": 1, "training_runs": 1, "epochs": 20, "epoch_losses": losses,
        "optimizer_updates": updates, "optimizer_steps": updates,
        "runtime_seconds": elapsed, "config": dict(CONFIG), "convergence": "FIXED_EPOCH_BUDGET_COMPLETE",
        "epoch_loss_semantics": "sum weighted minibatch sample losses / sum weights; forward losses use successive model states",
        "group_weight_limit": "Dataset weights sum to one per group; normalized minibatch SGD does not imply identical effective updates per group",
        "device": "cpu", "torch_version": torch.__version__, "threads": torch.get_num_threads(),
        "training_only": True, "dev_evaluations_during_training": 0,
        "test_evaluations_during_training": 0, **groups,
    }
    return model, metadata


def predict_cnn(model, pairs):
    """Single inference pass without labels; argmax of final-epoch logits."""
    checked_pairs(pairs)
    import numpy as np
    import torch

    require(sum(p.numel() for p in model.parameters() if p.requires_grad) == 5010,
            "BLOCKED_ARCHITECTURE_DIVERGENCE")
    require(all(p.device.type == "cpu" for p in model.parameters()), "CNN inference must remain CPU")
    model.eval()
    predictions, logits_rows, probabilities = [], [], []
    with torch.inference_mode():
        for start in range(0, len(pairs), 32):
            native = np.array(pairs[start:start + 32], dtype=np.uint8, copy=True, order="C")
            inputs = torch.from_numpy(native).to(dtype=torch.float32) / 255.0
            logits = model(inputs)
            require(tuple(logits.shape) == (len(native), 2) and bool(torch.isfinite(logits).all().item()),
                    "invalid final-epoch CNN logits")
            probability = torch.softmax(logits, dim=1)
            predictions.extend(int(value) for value in logits.argmax(dim=1).tolist())
            logits_rows.extend(logits.tolist())
            probabilities.extend(probability.tolist())
    return {"predictions": predictions, "logits": logits_rows, "probabilities": probabilities,
            "classes": [0, 1], "decision_scores": None,
            "score_semantics": "FINAL_EPOCH_LOGITS_AND_SOFTMAX; argmax class; no threshold search"}
