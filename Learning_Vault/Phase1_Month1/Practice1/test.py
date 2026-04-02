# %%
import pandas as pd
import duckdb
import akshare as ak
import os

# %%
df_szzs = ak.stock_zh_index_daily(symbol="sh000001")
print(df_szzs.head(10))
# %%
print(df_szzs.tail(10))
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir,'..','..','..','Database','files','market_data.duckdb')

conn = duckdb.connect(db_path)
conn.execute('''
    CREATE TABLE IF NOT EXISTS szzs (
        date DATE,
        open FLOAT,
        high FLOAT,
        low FLOAT,
        close FLOAT,
        volume BIGINT
    )
''')

# %%
conn.sql('''
    INSERT INTO szzs
    SELECT date, open, high, low, close, volume
    FROM df_szzs
''')

# %%
conn.sql('''
    DESC szzs
''').df()

# %%
