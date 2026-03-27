import duckdb
import pandas as pd
import numpy as np
import os

# 1. 动态寻址连接数据库
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
db_path = os.path.join(project_root, 'Database', 'files', 'market_data.duckdb')

conn = duckdb.connect(db_path, read_only=True)

# 2. 提取数据并转化为 Pandas DataFrame
# 注意：你的计划明确要求今天学习 Pandas 的 DatetimeIndex，所以我们用 .df() 而不是 .pl()
df = conn.sql("""
    SELECT trade_date, close_price 
    FROM etf_daily_kline 
    WHERE symbol = 'sh510300'
    ORDER BY trade_date
""").df()
conn.close()

# 3. 核心基建：设置时间序列索引 (DatetimeIndex)
# 这是 Pandas 处理金融时间序列的灵魂步骤，将普通列变成时间轴
df['trade_date'] = pd.to_datetime(df['trade_date'])
df.set_index('trade_date', inplace=True)

# ==========================================
# 💣 破坏测试：人工“挖空”模拟停牌/断网
# ==========================================
print("💣 正在对真实数据进行随机破坏，模拟数据缺失...")
# 随机选择 10 个日期，把它们的收盘价强行变成 NaN (Not a Number)
np.random.seed(42) # 保证每次挖空的位置一样
random_indices = np.random.choice(df.index, size=10, replace=False)
df.loc[random_indices, 'close_price'] = np.nan

# 我们找出其中被挖空的一天（比如离现在较近的一天）来看看灾难现场
print("\n🚨 灾难现场 (包含 NaN 的脏数据):")
dirty_sample = df[df['close_price'].isna()].head(3)
print(dirty_sample)

# ==========================================
# 🛠️ 抢修基建：前向填充 (Forward Fill)
# ==========================================
print("\n🛠️ 启动 ffill 前向填充修复逻辑...")

# ffill 的核心逻辑：如果今天没价格，就拿上一个有效交易日的价格填进来
# 我们将修复后的数据存在新列，方便对比
df['close_price_clean'] = df['close_price'].ffill()

# ==========================================
# 🔍 验尸报告
# ==========================================
print("\n✅ 修复结果对比:")
# 打印刚才那几个变成 NaN 的日期，看看它们现在被填成了什么
for date in dirty_sample.index:
    # 提取被挖空那一天的前后各一天的数据，展示修复过程
    start_date = date - pd.Timedelta(days=3)
    end_date = date + pd.Timedelta(days=3)
    # 取这几天的数据段
    context = df.loc[start_date:end_date]
    print(f"\n围绕 {date.date()} 的修复情况:")
    print(context[['close_price', 'close_price_clean']])
    break # 只展示一组，避免刷屏