import polars as pl
import os
import time

# 1. 动态定位 CSV 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
csv_path = os.path.join(project_root, 'Database', 'files', 'dummy_market_data.csv')

if not os.path.exists(csv_path):
    print(f"❌ 找不到数据文件，路径: {csv_path}")
    exit()

print("🚀 开始测试 Polars 懒加载与执行计划...\n")
start_time = time.time()

# 2. 构建“懒加载”查询计划 (注意这里用的是 scan_csv 而不是 read_csv)
lazy_query = (
    pl.scan_csv(csv_path)                      # 只是扫一眼结构，不加载数据！
    .filter(pl.col('volume') > 900000)         # WHERE volume > 900000
    .group_by('ticker')                        # GROUP BY ticker
    .agg([                                     # SELECT MAX(price) AS max_price
        pl.max('price').alias('max_price')
    ])
)

# 💡 给 SQL 工程师的惊喜：打印物理执行计划
print("--- 📊 物理执行计划 (类似 SQL 的 EXPLAIN) ---")
print(lazy_query.explain())
print("--------------------------------------------\n")

# 3. 真正扣动扳机，启动多线程计算
print("💥 收到 collect() 指令，多线程全速执行...")
result_df = lazy_query.collect()

end_time = time.time()

print(result_df)
print(f"\n⏱️ Polars 构建计划并计算总耗时: {end_time - start_time:.4f} 秒")