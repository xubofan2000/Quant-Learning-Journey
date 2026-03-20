import re
import os

LOG_FILE = 'D:\\project\\Bohr\\Learning_Log.md'

def update_progress():
    if not os.path.exists(LOG_FILE):
        print("未找到 Learning_Log.md")
        return
    
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在表格中查找打卡标记：| [x] | 或者 | [ ] |
    # 注意 Markdown 表格前后的空格
    total_matches = re.findall(r'\|\s*\[([xX ])\]\s*\|', content)
    if not total_matches:
        print("未在文件中找到任务复选框")
        return
        
    total_days = len(total_matches)
    completed_days = sum(1 for m in total_matches if m.lower() == 'x')
    
    percentage = int((completed_days / total_days) * 100) if total_days > 0 else 0
    
    # 动态生成长度为 28 的进度条
    bar_length = 28
    filled = int((completed_days / total_days) * bar_length) if total_days > 0 else 0
    empty = bar_length - filled
    bar = '=' * filled + '.' * empty
    
    # 正则替换天数进度：Phase 1 (X/28 Days)
    content = re.sub(
        r'### 📊 当前阶段进度: Phase 1 \(\d+/\d+ Days\)', 
        f'### 📊 当前阶段进度: Phase 1 ({completed_days}/{total_days} Days)', 
        content
    )
    
    # 正则替换字符进度条：进度条: [====....] X%
    content = re.sub(
        r'进度条: \[.*?\] \d+%', 
        f'进度条: [{bar}] {percentage}%', 
        content
    )
    
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"✅ 进度已更新: {completed_days}/{total_days} ({percentage}%)\n刷新了进度条: [{bar}]")

if __name__ == '__main__':
    update_progress()
