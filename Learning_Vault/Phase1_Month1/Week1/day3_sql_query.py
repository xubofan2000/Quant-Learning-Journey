import duckdb
import os
import time

# 1. 动态定位昨天生成的 CSV 文件路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
csv_path = os.path.join(project_root, 'Database', 'files', 'dummy_market_data.csv')

# 安全校验
if not os.path.exists(csv_path):
    print(f"❌ 找不到数据文件，请确认 Day 2 脚本已成功运行！路径: {csv_path}")
    exit()

print(f"🚀 开始使用 DuckDB 狂飙查询 10 万行 CSV...\n")

start_time = time.time()

# 2. 核心魔法：写给 SQL 老兵的极速查询
# 仔细看 FROM 后面的语法，我们直接把物理路径当成了“表名”！
# DuckDB 会自动推断 CSV 的列名和数据类型，并利用列式引擎的优势跳过不需要扫描的列（比如 date 列）。
sql_query = f"""
    SELECT 
        ticker,
        MAX(price) AS highest_price,
        SUM(volume) AS total_volume,
        COUNT(*) AS trade_days
    FROM '{csv_path}'
    GROUP BY ticker
    ORDER BY total_volume DESC
"""

# 3. 执行查询并取回结果
# .df() 只是为了把结果包装成 Pandas DataFrame 以便在控制台打印得更整齐，
# 实际上几十兆数据的过滤和数学计算，全程都在 DuckDB 的 C++ 引擎里完成了。
result_df = duckdb.query(sql_query).df()

end_time = time.time()

print(result_df)
print(f"\n⏱️ 聚合查询耗时: {end_time - start_time:.4f} 秒")
print("💡 核心认知：你根本没有写 pd.read_csv()！数据没有被整体载入内存，这叫 '零拷贝查询 (Zero-Copy Query)'。")