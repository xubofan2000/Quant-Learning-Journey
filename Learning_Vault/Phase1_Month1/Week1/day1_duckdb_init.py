import duckdb
import os

# 1. 定义数据库文件路径 (相当于在本地创建一个轻量级的数据仓库)
db_path = 'D:\project\Bohr\Database\market_data.duckdb'

# 如果存在旧文件，先清理掉，保证每次运行都是纯净状态
if os.path.exists(db_path):
    os.remove(db_path)
    print("🧹 已清理旧的数据库文件。")

# 2. 连接/创建 DuckDB 数据库
# duckdb.connect() 如果文件不存在会自动创建。这比安装重量级的 MySQL 服务器轻量一万倍。
conn = duckdb.connect(db_path)
print(f"✅ 成功连接到本地列式数据库: {db_path}")

# 3. 执行纯正的 SQL：建表
conn.execute('''
    CREATE TABLE stock_prices (
        date DATE,
        ticker VARCHAR,
        close_price DOUBLE,
        volume BIGINT
    )
''')
print("✅ 成功创建空表: stock_prices")

# 4. 验证表结构 (使用 SQL 的 DESCRIBE)
print("\n📊 表结构如下:")
df_schema = conn.execute("DESCRIBE stock_prices").df() # .df() 直接将查询结果转为 Pandas DataFrame 方便打印
print(df_schema)

# 5. 关闭连接，释放文件锁
conn.close()
print("\n🔒 数据库连接已关闭，初始化基建完成！")