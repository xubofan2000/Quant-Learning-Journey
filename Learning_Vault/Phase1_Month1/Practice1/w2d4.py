# ============================================================
# Week 2 Day 4 练习：多表关联与超额收益计算
# ============================================================
# 💡 规则：每个 TODO 处需要你自己填写代码，完成后运行脚本
#    如果所有 assert 和 print 都正常输出，说明你全部通关！
# ============================================================

import duckdb
import pandas as pd
import numpy as np
import os

# ==========================================
# 🔧 基建（已完成，不用改）
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
db_path = os.path.join(project_root, 'Database', 'files', 'market_data.duckdb')

conn = duckdb.connect(db_path, read_only=True)
df_etf = conn.sql("""
    SELECT trade_date, close_price, volume
    FROM etf_daily_kline 
    WHERE symbol = 'sh510300'
    ORDER BY trade_date
""").df()
conn.close()

df_etf['trade_date'] = pd.to_datetime(df_etf['trade_date'])
df_etf.rename(columns={'close_price': 'etf_close', 'volume': 'etf_volume'}, inplace=True)

# 构造一份模拟的"基准指数"数据（故意比 ETF 少几天，模拟真实场景）
np.random.seed(42)
all_dates = df_etf['trade_date'].tolist()
# 随机丢弃 20 个交易日，模拟指数数据缺失
drop_indices = np.random.choice(len(all_dates), size=20, replace=False)
index_dates = [d for i, d in enumerate(all_dates) if i not in drop_indices]
df_index = pd.DataFrame({
    'trade_date': index_dates,
    'index_close': np.random.uniform(3000, 3500, size=len(index_dates)).cumsum() / len(index_dates) + 3000
})

print(f"📊 ETF 数据: {len(df_etf)} 行")
print(f"📊 指数数据: {len(df_index)} 行 (故意少了 20 天)")
print("=" * 50)


# ==========================================
# 练习 1：执行 LEFT JOIN
# ==========================================
# TODO: 用 pd.merge 将 df_etf（左表）和 df_index（右表）按 trade_date 做 LEFT JOIN
# 提示：参数是 on=?, how=?
# df_merged = pd.merge(???)

df_merged = pd.merge(
    df_etf,
    df_index,
    on = 'trade_date',
    how = 'left'
)  # ← 替换这行


# --- 校验 ---
assert df_merged is not None, "❌ 你还没写 merge 代码！"
assert len(df_merged) == len(df_etf), \
    f"❌ 行数不对！期望 {len(df_etf)} 行，实际 {len(df_merged)} 行。检查你的 how 参数"
print("✅ 练习1 通过：LEFT JOIN 正确，合并后行数 == 左表行数")


# ==========================================
# 练习 2：统计有多少天的指数数据缺失（NaN）
# ==========================================
# TODO: 算出 df_merged 中 index_close 列有多少个 NaN
# 提示：.isna().sum()
# nan_count = ???

nan_count = df_merged['index_close'].isna().sum() # ← 替换这行


# --- 校验 ---
assert nan_count is not None, "❌ 你还没写 NaN 统计代码！"
assert nan_count == 20, f"❌ NaN 数量不对！期望 20，实际 {nan_count}"
print(f"✅ 练习2 通过：发现 {nan_count} 天的指数数据缺失")


# ==========================================
# 练习 3：计算日收益率
# ==========================================
# 先设置时间索引
df_merged = df_merged.set_index('trade_date').sort_index()

# TODO: 分别计算 ETF 和指数的日简单收益率
# 提示：用 .pct_change()
# df_merged['etf_return'] = ???
# df_merged['index_return'] = ???

# ← 在这里写你的代码
df_merged['etf_return'] = df_merged['etf_close'].pct_change()
df_merged['index_return'] = df_merged['index_close'].pct_change()

# --- 校验 ---
assert 'etf_return' in df_merged.columns, "❌ 缺少 etf_return 列！"
assert 'index_return' in df_merged.columns, "❌ 缺少 index_return 列！"
# ETF 收益率不应该全是 NaN（除了第一行）
assert df_merged['etf_return'].dropna().shape[0] > 100, "❌ etf_return 大部分是 NaN，检查计算逻辑"
print("✅ 练习3 通过：日收益率计算正确")


# ==========================================
# 练习 4：计算超额收益
# ==========================================
# TODO: 超额收益 = ETF收益率 - 指数收益率
# df_merged['excess_return'] = ???

# ← 在这里写你的代码
df_merged['excess_return'] = df_merged['etf_return']-df_merged['index_return']

# --- 校验 ---
assert 'excess_return' in df_merged.columns, "❌ 缺少 excess_return 列！"
print("✅ 练习4 通过：超额收益计算完成")

# 打印统计结果
df_clean = df_merged.dropna(subset=['excess_return'])
win_rate = (df_clean['excess_return'] > 0).mean() * 100
print(f"   📈 跑赢大盘天数占比: {win_rate:.1f}%")


# ==========================================
# 练习 5：INNER JOIN 对比
# ==========================================
# TODO: 用 pd.merge 对原始的 df_etf 和 df_index 做 INNER JOIN
# （注意：这里要用原始的 df_etf 和 df_index，不是 df_merged）
# df_inner = pd.merge(???)

df_inner = pd.merge(df_etf,df_index,on='trade_date',how='inner')  # ← 替换这行


# --- 校验 ---
assert df_inner is not None, "❌ 你还没写 INNER JOIN 代码！"
expected_inner = len(df_etf) - 20  # INNER JOIN 应该比 LEFT JOIN 少 20 行
assert len(df_inner) == expected_inner, \
    f"❌ INNER JOIN 行数不对！期望 {expected_inner}，实际 {len(df_inner)}"
print(f"✅ 练习5 通过：INNER JOIN = {len(df_inner)} 行，比 LEFT JOIN 少了 {len(df_etf) - len(df_inner)} 天")


# ==========================================
# 练习 6（加分题）：为什么量化场景不用 INNER JOIN？
# ==========================================
# TODO: 把你的理解写在下面的字符串里（不用写代码，写中文即可）
your_answer = """
内关联会按照两个数据集的关联键取交集。在量化交易中，我们通常需要处理时间序列数据，
如果两个数据集中有不匹配的行，内关联会导致数据丢失，从而影响策略的准确性。
"""

if len(your_answer.strip()) > 10:
    print(f"✅ 练习6 你的回答：{your_answer.strip()}")
else:
    print("⏭️ 练习6 跳过（选做题）")


# ==========================================
print("\n" + "=" * 50)
print("🎉 全部练习完成！你已掌握 Pandas 多表关联的核心技能。")
print("=" * 50)
