from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "project" / "scripts"))

from curriculum_audit import audit_curriculum


class CurriculumAuditTests(unittest.TestCase):
    def test_repository_curriculum_contract_is_complete(self) -> None:
        self.assertEqual([], audit_curriculum(PROJECT_ROOT))


if __name__ == "__main__":
    unittest.main()
