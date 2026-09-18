"""Solute identity authority contracts; only fresh synthetic repository fixtures."""

import copy
import hashlib
import importlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from snbi_fragmentation import ti2_authority as legacy
from snbi_fragmentation import ti2r_frag_authority as previous
from snbi_fragmentation import ti2r_frag_direct_authority as direct_previous

ROOT = Path(__file__).absolute().parents[1]
C2_SHA = "d" * 40


class ExplodingPath:
    def __fspath__(self):
        raise AssertionError("unauthorized asset path was examined")

    def __str__(self):
        raise AssertionError("unauthorized asset was formatted")


class SoluteAuthorityTests(unittest.TestCase):
    def setUp(self):
        # Import inside setup makes the preserved preimplementation RED explicit.
        self.auth = importlib.import_module("snbi_fragmentation.ti2r_solute_direct_authority")
        temp_parent = ROOT / ".bootstrap-test-tmp"
        self.assertFalse(temp_parent.is_symlink())
        temp_parent.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="solute-direct-authority-", dir=temp_parent)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        governance = {**legacy.CLOSED_STATE, **legacy.BOUNDARY_STATE}
        self.write("pyproject.toml", "[tool.snbi]\n" + "\n".join(
            f"{key} = {json.dumps(value)}" for key, value in governance.items()) + "\n")
        self.write(previous.AUTHORITY_PATH, json.dumps(previous.expected_authority("CLOSED_CONSUMED")))
        self.write(direct_previous.AUTHORITY_PATH, json.dumps(direct_previous.expected_authority("CLOSED_CONSUMED")))
        self.set_state("ACTIVE_ONE_SHOT")
        self.hashes = {}
        for relative in self.auth.FROZEN_TEXT_PATHS:
            if relative not in ("pyproject.toml", previous.AUTHORITY_PATH, direct_previous.AUTHORITY_PATH):
                self.write(relative, "{}\n")
            self.hashes[relative] = hashlib.sha256((self.root / relative).read_bytes()).hexdigest()
        self.payloads = {source: bytes(width * height * 3 // 2)
                         for source, (width, height) in self.auth.DIMENSIONS.items()}
        digests = {source: hashlib.sha256(payload).hexdigest() for source, payload in self.payloads.items()}
        self.assets = []
        self.exposure = {}
        for asset_id, role in self.auth.ASSET_ROLES.items():
            source, index = asset_id.split(":")
            width, height = self.auth.DIMENSIONS[source]
            self.assets.append({
                "asset_id": asset_id, "source_id": source, "frame_index": int(index), "role": role,
                "path": f"data/derived/ti2-pilot/{source}-{int(index):04d}.raw",
                "width": width, "height": height, "frame_bytes": len(self.payloads[source]),
                "image_sha256": digests[source], "pixel_format": "yuv420p", "bit_depth": 8,
            })
            self.exposure[asset_id] = {"holdout_eligible_this_phase": role == "holdout",
                                       "evidence": ["artifacts/evidence/TI2R_FRAG_DIRECT/result.json"],
                                       "previous_exposure": ["PRIOR_FRAGMENT_REFERENCE_USE" if source in ("ESM1", "ESM4") else "PRIOR_TI2_EXPOSURE_DOCUMENTED"]}
        identity = patch.object(self.auth, "_git_identity", return_value=(self.auth.BRANCH, C2_SHA))
        identity.start()
        self.addCleanup(identity.stop)

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def set_state(self, state):
        self.write(self.auth.AUTHORITY_PATH, json.dumps(self.auth.expected_authority(state)))

    def begin(self, **kwargs):
        arguments = dict(c2_sha=C2_SHA, frozen_hashes=self.hashes, assets=self.assets, exposure=self.exposure)
        arguments.update(kwargs)
        return self.auth.begin_session(self.root, **arguments)

    def materialize(self, asset_id):
        asset = next(item for item in self.assets if item["asset_id"] == asset_id)
        path = self.root / asset["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.payloads[asset["source_id"]])
        return path

    def development(self, session, pair="ESM2-to-ESM1"):
        for asset_id, role in self.auth.ASSET_ROLES.items():
            if role == "development" and asset_id.split(":")[0] in self.auth.PAIR_SOURCES[pair]:
                self.materialize(asset_id)
                self.auth.read_asset(session, asset_id, role=role)

    def test_exact_authority_and_finite_candidate_schema(self):
        state = self.auth.expected_authority("ACTIVE_ONE_SHOT")
        self.assertEqual(self.auth.validate_authority(state), [])
        self.assertEqual(state["phase"], "TI2R_SOLUTE_DIRECT")
        self.assertEqual(state["allowed_offsets"]["ESM2-to-ESM1"], {"x": [0], "y": [0]})
        self.assertEqual(state["allowed_offsets"]["ESM5-to-ESM4"], {"x": [0], "y": [0]})
        for key, value in (("max_invocations", True), ("ti3_plus_authorized", 0), ("ti2r_execution_authorized", "true"), ("unknown", True)):
            changed = copy.deepcopy(state)
            changed[key] = value
            self.assertTrue(self.auth.validate_authority(changed))

    def test_prepared_and_consumed_deny_before_asset_path_or_receipt(self):
        for state in ("PREPARED_INACTIVE", "CLOSED_CONSUMED"):
            self.set_state(state)
            with patch.object(self.auth, "_validate_assets") as assets, patch.object(self.auth, "_write_exclusive") as write:
                with self.assertRaises(self.auth.SoluteIOBlocked):
                    self.begin(assets=ExplodingPath())
                assets.assert_not_called()
                write.assert_not_called()

    def test_old_frag_must_be_consumed_and_legacy_cannot_be_reactivated(self):
        for old_state in ("PREPARED_INACTIVE", "ACTIVE_ONE_SHOT"):
            self.write(previous.AUTHORITY_PATH, json.dumps(previous.expected_authority(old_state)))
            with self.assertRaises(self.auth.SoluteAuthorityError):
                self.begin()
        self.write(previous.AUTHORITY_PATH, json.dumps(previous.expected_authority("CLOSED_CONSUMED")))
        project = (self.root / "pyproject.toml").read_text()
        self.write("pyproject.toml", project.replace("ti2_execution_authorized = false", "ti2_execution_authorized = true"))
        with self.assertRaises(self.auth.SoluteAuthorityError):
            self.begin()

    def test_fragment_direct_authority_must_also_be_consumed(self):
        for old_state in ("PREPARED_INACTIVE", "ACTIVE_ONE_SHOT"):
            self.write(direct_previous.AUTHORITY_PATH, json.dumps(direct_previous.expected_authority(old_state)))
            with self.assertRaises(self.auth.SoluteAuthorityError):
                self.begin()

    def test_exposure_requires_exact_fields_and_explicit_previous_exposure(self):
        mutations = (
            {"previous_exposure": []}, {"previous_exposure": [True]},
            {"holdout_eligible_this_phase": 1}, {"holdout_sealed": True},
            {"evidence": []}, {"evidence": [""]},
        )
        for mutation in mutations:
            exposure = copy.deepcopy(self.exposure)
            exposure["ESM1:73"].update(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(self.auth.SoluteIOBlocked):
                self.begin(exposure=exposure)
        exposure = copy.deepcopy(self.exposure)
        del exposure["ESM1:73"]["previous_exposure"]
        with self.assertRaises(self.auth.SoluteIOBlocked):
            self.begin(exposure=exposure)

    def test_dimension_divergence_blocks_before_any_experimental_path(self):
        for field, value in (("width", 1279), ("height", 1020), ("width", True)):
            assets = copy.deepcopy(self.assets)
            assets[0][field] = value
            with patch.object(self.auth, "_write_exclusive") as write:
                with self.assertRaisesRegex(self.auth.SoluteIOBlocked, "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE"):
                    self.begin(assets=assets)
                write.assert_not_called()
        self.assertFalse((self.root / "data").exists())

    def test_exact_twenty_asset_allowlist_forbids_esm3_esm6_role_and_path_aliases(self):
        mutations = (("source_id", "ESM3"), ("source_id", "ESM6"), ("role", "holdout"),
                     ("asset_id", "ESM1:73"), ("path", "data/derived/ti2-pilot/../other.raw"))
        for key, value in mutations:
            assets = copy.deepcopy(self.assets)
            assets[0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(self.auth.SoluteIOBlocked):
                self.begin(assets=assets)
        with self.assertRaises(self.auth.SoluteIOBlocked):
            self.begin(assets=self.assets[:-1])

    def test_receipt_precedes_pixels_and_is_single_use(self):
        session = self.begin()
        self.assertFalse((self.root / "data").exists())
        receipt = json.loads((self.root / self.auth.RECEIPT_PATH).read_text())
        self.assertEqual(receipt["phase"], "TI2R_SOLUTE_DIRECT")
        self.assertEqual(receipt["invocation_counter"], 1)
        self.assertEqual(receipt["experimental_bytes_before_receipt"], 0)
        self.assertEqual(len(receipt["allowed_assets"]), 20)
        self.assertEqual(session.opened_assets, [])
        with self.assertRaises(self.auth.SoluteIOBlocked):
            self.begin()
        with self.assertRaises(self.auth.SoluteIOBlocked):
            self.auth.SoluteSession(self.root, C2_SHA, {}, {}, b"{}")

    def test_frozen_text_hash_and_complete_input_set_required(self):
        self.write("configs/registration/ti2r-solute-direct-method.json", '{"modified":true}')
        with self.assertRaises(self.auth.SoluteIOBlocked):
            self.begin()
        with self.assertRaises(self.auth.SoluteIOBlocked):
            self.begin(frozen_hashes={"pyproject.toml": self.hashes["pyproject.toml"]})
        self.assertFalse((self.root / self.auth.RECEIPT_PATH).exists())

    def test_wrong_branch_or_changed_c2_prevents_asset_examination(self):
        for identity in (("main", C2_SHA), (self.auth.BRANCH, "f" * 40)):
            with patch.object(self.auth, "_git_identity", return_value=identity), patch.object(self.auth, "_validate_assets") as assets:
                with self.assertRaises(self.auth.SoluteIOBlocked):
                    self.begin()
                assets.assert_not_called()

    def test_allowed_read_is_native_and_only_once(self):
        self.materialize("ESM1:0")
        session = self.begin()
        self.assertEqual(self.auth.read_asset(session, "ESM1:0", role="development"), self.payloads["ESM1"])
        self.assertEqual(session.opened_assets[0]["bytes_read"], len(self.payloads["ESM1"]))
        self.assertTrue(session.opened_assets[0]["file_opened"])
        with self.assertRaises(self.auth.SoluteIOBlocked):
            self.auth.read_asset(session, "ESM1:0", role="development")

    def test_consumed_state_denies_before_path_coercion(self):
        session = self.begin()
        self.set_state("CLOSED_CONSUMED")
        with patch.object(self.auth, "_git_identity") as identity:
            with self.assertRaises(self.auth.SoluteIOBlocked):
                self.auth.read_asset(session, ExplodingPath(), role="development")
            identity.assert_not_called()
        with self.assertRaises(self.auth.SoluteIOBlocked):
            session.write_result({"forbidden": True})

    def test_forbidden_asset_and_holdout_role_never_reach_pixel_path(self):
        session = self.begin()
        for asset_id, role in (("ESM3:0", "development"), ("ESM6:0", "development"),
                               ("ESM1:73", "development"), (ExplodingPath(), "development")):
            with patch.object(session, "_require"), patch.object(self.auth, "_parent_fd") as path:
                with self.assertRaises(self.auth.SoluteIOBlocked):
                    self.auth.read_asset(session, asset_id, role=role)
                path.assert_not_called()

    def test_holdout_needs_phase_eligibility_and_frozen_identity(self):
        self.exposure["ESM1:73"]["holdout_eligible_this_phase"] = False
        session = self.begin()
        self.development(session)
        session.freeze_identity("ESM2-to-ESM1", {"offset": [0, 0], "development_pass": True})
        with self.assertRaises(self.auth.SoluteIOBlocked):
            self.auth.read_asset(session, "ESM1:73", role="holdout")
        self.assertNotIn("ESM1:73", session.attempted)

    def test_holdout_opens_only_after_six_development_assets_and_finite_freeze(self):
        session = self.begin()
        with self.assertRaises(self.auth.SoluteIOBlocked):
            session.freeze_identity("ESM2-to-ESM1", {"offset": [0, 0], "development_pass": True})
        with self.assertRaises(self.auth.SoluteIOBlocked):
            self.auth.read_asset(session, "ESM1:73", role="holdout")
        self.development(session)
        session.freeze_identity("ESM2-to-ESM1", {"offset": [0, 0], "development_pass": True})
        self.materialize("ESM1:73")
        self.assertEqual(self.auth.read_asset(session, "ESM1:73", role="holdout"), self.payloads["ESM1"])
        with self.assertRaises(self.auth.SoluteIOBlocked):
            session.freeze_identity("ESM2-to-ESM1", {"offset": [0, 0], "development_pass": True})

    def test_subpixel_bool_negative_and_outside_candidate_offsets_rejected(self):
        session = self.begin()
        for pair, offset in (("ESM2-to-ESM1", [0.0, 0]), ("ESM2-to-ESM1", [False, 0]),
                             ("ESM2-to-ESM1", [-1, 0]), ("ESM2-to-ESM1", [3, 0]),
                             ("ESM2-to-ESM1", [0, 7]), ("ESM5-to-ESM4", [0, 1])):
            with self.subTest(pair=pair, offset=offset), self.assertRaises(self.auth.SoluteIOBlocked):
                session.freeze_identity(pair, {"offset": offset, "development_pass": True})

    def test_negative_controls_cannot_be_promoted_to_transformations(self):
        session = self.begin()
        self.development(session)
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx or dy:
                    with self.subTest(dx=dx, dy=dy), self.assertRaises(self.auth.SoluteIOBlocked):
                        session.freeze_identity("ESM2-to-ESM1", {"offset": [dx, dy], "development_pass": True})
        with self.assertRaises(self.auth.SoluteIOBlocked):
            session.freeze_identity("ESM2-to-ESM1", {
                "offset": [0, 0], "development_pass": True,
                "matrix": [[1, 0, 1], [0, 1, 0], [0, 0, 1]],
            })
        session.freeze_identity("ESM2-to-ESM1", {
            "offset": [0, 0], "development_pass": True,
            "matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        })

    def test_eligibility_requires_positive_text_and_unknown_states_fail_closed(self):
        self.exposure["ESM1:73"]["evidence"] = []
        with self.assertRaises(self.auth.SoluteIOBlocked):
            self.begin()
        self.write(self.auth.AUTHORITY_PATH, '{"state":"UNKNOWN"}')
        with self.assertRaises(self.auth.SoluteAuthorityError):
            self.auth.load_authority(self.root)

    def test_symlink_missing_and_digest_divergence_fail_without_retry(self):
        missing = "ESM1:0"
        bad = self.materialize("ESM1:146")
        bad.write_bytes(b"x" * len(self.payloads["ESM1"]))
        link = self.materialize("ESM1:293")
        link.unlink()
        link.symlink_to(bad.name)
        session = self.begin()
        for asset_id in (missing, "ESM1:146", "ESM1:293"):
            with self.assertRaisesRegex(self.auth.SoluteIOBlocked, "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE"):
                self.auth.read_asset(session, asset_id, role="development")
        self.assertEqual(sum(item["file_opened"] for item in session.opened_assets), 1)

    def test_receipt_exposure_and_candidate_cannot_drift(self):
        session = self.begin()
        session.exposure["ESM1:73"]["holdout_eligible_this_phase"] = False
        with self.assertRaises(self.auth.SoluteIOBlocked):
            self.auth.read_asset(session, "ESM1:0", role="development")
        session.exposure["ESM1:73"]["holdout_eligible_this_phase"] = True
        self.development(session)
        session.freeze_identity("ESM2-to-ESM1", {"offset": [0, 0], "development_pass": True})
        self.write("artifacts/evidence/TI2R_SOLUTE_DIRECT/ESM2-to-ESM1-freeze.json", "{}")
        with self.assertRaises(self.auth.SoluteIOBlocked):
            self.auth.read_asset(session, "ESM1:73", role="holdout")
        (self.root / self.auth.RECEIPT_PATH).unlink()
        with self.assertRaisesRegex(self.auth.SoluteIOBlocked, "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE"):
            self.auth.read_asset(session, "ESM1:219", role="holdout")

    def test_result_exclusive_and_text_api_never_opens_experimental_paths(self):
        session = self.begin()
        session.write_result({"TI2R_SOLUTE_DIRECT": "BLOCKED_INTERRUPTED"})
        with self.assertRaises(FileExistsError):
            session.write_result({"TI2R_SOLUTE_DIRECT": "PASS"})
        for relative in ("data/source.json", "data/derived/ti2-pilot/ESM1-0000.raw", "../pyproject.toml", ExplodingPath()):
            with patch.object(self.auth, "_read_regular") as read, self.assertRaises(self.auth.SoluteIOBlocked):
                self.auth.read_text_file(self.root, relative)
            read.assert_not_called()


if __name__ == "__main__":
    unittest.main()
