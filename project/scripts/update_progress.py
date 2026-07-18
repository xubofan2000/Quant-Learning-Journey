from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_FILE = PROJECT_ROOT / "Learning_Log.md"

def summarize_legacy_checkins() -> tuple[int, int]:
    """Report historical check-ins without changing capability or log files."""
    if not LOG_FILE.exists():
        raise FileNotFoundError("未找到 Learning_Log.md")

    completed_days = 0
    total_days = 0
    for line in LOG_FILE.read_text(encoding="utf-8").splitlines():
        if "**Day " not in line or not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or cells[0].lower() not in {"[x]", "[ ]"}:
            continue
        total_days += 1
        completed_days += cells[0].lower() == "[x]"

    print(
        f"历史打卡记录：{completed_days}/{total_days}。"
        "此命令不再写入进度条，也不更新能力等级；请使用 JOB_CAPABILITY_MATRIX.md。"
    )
    return completed_days, total_days


def update_progress() -> tuple[int, int]:
    """Backward-compatible entry point; no longer mutates Learning_Log.md."""
    return summarize_legacy_checkins()

if __name__ == '__main__':
    update_progress()
