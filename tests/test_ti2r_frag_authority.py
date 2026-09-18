"""Single-use custody contracts using only fresh synthetic repository fixtures."""

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from snbi_fragmentation import ti2_authority as legacy
from snbi_fragmentation import ti2r_frag_authority as authority


ROOT = Path(__file__).absolute().parents[1]
C2_SHA = "c" * 40
IDENTITY = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


class ExplodingPath:
    def __fspath__(self):
        raise AssertionError("an unauthorized asset must not be coerced")

    def __str__(self):
        raise AssertionError("an unauthorized asset must not be formatted")


class FragAuthorityTests(unittest.TestCase):
    def setUp(self):
        temporary_root = ROOT / ".bootstrap-test-tmp"
        self.assertFalse(temporary_root.is_symlink())
        temporary_root.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="frag-authority-", dir=temporary_root)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        governance = {**legacy.CLOSED_STATE, **legacy.BOUNDARY_STATE}
        self.project = "[tool.snbi]\n" + "\n".join(f"{key} = {json.dumps(value)}" for key, value in governance.items()) + "\n"
        self.write("pyproject.toml", self.project)
        self.set_state("ACTIVE_ONE_SHOT")
        self.hashes = {}
        for relative in authority.FROZEN_TEXT_PATHS:
            if relative != "pyproject.toml":
                self.write(relative, "{}\n")
            self.hashes[relative] = hashlib.sha256((self.root / relative).read_bytes()).hexdigest()
        self.payload = b"synthetic-native-buffer-only\x00\x01\x02"
        self.assets = []
        self.exposure = {}
        for asset_id, role in authority.ASSET_ROLES.items():
            source, index = asset_id.split(":")
            self.assets.append({
                "source_id": source, "frame_index": int(index),
                "path": f"data/derived/ti2-pilot/{source}-{int(index):04d}.raw",
                "frame_bytes": len(self.payload), "image_sha256": hashlib.sha256(self.payload).hexdigest(),
            })
            self.exposure[asset_id] = {
                "validation_sealed": role == "validation",
                "evidence": ["synthetic fixture: positively attested prior non-use"],
            }
        identity = patch.object(authority, "_git_identity", return_value=(authority.BRANCH, C2_SHA))
        identity.start()
        self.addCleanup(identity.stop)

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def set_state(self, state):
        self.write(authority.AUTHORITY_PATH, json.dumps(authority.expected_authority(state)))

    def begin(self, **overrides):
        values = dict(c2_sha=C2_SHA, frozen_hashes=self.hashes, assets=self.assets, exposure=self.exposure)
        values.update(overrides)
        return authority.begin_session(self.root, **values)

    def materialize_synthetic(self):
        for asset in self.assets:
            path = self.root / asset["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(self.payload)

    def freeze_bottom_up(self, session):
        for asset_id, role in authority.ASSET_ROLES.items():
            if role == "development" and asset_id.split(":")[0] in ("ESM1", "ESM3"):
                authority.read_asset(session, asset_id, role=role)
        session.freeze_candidate("ESM3-to-ESM1", {"matrix": IDENTITY, "development_pass": True})

    def test_exact_schema_rejects_unknown_truthy_fields_and_nested_bool_indices(self):
        for key, value in (("max_invocations", True), ("ti3_plus_authorized", 0),
                           ("ti2r_execution_authorized", "true"), ("extra_authority", True)):
            state = authority.expected_authority("ACTIVE_ONE_SHOT")
            state[key] = value
            with self.subTest(key=key):
                self.assertTrue(authority.validate_authority(state))
        state = authority.expected_authority("ACTIVE_ONE_SHOT")
        state["allowed_frame_indices"]["ESM1"]["development"][0] = False
        self.assertTrue(authority.validate_authority(state))

    def test_prepared_and_consumed_deny_before_asset_or_receipt_io(self):
        for state in ("PREPARED_INACTIVE", "CLOSED_CONSUMED"):
            self.set_state(state)
            with self.subTest(state=state), patch.object(authority, "_validate_assets") as assets, patch.object(authority, "_write_exclusive") as write:
                with self.assertRaises(authority.FragIOBlocked):
                    self.begin(assets=ExplodingPath())
                assets.assert_not_called()
                write.assert_not_called()

    def test_legacy_concurrent_authority_rejected_before_new_namespace_open(self):
        self.write("pyproject.toml", self.project.replace('ti2_execution_authorized = false', 'ti2_execution_authorized = true'))
        with patch.object(authority, "_read_regular") as read:
            with self.assertRaises(authority.FragAuthorityError):
                self.begin()
            read.assert_not_called()

    def test_duplicate_json_and_symlink_authority_fail_closed(self):
        self.write(authority.AUTHORITY_PATH, '{"state":"ACTIVE_ONE_SHOT","state":"ACTIVE_ONE_SHOT"}')
        with self.assertRaises(authority.FragAuthorityError):
            authority.load_authority(self.root)
        path = self.root / authority.AUTHORITY_PATH
        path.unlink()
        self.write("configs/authority/synthetic-target.json", json.dumps(authority.expected_authority("ACTIVE_ONE_SHOT")))
        path.symlink_to("synthetic-target.json")
        with self.assertRaises(authority.FragAuthorityError):
            authority.load_authority(self.root)

    def test_exact_twenty_assets_excludes_esm2_esm5_and_alias_paths_before_io(self):
        for source in ("ESM2", "ESM5"):
            changed = copy.deepcopy(self.assets)
            changed[0]["source_id"] = source
            with self.subTest(source=source), patch.object(authority, "_write_exclusive") as write:
                with self.assertRaises(authority.FragIOBlocked):
                    self.begin(assets=changed)
                write.assert_not_called()
        changed = copy.deepcopy(self.assets)
        changed[0]["path"] = "data/derived/ti2-pilot/../elsewhere.raw"
        with self.assertRaises(authority.FragIOBlocked):
            self.begin(assets=changed)
        with self.assertRaises(authority.FragIOBlocked):
            self.begin(assets=self.assets[:-1])

    def test_exclusive_receipt_created_before_any_experimental_path(self):
        self.assertFalse((self.root / "data").exists())
        session = self.begin()
        self.assertFalse((self.root / "data").exists())
        receipt = json.loads((self.root / authority.RECEIPT_PATH).read_text())
        self.assertEqual(receipt["invocation_counter"], 1)
        self.assertEqual(receipt["experimental_bytes_before_receipt"], 0)
        self.assertEqual(set(receipt["allowed_assets"]), set(authority.ASSET_ROLES))
        self.assertEqual(session.content_bytes_read, 0)
        with self.assertRaisesRegex(authority.FragIOBlocked, "already consumed"):
            self.begin()
        with self.assertRaisesRegex(authority.FragIOBlocked, "atomic single-use receipt"):
            authority.Session(self.root, C2_SHA, {}, {}, b"{}")

    def test_mutated_frozen_input_or_incomplete_hashes_block_receipt(self):
        self.write("configs/registration/ti2r-frag-method.json", '{"changed":true}')
        with self.assertRaisesRegex(authority.FragIOBlocked, "hash mismatch"):
            self.begin()
        self.assertFalse((self.root / authority.RECEIPT_PATH).exists())
        with self.assertRaises(authority.FragIOBlocked):
            self.begin(frozen_hashes={"pyproject.toml": self.hashes["pyproject.toml"]})

    def test_wrong_branch_or_c2_head_denies_before_experimental_path(self):
        for identity in (("main", C2_SHA), (authority.BRANCH, "d" * 40)):
            with self.subTest(identity=identity), patch.object(authority, "_git_identity", return_value=identity), patch.object(authority, "_validate_assets") as assets:
                with self.assertRaises(authority.FragIOBlocked):
                    self.begin()
                assets.assert_not_called()

    def test_exact_synthetic_read_hash_size_and_no_reopening(self):
        self.materialize_synthetic()
        session = self.begin()
        self.assertEqual(authority.read_asset(session, "ESM1:0", role="development"), self.payload)
        self.assertEqual(session.content_bytes_read, len(self.payload))
        self.assertEqual(session.opened_assets, [{"asset_id": "ESM1:0", "role": "development", "status": "PASS", "bytes_read": len(self.payload)}])
        with self.assertRaisesRegex(authority.FragIOBlocked, "already attempted"):
            authority.read_asset(session, "ESM1:0", role="development")

    def test_unauthorized_asset_and_role_never_reach_path_io(self):
        session = self.begin()
        for asset_id, role in (("ESM2:0", "development"), ("ESM5:0", "development"),
                               ("ESM1:73", "development"), (ExplodingPath(), "development")):
            with self.subTest(asset_type=type(asset_id).__name__), patch.object(session, "_require"), patch.object(authority, "_parent_fd") as path:
                with self.assertRaises(authority.FragIOBlocked):
                    authority.read_asset(session, asset_id, role=role)
                path.assert_not_called()

    def test_consumption_denies_before_asset_coercion_or_experimental_path(self):
        session = self.begin()
        self.set_state("CLOSED_CONSUMED")
        with patch.object(authority, "_git_identity") as identity:
            with self.assertRaises(authority.FragIOBlocked):
                authority.read_asset(session, ExplodingPath(), role="development")
            identity.assert_not_called()
        with self.assertRaises(authority.FragIOBlocked):
            session.write_result({"result": "forbidden after closure"})

    def test_validation_denied_without_positive_seal_even_after_candidate(self):
        self.materialize_synthetic()
        self.exposure["ESM1:73"]["validation_sealed"] = False
        session = self.begin()
        self.freeze_bottom_up(session)
        with patch.object(session, "_require"), patch.object(authority, "_parent_fd") as path:
            with self.assertRaisesRegex(authority.FragIOBlocked, "positive custody"):
                authority.read_asset(session, "ESM1:73", role="validation")
            path.assert_not_called()

    def test_validation_denied_before_freeze_then_opens_once(self):
        self.materialize_synthetic()
        session = self.begin()
        with self.assertRaisesRegex(authority.FragIOBlocked, "frozen development candidate"):
            authority.read_asset(session, "ESM1:73", role="validation")
        self.freeze_bottom_up(session)
        freeze = self.root / "artifacts/evidence/TI2R_FRAG/ESM3-to-ESM1-freeze.json"
        self.assertEqual(json.loads(freeze.read_text())["record"]["matrix"], IDENTITY)
        self.assertEqual(authority.read_asset(session, "ESM1:73", role="validation"), self.payload)
        with self.assertRaises(authority.FragIOBlocked):
            session.freeze_candidate("ESM3-to-ESM1", {"matrix": IDENTITY, "development_pass": True})
        freeze.write_text("{}")
        with self.assertRaisesRegex(authority.FragIOBlocked, "immutable freeze"):
            authority.read_asset(session, "ESM1:219", role="validation")

    def test_positive_seal_requires_nonempty_affirmative_text_reference(self):
        self.exposure["ESM1:73"]["evidence"] = []
        with self.assertRaisesRegex(authority.FragIOBlocked, "positive validation custody"):
            self.begin()

    def test_reflection_and_premature_candidate_rejected(self):
        session = self.begin()
        for matrix in ([[[-1, 0, 0], [0, 1, 0], [0, 0, 1]],
                        [[-1, 0, 0], [0, -1, 0], [0, 0, 1]],
                        [[1, 0, 0], [0, 1, 0], [0.1, 0, 1]]]):
            with self.subTest(matrix=matrix), self.assertRaises(authority.FragIOBlocked):
                session.freeze_candidate("ESM3-to-ESM1", {"matrix": matrix, "development_pass": True})
        with self.assertRaisesRegex(authority.FragIOBlocked, "all six development"):
            session.freeze_candidate("ESM3-to-ESM1", {"matrix": IDENTITY, "development_pass": True})

    def test_missing_size_digest_and_symlink_pilot_fail_without_retry(self):
        self.materialize_synthetic()
        paths = {f"{a['source_id']}:{a['frame_index']}": self.root / a["path"] for a in self.assets}
        paths["ESM1:0"].unlink()
        paths["ESM1:146"].write_bytes(b"wrong size")
        paths["ESM1:293"].write_bytes(b"x" * len(self.payload))
        paths["ESM3:0"].unlink()
        paths["ESM3:0"].symlink_to(paths["ESM3:146"].name)
        session = self.begin()
        for asset_id in ("ESM1:0", "ESM1:146", "ESM1:293", "ESM3:0"):
            with self.subTest(asset_id=asset_id), self.assertRaisesRegex(authority.FragIOBlocked, "BLOCKED_PILOT_UNAVAILABLE"):
                authority.read_asset(session, asset_id, role="development")
        self.assertEqual(session.content_bytes_read, len(self.payload))
        self.assertEqual(len(session.attempted), 4)

    def test_directory_symlink_rejected_without_following(self):
        session = self.begin()
        (self.root / "synthetic-alternative").mkdir()
        (self.root / "data").symlink_to("synthetic-alternative", target_is_directory=True)
        with self.assertRaisesRegex(authority.FragIOBlocked, "BLOCKED_PILOT_UNAVAILABLE"):
            authority.read_asset(session, "ESM1:0", role="development")
        self.assertEqual(session.content_bytes_read, 0)

    def test_receipt_and_in_memory_allowlist_are_immutable(self):
        session = self.begin()
        session.assets["ESM1:0"]["path"] = "data/forbidden.raw"
        with self.assertRaisesRegex(authority.FragIOBlocked, "drifted"):
            authority.read_asset(session, "ESM1:0", role="development")
        receipt = self.root / authority.RECEIPT_PATH
        receipt.write_text("{}")
        with self.assertRaisesRegex(authority.FragIOBlocked, "receipt changed"):
            authority.read_asset(session, "ESM1:0", role="development")

    def test_result_written_only_once_under_active_receipt(self):
        session = self.begin()
        session.write_result({"TI2R_FRAG": "BLOCKED_INTERRUPTED"})
        result = self.root / "artifacts/evidence/TI2R_FRAG/result.json"
        self.assertEqual(json.loads(result.read_text())["TI2R_FRAG"], "BLOCKED_INTERRUPTED")
        with self.assertRaises(FileExistsError):
            session.write_result({"TI2R_FRAG": "PASS"})

    def test_text_reader_rejects_experimental_paths_before_open(self):
        for relative in ("data/derived/ti2-pilot/ESM1-0000.raw", "data/source.json", "../pyproject.toml", ExplodingPath()):
            with patch.object(authority, "_read_regular") as read, self.assertRaises(authority.FragIOBlocked):
                authority.read_text_file(self.root, relative)
            read.assert_not_called()


if __name__ == "__main__":
    unittest.main()
