import akshare as ak
import pandas as pd
import duckdb
import os
from datetime import datetime

# ==========================================
# 1. 动态寻址与基建连接
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
db_path = os.path.join(project_root, 'Database', 'files', 'market_data.duckdb')

# 确保 Database 目录存在
os.makedirs(os.path.dirname(db_path), exist_ok=True)

print("🔌 连接 DuckDB 列式引擎...")
conn = duckdb.connect(db_path)

# 创建事实表 (Fact Table)。注意我们没有定义 PRIMARY KEY，因为 OLAP 极少使用物理主键锁
conn.execute("""
    CREATE TABLE IF NOT EXISTS etf_daily_kline (
        symbol VARCHAR,
        trade_date DATE,
        open_price DOUBLE,
        close_price DOUBLE,
        high_price DOUBLE,
        low_price DOUBLE,
        volume BIGINT,
        turnover DOUBLE
    )
""")

# ==========================================
# 2. 探查水位线 (Watermark) - 决定全量还是增量
# ==========================================
# 经典 OLAP 提数法：向数据库询问“你目前记录到的最新日期是哪天？”
latest_date_df = conn.execute("SELECT MAX(trade_date) FROM etf_daily_kline WHERE symbol = 'sh510300'").df()
latest_date = latest_date_df.iloc[0, 0]

if pd.isna(latest_date):
    start_date = "20190101" # 数据库是空的，全量抓取 5 年
    print("📊 数据库为空，准备执行全量初始化抓取 (从 2019-01-01 开始)...")
else:
    # 数据库有数据，把最新日期作为起始点重新抓（处理重叠）
    start_date = latest_date.strftime("%Y%m%d")
    print(f"📊 发现历史数据，水位线为 {start_date}，准备执行增量补齐...")

end_date = datetime.now().strftime("%Y%m%d")

# ==========================================
# 3. 联网 Extract (抽取) 与 Transform (清洗)
# ==========================================
print(f"🚀 调用 AKShare 抓取沪深300ETF (sh510300) 日线行情...")
# 注意：ETF 接口与个股不同，这里使用 fund_etf_hist_em
df = ak.fund_etf_hist_em(symbol="510300", period="daily", start_date=start_date, end_date=end_date, adjust="qfq")

if df.empty:
    print("✅ 数据已经是最新，无需更新。收工！")
else:
    # 复用你优秀的重命名规范
    rename_mapping = {
        '日期': 'trade_date', '开盘': 'open_price', '收盘': 'close_price',
        '最高': 'high_price', '最低': 'low_price', '成交量': 'volume', '成交额': 'turnover'
    }
    df.rename(columns=rename_mapping, inplace=True)
    df['symbol'] = 'sh510300'
    df['trade_date'] = pd.to_datetime(df['trade_date']).dt.date
    
    clean_df = df[['symbol', 'trade_date', 'open_price', 'close_price', 'high_price', 'low_price', 'volume', 'turnover']]

    # ==========================================
    # 4. Load (加载)：OLAP 经典的幂等写入
    # ==========================================
    min_new_date = clean_df['trade_date'].min()
    
    print(f"💾 准备将 {len(clean_df)} 条数据刷入硬盘...")
    # 开启事务保证原子性
    conn.execute("BEGIN TRANSACTION")
    try:
        # 【核心魔法】：既然底层是不可变数据块，我们就先大刀阔斧地把重叠的日期数据删掉，然后再全量 Append。
        # 这种 "DELETE + INSERT" 的组合，在列式数据库里比逐行判断的主键冲突 (UPSERT) 要快得多！
        conn.execute(f"DELETE FROM etf_daily_kline WHERE symbol = 'sh510300' AND trade_date >= '{min_new_date}'")
        
        # 零拷贝直接从 Pandas DataFrame 抽数据落盘
        conn.execute("INSERT INTO etf_daily_kline SELECT * FROM clean_df")
        
        conn.execute("COMMIT")
        print("✅ 增量写入成功！")
    except Exception as e:
        conn.execute("ROLLBACK")
        print(f"❌ 写入失败，已回滚保护数据: {e}")

# ==========================================
# 5. 验证查询
# ==========================================
print("\n🔍 数据库最新 5 条记录巡检:")
print(conn.execute("SELECT * FROM etf_daily_kline ORDER BY trade_date DESC LIMIT 5").df())

conn.close()