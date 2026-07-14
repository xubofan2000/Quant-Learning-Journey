"""Audit the agreement between learning plan, check-in log, and artifacts."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


WEEK_PATTERN = re.compile(r"^##\s+Week\s+(\d+)", re.IGNORECASE)
DAY_HEADING_PATTERN = re.compile(r"^###\s+Day\s+(\d+)", re.IGNORECASE)
DAY_CELL_PATTERN = re.compile(r"\*\*Day\s+(\d+)\*\*|Day\s+(\d+)", re.IGNORECASE)
CHECKBOX_PATTERN = re.compile(r"-\s+\[([xX ])\]\s+任务")


@dataclass(frozen=True, order=True)
class DayKey:
    week: int
    day: int


@dataclass
class DayState:
    planned_complete: bool | None = None
    logged_complete: bool | None = None
    logged_reviewed: bool | None = None  # Track review status
    has_code: bool = False
    has_assessment: bool = False
    has_summary: bool = False


def parse_plan(plan_path: Path) -> dict[DayKey, bool]:
    """Return task completion states declared in the learning plan."""
    plan_states: dict[DayKey, bool] = {}
    current_week: int | None = None
    current_day: int | None = None
    day_lines: list[str] = []

    def save_current_day() -> None:
        if current_week is None or current_day is None:
            return
        checkbox_match = CHECKBOX_PATTERN.search("\n".join(day_lines))
        if checkbox_match is not None:
            plan_states[DayKey(current_week, current_day)] = checkbox_match.group(1).lower() == "x"

    for line in plan_path.read_text(encoding="utf-8").splitlines():
        week_match = WEEK_PATTERN.match(line)
        day_match = DAY_HEADING_PATTERN.match(line)

        if week_match is not None:
            save_current_day()
            current_week = int(week_match.group(1))
            current_day = None
            day_lines = []
        elif day_match is not None:
            save_current_day()
            current_day = int(day_match.group(1))
            day_lines = [line]
        elif current_day is not None:
            day_lines.append(line)

    save_current_day()
    return plan_states


def parse_learning_log(log_path: Path) -> dict[DayKey, tuple[bool, bool]]:
    """Return user-confirmed completion and review states from Markdown log tables."""
    log_states: dict[DayKey, tuple[bool, bool]] = {}
    current_week: int | None = None

    for line in log_path.read_text(encoding="utf-8").splitlines():
        week_match = re.search(r"Week\s+(\d+)", line, re.IGNORECASE)
        if week_match is not None:
            current_week = int(week_match.group(1))

        if current_week is None or not line.lstrip().startswith("|"):
            continue

        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue

        day_match = DAY_CELL_PATTERN.search(cells[2])
        if day_match is None:
            continue

        day_number = int(day_match.group(1) or day_match.group(2))
        is_complete = cells[0].lower() == "[x]"
        is_reviewed = cells[1].lower() == "[x]"
        log_states[DayKey(current_week, day_number)] = (is_complete, is_reviewed)

    return log_states


def inspect_artifacts(vault_path: Path, keys: set[DayKey]) -> dict[DayKey, tuple[bool, bool, bool]]:
    """Check the standard code, assessment, and summary artifacts for each day."""
    artifact_states: dict[DayKey, tuple[bool, bool, bool]] = {}

    for key in keys:
        week_path = vault_path / f"Week{key.week}"
        code_files = list(week_path.glob(f"day{key.day}_*.py"))
        assessment_files = list(week_path.glob(f"Day{key.day}_学习检验.md"))
        summary_files = [
            file_path
            for file_path in week_path.glob(f"Day{key.day}_*总结.md")
            if "学习检验" not in file_path.name
        ]
        artifact_states[key] = (bool(code_files), bool(assessment_files), bool(summary_files))

    return artifact_states


def audit_project(root_path: Path) -> dict[DayKey, DayState]:
    """Build a derived project state without changing any learning records."""
    plan_states = parse_plan(root_path / "curriculum" / "plans" / "TODO_Phase1.md")
    log_states = parse_learning_log(root_path / "Learning_Log.md")
    all_keys = set(plan_states) | set(log_states)
    artifact_states = inspect_artifacts(root_path / "Learning_Vault" / "Phase1_Month1", all_keys)

    results: dict[DayKey, DayState] = {}
    for key in sorted(all_keys):
        has_code, has_assessment, has_summary = artifact_states[key]
        logged_complete, logged_reviewed = log_states.get(key, (None, None))
        results[key] = DayState(
            planned_complete=plan_states.get(key),
            logged_complete=logged_complete,
            logged_reviewed=logged_reviewed,
            has_code=has_code,
            has_assessment=has_assessment,
            has_summary=has_summary,
        )
    return results


def classify_state(state: DayState) -> str:
    """Return a concise status based on the three independent evidence sources."""
    if state.logged_complete and state.planned_complete and state.has_code:
        return "完成"
    if state.has_code and not state.logged_complete:
        return "待学习者确认"
    if state.logged_complete and not state.has_code:
        return "缺少代码产物"
    if state.logged_complete != state.planned_complete:
        return "计划与打卡不一致"
    return "未开始"


def detect_large_untracked_files(root_path: Path) -> list[str]:
    """Scan Database/ directory for large files (e.g. > 10MB) that might break Git limits."""
    db_path = root_path / "Database"
    if not db_path.exists():
        return []
    large_files: list[str] = []
    limit_bytes = 10 * 1024 * 1024
    for file_path in db_path.rglob("*"):
        if file_path.is_file() and file_path.stat().st_size > limit_bytes:
            rel_path = file_path.relative_to(root_path)
            large_files.append(f"`{rel_path.as_posix()}` ({file_path.stat().st_size / 1024 / 1024:.1f} MB)")
    return large_files


def render_report(states: dict[DayKey, DayState], root_path: Path) -> str:
    """Render a human-readable Markdown report."""
    total_days = len(states)
    completed_days = sum(1 for state in states.values() if state.logged_complete)
    next_day = next((key for key, state in states.items() if not state.logged_complete), None)
    lines = [
        "# Bohr 学习状态审计",
        "",
        "此报告由脚本派生，不是新的进度事实源。",
        "",
        f"- 项目根目录：`{root_path.as_posix()}`",
        f"- 学习者已确认：{completed_days}/{total_days}",
        f"- 下一待确认任务：Week {next_day.week} / Day {next_day.day}" if next_day else "- 下一待确认任务：无",
        "",
        "| 任务 | TODO | 打卡 | 代码 | 检验 | 总结 | 状态 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for key, state in states.items():
        lines.append(
            "| Week {week} Day {day} | {plan} | {log} | {code} | {assessment} | {summary} | {status} |".format(
                week=key.week,
                day=key.day,
                plan="完成" if state.planned_complete else "未完成",
                log="完成" if state.logged_complete else "未确认",
                code="有" if state.has_code else "无",
                assessment="有" if state.has_assessment else "无",
                summary="有" if state.has_summary else "无",
                status=classify_state(state),
            )
        )

    pending_confirmation = [key for key, state in states.items() if classify_state(state) == "待学习者确认"]
    if pending_confirmation:
        formatted_days = "、".join(f"Week {key.week} Day {key.day}" for key in pending_confirmation)
        lines.extend(["", f"> 提示：{formatted_days} 已有代码，但尚未完成学习者确认与正式打卡。"])

    # Spaced repetition reminder
    needs_review = [
        f"Week {key.week} Day {key.day}"
        for key, state in sorted(states.items())
        if state.logged_complete and not state.logged_reviewed
    ]
    if needs_review:
        formatted_reviews = "、".join(needs_review)
        lines.extend(["", f"> 🔁 **间隔重复复习提醒**：{formatted_reviews} 已完成打卡但尚未复习。请根据艾宾浩斯记忆法安排复习，并在 `Learning_Log.md` 中勾选。"])

    # Git large file warning
    large_files = detect_large_untracked_files(root_path)
    if large_files:
        formatted_files = "，".join(large_files)
        lines.extend(["", f"> ⚠️ **Git 大文件安全预警**：检测到 `Database/` 下有超过 10MB 的文件：{formatted_files}。请确保它们已在 `.gitignore` 中排除，以防误提交。"])

    return "\n".join(lines) + "\n"


def main() -> None:
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description="审计 Bohr 的计划、打卡和学习产物一致性。")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--write-report", action="store_true", help="将派生报告写入 reports/PROJECT_STATUS.md")
    arguments = parser.parse_args()

    root_path = arguments.root.resolve()
    report = render_report(audit_project(root_path), root_path)
    print(report, end="")

    if arguments.write_report:
        report_path = root_path / "project" / "reports" / "PROJECT_STATUS.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        print(f"报告已写入：{report_path}")


if __name__ == "__main__":
    main()
