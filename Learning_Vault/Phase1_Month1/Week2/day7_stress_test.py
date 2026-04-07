"""
day7_stress_test.py - Week 2 大满贯：50 只股票的 Pipeline 压力测试

目标：
1. 生成 50 只模拟股票的 5 年日线数据
2. 逐只通过 DataHandler 管道（清洗 + 特征工程）
3. 合并为面板数据（长表形式），输出 Parquet
4. 监控内存占用和处理速度
"""

import pandas as pd
import numpy as np
import os
import sys
import time
from tqdm import tqdm

# ==========================================
# 📦 1. 生成 50 只模拟股票的历史数据
# ==========================================
# 用几何布朗运动 (GBM) 模拟真实的股价走势
# 这是金融量化中最常用的股价模拟模型

def generate_stock_data(
    symbol: str,
    start_date: str = "2019-01-02",
    trading_days: int = 1755,
    initial_price: float = None,
    annual_return: float = None,
    annual_volatility: float = None,
    seed: int = None
) -> pd.DataFrame:
    """用几何布朗运动生成单只股票的模拟日线数据。"""
    if seed is not None:
        np.random.seed(seed)
    
    # 随机化参数让每只股票走势不同
    if initial_price is None:
        initial_price = np.random.uniform(5, 200)
    if annual_return is None:
        annual_return = np.random.uniform(-0.1, 0.3)   # 年化收益 -10%~30%
    if annual_volatility is None:
        annual_volatility = np.random.uniform(0.15, 0.5)  # 年化波动 15%~50%

    # GBM 参数转换为日度
    dt = 1 / 252
    daily_return = (annual_return - 0.5 * annual_volatility**2) * dt
    daily_vol = annual_volatility * np.sqrt(dt)

    # 生成日收益率序列
    returns = np.random.normal(daily_return, daily_vol, trading_days)
    prices = initial_price * np.exp(np.cumsum(returns))

    # 构造 DataFrame
    dates = pd.bdate_range(start=start_date, periods=trading_days)
    volume = np.random.randint(1_000_000, 50_000_000, size=trading_days)

    df = pd.DataFrame({
        'trade_date': dates,
        'symbol': symbol,
        'close_price': np.round(prices, 3),
        'volume': volume
    })

    # 随机挖空 0~3% 的数据模拟停牌
    n_holes = np.random.randint(0, int(trading_days * 0.03))
    if n_holes > 0:
        hole_idx = np.random.choice(trading_days, size=n_holes, replace=False)
        df.loc[hole_idx, 'close_price'] = np.nan

    return df


print("📦 生成 50 只模拟股票数据...")
np.random.seed(2026)

stock_symbols = [f"SIM{str(i).zfill(4)}" for i in range(1, 51)]
all_raw_data = []

for symbol in tqdm(stock_symbols, desc="生成数据", unit="只"):
    df = generate_stock_data(symbol, seed=hash(symbol) % 2**31)
    all_raw_data.append(df)

# 合并为一张大表
df_universe = pd.concat(all_raw_data, ignore_index=True)
print(f"  📊 原始面板: {df_universe.shape[0]:,} 行 × {df_universe.shape[1]} 列")
print(f"  🏷️ 股票数量: {df_universe['symbol'].nunique()}")
print(f"  💾 内存占用: {df_universe.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")


# ==========================================
# ⚙️ 2. 批量管道处理（逐股票清洗 + 特征工程）
# ==========================================
def process_single_stock(df_stock: pd.DataFrame) -> pd.DataFrame:
    """对单只股票进行清洗和特征工程。"""
    df = df_stock.copy()
    symbol = df['symbol'].iloc[0]
    
    # 设置时间索引
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.set_index('trade_date').sort_index()
    
    # Stage 1: 清洗 —— 前向填充停牌缺失值
    df['close_price'] = df['close_price'].ffill()
    
    # Stage 2: 特征工程
    df['SMA_5'] = df['close_price'].rolling(5).mean()
    df['SMA_20'] = df['close_price'].rolling(20).mean()
    df['daily_return'] = df['close_price'].pct_change()
    df['log_return'] = np.log(df['close_price'] / df['close_price'].shift(1))
    
    # 去掉预热期
    df = df.iloc[20:]
    
    return df


print("\n⚙️ 批量管道处理中...")
t0 = time.perf_counter()

processed_frames = []
mem_snapshots = []

for symbol in tqdm(stock_symbols, desc="管道处理", unit="只", ncols=80):
    df_stock = df_universe[df_universe['symbol'] == symbol]
    df_processed = process_single_stock(df_stock)
    processed_frames.append(df_processed)
    
    # 每处理 10 只记录一次内存
    if len(processed_frames) % 10 == 0:
        current_mem = sum(f.memory_usage(deep=True).sum() for f in processed_frames)
        mem_snapshots.append((len(processed_frames), current_mem / 1024 / 1024))

elapsed = time.perf_counter() - t0


# ==========================================
# 📊 3. 合并为面板数据
# ==========================================
print("\n📊 合并面板数据 (Panel Data)...")

# 长表形式（Long Format）：symbol 作为普通列，trade_date 作为索引
df_panel = pd.concat(processed_frames)

# 也可以转为 MultiIndex 形式
df_multi = df_panel.set_index('symbol', append=True).swaplevel()

print(f"  长表形式:     {df_panel.shape[0]:,} 行 × {df_panel.shape[1]} 列")
print(f"  MultiIndex:   {df_multi.shape[0]:,} 行, 索引层级 = {df_multi.index.names}")
print(f"  处理耗时:     {elapsed:.2f}s")
print(f"  平均每只:     {elapsed/50*1000:.0f}ms")

final_mem = df_panel.memory_usage(deep=True).sum() / 1024 / 1024
print(f"  最终内存:     {final_mem:.1f} MB")

# ==========================================
# 📈 4. 内存增长曲线
# ==========================================
print("\n📈 内存增长轨迹:")
for count, mem in mem_snapshots:
    bar = "█" * int(mem / max(m for _, m in mem_snapshots) * 30)
    print(f"  {count:>3} 只 | {mem:>6.1f} MB | {bar}")

# ==========================================
# 💾 5. 保存面板数据为 Parquet
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
output_path = os.path.join(project_root, 'Database', 'files', 'panel_50stocks.parquet')

df_panel.to_parquet(output_path, engine='pyarrow', compression='snappy')
parquet_size = os.path.getsize(output_path) / 1024 / 1024

print(f"\n💾 面板数据已保存:")
print(f"  路径:       {output_path}")
print(f"  内存占用:   {final_mem:.1f} MB")
print(f"  Parquet:    {parquet_size:.1f} MB")
print(f"  压缩率:     {final_mem / parquet_size:.1f}x")

# ==========================================
# 🔬 6. 面板数据验证：按股票聚合统计
# ==========================================
print("\n🔬 面板数据验证 (按股票聚合):")
summary = df_panel.groupby('symbol').agg(
    days=('close_price', 'count'),
    avg_price=('close_price', 'mean'),
    annual_return=('log_return', lambda x: (np.exp(x.sum()) - 1) * 100),
    volatility=('daily_return', lambda x: x.std() * np.sqrt(252) * 100),
    max_drawdown=('close_price', lambda x: ((x / x.cummax()) - 1).min() * 100)
).round(2)

# 展示表现最好和最差的各 5 只
print("\n📈 年化收益 TOP 5:")
print(summary.nlargest(5, 'annual_return')[['annual_return', 'volatility', 'max_drawdown']])

print("\n📉 年化收益 BOTTOM 5:")
print(summary.nsmallest(5, 'annual_return')[['annual_return', 'volatility', 'max_drawdown']])

print(f"\n✅ Week 2 压力测试完成！50 只股票全部通过管道，面板数据已落盘。")
