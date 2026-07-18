from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "project" / "scripts"))

from project_audit import DayKey, audit_project, classify_state, render_report


class ProjectAuditTests(unittest.TestCase):
    def create_fixture_project(self, fixture_root: Path) -> None:
        (fixture_root / "curriculum" / "plans").mkdir(parents=True)
        (fixture_root / "Learning_Vault" / "Phase1_Month1" / "Week1").mkdir(parents=True)
        (fixture_root / "curriculum" / "plans" / "TODO_Phase1.md").write_text(
            "## Week 1\n\n### Day 1\n- [x] 任务：完成示例\n\n### Day 2\n- [ ] 任务：完成示例\n",
            encoding="utf-8",
        )
        (fixture_root / "Learning_Log.md").write_text(
            "<summary>Week 1</summary>\n| 打卡 | 复习 | Day |\n| [x] | [ ] | **Day 1** |\n| [ ] | [ ] | **Day 2** |\n",
            encoding="utf-8",
        )
        week_path = fixture_root / "Learning_Vault" / "Phase1_Month1" / "Week1"
        (week_path / "day1_example.py").write_text("print('ok')\n", encoding="utf-8")
        (week_path / "day2_example.py").write_text("print('pending')\n", encoding="utf-8")

    def test_audit_classifies_confirmed_and_pending_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            self.create_fixture_project(fixture_root)

            states = audit_project(fixture_root)

        self.assertEqual("历史记录一致（非掌握证明）", classify_state(states[DayKey(1, 1)]))
        self.assertEqual("有文件，待学习者验收", classify_state(states[DayKey(1, 2)]))

    def test_report_names_the_next_unconfirmed_day(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            self.create_fixture_project(fixture_root)

            report = render_report(audit_project(fixture_root), fixture_root)

        self.assertIn("下一历史待验收项：Week 1 / Day 2", report)
        self.assertIn("有文件，待学习者验收", report)
        self.assertIn("不判断能力掌握", report)
