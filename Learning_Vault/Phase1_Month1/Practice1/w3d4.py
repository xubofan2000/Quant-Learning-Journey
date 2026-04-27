# %%
# 导入所需库
from math import isclose
import pandas as pd
import numpy as np
import os
import time

# %%
#step 1 加载数据
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir,'..','..','..'))
parquet_path = os.path.abspath(os.path.join(project_root,'Database','files','panel_50stocks.parquet'))

# df_panel是50只随机生成的股票的长表数据
df_panel = pd.read_parquet(parquet_path)
# selected是5只股票的列表，N是股票数量
selected = ['SIM0001','SIM0010','SIM0020','SIM0035','SIM0050']
N = len(selected)

# %%
# 长表转成宽表，结构为：行是日期，列是股票代码，值是日收益率
df_returns = df_panel[df_panel['symbol'].isin(selected)].pivot_table(
    index = 'trade_date',
    columns = 'symbol',
    values = 'daily_return'
).dropna()
print(df_returns.sample(10))

# %%
R = df_returns.to_numpy()
T,N = R.shape
print(T,N)

# %%
# step 2 构建协方差矩阵Sigma
mu = R.mean(axis=0)
R_centered = R - mu
Sigma = R_centered.T @ R_centered / (T - 1)
print(Sigma)

# %%
np.var(R, axis=0, ddof=1)

# %%
# 验证协方差矩阵Sigma(N,N) 手搓 等效于 np.cov
assert np.allclose(Sigma, np.cov(R, rowvar=False))
# %%
# 验证协方差举证Sigma的对角线元素 等效于 np.var
assert np.allclose(np.diag(Sigma), np.var(R, axis=0, ddof=1))

# %%
# step 3 组合方差 w^T Sigma w
# 3.1. 等权重示例
w_equal = np.ones(N) / N
step1 = Sigma @ w_equal
var_p = w_equal.T @ step1
print(f'等权重组合方差为：{var_p:.6f}')
sigma_p = np.sqrt(var_p)
print(f'等权重组合波动率为：{sigma_p:.6f}')

# %% 验证与历史序列的std是否一致
portfolio_ret_series = R @ w_equal
sigma_p_historical = portfolio_ret_series.std(ddof = 1)

# %%
assert np.isclose(sigma_p, sigma_p_historical, rtol = 1e-6), "等权重组合波动率验证失败"
print("等权重组合波动率验证通过")

# %%
# step 4 模拟不同权重的组合
np.random.seed(43)
M = 50000
W_all = np.random.dirichlet(np.ones(N), size=M) # 狄利克雷分布
WS = (W_all @ Sigma)
var_matrix = (WS * W_all).sum(axis=1)

# %%
