"""
day5_markowitz_optimizer.py - Week 3 Day 5: 真正的马科维茨优化 (SciPy SLSQP)

核心认知跃迁：
    Day 4 中，我们通过“暴力撒点”（Monte Carlo）勾勒了有效前沿的轮廓。
    但真正的工程实践中，依靠随机性寻找“最优点”效率极低，且无法保证找到真正的边界。
    
    今天，我们引入运筹学和凸优化的武器：`scipy.optimize`。
    我们将马科维茨模型转化为一个标准的带有约束条件的最优化问题：
    
    【目标】：最小化组合方差  min: w^T @ Σ @ w
    【约束 1】：权重之和等于 1 (Σw = 1) -> 满仓约束
    【约束 2】：权重非负 (w >= 0) -> 做多约束（不允许做空）
    【约束 3 (可选)】：达到目标期望收益率 (w^T @ μ >= r_target)

目标：
1. 编写目标函数（组合波动率和负夏普比率先）。
2. 使用 `scipy.optimize.minimize` 求解全局最小方差组合 (GMVP) 和 最大夏普组合。
3. 动态调整目标收益率 $r_{target}$，求解对应的最小方差，从而精确描绘出那条平滑的“有效前沿 (Efficient Frontier)”。
"""

import numpy as np
import pandas as pd
import scipy.optimize as sco
import os

# ==========================================
# 📦 1. 数据准备工作 (和 Day 4 相同)
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
parquet_path = os.path.join(project_root, 'Database', 'files', 'panel_50stocks.parquet')

print("📦 加载面板数据...")
df_panel = pd.read_parquet(parquet_path)

# 继续选用这 5 只代表性股票
selected = ['SIM0001', 'SIM0010', 'SIM0020', 'SIM0035', 'SIM0050']
N = len(selected)

df_returns = df_panel[df_panel['symbol'].isin(selected)].pivot_table(
    index='trade_date',
    columns='symbol',
    values='daily_return'
).dropna()

R = df_returns.values
T, N = R.shape

# 核心金融参数
mu = R.mean(axis=0)                      
mu_ann = mu * 252                        # 年化期望收益
R_centered = R - mu                      
Sigma = (R_centered.T @ R_centered) / (T - 1) 
Sigma_ann = Sigma * 252                  # 年化协方差矩阵

print(f"\n🎯 选取标的 ({N} 只): {selected}")
print(f"   各类资产年化收益率: {(mu_ann*100).round(2)}%")


# ==========================================
# 🧮 2. 定义优化器的目标函数与基础构件
# ==========================================
print("\n" + "=" * 60)
print("🧮 定义目标函数 (Objective Functions)")
print("=" * 60)

def port_variance(w):
    """目标函数 1：计算组合（年化）方差。我们将尝试 minimze 这个值"""
    return w.T @ Sigma_ann @ w

def port_volatility(w):
    """计算组合（年化）波动率（标准差）"""
    return np.sqrt(port_variance(w))

def port_return(w):
    """计算组合（年化）期望收益"""
    return w.T @ mu_ann

def min_func_sharpe(w):
    """目标函数 2：计算组合负夏普比率（因为 scipy 只有 minimize，没有 maximize，所以加个负号）"""
    # 假设无风险利率 rf = 0
    return - (port_return(w) / port_volatility(w))

# 通用约束：所有权重之和必须为 1
# 在 scipy 中，等式约束定义为 "返回 0 的函数"，即 sum(w) - 1 = 0
eq_cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})

# 通用边界：每个股票的权重在 0 到 1 之间（不允许做空，也不允许借钱杠杆）
bounds = tuple((0, 1) for _ in range(N))

# 初始猜测：等权作为优化的起点
init_guess = np.ones(N) / N

print("  ✅ 成功定义: 最小化方差函数、最小化负夏普函数、等式约束 (sum(w)=1)、边界参数 (0 <= w <= 1)。")


# ==========================================
# 🚀 3. 求解：全局最小方差组合 (GMVP)
# ==========================================
print("\n" + "=" * 60)
print("🚀 求解: 全局最小方差组合 (Global Minimum Variance Portfolio)")
print("=" * 60)

# 使用 SLSQP (Sequential Least Squares Programming) 这是带约束非线性优化的首选
opt_gmvp = sco.minimize(
    port_variance,       # 优化的目标函数
    init_guess,          # 初始权重
    method='SLSQP',      # 优化算法
    bounds=bounds,       # 变量边界
    constraints=eq_cons  # 约束条件
)

assert opt_gmvp['success'], "GMVP 优化失败！"
w_gmvp = opt_gmvp['x']

print("\n  🛡️ GMVP 最优结果:")
for sym, weight in zip(selected, w_gmvp):
    print(f"     {sym}: {weight*100:>6.2f}%")
print(f"  -> 预期年化收益 : {port_return(w_gmvp)*100:.2f}%")
print(f"  -> 最低年化波动 : {port_volatility(w_gmvp)*100:.2f}%")


# ==========================================
# 🎯 4. 求解：最大夏普比率组合 (Tangency Portfolio)
# ==========================================
print("\n" + "=" * 60)
print("🎯 求解: 最大夏普比例组合 (Maximum Sharpe Portfolio)")
print("=" * 60)

opt_sharpe = sco.minimize(
    min_func_sharpe,     # 最小化“负”夏普 -> 就是最大化夏普
    init_guess,
    method='SLSQP',
    bounds=bounds,
    constraints=eq_cons
)

assert opt_sharpe['success'], "最大夏普优化失败！"
w_sharpe = opt_sharpe['x']

print("\n  🗡️ 最大夏普最优结果:")
for sym, weight in zip(selected, w_sharpe):
    print(f"     {sym}: {weight*100:>6.2f}%")
print(f"  -> 预期年化收益 : {port_return(w_sharpe)*100:.2f}%")
print(f"  -> 最低年化波动 : {port_volatility(w_sharpe)*100:.2f}%")
print(f"  -> 极致夏普比率 : {-opt_sharpe['fun']:.3f} (对比Day4蒙特卡洛最优:约0.857)")


# ==========================================
# 📈 5. 精确描绘有效前沿 (Efficient Frontier)
# ==========================================
print("\n" + "=" * 60)
print("📈 计算解析版有效前沿边界 (Efficient Frontier)")
print("=" * 60)

# 我们在 GMVP 收益率到最大单目标预期收益率之间，均匀撒 30 个目标收益率
target_returns = np.linspace(port_return(w_gmvp), mu_ann.max(), 30)
target_vols = []

for r_target in target_returns:
    # 新增约束：当前组合收益率必须恰好等于 r_target
    constraints = (
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},         # 权重和为1
        {'type': 'eq', 'fun': lambda x: port_return(x) - r_target} # 收益率为目标值
    )
    
    res = sco.minimize(
        port_volatility, 
        init_guess, 
        method='SLSQP', 
        bounds=bounds, 
        constraints=constraints
    )
    
    if res['success']:
        target_vols.append(res['fun'])
    else:
        # 当 target return 过高（特别是强制做多的边界外），优化器会失败
        target_vols.append(np.nan)

target_vols = np.array(target_vols)

print(f"  计算完成。在收益率 [{target_returns.min()*100:.1f}%, {target_returns.max()*100:.1f}%] 区间提取了 {len(target_vols)} 个边界点。")
print("  这也就是有效前沿在图表中那条完美的“左侧边界弧线”。")

# 取出部分数据展示
print("\n  部分有效前沿数值:")
print("    目标收益(%)   对应的最小波动率(%)")
for i in range(0, 30, 5):
    if not np.isnan(target_vols[i]):
        print(f"       {target_returns[i]*100:>6.2f}%  ->  {target_vols[i]*100:>6.2f}%")


# ==========================================
# 🧠 6. 回溯反思点
# ==========================================
print("\n" + "=" * 60)
print("📌 Day 5 总结")
print("=" * 60)
print("""
  ✅ 掌握：使用 `scipy.optimize.minimize` 取代暴力穷举寻找最优解
  ✅ 掌握：将复杂的投资问题，利用数学抽象成“目标函数”、“等式约束”和“边界”
  ✅ 发现：与 Day 4 蒙特卡洛相比，求解器不但极快（毫秒级出结果），而且找到了比随机点（夏普=0.857）更完美的数值解（真正的夏普极值），揭示了数学求导下降的绝对统治力。
  ✅ 实测：我们用优化器强行将收益锁定成一系列特定值并求其最小波动，成功倒逼出了那条传奇的“有效前沿抛物线”。

  Week 3 的使命已经结束：
  你手眼并用地打通了从单只股票日收益 -> 面板数据组装 -> w @ * 矩阵加速 -> Σ 协方差提取 -> 马科维茨解析求解 的所有工程底层。理论已经完美转化为实弹代码。
  
  很快，你就可以用真实的中国 A 股/ETF 市场数据喂给你的机器，它能立刻告诉你，“你要扛 15% 波动率的话，买哪几只，配什么比例是绝对最优的。”

  🔜 明天开启 Week 4：引入概率统计，直面金融市场最诡异的尖峰厚尾与偏度挑战。
""")
