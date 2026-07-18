"""Validate the employment-oriented curriculum contract without changing files."""

from __future__ import annotations

import re
from pathlib import Path


REQUIRED_FILES = (
    "README.md",
    "Learning_Log.md",
    "curriculum/plans/JOB_CAPABILITY_MATRIX.md",
    "curriculum/plans/NEXT_12_WEEKS.md",
    "curriculum/plans/Phase2_执行计划.md",
    "curriculum/plans/Phase3_执行计划.md",
    "curriculum/plans/Phase4_执行计划.md",
    "curriculum/knowledge-base/README.md",
    "project/docs/ROADMAP.md",
    "project/docs/ENGINEERING_BASELINE.md",
    "project/docs/RESEARCH_PROTOCOL.md",
    "project/templates/WEEKLY_ACCEPTANCE_TEMPLATE.md",
    ".agent/skills/quant-learning-workflow/SKILL.md",
    ".agents/skills/quant-learning-workflow/SKILL.md",
)

WEEK_FIELDS = (
    "目标岗位能力",
    "学习目标",
    "输入材料",
    "实践任务",
    "交付物",
    "自动测试",
    "口述验收",
    "退出门槛",
    "预计时间",
    "未通过时的补救措施",
)


def _read(root_path: Path, relative_path: str) -> str:
    return (root_path / relative_path).read_text(encoding="utf-8")


def audit_curriculum(root_path: Path) -> list[str]:
    """Return human-readable contract violations; an empty list means pass."""
    errors: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root_path / relative_path).is_file():
            errors.append(f"缺少必需文件：{relative_path}")

    if errors:
        return errors

    readme = _read(root_path, "README.md")
    matrix = _read(root_path, "curriculum/plans/JOB_CAPABILITY_MATRIX.md")
    plan = _read(root_path, "curriculum/plans/NEXT_12_WEEKS.md")
    roadmap = _read(root_path, "project/docs/ROADMAP.md")
    phase3 = _read(root_path, "curriculum/plans/Phase3_执行计划.md")
    phase4 = _read(root_path, "curriculum/plans/Phase4_执行计划.md")

    for link in ("JOB_CAPABILITY_MATRIX.md", "NEXT_12_WEEKS.md"):
        if link not in readme:
            errors.append(f"README 未链接 {link}")

    for required_text in ("独立实现", "测试通过", "能解释", "文件存在", "AI"):
        if required_text not in matrix:
            errors.append(f"能力矩阵缺少验收约束：{required_text}")

    for week_number in range(1, 13):
        match = re.search(
            rf"^## Week {week_number}：.*?(?=^## Week {week_number + 1}：|^## 12 周结束后的决策|\Z)",
            plan,
            flags=re.MULTILINE | re.DOTALL,
        )
        if match is None:
            errors.append(f"12 周计划缺少 Week {week_number}")
            continue
        week_block = match.group(0)
        for field in WEEK_FIELDS:
            if f"### {field}" not in week_block:
                errors.append(f"Week {week_number} 缺少字段：{field}")

    for role in ("量化数据开发", "量化研究平台 Python 开发", "投研"):
        if role not in roadmap:
            errors.append(f"全年路线缺少目标岗位：{role}")

    for allocation in ("15%", "25%", "31%", "19%", "最多 10%"):
        if allocation not in roadmap:
            errors.append(f"全年路线缺少时间预算：{allocation}")

    if "2-3 周" not in phase3 or "最终样本外" not in phase3:
        errors.append("Phase 3 未同时满足 2-3 周上限和最终样本外前置门槛")
    if "4-6 周" not in phase4 or "模拟" not in phase4:
        errors.append("Phase 4 未明确 4-6 周模拟执行边界")

    for skill_path in (
        ".agent/skills/quant-learning-workflow/SKILL.md",
        ".agents/skills/quant-learning-workflow/SKILL.md",
    ):
        skill = _read(root_path, skill_path)
        if "能力验收路由（最高优先级）" not in skill or "NEXT_12_WEEKS.md" not in skill:
            errors.append(f"学习工作流未切换到能力验收路由：{skill_path}")

    return errors


def main() -> None:
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root_path = Path(__file__).resolve().parents[2]
    errors = audit_curriculum(root_path)
    if errors:
        print("课程一致性审计失败：")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("课程一致性审计通过：12 周字段、能力门槛、岗位目标和阶段上限均已声明。")


if __name__ == "__main__":
    main()
