# %%
import pandas as pd
import numpy as np
import duckdb
import os

# %%
# 动态寻址
current_dir = os.path.dirname(os.path.abspath(__file__)) # 当前目录
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..')) # 向上找三层到项目根目录
db_path = os.path.abspath(os.path.join(project_root,'Database','files','market_data.duckdb'))

# 连接动态寻址的数据库表，写SQL查询语句实例化为df
conn = duckdb.connect(db_path)
df = conn.sql("""
    SELECT trade_date, close_price
    FROM etf_daily_kline
    WHERE symbol = 'sh510300'
    ORDER BY trade_date
""").df()

conn.close()

# %%
# 设置交易日期为时间格式并作为index
df['trade_date'] = pd.to_datetime(df['trade_date'])
df.set_index('trade_date', inplace=True)

# 简单收益率
df['simple_return'] = df['close_price'].pct_change()
# 对数收益率v1
df['log_return_v1'] = np.log(df['close_price']/df['close_price'].shift(1))
# 对数收益率v2
df['log_return_v2'] = np.log(df['close_price'])-np.log(df['close_price'].shift(1))
# 检验对数收益率的两种算法是否一致，一致才会继续
pd.testing.assert_series_equal(
    df['log_return_v1'].dropna(),
    df['log_return_v2'].dropna(),
    check_names=False,
    atol=1e-12
)
print("对数收益率的两种算法一致")

print("\n简单vs对数收益率，最近10天")
print(df[['close_price','simple_return','log_return_v1']].dropna().tail(10))

# %%
print("可加性验证")

df_2025 = df.loc['20250101':'20251231'].dropna()

if len(df_2025)>0:
    last_price_2024 = df.loc[:'20241231','close_price'].iloc[-1]
    ground_truth = df_2025['close_price'].iloc[-1]/last_price_2024 - 1
    cumulative_simple = (1+df_2025['simple_return']).prod()-1
    cumulative_log = np.exp(df_2025['log_return_v1'].sum())-1
    print(f"2024年末收盘价：{last_price_2024:.3f}")
    print(f"2025年末收盘价：{df_2025['close_price'].iloc[-1]:.3f}")
    print(f"地面真相（YTD标准算法）：{ground_truth:.6f} ({ground_truth*100:.2f}%)")
    print(f"简单收益率连乘：{cumulative_simple:.6f} ({cumulative_simple*100:.2f}%)")
    print(f"对数收益率求和后还原：{cumulative_log:.6f} ({cumulative_log*100:.2f}%)")
    print(f"\n💡 三者完全吻合！基准统一为2024年末收盘价，计入了完整的2025年每一天收益。")
    print(f"   对数收益率只用了一次 sum()，简单收益率需要 prod() 连乘——加法更快更稳。")
else:
    print("⚠️ 数据库中暂无2025年数据，请检查数据抓取范围。")

# %%
