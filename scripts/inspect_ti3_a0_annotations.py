"""Bounded TI3-A0 inspection of ten explicitly authorized existing buffers.

No ML, decoding, G2 kernel invocation, or additional frame selection.
The same guarded reader may be used once for the later extraction phase.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).absolute().parents[1]
EVIDENCE = ROOT / "artifacts/evidence/TI3_A0"
DIAGNOSTICS = ROOT / ".bootstrap-test-tmp/ti3-a0-20260919-inspection"
CHECKPOINT = "1e7f5e8b382e84fd1259637722ce9774ffed7df3"
ALLOWLIST = {"ESM3": (0, 73, 146, 219, 293), "ESM6": (0, 98, 197, 295, 394)}


def now():
    return datetime.now(timezone.utc).isoformat()


def read_relative(path):
    """Open every path component with NOFOLLOW, never traversing outside root."""
    p = Path(path)
    if p.is_absolute() or ".." in p.parts or not p.parts:
        raise ValueError("unsafe relative path")
    d = os.open(ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in p.parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=d)
            os.close(d)
            d = child
        fd = os.open(p.parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=d)
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            os.close(fd)
            raise ValueError("not a regular file")
        return fd
    finally:
        os.close(d)


def text_json(relative):
    with os.fdopen(read_relative(relative), "r", encoding="utf-8") as stream:
        return json.load(stream)


def write_json(name, value, exclusive=False):
    if Path(name).name != name or not name.endswith(".json"):
        raise ValueError("only a named evidence JSON output")
    flags = os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW
    flags |= os.O_EXCL if exclusive else os.O_TRUNC
    fd = os.open(EVIDENCE / name, flags, 0o644)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def preflight(phase):
    if phase not in {"characterization", "extraction"}:
        raise ValueError("phase outside authorization")
    if os.path.lexists(EVIDENCE / "results.json"):
        raise ValueError("terminal TI3-A0 evidence permanently closes access")
    for p in [ROOT / "artifacts", ROOT / "artifacts/evidence", EVIDENCE, ROOT / ".bootstrap-test-tmp"]:
        if not stat.S_ISDIR(p.lstat().st_mode):
            raise ValueError("output parent must be a real directory")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    if head != CHECKPOINT or branch != "feat/ti3-canonical-dataset-baseline":
        raise ValueError("checkpoint or branch divergence")
    authority = text_json("artifacts/evidence/TI3_A0/preflight.json")
    if authority["phase"] != "TI3_A0" or authority["allowed_phases"] != ["characterization", "extraction"]:
        raise ValueError("authority scope divergence")
    with os.fdopen(read_relative("artifacts/evidence/TI3_A0/authorization.md"), "rb") as stream:
        if hashlib.sha256(stream.read()).hexdigest() != authority["authorization_sha256"]:
            raise ValueError("authorization bytes differ")
    if text_json("artifacts/evidence/TI2R_SOLUTE_HOLDOUT/repair-1/terminal-state.json")["HOLDOUT_SOLUTE"] != "CONSUMED":
        raise ValueError("historical holdout must remain consumed")
    manifest = text_json("artifacts/evidence/TI3_A0/development-manifest.json")
    original = text_json("artifacts/metadata/ti2-pilot-manifest.json")
    originals = {(r["source_id"], r["frame_index"]): r for r in original["images"]}
    wanted = {(s, i) for s, indices in ALLOWLIST.items() for i in indices}
    actual = {(r["source_id"], r["frame_index"]) for r in manifest["assets"]}
    if actual != wanted or len(manifest["assets"]) != 10:
        raise ValueError("exact ten-asset allowlist required")
    for row in manifest["assets"]:
        source, index = row["source_id"], row["frame_index"]
        if row["path"] != f"data/derived/ti2-pilot/{source}-{index:04d}.raw":
            raise ValueError("noncanonical path")
        if row["use"] != "ANNOTATION_CONTRACT_DEVELOPMENT_ONLY" or row["final_test_eligible"] is not False:
            raise ValueError("permanent development exclusion required")
        expected = originals[(source, index)]
        for key in ("path", "width", "height", "frame_bytes", "image_sha256", "experimental_time_s", "pixel_format"):
            if row[key] != expected[key]:
                raise ValueError("pilot metadata divergence: " + key)
    receipt = {"phase": phase, "started_at_utc": now(), "checkpoint": head,
               "asset_ids": [r["asset_id"] for r in manifest["assets"]], "ml_runs": 0,
               "new_frame_access": False, "one_invocation_for_this_phase": True}
    write_json(phase + "-receipt.json", receipt, exclusive=True)
    audit = {"phase": phase, "started_at_utc": now(), "status": "STARTED", "assets": [],
             "open_attempts": 0, "open_count": 0, "content_bytes_read": 0,
             "max_source_opens_per_asset_in_this_phase": 1, "new_frames": 0}
    write_json(phase + "-io.json", audit, exclusive=True)
    return manifest["assets"], audit


def read_asset(row, audit):
    if any(a["asset_id"] == row["asset_id"] for a in audit["assets"]):
        raise ValueError("duplicate source open in phase")
    record = {"asset_id": row["asset_id"], "path": row["path"], "open_attempts": 1,
              "open_count": 0, "content_bytes_read": 0, "status": "OPEN_PENDING"}
    audit["assets"].append(record)
    audit["open_attempts"] += 1
    write_json(audit["phase"] + "-io.json", audit)
    try:
        fd = read_relative(row["path"])
        record["open_count"] = 1
        audit["open_count"] += 1
        with os.fdopen(fd, "rb") as stream:
            raw = stream.read(row["frame_bytes"] + 1)
        record["content_bytes_read"] = len(raw)
        audit["content_bytes_read"] += len(raw)
        record["sha256"] = hashlib.sha256(raw).hexdigest()
        if len(raw) != row["frame_bytes"] or record["sha256"] != row["image_sha256"]:
            raise ValueError("experimental custody divergence")
        record["status"] = "AUTHENTICATED"
        return raw
    except Exception:
        record["status"] = "FAILED"
        audit["status"] = "FAILED"
        raise
    finally:
        write_json(audit["phase"] + "-io.json", audit)


def planes(raw, width, height):
    import numpy as np
    n = width * height
    a = np.frombuffer(raw, dtype=np.uint8)
    if len(a) != n * 3 // 2:
        raise ValueError("invalid YUV420p size")
    return a[:n].reshape(height, width), a[n:n+n//4].reshape(height//2, width//2), a[n+n//4:].reshape(height//2, width//2)


def characterize():
    import numpy as np
    from scipy import ndimage
    from PIL import Image
    assets, audit = preflight("characterization")
    DIAGNOSTICS.mkdir(exist_ok=False)
    reports = []
    for row in assets:
        raw = read_asset(row, audit)
        y, u, v = planes(raw, row["width"], row["height"])
        distance = np.maximum(np.abs(u.astype(np.int16)-128), np.abs(v.astype(np.int16)-128))
        mask = (distance >= 20).repeat(2, axis=0).repeat(2, axis=1)
        labels, count = ndimage.label(mask, structure=np.ones((3, 3)))
        areas = np.bincount(labels.ravel())
        components = []
        for label, bounds in enumerate(ndimage.find_objects(labels), 1):
            if bounds is None:
                continue
            sy, sx = bounds
            components.append({"component_id": label, "pixels": int(areas[label]),
                               "bbox_xyxy": [sx.start, sy.start, sx.stop, sy.stop]})
        colored = distance >= 20
        pairs, frequencies = np.unique(np.stack([u[colored], v[colored]], axis=1), axis=0, return_counts=True)
        order = np.argsort(-frequencies)[:10]
        # Display-only BT.601 limited-range approximation. Analysis uses native U/V.
        uf = (u.astype(float)-128).repeat(2, axis=0).repeat(2, axis=1)
        vf = (v.astype(float)-128).repeat(2, axis=0).repeat(2, axis=1)
        yf = (y.astype(float)-16) * (255/219)
        rgb = np.stack([yf+1.596027*vf, yf-0.391762*uf-0.812968*vf, yf+2.017232*uf], axis=2)
        rgb = np.rint(np.clip(rgb, 0, 255)).astype(np.uint8)
        output = DIAGNOSTICS / (row["asset_id"].replace(":", "-") + ".png")
        Image.fromarray(rgb).save(output)
        with output.open("rb") as stream:
            png_hash = hashlib.sha256(stream.read()).hexdigest()
        reports.append({"asset_id": row["asset_id"], "width": row["width"], "height": row["height"],
                        "experimental_time_s": row["experimental_time_s"],
                        "native_chroma_counts": {str(t): int((distance >= t).sum()) for t in [8,16,20,32,64]},
                        "dominant_colored_uv": [{"u": int(pairs[k,0]), "v": int(pairs[k,1]), "count": int(frequencies[k])} for k in order],
                        "components_at_chroma20": components,
                        "diagnostic_path": str(output.relative_to(ROOT)), "diagnostic_sha256": png_hash})
    audit["status"] = "COMPLETED"
    audit["finished_at_utc"] = now()
    write_json("characterization-io.json", audit)
    write_json("characterization.json", {"phase":"CHARACTERIZATION_DEVELOPMENT_ONLY", "frames":reports,
        "method":"native chroma summaries and connected-component geometry, no event labels",
        "display":"illustrative BT.601 limited-range RGB; colorimetry not certified; analysis native YUV420p",
        "ml_runs":0, "new_frames":0}, exclusive=True)
    print(json.dumps({"status":"COMPLETED", "source_files_opened":audit["open_count"],
                      "source_bytes":audit["content_bytes_read"], "diagnostics":[r["diagnostic_path"] for r in reports]}))


if __name__ == "__main__":
    characterize()
