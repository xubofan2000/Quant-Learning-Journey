import duckdb
import pandas as pd
import os

# 1. 动态寻址
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
db_path = os.path.join(project_root, 'Database', 'files', 'market_data.duckdb')

print("🚀 开启 Day 7：终极对账 (DuckDB vs Pandas)...\n")

# 注意：这里加了 read_only=True，保护你的心血数据绝不会被意外修改
conn = duckdb.connect(db_path, read_only=True)

# ==========================================
# 💎 破局：用 Python 充当你的专属“数据可视化客户端”
# ==========================================
print("👀 预览数据库前 5 行 (解决刚才插件打不开的问题):")
print(conn.sql("SELECT * FROM etf_daily_kline ORDER BY trade_date DESC LIMIT 5").df())
print("-" * 60)

# ==========================================
# 引擎 1：DuckDB SQL 计算月度均价 (在硬盘和 C++ 层面计算)
# ==========================================
print("🧠 引擎 1: DuckDB SQL 正在计算...")
duck_df = conn.sql("""
    SELECT 
        strftime(trade_date, '%Y-%m') AS month,
        ROUND(AVG(close_price), 4) AS avg_close
    FROM etf_daily_kline
    GROUP BY month
    ORDER BY month
""").df()

# ==========================================
# 引擎 2：Pandas 重采样计算 (在内存层面计算)
# ==========================================
print("🧠 引擎 2: Pandas 内存重采样正在计算...")
# 先把最基础的两列数据原封不动拉进内存
raw_df = conn.sql("SELECT trade_date, close_price FROM etf_daily_kline").df()

# Pandas 经典的时间序列处理流 (Time Series Resampling)
raw_df['trade_date'] = pd.to_datetime(raw_df['trade_date'])
raw_df.set_index('trade_date', inplace=True)

# 'ME' 代表 Month End，把每天的收盘价按月打包求平均
pandas_df = raw_df.resample('ME')['close_price'].mean().reset_index()

# 格式化对齐，为了稍后的公平比对
pandas_df['month'] = pandas_df['trade_date'].dt.strftime('%Y-%m')
pandas_df['avg_close'] = pandas_df['close_price'].round(4)
pandas_df = pandas_df[['month', 'avg_close']] # 只留我们要比对的两列

# ==========================================
# ⚖️ 终极风控：自动化断言 (Assert)
# ==========================================
print("⚖️ 开始执行严格对账校验...")
try:
    # 强制比对两者的 avg_close 序列
    pd.testing.assert_series_equal(
        duck_df['avg_close'], 
        pandas_df['avg_close'], 
        check_names=False,
        check_exact=False,  # 关闭绝对一致性检查
        atol=1e-3           # Absolute Tolerance: 允许 0.001 的极小误差
    )
    print("\n🎉【恭喜】对账完美通过！双引擎结果吻合（误差在 0.001 容忍度内）！")
except AssertionError as e:
    print("\n❌ 对账失败！系统发现致命差异：\n", e)

conn.close()