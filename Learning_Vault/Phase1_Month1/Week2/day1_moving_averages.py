import duckdb
import polars as pl
import os

# 1. 动态寻址连接数据库
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
db_path = os.path.join(project_root, 'Database', 'files', 'market_data.duckdb')

print("🔌 连接 DuckDB 并提取数据...")
conn = duckdb.connect(db_path, read_only=True)

# 2. 跨维度的握手：DuckDB 直接输出 Polars DataFrame！
# 注意看最后的 .pl()，DuckDB 会基于 Apache Arrow 内存格式，瞬间把数据交给 Polars，全程不拷贝！
df = conn.sql("""
    SELECT trade_date, close_price 
    FROM etf_daily_kline 
    WHERE symbol = 'sh510300'
""").pl()
conn.close()

# 3. 时间序列的铁律：必须排序！
# 在做任何滚动计算前，确保数据是按时间正序排列的，否则全错。
df = df.sort("trade_date")

print("⚙️ 启动 Polars 引擎，计算特征因子...")

# 4. Polars 链式特征工程 (Feature Engineering)
# 用 with_columns 可以同时高效地并行新增多列
result_df = df.with_columns([
    # 计算 20 日简单移动平均 (SMA)
    pl.col("close_price")
      .rolling_mean(window_size=20)
      .alias("SMA_20"),
      
    # 计算 20 日指数移动平均 (EMA)
    # span=20 在底层的效果等同于 alpha = 2 / (20 + 1)
    pl.col("close_price")
      .ewm_mean(span=20, adjust=False)
      .alias("EMA_20")
])

# 5. 打印对比结果
# 我们跳过前 20 行（因为前 20 天的 SMA_20 会是 null），看后面的数据
print("\n📊 SMA vs EMA 计算结果对比 (截取部分):")
print(result_df.drop_nulls().head(10))

# 验证 EMA 的灵敏度：我们选取最近的 5 天数据看看差异
print("\n🔍 观察最新 5 天的数据 (注意看 EMA 是不是比 SMA 更贴近当天的 close_price):")
print(result_df.tail(5))