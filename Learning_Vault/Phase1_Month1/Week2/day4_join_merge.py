import duckdb
import pandas as pd
import akshare as ak
import os

# 1. 动态寻址连接数据库
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
db_path = os.path.join(project_root, 'Database', 'files', 'market_data.duckdb')

# ==========================================
# 📚 准备两张表：一只 ETF（个股角色）+ 一个基准指数
# ==========================================

# 表A：从 DuckDB 读取已有的沪深300ETF (sh510300) 作为"个股"
print("📂 从 DuckDB 读取沪深300ETF数据...")
conn = duckdb.connect(db_path, read_only=True)
df_etf = conn.sql("""
    SELECT trade_date, close_price, volume
    FROM etf_daily_kline 
    WHERE symbol = 'sh510300'
    ORDER BY trade_date
""").df()
conn.close()

df_etf['trade_date'] = pd.to_datetime(df_etf['trade_date'])
df_etf.rename(columns={
    'close_price': 'etf_close',
    'volume': 'etf_volume'
}, inplace=True)

print(f"  ETF 数据量: {len(df_etf)} 行, 日期范围: {df_etf['trade_date'].min().date()} ~ {df_etf['trade_date'].max().date()}")

# 表B：用 AKShare 抓取上证指数 (sh000001) 作为"大盘基准"
# 我们故意取一个日期范围更大的数据集，来体现 LEFT JOIN 的意义
print("🌐 从 AKShare 抓取上证指数数据...")
df_index = ak.stock_zh_index_daily(symbol="sh000001")

# 只保留需要的列并重命名
df_index = df_index.rename(columns={
    'date': 'trade_date',
    'close': 'index_close',
    'volume': 'index_volume'
})[['trade_date', 'index_close', 'index_volume']]

df_index['trade_date'] = pd.to_datetime(df_index['trade_date'])
print(f"  上证指数数据量: {len(df_index)} 行, 日期范围: {df_index['trade_date'].min().date()} ~ {df_index['trade_date'].max().date()}")

# ==========================================
# 🔗 2. LEFT JOIN：以 ETF 为主表，按日期关联上证指数
# SQL 等价：SELECT * FROM df_etf LEFT JOIN df_index ON df_etf.trade_date = df_index.trade_date
# ==========================================
print("\n🔗 执行 LEFT JOIN (Pandas merge)...")

df_merged = pd.merge(
    df_etf,            # 左表（主表）：你关心的 ETF
    df_index,          # 右表（参照表）：大盘基准
    on='trade_date',   # 关联键
    how='left'         # LEFT JOIN：保留左表所有行，右表没匹配到的填 NaN
)

print(f"\n--- 合并结果 ---")
print(f"  左表(ETF)行数:   {len(df_etf)}")
print(f"  右表(指数)行数:  {len(df_index)}")
print(f"  合并后行数:      {len(df_merged)}")

# ==========================================
# ⚠️ 3. LEFT JOIN 的第一条铁律：行数校验
# ==========================================
# 如果合并后行数 > 左表行数，说明右表有重复的 trade_date（一对多匹配导致行数膨胀）
# 这是 JOIN 操作中最隐蔽最致命的陷阱
assert len(df_merged) == len(df_etf), \
    f"❌ 行数膨胀！合并后 {len(df_merged)} 行 > 左表 {len(df_etf)} 行，右表存在重复日期！"
print("✅ 行数校验通过：合并后行数 == 左表行数，无重复键膨胀")

# 检查右表有多少天没匹配上（NaN）
nan_count = df_merged['index_close'].isna().sum()
print(f"📊 未匹配的天数（NaN）: {nan_count} 天")

if nan_count > 0:
    print("  这些天的 ETF 有交易但上证指数没数据（可能是数据源覆盖范围差异）:")
    print(df_merged[df_merged['index_close'].isna()][['trade_date', 'etf_close']].head(5))

# ==========================================
# 📊 4. 核心应用：计算超额收益 (Excess Return / Alpha)
# ==========================================
# 超额收益 = 个股收益率 - 基准收益率
# 如果 > 0，说明你跑赢了大盘；如果 < 0，说明跑输了
import numpy as np

df_merged = df_merged.set_index('trade_date').sort_index()

# 用对数收益率计算超额收益（Day 3 的时间可加性在这里派上用场）
df_merged['etf_log_ret'] = np.log(df_merged['etf_close'] / df_merged['etf_close'].shift(1))
df_merged['index_log_ret'] = np.log(df_merged['index_close'] / df_merged['index_close'].shift(1))
df_merged['excess_log_ret'] = df_merged['etf_log_ret'] - df_merged['index_log_ret']

# 同时保留简单收益率，供日度展示用（人类更易读）
df_merged['etf_return'] = df_merged['etf_close'].pct_change()
df_merged['index_return'] = df_merged['index_close'].pct_change()
df_merged['excess_return'] = df_merged['etf_return'] - df_merged['index_return']

# 只看有完整数据（无NaN）的行
df_clean = df_merged.dropna(subset=['excess_log_ret'])

print(f"\n--- 超额收益统计 (全区间) ---")
print(f"  日均超额收益:     {df_clean['excess_return'].mean()*100:.4f}%")
print(f"  跑赢大盘天数占比: {(df_clean['excess_return'] > 0).mean()*100:.1f}%")

# 按年度统计超额收益（基于对数收益率的严谨聚合）
# 对数收益率可以直接 .sum()，然后 exp() 还原为真实百分比涨幅
print("\n--- 年度超额收益汇总（基于对数收益率严谨聚合）---")
annual_alpha_log = df_clean['excess_log_ret'].resample('YE').sum()
annual_alpha_real = (np.exp(annual_alpha_log) - 1) * 100
for year, alpha in annual_alpha_real.items():
    emoji = "📈" if alpha > 0 else "📉"
    print(f"  {emoji} {year.year}年: {alpha:+.2f}%")

# ==========================================
# 🔬 5. 对比实验：INNER JOIN vs LEFT JOIN 的区别
# ==========================================
print("\n🔬 JOIN 类型对比实验:")

df_inner = pd.merge(df_etf, df_index, on='trade_date', how='inner')
df_left = pd.merge(df_etf, df_index, on='trade_date', how='left')
df_outer = pd.merge(df_etf, df_index, on='trade_date', how='outer')

print(f"  INNER JOIN: {len(df_inner)} 行 （只保留两表都有的交易日）")
print(f"  LEFT JOIN:  {len(df_left)} 行  （保留ETF所有交易日，指数缺失的填NaN）")
print(f"  OUTER JOIN: {len(df_outer)} 行  （保留双方所有日期，各自缺失的填NaN）")
print(f"\n💡 量化场景下几乎总是用 LEFT JOIN：以你的持仓标的为主，基准数据缺失时宁可填NaN")
print(f"   也不能丢掉主表的任何一天——因为每一天的持仓都影响你的净值曲线。")

# 展示最终对齐结果
print("\n--- 最终对齐表（最近5天）---")
print(df_merged[['etf_close', 'index_close', 'etf_return', 'index_return', 'excess_return']].tail(5))
