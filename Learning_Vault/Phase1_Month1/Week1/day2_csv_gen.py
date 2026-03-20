import pandas as pd
import numpy as np
import os
import time

# 启动计时器，感受一下向量化的速度
start_time = time.time()

print("🚀 开始生成 10 万行模拟行情数据...")

# 1. 设置随机种子，保证每次运行生成的“随机数”都一样，方便后续对账调试
np.random.seed(42)

# 2. 定义基础数据池 (模拟 5 只 A 股核心资产)
tickers = ['600519', '000001', '600036', '002594', '000858']
num_rows = 100000

# 3. 向量化生成核心列 (核心考点：千万不要用 for 循环生成 10 万次，用 NumPy 的底层 C 语言数组一次性生成)
# 随机选择股票代码
random_tickers = np.random.choice(tickers, size=num_rows)
# 生成随机日期 (从 2020-01-01 开始，往后随机加上 0~1500 天)
random_dates = pd.to_datetime('2020-01-01') + pd.to_timedelta(np.random.randint(0, 1500, size=num_rows), unit='D')
# 生成随机价格 (10 到 500 之间，保留两位小数)
random_prices = np.round(np.random.uniform(10, 500, size=num_rows), 2)
# 生成随机成交量 (1000 到 1000000 之间)
random_volumes = np.random.randint(1000, 1000000, size=num_rows)

# 4. 组装成 Pandas DataFrame (在你的脑海里，把它等价于 SQL 里的内存临时表)
df = pd.DataFrame({
    'date': random_dates,
    'ticker': random_tickers,
    'price': random_prices,
    'volume': random_volumes
})

# 5. 按照日期和代码排序，模拟真实的时间序列切片
df = df.sort_values(by=['date', 'ticker']).reset_index(drop=True)

# 6. 动态定位保存路径 (基于当前脚本位置，向上推导工程根目录)
current_dir = os.path.dirname(os.path.abspath(__file__))
# 你的脚本在 Week1，往上跳 3 级 (Week1 -> Phase1_Month1 -> Learning_Vault -> Bohr根目录)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))

# 拼接出你想要的 Database/files 目录
db_dir = os.path.join(project_root, 'Database', 'files')

# 【关键保障】如果这个目录不存在，自动帮你创建，不报错
os.makedirs(db_dir, exist_ok=True)

csv_path = os.path.join(db_dir, 'dummy_market_data.csv')

# 7. 导出为 CSV 文件
df.to_csv(csv_path, index=False)

end_time = time.time()
print(f"✅ 生成完毕！文件已保存至: {csv_path}")
print(f"⏱️ 耗时: {end_time - start_time:.2f} 秒")
print(f"\n📊 你的临时表前 5 行预览:\n{df.head()}")