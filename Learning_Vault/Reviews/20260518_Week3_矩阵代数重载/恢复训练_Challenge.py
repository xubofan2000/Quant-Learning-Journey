# %% [0. 环境准备：模拟生成量化环境数据]
import numpy as np
from scipy import linalg

# 设定基础维度
T = 252       # 252个交易日
N = 50        # 50只股票
M = 1000      # 1000种随机策略

np.random.seed(42)
# 模拟收益率矩阵 (T, N)，假设年化收益率在 -20% 到 30% 之间，波动率合理
R = np.random.normal(loc=0.05/252, scale=0.2/np.sqrt(252), size=(T, N))

# 模拟策略权重矩阵 (M, N)，使用 Dirichlet 分布保证每行和为 1 且非负
W = np.random.dirichlet(np.ones(N), size=M)

print(f"📦 模拟数据加载完成: R.shape={R.shape}, W.shape={W.shape}")


# %% [Challenge 1: 手撸协方差矩阵]
# 任务：不能使用 np.cov，纯手工用矩阵乘法计算协方差矩阵 Sigma
# 提示：先算均值 -> 减去均值 (Broadcasting) -> 矩阵乘法求内积 -> 除以自由度(T-1)

# TODO: 在下方填入你的代码
mu = ...
R_centered = ...
Sigma = ...


# 【测试用例】跑通不报错就算过关！
Sigma_numpy = np.cov(R.T, ddof=1)
assert Sigma.shape == (N, N), f"维度不对，期望 ({N}, {N})，实际是 {Sigma.shape}"
assert np.allclose(Sigma, Sigma_numpy), "协方差计算结果不正确"
print("✅ Challenge 1 通关：手撸协方差矩阵毫无破绽！")


# %% [Challenge 2: 组合方差的二次型]
# 任务：已知单策略权重向量 w_single，利用刚才算出的 Sigma 计算其组合方差 var_p
w_single = W[0]  # shape: (N,)

# TODO: 在下方填入你的代码 (一行搞定)
var_p = ...


# 【测试用例】
assert isinstance(var_p, float), "方差应该是一个标量 float"
assert np.isclose(var_p, w_single.dot(Sigma_numpy).dot(w_single)), "方差计算不正确"
print(f"✅ Challenge 2 通关：组合方差算得对！(年化波动率约为 {np.sqrt(var_p * 252)*100:.2f}%)")


# %% [Challenge 3: 特征值分解与 PCA]
# 任务：使用 scipy.linalg.eigh 对 Sigma 进行特征值分解。
# 提取出最大的特征值（注意 eigh 返回的顺序），并计算"第一主成分（PC1）的方差解释率"

# TODO: 在下方填入你的代码
# 1. 特征值分解
eigenvalues, eigenvectors = ...

# 2. 获取最大特征值（提示：eigh 返回的是升序）
max_eigenvalue = ...

# 3. 计算 PC1 方差解释率 = 最大特征值 / 所有特征值之和
pc1_ratio = ...


# 【测试用例】
assert len(eigenvalues) == N, "特征值数量不对"
assert max_eigenvalue == np.max(eigenvalues), "没有取到最大的特征值"
assert 0 < pc1_ratio < 1, "解释率应该在 0 到 1 之间"
print(f"✅ Challenge 3 通关：PC1 方差解释率为 {pc1_ratio*100:.2f}% (因为是模拟的纯随机数据，所以比例极低，真实股票市场通常在 30%-50% 之间)")


# %% [Challenge 4: Broadcasting 无循环回测]
# 任务：不要用 for 循环！利用 Broadcasting 一次性算出 1000 个策略在 252 天的全量资金净值曲线。
# 提示：先算收益率矩阵 (T, M) -> 加上 1 -> 沿时间轴做累乘 (cumprod)

# TODO: 在下方填入你的代码
# 1. 计算所有策略的每日组合收益 (T, M)
returns_matrix = ...

# 2. 计算净值曲线 (T, M)
nav_curves = ...


# 【测试用例】
assert returns_matrix.shape == (T, M), f"收益矩阵维度错误: {returns_matrix.shape}"
assert nav_curves.shape == (T, M), f"净值曲线维度错误: {nav_curves.shape}"
assert np.allclose(nav_curves[0], 1 + returns_matrix[0]), "第一天的净值逻辑不对"
print("✅ Challenge 4 通关：恭喜找回 Broadcasting 的快感！")
print("\n🎉 全部恢复训练完成！您可以放心进入 Week 4 了！")

# %%
