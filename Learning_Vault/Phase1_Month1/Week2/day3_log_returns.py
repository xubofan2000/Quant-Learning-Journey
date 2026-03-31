import duckdb
import pandas as pd
import numpy as np
import os

# 1. 动态寻址连接数据库
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
db_path = os.path.join(project_root, 'Database', 'files', 'market_data.duckdb')

conn = duckdb.connect(db_path, read_only=True)
df = conn.sql("""
    SELECT trade_date, close_price 
    FROM etf_daily_kline 
    WHERE symbol = 'sh510300'
    ORDER BY trade_date
""").df()
conn.close()

df['trade_date'] = pd.to_datetime(df['trade_date'])
df.set_index('trade_date', inplace=True)

# ==========================================
# 📚 1. 简单收益率 (Simple Return) —— 昨天 Day 2 已掌握
# 公式：r = (P_t - P_{t-1}) / P_{t-1}
# ==========================================
df['simple_return'] = df['close_price'].pct_change()

# ==========================================
# 📚 2. 对数收益率 (Log Return / Continuously Compounded Return)
# 公式：r_log = ln(P_t / P_{t-1}) = ln(P_t) - ln(P_{t-1})
# ==========================================
# 写法A：直观版 —— 先算比值再取对数
df['log_return_v1'] = np.log(df['close_price'] / df['close_price'].shift(1))

# 写法B：等价拆分版 —— 先各自取对数再做差（数学上完全等价：ln(a/b) = ln(a) - ln(b)）
df['log_return_v2'] = np.log(df['close_price']) - np.log(df['close_price'].shift(1))

# 校验两种写法结果一致
pd.testing.assert_series_equal(
    df['log_return_v1'].dropna(), df['log_return_v2'].dropna(),
    check_names=False, atol=1e-12
)
print("✅ 两种对数收益率写法校验通过！\n")

# ==========================================
# 🔬 3. 核心对比：简单收益率 vs 对数收益率
# ==========================================
print("--- 简单 vs 对数收益率（最近10天）---")
print(df[['close_price', 'simple_return', 'log_return_v1']].dropna().tail(10))

# ==========================================
# 💎 4. 对数收益率的杀手级优势：时间可加性
# ==========================================
# 假设你想算 2024 全年的 YTD 收益
# 金融业务标准：起点是 2023 年最后一个交易日的收盘价（即"买入价"）
# 简单收益率必须用连乘：(1+r1) * (1+r2) * ... * (1+rN) - 1
# 对数收益率只需要直接相加：r_log1 + r_log2 + ... + r_logN
print("\n--- 💎 可加性实战验证 ---")

# 取 2024 全年数据（保留完整的收益率序列，不做任何截断）
df_2024 = df.loc['2024-01-01':'2024-12-31'].dropna()

if len(df_2024) > 0:
    # 地面真相（金融业务标准 YTD 算法）：
    # 分母用 2023 年末最后一个交易日的收盘价，而不是 2024 年首日收盘价
    # 因为 2024 年第一天的涨跌本身就属于 "2024 年收益" 的一部分
    last_price_2023 = df.loc[:'2023-12-31', 'close_price'].iloc[-1]
    ground_truth = df_2024['close_price'].iloc[-1] / last_price_2023 - 1

    # 方式A：简单收益率累计 → 必须连乘（保留全部天数，包括第一天）
    cumulative_simple = (1 + df_2024['simple_return']).prod() - 1

    # 方式B：对数收益率累计 → 直接求和，再 exp 还原
    cumulative_log = np.exp(df_2024['log_return_v1'].sum()) - 1

    print(f"📌 2023年末收盘价（基准）: {last_price_2023:.3f}")
    print(f"📌 2024年末日价格:         {df_2024['close_price'].iloc[-1]:.3f}")
    print(f"✅ 地面真相（YTD标准算法）:  {ground_truth:.6f} ({ground_truth*100:.2f}%)")
    print(f"✅ 简单收益率连乘:           {cumulative_simple:.6f} ({cumulative_simple*100:.2f}%)")
    print(f"✅ 对数收益率求和后还原:     {cumulative_log:.6f} ({cumulative_log*100:.2f}%)")
    print(f"\n💡 三者完全吻合！基准统一为2023年末收盘价，计入了完整的2024年每一天收益。")
    print(f"   对数收益率只用了一次 sum()，简单收益率需要 prod() 连乘——加法更快更稳。")
else:
    print("⚠️ 数据库中暂无2024年数据，请检查数据抓取范围。")

# ==========================================
# 📊 5. 数值稳定性：当收益率很小时两者几乎相等
# ==========================================
print("\n--- 📊 简单 vs 对数收益率的差值分析 ---")
df['return_diff'] = df['simple_return'] - df['log_return_v1']
stats = df['return_diff'].dropna().describe()
print(f"均值差异:   {stats['mean']:.8f}")
print(f"最大差异:   {stats['max']:.8f}")
print(f"标准差:     {stats['std']:.8f}")
print(f"\n💡 日度级别下两者差异极小（万分之几），但在月度/年度累计时差异会被放大。")
print(f"   对数收益率因为可加性，在多周期聚合与风险建模中是更优选择。")
