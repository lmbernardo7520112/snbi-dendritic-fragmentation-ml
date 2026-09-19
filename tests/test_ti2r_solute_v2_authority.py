"""V2 authority tests use only fresh synthetic fixtures inside the repository."""

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from snbi_fragmentation import ti2_authority as legacy
from snbi_fragmentation import ti2r_frag_authority as frag
from snbi_fragmentation import ti2r_frag_direct_authority as direct
from snbi_fragmentation import ti2r_solute_direct_authority as solute
from snbi_fragmentation import ti2r_solute_v2_authority as auth


ROOT = Path(__file__).absolute().parents[1]
C1_SHA = "c" * 40


class ExplodingPath:
    def __fspath__(self):
        raise AssertionError("forbidden path was examined")

    def __str__(self):
        raise AssertionError("forbidden input was formatted")


def ci_evidence():
    jobs = [{"name": name, "status": "completed", "conclusion": "success",
             "steps": [{"name": "synthetic contract", "status": "completed", "conclusion": "success"}]}
            for name in ("deterministic-contracts", "scientific-synthetic-contracts")]
    return {
        "repository": auth.REPOSITORY, "branch": auth.BRANCH, "head_sha": C1_SHA,
        "published": True,
        "pull_request": {"number": 10, "state": "OPEN", "draft": True,
                         "head_sha": C1_SHA, "base_sha": auth.BASE_SHA},
        "runs": [{"databaseId": number, "event": event, "headSha": C1_SHA,
                  "status": "completed", "conclusion": "success",
                  "url": f"https://github.com/{auth.REPOSITORY}/actions/runs/{number}",
                  "jobs": copy.deepcopy(jobs)}
                 for number, event in ((123, "push"), (124, "pull_request"))],
    }


class V2AuthorityTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / ".bootstrap-test-tmp"
        self.assertFalse(parent.is_symlink())
        parent.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="solute-v2-authority-", dir=parent)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        governance = {**legacy.CLOSED_STATE, **legacy.BOUNDARY_STATE}
        self.write("pyproject.toml", "[tool.snbi]\n" + "\n".join(
            f"{key} = {json.dumps(value)}" for key, value in governance.items()) + "\n")
        for older in (frag, direct, solute):
            self.write(older.AUTHORITY_PATH, json.dumps(older.expected_authority("CLOSED_CONSUMED")))
        self.write(auth.AUTHORITY_PATH, json.dumps(auth.expected_authority()))
        self.hashes = {}
        preserved = {"pyproject.toml", frag.AUTHORITY_PATH, direct.AUTHORITY_PATH,
                     solute.AUTHORITY_PATH, auth.AUTHORITY_PATH}
        for relative in auth.FROZEN_TEXT_PATHS:
            if relative not in preserved:
                self.write(relative, "{}\n")
            self.hashes[relative] = hashlib.sha256((self.root / relative).read_bytes()).hexdigest()
        self.payloads = {source: bytes(width * height * 3 // 2)
                         for source, (width, height) in auth.DIMENSIONS.items()}
        self.assets, self.exposure = [], {}
        for identity in auth.ASSET_ROLES:
            source, index = identity.split(":")
            width, height = auth.DIMENSIONS[source]
            self.assets.append({
                "asset_id": identity, "source_id": source, "frame_index": int(index),
                "role": "development", "path": f"data/derived/ti2-pilot/{source}-{int(index):04d}.raw",
                "width": width, "height": height, "frame_bytes": len(self.payloads[source]),
                "image_sha256": hashlib.sha256(self.payloads[source]).hexdigest(),
                "pixel_format": "yuv420p", "bit_depth": 8,
            })
            self.exposure[identity] = {"development_eligible_this_phase": True,
                                       "evidence": ["synthetic positive custody fixture"],
                                       "previous_exposure": ["explicit previously exposed development"]}
        identity = patch.object(auth, "_git_identity", return_value=(auth.BRANCH, C1_SHA))
        identity.start()
        self.addCleanup(identity.stop)
        git = patch.object(auth, "_git_read", side_effect=self.git_read)
        git.start()
        self.addCleanup(git.stop)

    def git_read(self, root, *arguments):
        if arguments == ("rev-list", "--parents", "-n", "1", "HEAD"):
            return C1_SHA + " " + auth.BASE_SHA
        if arguments == ("rev-parse", "refs/remotes/origin/" + auth.BRANCH):
            return C1_SHA
        if arguments == ("status", "--porcelain=v1", "--untracked-files=all"):
            return ""
        raise AssertionError("unregistered Git read")

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def begin(self, **changes):
        arguments = {"c1_sha": C1_SHA, "frozen_hashes": self.hashes,
                     "assets": self.assets, "exposure": self.exposure, "ci_evidence": ci_evidence()}
        arguments.update(changes)
        return auth.begin_session(self.root, **arguments)

    def materialize(self, identity):
        asset = next(item for item in self.assets if item["asset_id"] == identity)
        path = self.root / asset["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.payloads[asset["source_id"]])
        return path

    def test_exact_schema_rejects_truthy_unknown_and_old_active_state(self):
        authority = auth.expected_authority()
        self.assertEqual(auth.validate_authority(authority), [])
        self.assertFalse(authority["ti2r_solute_holdout_authorized"])
        self.assertEqual(len(auth.ASSET_ROLES), 12)
        self.assertEqual(len(auth.HOLDOUT_ASSETS), 8)
        for field, value in (("state", "ACTIVE_ONE_SHOT"), ("max_invocations", True),
                             ("development_execution_after_c1_ci_authorized", 1),
                             ("ti2r_solute_holdout_authorized", True), ("unknown", True)):
            changed = copy.deepcopy(authority)
            changed[field] = value
            self.assertTrue(auth.validate_authority(changed))

    def test_previous_authority_chain_must_be_consumed(self):
        for older in (frag, direct, solute):
            self.write(older.AUTHORITY_PATH, json.dumps(older.expected_authority("ACTIVE_ONE_SHOT")))
            with self.subTest(older=older.__name__), self.assertRaises(auth.V2AuthorityError):
                self.begin()
            self.write(older.AUTHORITY_PATH, json.dumps(older.expected_authority("CLOSED_CONSUMED")))
        self.write("pyproject.toml", (self.root / "pyproject.toml").read_text().replace(
            "ti2_execution_authorized = false", "ti2_execution_authorized = true"))
        with self.assertRaises(auth.V2AuthorityError):
            self.begin()

    def test_absent_ci_blocks_before_asset_validation_and_receipt(self):
        for evidence in (None, {}, {"published": True}):
            with patch.object(auth, "_validate_assets") as assets, patch.object(auth, "_write_exclusive") as write:
                with self.assertRaises(auth.V2IOBlocked):
                    self.begin(ci_evidence=evidence, assets=ExplodingPath())
                assets.assert_not_called()
                write.assert_not_called()

    def test_ci_requires_same_sha_repository_branch_and_publication(self):
        for field, value in (("repository", "other/repo"), ("branch", "main"),
                             ("head_sha", "a" * 40), ("published", 1)):
            evidence = ci_evidence()
            evidence[field] = value
            with self.subTest(field=field), self.assertRaises(auth.V2IOBlocked):
                self.begin(ci_evidence=evidence)

    def test_ci_requires_open_draft_pr_exact_base_and_head(self):
        for field, value in (("number", True), ("state", "MERGED"), ("draft", False),
                             ("head_sha", "a" * 40), ("base_sha", "b" * 40)):
            evidence = ci_evidence()
            evidence["pull_request"][field] = value
            with self.subTest(field=field), self.assertRaises(auth.V2IOBlocked):
                self.begin(ci_evidence=evidence)

    def test_ci_requires_distinct_push_pr_runs_same_c1_success(self):
        for field, value in (("databaseId", 124), ("event", "pull_request"),
                             ("headSha", "a" * 40), ("status", "in_progress"),
                             ("conclusion", "failure"), ("url", "https://example.invalid")):
            evidence = ci_evidence()
            evidence["runs"][0][field] = value
            with self.subTest(field=field), self.assertRaises(auth.V2IOBlocked):
                self.begin(ci_evidence=evidence)

    def test_ci_missing_skipped_cancelled_job_or_step_denies(self):
        for conclusion in ("skipped", "cancelled", "failure", None):
            for location in ("job", "step"):
                evidence = ci_evidence()
                job = evidence["runs"][0]["jobs"][0]
                target = job if location == "job" else job["steps"][0]
                target["conclusion"] = conclusion
                with self.subTest(location=location, conclusion=conclusion), self.assertRaises(auth.V2IOBlocked):
                    self.begin(ci_evidence=evidence)
        for field in ("runs",):
            evidence = ci_evidence()
            evidence[field].pop()
            with self.assertRaises(auth.V2IOBlocked):
                self.begin(ci_evidence=evidence)
        evidence = ci_evidence()
        evidence["runs"][0]["jobs"].pop()
        with self.assertRaises(auth.V2IOBlocked):
            self.begin(ci_evidence=evidence)

    def test_dirty_unpublished_or_extra_commit_cannot_start(self):
        for target, value in (("status", " M forbidden.py"), ("rev-parse", "a" * 40),
                              ("rev-list", C1_SHA + " " + "b" * 40)):
            def response(root, *arguments):
                return value if arguments[0] == target else self.git_read(root, *arguments)
            with patch.object(auth, "_git_read", side_effect=response), self.assertRaises(auth.V2IOBlocked):
                self.begin()
        with patch.object(auth, "_git_identity", return_value=("main", C1_SHA)), self.assertRaises(auth.V2IOBlocked):
            self.begin()
        self.assertFalse((self.root / auth.RECEIPT_PATH).exists())

    def test_all_eight_holdouts_denied_before_any_session_or_path_access(self):
        class NoSession:
            def _require(self):
                raise AssertionError("holdout reached even session validation")
        for identity in auth.HOLDOUT_ASSETS:
            for role in ("holdout", "development", "validation"):
                with patch.object(auth, "_parent_fd") as path, self.assertRaises(auth.V2IOBlocked):
                    auth.read_asset(NoSession(), identity, role=role)
                path.assert_not_called()

    def test_external_sources_roles_and_path_coercion_are_forbidden(self):
        for identity, role in (("ESM3:0", "development"), ("ESM6:0", "development"),
                               ("ESM1:0", "holdout"), (ExplodingPath(), "development")):
            with patch.object(auth, "_parent_fd") as path, self.assertRaises(auth.V2IOBlocked):
                auth.read_asset(None, identity, role=role)
            path.assert_not_called()

    def test_holdout_cannot_be_role_spoofed_into_asset_list(self):
        assets = copy.deepcopy(self.assets)
        assets[0].update(source_id="ESM1", frame_index=73, asset_id="ESM1:73", role="development")
        with self.assertRaises(auth.V2IOBlocked):
            self.begin(assets=assets)
        self.assertFalse((self.root / auth.RECEIPT_PATH).exists())

    def test_dimensions_format_and_exact_asset_paths_are_enforced(self):
        for field, value in (("width", True), ("height", 1020), ("bit_depth", 16),
                             ("frame_bytes", 1), ("path", "data/../source.raw"),
                             ("pixel_format", "rgb24"), ("image_sha256", "unknown")):
            assets = copy.deepcopy(self.assets)
            assets[0][field] = value
            with self.subTest(field=field), self.assertRaises(auth.V2IOBlocked):
                self.begin(assets=assets)

    def test_exposure_requires_twelve_affirmative_prior_exposures(self):
        for field, value in (("development_eligible_this_phase", 1), ("evidence", []),
                             ("previous_exposure", []), ("unknown", True)):
            exposure = copy.deepcopy(self.exposure)
            exposure["ESM1:0"][field] = value
            with self.subTest(field=field), self.assertRaises(auth.V2IOBlocked):
                self.begin(exposure=exposure)

    def test_receipt_precedes_any_bytes_and_prevents_second_invocation(self):
        session = self.begin()
        receipt = json.loads((self.root / auth.RECEIPT_PATH).read_text())
        self.assertEqual(receipt["invocation_counter"], 1)
        self.assertEqual(receipt["experimental_bytes_before_receipt"], 0)
        self.assertEqual(len(receipt["allowed_assets"]), 12)
        self.assertEqual(receipt["holdout_content_bytes_read"], 0)
        self.assertEqual(session.opened_assets, [])
        self.assertFalse((self.root / "data").exists())
        with self.assertRaises(auth.V2IOBlocked):
            self.begin()
        with self.assertRaises(auth.V2IOBlocked):
            auth.V2Session(self.root, C1_SHA, {}, {}, b"{}")

    def test_frozen_complete_set_and_post_receipt_drift_are_blocking(self):
        with self.assertRaises(auth.V2IOBlocked):
            self.begin(frozen_hashes={"pyproject.toml": self.hashes["pyproject.toml"]})
        session = self.begin()
        self.write("configs/registration/ti2r-solute-direct-method.json", '{"changed":true}')
        with self.assertRaises(auth.V2IOBlocked):
            auth.read_asset(session, "ESM1:0")
        self.assertEqual(session.opened_assets, [])

    def test_one_successful_native_read_has_exact_counters(self):
        self.materialize("ESM1:0")
        session = self.begin()
        content = auth.read_asset(session, "ESM1:0")
        self.assertEqual(content, self.payloads["ESM1"])
        self.assertEqual(session.content_bytes_read, len(content))
        self.assertEqual(session.opened_assets, [{"asset_id": "ESM1:0", "role": "development",
                                                "status": "PASS", "file_opened": True,
                                                "bytes_read": len(content)}])
        with self.assertRaises(auth.V2IOBlocked):
            auth.read_asset(session, "ESM1:0")

    def test_missing_and_symlink_reads_are_never_retried(self):
        target = self.materialize("ESM1:146")
        link = self.materialize("ESM1:293")
        link.unlink()
        link.symlink_to(target.name)
        session = self.begin()
        for identity in ("ESM1:0", "ESM1:293"):
            with self.assertRaises(auth.V2IOBlocked):
                auth.read_asset(session, identity)
            with self.assertRaises(auth.V2IOBlocked):
                auth.read_asset(session, identity)
        self.assertEqual(session.content_bytes_read, 0)
        self.assertFalse(any(item["file_opened"] for item in session.opened_assets))

    def test_digest_failure_preserves_bytes_and_open_counters(self):
        path = self.materialize("ESM1:0")
        path.write_bytes(b"x" * len(self.payloads["ESM1"]))
        session = self.begin()
        with self.assertRaises(auth.V2IOBlocked):
            auth.read_asset(session, "ESM1:0")
        self.assertEqual(session.opened_assets[0]["status"], "BLOCKED_DIGEST")
        self.assertTrue(session.opened_assets[0]["file_opened"])
        self.assertEqual(session.content_bytes_read, len(self.payloads["ESM1"]))

    def test_receipt_exposure_and_head_drift_block_before_pixels(self):
        session = self.begin()
        session.exposure["ESM1:0"]["evidence"] = ["changed"]
        with self.assertRaises(auth.V2IOBlocked):
            auth.read_asset(session, "ESM1:0")
        session.exposure = copy.deepcopy(self.exposure)
        with patch.object(auth, "_git_identity", return_value=(auth.BRANCH, "a" * 40)), self.assertRaises(auth.V2IOBlocked):
            auth.read_asset(session, "ESM1:0")
        self.write(auth.RECEIPT_PATH, "{}")
        with self.assertRaises(auth.V2IOBlocked):
            auth.read_asset(session, "ESM1:0")
        self.assertEqual(session.opened_assets, [])

    def test_finish_closes_before_result_and_never_changes_c1_authority(self):
        before = (self.root / auth.AUTHORITY_PATH).read_bytes()
        session = self.begin()
        report = {"TI2R_SOLUTE_V2_DEV": "BLOCKED_OPERATIONAL_REQUIRES_AUTHOR_DECISION"}
        writes = []
        real_write = auth._write_exclusive
        def write(root, relative, content):
            writes.append(relative)
            return real_write(root, relative, content)
        with patch.object(auth, "_write_exclusive", side_effect=write):
            terminal = session.finish(report)
        self.assertEqual(writes, [auth.TERMINAL_PATH, auth.RESULT_PATH])
        self.assertEqual(terminal["state"], "CLOSED_CONSUMED")
        self.assertEqual(terminal["holdout_content_bytes_read"], 0)
        self.assertEqual(terminal["holdout_open_count"], 0)
        self.assertFalse(terminal["TI2R_SOLUTE_HOLDOUT_AUTHORIZED"])
        self.assertEqual((self.root / auth.AUTHORITY_PATH).read_bytes(), before)
        with self.assertRaises(auth.V2IOBlocked):
            session.finish(report)
        with self.assertRaises(auth.V2IOBlocked):
            self.begin()
        with self.assertRaises(auth.V2IOBlocked):
            auth.read_asset(session, "ESM1:0")

    def test_failed_result_write_still_consumes_authority_permanently(self):
        session = self.begin()
        real_write = auth._write_exclusive
        def write(root, relative, content):
            if relative == auth.RESULT_PATH:
                raise OSError("synthetic result-write failure")
            return real_write(root, relative, content)
        with patch.object(auth, "_write_exclusive", side_effect=write), self.assertRaises(OSError):
            session.finish({"TI2R_SOLUTE_V2_DEV": "BLOCKED_OPERATIONAL_REQUIRES_AUTHOR_DECISION"})
        self.assertTrue(session.closed)
        self.assertTrue((self.root / auth.TERMINAL_PATH).is_file())
        with self.assertRaises(auth.V2IOBlocked):
            auth.load_authority(self.root)

    def test_invalid_result_closes_with_operational_failure(self):
        session = self.begin()
        with self.assertRaises(auth.V2IOBlocked):
            session.finish({"TI2R_SOLUTE_V2_DEV": "invented PASS"})
        terminal = json.loads((self.root / auth.TERMINAL_PATH).read_text())
        self.assertEqual(terminal["TI2R_SOLUTE_V2_DEV"], "BLOCKED_OPERATIONAL_REQUIRES_AUTHOR_DECISION")
        self.assertFalse((self.root / auth.RESULT_PATH).exists())

    def test_any_terminal_presence_including_malformed_or_symlink_denies(self):
        terminal = self.root / auth.TERMINAL_PATH
        for contents in ("", "{malformed", '{"state":"ACTIVE_ONE_SHOT"}'):
            self.write(auth.TERMINAL_PATH, contents)
            with self.assertRaises(auth.V2IOBlocked):
                self.begin()
        terminal.unlink()
        terminal.symlink_to("missing-target")
        with self.assertRaises(auth.V2IOBlocked):
            self.begin()

    def test_text_api_rejects_data_and_nonallowlisted_text_before_open(self):
        for relative in ("data/source.json", "data/derived/ti2-pilot/ESM1-0073.raw",
                         "../pyproject.toml", "README.md", ExplodingPath()):
            with patch.object(auth, "_read_regular") as read, self.assertRaises(auth.V2IOBlocked):
                auth.read_text_file(self.root, relative)
            read.assert_not_called()


if __name__ == "__main__":
    unittest.main()
