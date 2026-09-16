import unittest

from scripts.check_ti1_scope import audit


class TI1ScopeGuardTests(unittest.TestCase):
    def test_repository_stays_inside_ti1(self):
        self.assertEqual(audit()["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
