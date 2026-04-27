"""
detect_progress.py - 自动检测 Bohr 项目当前学习进度

用法：
    python .agent/skills/quant-learning-workflow/scripts/detect_progress.py

输出：JSON 格式的进度摘要，供 agent 精确定位当前状态，无需大量读取文件。
"""

import os
import re
import sys
import json
from pathlib import Path

# 强制 stdout 使用 UTF-8，避免 Windows 终端乱码
sys.stdout.reconfigure(encoding='utf-8')

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[4]  # scripts/ -> quant-learning-workflow/ -> skills/ -> .agent/ -> root

LOG_FILE = PROJECT_ROOT / "Learning_Log.md"
PLANS_DIR = PROJECT_ROOT / "plans"
VAULT_DIR = PROJECT_ROOT / "Learning_Vault"


def parse_log_status(log_content: str) -> list[dict]:
    """
    从 Learning_Log.md 中解析每一天的打卡状态。
    返回 list of dict，每项包含 week, day, checked, file_path, summary
    """
    entries = []
    # 匹配表格行：| [x] | ... | **Day N** | 路径 | 摘要 |
    pattern = re.compile(
        r'\|\s*\[([xX ])\]\s*\|.*?\|\s*\*\*Day\s*(\d+)\*\*\s*\|([^|]*)\|([^|]*)\|'
    )
    
    current_week = None
    for line in log_content.splitlines():
        # 检测 Week 标题行
        week_match = re.search(r'Week\s*(\d+)', line)
        if week_match and '<summary>' in line:
            current_week = int(week_match.group(1))
        
        match = pattern.search(line)
        if match and current_week is not None:
            checked = match.group(1).lower() == 'x'
            day_num = int(match.group(2))
            file_path = match.group(3).strip()
            summary = match.group(4).strip()
            entries.append({
                "week": current_week,
                "day": day_num,
                "checked": checked,
                "file_path": file_path,
                "summary": summary
            })
    return entries


def parse_todo_task(todo_content: str, week: int, day: int) -> dict:
    """
    从 TODO_Phase1.md 中提取指定 Week/Day 的任务描述。
    返回 {task_description, deliverable, checked}
    """
    lines = todo_content.splitlines()
    
    current_week = 0
    current_day = 0
    in_target_day = False
    task_lines = []
    checked = False
    
    day_counter = 0  # 全局 Day 编号（跨 Week 累计）
    week_day_counter = 0  # 当前 Week 内的 Day 编号
    
    for line in lines:
        # 检测 Week 标题
        week_match = re.search(r'## Week\s*(\d+)', line)
        if week_match:
            current_week = int(week_match.group(1))
            week_day_counter = 0
            continue
        
        # 检测 Day 标题
        day_match = re.search(r'### Day\s*(\d+)', line)
        if day_match:
            week_day_counter += 1
            day_counter += 1
            in_target_day = (current_week == week and week_day_counter == day)
            if not in_target_day and task_lines:
                break  # 找到目标 Day 的内容后遇到下一个 Day，退出
            continue
        
        if in_target_day:
            # 检测任务行：- [X] 任务: ...
            task_match = re.search(r'-\s*\[([xX ])\]\s*任务[：:]\s*(.*)', line)
            if task_match:
                checked = task_match.group(1).lower() == 'x'
                task_lines.append(('task', task_match.group(2).strip()))
            
            # 检测产出行：- [X] 产出: ...
            output_match = re.search(r'-\s*\[([xX ])\]\s*产出[：:]\s*(.*)', line)
            if output_match:
                task_lines.append(('output', output_match.group(2).strip()))
    
    task_desc = next((v for k, v in task_lines if k == 'task'), "")
    deliverable = next((v for k, v in task_lines if k == 'output'), "")
    
    return {
        "checked": checked,
        "task_description": task_desc,
        "deliverable": deliverable
    }


def scan_vault_files(week: int, day: int) -> dict:
    """
    扫描 Learning_Vault 中当前 Week 目录，检查实际文件状态。
    """
    week_dir = VAULT_DIR / "Phase1_Month1" / f"Week{week}"
    
    if not week_dir.exists():
        return {"code_exists": False, "summary_exists": False, "actual_code_files": []}
    
    all_files = list(week_dir.iterdir())
    py_files = [f.name for f in all_files if f.suffix == '.py' and f.name.startswith(f'day{day}')]
    md_files = [f.name for f in all_files if f.suffix == '.md' and f.name.startswith(f'Day{day}')]
    
    return {
        "code_exists": len(py_files) > 0,
        "summary_exists": len(md_files) > 0,
        "actual_code_files": py_files,
        "actual_summary_files": md_files,
        "week_dir": str(week_dir)
    }


def detect_progress() -> dict:
    """主检测函数，返回完整的进度状态。"""
    
    if not LOG_FILE.exists():
        return {"error": f"Learning_Log.md not found at {LOG_FILE}"}
    
    log_content = LOG_FILE.read_text(encoding='utf-8')
    entries = parse_log_status(log_content)
    
    if not entries:
        return {"error": "No entries found in Learning_Log.md"}
    
    # 找到第一个未打卡的 Day
    unchecked = [e for e in entries if not e["checked"]]
    
    if not unchecked:
        # 全部完成
        last = entries[-1]
        return {
            "status": "all_completed",
            "message": "Phase 1 Month 1 全部 28 天已完成！可以制定下月计划。",
            "last_day": last
        }
    
    current = unchecked[0]
    week = current["week"]
    day = current["day"]
    
    # 读取 TODO
    todo_file = PLANS_DIR / "TODO_Phase1.md"
    todo_info = {}
    if todo_file.exists():
        todo_content = todo_file.read_text(encoding='utf-8-sig')  # utf-8-sig 处理 BOM
        todo_info = parse_todo_task(todo_content, week, day)
    
    # 扫描实际文件
    vault_info = scan_vault_files(week, day)
    
    # 判断状态
    if not vault_info["code_exists"]:
        day_status = "not_started"
    elif vault_info["code_exists"] and not vault_info["summary_exists"]:
        day_status = "code_exists_no_summary"
        
        # 检测文件名是否与 TODO 计划一致（防幻觉检查）
        actual_files = vault_info["actual_code_files"]
        todo_keywords = todo_info.get("task_description", "").lower()
        # 这里做简单关键词匹配，详细判断留给 agent
        vault_info["deviation_warning"] = len(actual_files) > 0 and bool(todo_keywords)
    else:
        day_status = "completed"
    
    # 前一天的文件（用于上下文衔接）
    prev_week, prev_day = week, day - 1
    if prev_day == 0:
        prev_week -= 1
        prev_day = 7
    prev_vault = scan_vault_files(prev_week, prev_day) if prev_day > 0 else {}
    
    result = {
        "current_phase": "Phase1",
        "current_month": "Month1",
        "current_week": f"Week{week}",
        "current_day": f"Day{day}",
        "day_status": day_status,
        "vault_info": vault_info,
        "todo_info": todo_info,
        "vault_path": str(VAULT_DIR / "Phase1_Month1" / f"Week{week}"),
        "previous_day_code": prev_vault.get("actual_code_files", []),
        "completed_days": len(entries) - len(unchecked),
        "total_days": len(entries),
        "progress_pct": round((len(entries) - len(unchecked)) / len(entries) * 100)
    }
    
    return result


if __name__ == "__main__":
    result = detect_progress()
    print(json.dumps(result, ensure_ascii=False, indent=2))
