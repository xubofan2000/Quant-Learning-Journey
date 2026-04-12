# %%
from copy import replace
import numpy as np
import pandas as pd
import os

# %%
df = pd.read_parquet(r'D:\project\Bohr\Database\files\panel_50stocks.parquet')
print(df.sample(10))

# %%
df.index.name
df.describe()
df.info()

# %%
df.index.dtype
print(df.index.name)
df.index.values

# %%
df_pivot = df.pivot_table(index=df.index.name if df.index.name else 'trade_date', 
                columns='symbol', 
                values='daily_return')
print(df_pivot.head())
# %%
df_pivot.index.name
# %%
df_pivot.sort_index(inplace=True)

# %%
df_pivot_50 = df_pivot.head(50)
R = df_pivot_50.to_numpy()
print(R.shape)
print(R)
# %%
weight = np.ones(50)/50
print(weight)

# %%
weight*R
# %%
R*weight
# %%
assert np.allclose(weight*R, R*weight), '不相等'
# %%
print(weight.shape)
weight.reshape(1,-1).shape
print(weight.reshape(1,-1))

# %%
df_w = pd.DataFrame(weight.reshape(1,-1),columns=df_pivot_50.columns)
print(df_w)
# %%
df_w2 = pd.Series(weight,index=df_pivot_50.columns)
print(df_w2)
# %%
df_pivot_50
# %%
df_pivot_50 @ weight
# %%
type(df_pivot_50 @ df_w2)
# %%
df_w2 @ df_pivot_50
# %%
type(df_w.iloc[0])
# %%
df_pivot_50.iloc[0:2]
# %%
df_pivot_50.loc[:,'SIM0001']
# %%
df_pivot_50 @ df_w2
#
# %%
df_pivot_50.values
# %%
type(df_pivot_50.index)
# %%
