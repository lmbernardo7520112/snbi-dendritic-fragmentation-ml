"""Frozen TI3-B operations on already authorized in-memory TRAIN/DEV inputs.

No I/O, registration, baseline rerun, sample selection or model persistence.
The caller owns the immutable sample manifest, paired provenance, exclusive
receipt, single-read custody and hash checks. Array-only feature/model helpers
accept only inputs admitted by those controls; they cannot infer provenance.
"""

import math

from .ti3_baseline import (
    BaselineContractError, REQUIRED_VERSIONS, RF_PARAMETERS,
    _classification_metrics, _scientific_runtime, _validate_learning_inputs,
    lbp_features,
)
from .ti3_dataset import ACQUISITIONS, DIMENSIONS, FRAME_SPLITS, patch_xyxy, support_xyxy


STRUCTURAL_FOR_SOLUTAL = {"ESM2": "ESM1", "ESM5": "ESM4"}
ALLOWED_SOLUTAL_FRAMES = frozenset({
    ("ESM2", 73), ("ESM2", 146), ("ESM2", 219), ("ESM5", 98), ("ESM5", 197),
})
STRUCTURAL_DEV_BALANCED_ACCURACY = 0.6875
FEATURE_DIMENSION = 20


class AblationContractError(ValueError):
    """A violation is terminal; no replacement, coordinate adjustment or retry."""

    def __init__(self, code, message):
        self.code = code
        super().__init__(f"{code}: {message}")


def _require(condition, code, message):
    if not condition:
        raise AblationContractError(code, message)


def _solute_metadata(image, structural_samples):
    """Deny all unauthorized metadata before inspecting buffer or array values."""
    _require(type(image) is dict, "CONFIGURATION_DIVERGENCE", "solute image metadata required")
    source, frame = image.get("source_id"), image.get("frame_index")
    _require(type(source) is str and type(frame) is int,
             "FORBIDDEN_INPUT", "explicit solute source/frame required")
    _require((source, frame) in ALLOWED_SOLUTAL_FRAMES,
             "FORBIDDEN_INPUT", "input outside exact solutal TRAIN/DEV allowlist")
    structural_source = STRUCTURAL_FOR_SOLUTAL[source]
    split = FRAME_SPLITS[(structural_source, frame)]
    width, height = DIMENSIONS[structural_source]
    acquisition = ACQUISITIONS[structural_source]
    _require(image.get("split") == split, "FORBIDDEN_INPUT", "solute image split differs")
    _require(type(image.get("width")) is int and type(image.get("height")) is int
             and (image["width"], image["height"]) == (width, height)
             and image.get("acquisition_id") == acquisition,
             "CONFIGURATION_DIVERGENCE", "native dimensions or acquisition differ")
    _require(image.get("pixel_format") == "yuv420p" and type(image.get("bit_depth")) is int
             and image["bit_depth"] == 8 and type(image.get("frame_bytes")) is int
             and image["frame_bytes"] == width * height * 3 // 2,
             "CONFIGURATION_DIVERGENCE", "native representation differs")
    _require(type(structural_samples) is list and structural_samples,
             "CONFIGURATION_DIVERGENCE", "original structural samples required")
    support = support_xyxy(width, height)
    boxes, ids = [], set()
    for sample in structural_samples:
        _require(type(sample) is dict, "CONFIGURATION_DIVERGENCE", "sample metadata required")
        _require(sample.get("source_id") == structural_source
                 and type(sample.get("frame_index")) is int and sample["frame_index"] == frame
                 and sample.get("split") == split,
                 "FORBIDDEN_INPUT", "structural and solutal source/frame/split must match")
        _require(sample.get("acquisition_id") == acquisition
                 and type(sample.get("width")) is int and type(sample.get("height")) is int
                 and (sample["width"], sample["height"]) == (width, height),
                 "CONFIGURATION_DIVERGENCE", "sample native provenance differs")
        sample_id = sample.get("sample_id")
        _require(type(sample_id) is str and sample_id and sample_id not in ids,
                 "CONFIGURATION_DIVERGENCE", "sample ID missing or duplicated")
        ids.add(sample_id)
        fields = ("center_x", "center_y", "patch_radius_px", "patch_side_px")
        _require(all(type(sample.get(key)) is int for key in fields)
                 and sample["patch_radius_px"] == 32 and sample["patch_side_px"] == 65,
                 "CONFIGURATION_DIVERGENCE", "unchanged integer 65x65 patch geometry required")
        box = patch_xyxy(sample["center_x"], sample["center_y"])
        _require(sample.get("patch_xyxy") == box and sample.get("mapping_offset_xy") == [0, 0],
                 "CONFIGURATION_DIVERGENCE", "frozen identity crop must not change")
        _require(support[0] <= box[0] < box[2] <= support[2]
                 and support[1] <= box[1] < box[3] <= support[3],
                 "BLOCKED_SOLUTAL_SUPPORT", "whole patch lacks frozen native geometric support")
        boxes.append((sample_id, box))
    return width, height, boxes


def checked_solutal_luminance(raw, image_metadata, structural_samples):
    """Admit unchanged native Y using the historical solutal geometry only.

    G2_SOLUTE excludes ceil(12% top), ceil(15% bottom) and four border pixels,
    explicitly without chroma classification. TI3's existing one-pixel erosion
    is retained for the LBP R=1 footprint. All pixels of every frozen patch must
    be supported. U/V neither define overlays nor change admission. This is
    geometric input support, not a newly certified scientific ROI or a measure
    of solute concentration. Structural chroma support remains the caller's
    independent, unchanged TI3-A check.
    """
    width, height, boxes = _solute_metadata(image_metadata, structural_samples)
    _require(type(raw) is bytes, "NATIVE_BUFFER_MISMATCH", "immutable native bytes required")
    count = width * height
    _require(len(raw) == count * 3 // 2,
             "NATIVE_BUFFER_MISMATCH", "complete native YUV420p buffer required")
    np = _scientific_runtime()
    luminance = np.frombuffer(raw, dtype=np.uint8, count=count).reshape(height, width)
    luminance.setflags(write=False)
    return luminance, {
        "status": "PASS", "sample_count": len(boxes),
        "samples_checked": [sample_id for sample_id, _ in boxes],
        "support_xyxy": support_xyxy(width, height),
        "support_contract": "SOLUTAL_GEOMETRY_12PCT_15PCT_BORDER4_EROSION1_NO_CHROMA",
        "representation": "NATIVE_Y_RELATIVE_SOLUTE_FIELD",
    }


def extract_solutal_patch(luminance, image_metadata, structural_sample):
    """Copy the exact paired 65x65 native Y crop, with metadata checked first."""
    width, height, boxes = _solute_metadata(image_metadata, [structural_sample])
    np = _scientific_runtime()
    _require(isinstance(luminance, np.ndarray) and luminance.dtype == np.dtype("uint8")
             and luminance.shape == (height, width),
             "NATIVE_BUFFER_MISMATCH", "unchanged native uint8 luminance required")
    _, (x0, y0, x1, y1) = boxes[0]
    return luminance[y0:y1, x0:x1].copy()


def multimodal_features(structural_patch, solutal_patch):
    """Concatenate the unchanged TI3-A histograms in structural/solutal order."""
    np = _scientific_runtime()
    structural = lbp_features(structural_patch)
    solutal = lbp_features(solutal_patch)
    return np.concatenate((structural, solutal))


def _validate_features(np, features, labels, split):
    _require(isinstance(features, np.ndarray) and features.ndim == 2
             and features.shape[0] > 0 and features.shape[1] == FEATURE_DIMENSION
             and features.dtype.kind in "fiu",
             "FEATURE_CONTRACT", f"{split} requires a numeric N-by-20 matrix")
    # Reuse both ten-feature histogram and weak-label contracts independently.
    try:
        _validate_learning_inputs(np, features[:, :10], labels, split)
        _validate_learning_inputs(np, features[:, 10:], labels, split)
    except BaselineContractError as exc:
        raise AblationContractError("FEATURE_CONTRACT", str(exc)) from exc


def development_decision(multimodal_balanced_accuracy):
    """Strict improvement only; an exact tie retains the simpler frozen model."""
    _require(type(multimodal_balanced_accuracy) in (int, float)
             and math.isfinite(multimodal_balanced_accuracy)
             and 0.0 <= multimodal_balanced_accuracy <= 1.0,
             "METRIC_CONTRACT", "finite balanced accuracy in [0,1] required")
    delta = float(multimodal_balanced_accuracy - STRUCTURAL_DEV_BALANCED_ACCURACY)
    return {
        "structural_reference_balanced_accuracy": STRUCTURAL_DEV_BALANCED_ACCURACY,
        "delta_dev_balanced_accuracy": delta,
        "dev_modality_preference": ("STRUCTURAL_PLUS_RELATIVE_SOLUTE" if delta > 0.0
                                    else "STRUCTURAL_ONLY"),
        "decision_scope": "INTERNAL_DEVELOPMENT_ONLY_NOT_EXTERNAL_GENERALIZATION",
    }


def evaluate_ablation(train_features, train_labels, dev_features, dev_labels):
    """One RF fit at the original defaults; no structural-baseline invocation.

    This array-only function is not an authority boundary. Only the caller's
    frozen manifest and exclusive receipt authorize scientific invocation.
    """
    np = _scientific_runtime()
    _validate_features(np, train_features, train_labels, "TRAIN")
    _validate_features(np, dev_features, dev_labels, "DEVELOPMENT")
    from sklearn.ensemble import RandomForestClassifier

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    parameters = model.get_params(deep=True)
    _require(parameters == RF_PARAMETERS, "MODEL_CONTRACT", "RF defaults differ from TI3-A")
    model.fit(train_features, train_labels)
    evaluations = {}
    for split, features, labels in (
        ("TRAIN", train_features, train_labels), ("DEVELOPMENT", dev_features, dev_labels),
    ):
        prediction = model.predict(features)
        probability = model.predict_proba(features)
        _require(np.array_equal(model.classes_, np.array([0, 1]))
                 and prediction.shape == labels.shape
                 and probability.shape == (len(labels), 2)
                 and np.isfinite(probability).all()
                 and not (probability < 0).any() and not (probability > 1).any()
                 and np.allclose(probability.sum(axis=1), 1.0, rtol=0.0, atol=1e-12),
                 "MODEL_CONTRACT", "RF predictions or probabilities violate frozen contract")
        evaluations[split] = {
            **_classification_metrics(labels, prediction), "true_labels": labels.tolist(),
            "predicted_labels": prediction.tolist(),
            "probabilities_class_order_0_1": probability.tolist(),
        }
    return {
        "status": "COMPLETED", "claim": "CONCORDANCE_WITH_PUBLISHED_LOCATION_WEAK_LABELS",
        "positive_semantics": "PUBLISHED_FRAGMENTATION_LOCATION_PRESENT",
        "background_semantics": "BACKGROUND_CANDIDATE_NOT_PHYSICAL_ABSENCE",
        "solute_semantics": "RELATIVE_SOLUTE_FIELD", "feature_dimension": FEATURE_DIMENSION,
        "feature_order": ["STRUCTURAL_LBP_10", "SOLUTAL_LBP_10"],
        "primary_metric": "balanced_accuracy", "class_order": [0, 1],
        "parameters": parameters, "dependency_versions": dict(REQUIRED_VERSIONS),
        "fit_calls": 1, "structural_baseline_fit_calls": 0, "tuning_runs": 0,
        "evaluations": evaluations, "final_test_evaluated": False,
        **development_decision(evaluations["DEVELOPMENT"]["balanced_accuracy"]),
    }
