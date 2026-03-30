import duckdb
import pandas as pd
import os

# 1. 动态寻址连接数据库
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
db_path = os.path.join(project_root, 'Database', 'files', 'market_data.duckdb')

conn = duckdb.connect(db_path, read_only=True)

df = conn.sql("""
    SELECT trade_date, close_price 
    FROM etf_daily_kline 
    WHERE symbol = 'sh510300'
    ORDER BY trade_date
""").df()
conn.close()

# 2. 构建 DatetimeIndex（复用 Day 1 的基建）
df['trade_date'] = pd.to_datetime(df['trade_date'])
df.set_index('trade_date', inplace=True)

# ==========================================
# 📚 核心概念：SQL Window Function 在 Pandas 中的映射
# SQL:  AVG(close_price) OVER (ORDER BY trade_date ROWS BETWEEN 4 PRECEDING AND CURRENT ROW)
# 等价于 Pandas 的 .rolling(window=5).mean()
# ==========================================

# 3. .rolling() —— 滚动窗口（SQL窗口函数的Python等价物）
print("⚙️ 正在计算移动平均线...\n")

# SMA_5: 过去5个交易日的简单移动平均（短期趋势信号）
# 窗口大小=5 意味着：取当前行 + 前面4行，共5天的均值
df['SMA_5'] = df['close_price'].rolling(window=5).mean()

# SMA_20: 过去20个交易日的简单移动平均（中期趋势信号）
df['SMA_20'] = df['close_price'].rolling(window=20).mean()

# 注意：前 N-1 行会是 NaN（因为还凑不够 N 天的数据来算平均）
print("--- 1. SMA 计算结果（跳过前20行NaN区） ---")
print(df.dropna().head(10))

# ==========================================
# 📚 核心概念：.shift() —— 时间位移（SQL的LAG/LEAD等价物）
# SQL:  LAG(close_price, 1) OVER (ORDER BY trade_date)
# 等价于 Pandas 的 .shift(1)
# ==========================================

# 4. .shift() —— 把整列数据往下或往上平移
# shift(1)：每一行的值变成"昨天的收盘价"
# 金融意义：计算日收益率的前置步骤（今天价格 / 昨天价格 - 1）
df['prev_close'] = df['close_price'].shift(1)

# 利用 shift 直接算出每日简单收益率
# 公式：(今天的价格 - 昨天的价格) / 昨天的价格
df['daily_return'] = (df['close_price'] - df['prev_close']) / df['prev_close']

# 验证：Pandas 内置的 pct_change() 做的事情一模一样
df['daily_return_verify'] = df['close_price'].pct_change()

print("\n--- 2. shift() 与收益率计算 ---")
print(df[['close_price', 'prev_close', 'daily_return', 'daily_return_verify']].dropna().head(10))

# ==========================================
# ⚖️ 5. 严格校验：手工 shift 计算 vs pct_change 结果断言
# ==========================================
print("\n⚖️ 执行 shift 手工计算 vs pct_change 对账校验...")
pd.testing.assert_series_equal(
    df['daily_return'].dropna(),
    df['daily_return_verify'].dropna(),
    check_names=False,
    atol=1e-10  # 浮点精度极高容差
)
print("🎉 对账通过！手工 shift 计算与 pct_change 结果完全吻合！")

# ==========================================
# 📊 6. 金叉/死叉信号探测（SMA交叉策略初探）
# ==========================================
# 当短期均线(SMA_5)从下方穿越长期均线(SMA_20)时 → 金叉（看涨信号）
# 当短期均线(SMA_5)从上方穿越长期均线(SMA_20)时 → 死叉（看跌信号）

# 用 shift 判断"昨天的状态" vs "今天的状态"
df['signal'] = 0
df.loc[(df['SMA_5'] > df['SMA_20']) & (df['SMA_5'].shift(1) <= df['SMA_20'].shift(1)), 'signal'] = 1   # 金叉
df.loc[(df['SMA_5'] < df['SMA_20']) & (df['SMA_5'].shift(1) >= df['SMA_20'].shift(1)), 'signal'] = -1  # 死叉

golden_cross = df[df['signal'] == 1]
death_cross = df[df['signal'] == -1]

print(f"\n--- 3. SMA 交叉信号统计 ---")
print(f"📈 金叉次数: {len(golden_cross)}，最近一次: {golden_cross.index[-1].date() if len(golden_cross) > 0 else 'N/A'}")
print(f"📉 死叉次数: {len(death_cross)}，最近一次: {death_cross.index[-1].date() if len(death_cross) > 0 else 'N/A'}")

# 展示最近5次金叉的发生日期和当时的价格
print("\n🔍 最近 5 次金叉:")
print(golden_cross[['close_price', 'SMA_5', 'SMA_20']].tail(5))
