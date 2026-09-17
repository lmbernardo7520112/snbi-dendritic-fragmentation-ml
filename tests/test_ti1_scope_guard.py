import unittest

from scripts.check_ti1_scope import audit


class TI1ScopeGuardTests(unittest.TestCase):
    def test_repository_stays_inside_ti1(self):
        self.assertEqual(audit(entries=[("100644", "README.md")])["status"], "PASS")

    def test_tracked_experimental_path_fails_closed(self):
        result = audit(entries=[("100644", "data/raw/ESM1.mp4")])
        self.assertEqual(result["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
