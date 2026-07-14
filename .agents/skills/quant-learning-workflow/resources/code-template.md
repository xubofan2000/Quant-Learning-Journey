# 代码文件规范

> 供 agent 生成 dayN_xxx.py 时参考。
> **核心原则：规范随 Phase 演进，不强制固定结构。**
> Phase 1 以教学演示为主，后续 Phase 会走向工程化/模块化，届时本文档同步更新。

---

## Phase 1 代码规范（当前适用）

### 必须遵守的规定（3条硬性要求）

**1. 模块 docstring（必须，放在文件最顶部）**

```python
"""
dayN_<name>.py - Week X Day Y: <中文描述>

核心认知跃迁：
    <从什么认知到什么认知的升级，1-3句话>

目标：
1. <具体目标1>
2. <具体目标2>
"""
```

**2. 路径动态定位（必须，禁止硬编码）**

```python
import os

# 正确方式 ✅
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
data_path = os.path.join(project_root, 'Database', 'files', 'panel_50stocks.parquet')

# 错误方式 ❌
data_path = 'D:\\project\\Bohr\\Database\\files\\panel_50stocks.parquet'
```

**3. 关键计算步骤必须有中文注释**，解释"为什么"而非"做了什么"：

```python
# ✅ 好的注释：解释为什么
R_centered = R - mu  # 去均值：让协方差矩阵只捕捉波动，不被方向性漂移污染

# ❌ 差的注释：只说做了什么
R_centered = R - mu  # 减去均值
```

---

### 推荐的代码组织方式（不强制）

Phase 1 的代码通常按以下逻辑流组织，用分隔符标识章节，方便阅读：

```python
# ==========================================
# 📦 1. 数据准备
# ==========================================

# ==========================================
# 🧮 2. 核心计算
# ==========================================

# ==========================================
# 📊 3. 结果验证/对比
# ==========================================

# ==========================================
# 📌 4. 总结输出
# ==========================================
```

emoji 前缀帮助快速定位（📦数据 🧮计算 📊验证 🚀优化 🎯目标 📌总结），但不是强制的。

---

### 禁止行为

| 禁止 | 原因 |
|------|------|
| 硬编码绝对路径 | 破坏可移植性，其他机器/路径会报错 |
| 无注释的数学公式实现 | 这是学习代码，理解优先于简洁 |
| 超前引入尚未学习的框架 | 如在 Phase1 Week1 使用 VectorBT |
| 将 Practice1/ 的草稿作为正式产出 | Practice1 是草稿区，正式文件在 WeekN/ |

---

### Week 3+ 数据加载标准模式

从 Phase1 Week3 开始，代码通常用 50 只股票面板数据：

```python
import pandas as pd
import numpy as np
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
parquet_path = os.path.join(project_root, 'Database', 'files', 'panel_50stocks.parquet')

df_panel = pd.read_parquet(parquet_path)

# 选取代表性股票（通常用这5只做演示）
selected = ['SIM0001', 'SIM0010', 'SIM0020', 'SIM0035', 'SIM0050']
N = len(selected)

df_returns = df_panel[df_panel['symbol'].isin(selected)].pivot_table(
    index='trade_date',
    columns='symbol',
    values='daily_return'
).dropna()

R = df_returns.values   # shape: (T, N)
T, N = R.shape
```

---

## 未来 Phase 规范预告（参考，届时更新本文档）

| Phase | 代码风格变化 |
|-------|------------|
| Phase 2 | 引入类封装（VectorBT 风格），代码从脚本走向模块 |
| Phase 3 | Agent/工具函数解耦，接口化设计 |
| Phase 4 | 生产级代码规范，异常处理、日志、配置分离 |
