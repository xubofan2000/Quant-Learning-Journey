import duckdb
import pandas as pd
import numpy as np
import os
import time

# 1. 动态寻址
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
db_path = os.path.join(project_root, 'Database', 'files', 'market_data.duckdb')
output_dir = os.path.join(project_root, 'Database', 'files')

# ==========================================
# 📚 1. 构建"清洗后的宽表"（串联 Day 1~4 的全部成果）
# ==========================================
print("📂 构建特征宽表...")

conn = duckdb.connect(db_path, read_only=True)

# 从 DuckDB 读取 ETF 数据
df_etf = conn.sql("""
    SELECT trade_date, close_price, volume
    FROM etf_daily_kline 
    WHERE symbol = 'sh510300'
    ORDER BY trade_date
""").df()

# 如果有上证指数表，也读出来做 JOIN（Day 4 你已经落盘了）
try:
    df_index = conn.sql("""
        SELECT date AS trade_date, close AS index_close
        FROM szzs
        ORDER BY date
    """).df()
    has_index = True
    print("  ✅ 检测到 szzs 表，将执行 LEFT JOIN 构建宽表")
except:
    has_index = False
    print("  ⚠️ 未检测到 szzs 表，仅使用 ETF 数据")

conn.close()

# 构建时间索引
df_etf['trade_date'] = pd.to_datetime(df_etf['trade_date'])
df_etf.rename(columns={'close_price': 'etf_close', 'volume': 'etf_volume'}, inplace=True)

# LEFT JOIN（如果有指数数据）
if has_index:
    df_index['trade_date'] = pd.to_datetime(df_index['trade_date'])
    df = pd.merge(df_etf, df_index, on='trade_date', how='left')
    assert len(df) == len(df_etf), "行数膨胀！"
else:
    df = df_etf.copy()

df = df.set_index('trade_date').sort_index()

# Day 1: ffill 填充缺失值
df = df.ffill()

# Day 2: 滚动窗口特征
df['SMA_5'] = df['etf_close'].rolling(5).mean()
df['SMA_20'] = df['etf_close'].rolling(20).mean()

# Day 3: 收益率
df['etf_return'] = df['etf_close'].pct_change()
df['etf_log_ret'] = np.log(df['etf_close'] / df['etf_close'].shift(1))

if has_index:
    df['index_return'] = df['index_close'].pct_change()
    df['excess_return'] = df['etf_return'] - df['index_return']

# 去掉前 20 行的 NaN（SMA_20 需要 20 天的预热期）
df_clean = df.iloc[20:].copy()
print(f"  宽表构建完成: {df_clean.shape[0]} 行 × {df_clean.shape[1]} 列")

# ==========================================
# 💾 2. 保存为三种格式，进行体积与速度对比
# ==========================================
csv_path = os.path.join(output_dir, 'clean_data.csv')
parquet_path = os.path.join(output_dir, 'clean_data.parquet')

# 保存 CSV
df_clean.to_csv(csv_path)

# 保存 Parquet（Snappy 压缩，这是默认也是最常用的压缩算法）
df_clean.to_parquet(parquet_path, engine='pyarrow', compression='snappy')

csv_size = os.path.getsize(csv_path)
parquet_size = os.path.getsize(parquet_path)

print(f"\n--- 💾 文件体积对比 ---")
print(f"  CSV:     {csv_size / 1024:.1f} KB")
print(f"  Parquet: {parquet_size / 1024:.1f} KB")
print(f"  压缩比:  {csv_size / parquet_size:.1f}x （Parquet 比 CSV 小 {(1 - parquet_size/csv_size)*100:.0f}%）")

# ==========================================
# ⚡ 3. 读取速度对比
# ==========================================
print(f"\n--- ⚡ 读取速度对比 ---")

# CSV 读取
t0 = time.perf_counter()
for _ in range(10):
    _ = pd.read_csv(csv_path, index_col=0, parse_dates=True)
csv_time = (time.perf_counter() - t0) / 10

# Parquet 读取
t0 = time.perf_counter()
for _ in range(10):
    _ = pd.read_parquet(parquet_path)
parquet_time = (time.perf_counter() - t0) / 10

print(f"  CSV 平均读取:     {csv_time*1000:.1f} ms")
print(f"  Parquet 平均读取: {parquet_time*1000:.1f} ms")
print(f"  速度比:           {csv_time/parquet_time:.1f}x 快")

# ==========================================
# 🦆 4. DuckDB 直接查询 Parquet（零拷贝，不经过 Pandas）
# ==========================================
print(f"\n--- 🦆 DuckDB 直接查询 Parquet ---")

# DuckDB 可以直接对 Parquet 文件执行 SQL，不需要先 read 进内存
conn = duckdb.connect(':memory:')

# 查询示例：按月聚合平均收盘价
result = conn.sql(f"""
    SELECT 
        DATE_TRUNC('month', trade_date) AS month,
        ROUND(AVG(etf_close), 3) AS avg_close,
        ROUND(SUM(etf_log_ret), 4) AS monthly_log_return,
        COUNT(*) AS trading_days
    FROM '{parquet_path}'
    WHERE trade_date >= '2025-01-01'
    GROUP BY DATE_TRUNC('month', trade_date)
    ORDER BY month
""").df()

print("  直接对 Parquet 文件执行 SQL 聚合（2025年至今月度统计）:")
print(result.to_string(index=False))

# 速度对比：DuckDB 查询 Parquet vs CSV
t0 = time.perf_counter()
for _ in range(10):
    conn.sql(f"SELECT AVG(etf_close) FROM '{parquet_path}'").fetchone()
duckdb_parquet_time = (time.perf_counter() - t0) / 10

t0 = time.perf_counter()
for _ in range(10):
    conn.sql(f"SELECT AVG(etf_close) FROM '{csv_path}'").fetchone()
duckdb_csv_time = (time.perf_counter() - t0) / 10

conn.close()

print(f"\n  DuckDB 查询 Parquet: {duckdb_parquet_time*1000:.1f} ms")
print(f"  DuckDB 查询 CSV:     {duckdb_csv_time*1000:.1f} ms")
print(f"  Parquet 快 {duckdb_csv_time/duckdb_parquet_time:.1f}x")

# ==========================================
# 📊 5. Parquet 的元数据自省
# ==========================================
print(f"\n--- 📊 Parquet 元数据 ---")
import pyarrow.parquet as pq
meta = pq.read_metadata(parquet_path)
print(f"  行数: {meta.num_rows}")
print(f"  列数: {meta.num_columns}")
print(f"  行组数: {meta.num_row_groups}")
print(f"  创建库: {meta.created_by}")
print(f"\n  列级别类型信息:")
schema = pq.read_schema(parquet_path)
for i, field in enumerate(schema):
    print(f"    [{i}] {field.name}: {field.type}")

print(f"\n💡 Parquet 是自描述格式——列名、类型、压缩方式全部记录在文件尾部的 Footer 里。")
print(f"   读取时无需猜测或手动指定 dtype，彻底告别 CSV 的类型推断地狱。")
