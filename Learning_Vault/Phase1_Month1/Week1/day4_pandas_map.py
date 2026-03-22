import pandas as pd
import os
import time

# 1. 动态定位 Day 2 生成的 CSV 文件
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
csv_path = os.path.join(project_root, 'Database', 'files', 'dummy_market_data.csv')

if not os.path.exists(csv_path):
    print(f"❌ 找不到数据文件，路径: {csv_path}")
    exit()

print("🚀 开始加载数据并执行 Pandas 映射测试...\n")
start_time = time.time()

# ⚠️ 架构认知：这里必须把 10 万行数据全量反序列化加载到内存中。
# 注意对比加载时间与昨天 DuckDB 零拷贝查询时间的差异。
df = pd.read_csv(csv_path)
load_time = time.time()
print(f"✅ Pandas 加载 10 万行数据耗时: {load_time - start_time:.4f} 秒\n")

# ==========================================
# 映射 1: SELECT (列选择)
# SQL: SELECT ticker, price FROM df LIMIT 5;
# ==========================================
print("--- 1. SELECT 映射 ---")
# Pandas 中，传入一个包含列名的列表 [['列1', '列2']] 即可实现投影
df_select = df[['ticker', 'price']].head(5)
print(df_select, "\n")

# ==========================================
# 映射 2: WHERE (行过滤 / 布尔索引)
# SQL: SELECT * FROM df WHERE price > 480 LIMIT 5;
# ==========================================
print("--- 2. WHERE 映射 ---")
# Pandas 核心逻辑：先生成一列布尔值 (df['price'] > 480)，再把这列布尔值作为“遮罩(Mask)”塞回给 df[]
df_where = df[df['price'] > 480].head(5)
print(df_where, "\n")

# ==========================================
# 映射 3: GROUP BY 与 聚合
# SQL: SELECT ticker, SUM(volume) AS total_volume FROM df GROUP BY ticker;
# ==========================================
print("--- 3. GROUP BY 映射 ---")
# .reset_index() 的作用是把分组键 (ticker) 从特殊的索引位还原成普通的数据列，这是 Pandas 新手极易踩坑的点
df_groupby = df.groupby('ticker')['volume'].sum().reset_index()
df_groupby = df_groupby.rename(columns={'volume': 'total_volume'})
print(df_groupby, "\n")

# ==========================================
# 映射 4: 综合实战 (WHERE + GROUP BY)
# SQL: SELECT ticker, MAX(price) FROM df WHERE volume > 900000 GROUP BY ticker;
# ==========================================
print("--- 4. 综合实战 (链式调用) ---")
# 工业级 Pandas 代码通常写成流水的链式调用，从左读到右
df_complex = (
    df[df['volume'] > 900000]          # 1. 先 WHERE 过滤
    .groupby('ticker')['price']        # 2. 按 ticker 分组，只关注 price 列
    .max()                             # 3. 取 MAX
    .reset_index()                     # 4. 拍平索引
)
print(df_complex)

print(f"\n⏱️ Pandas 计算总耗时 (不含文件IO): {time.time() - load_time:.4f} 秒")