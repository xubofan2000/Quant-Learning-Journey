# 工程基线

## 环境

使用项目虚拟环境并固定核心依赖：

```powershell
.\.venv\Scripts\python.exe -m pip install -r project/requirements/requirements-core.txt
python -m unittest discover -s project/tests -v
```

`project/requirements/requirements-core.txt` 固定当前基础课程已经验证的直接依赖。进入 Week 4 或后续研究阶段前，先安装所需扩展并把实际验证过的版本补入对应阶段的依赖清单；不要在没有记录的环境中复现研究结论。

## 质量门槛

| 层级 | 要求 |
| --- | --- |
| 学习脚本 | 至少包含输入形状/结果的 `assert` 或明确 smoke test |
| 可复用模块 | 用 `unittest` 覆盖正常、边界和非法输入 |
| 数据处理 | 校验唯一键、日期范围、缺失率、重复行和输出行数 |
| 研究结果 | 记录配置、随机种子、数据版本和完整运行命令 |
| 提交前 | 运行项目审计与相关测试；不提交大数据、密钥或派生报告 |

## 数据与实验目录约定

- `Database/raw/`：不可修改的原始提取；保存来源、参数和提取日期。
- `Database/processed/`：可由原始数据重新构建的中间数据。
- `Learning_Vault/`：教学脚本、检验和总结。
- `experiments/`：具备研究卡、配置和结果的正式研究实验；进入 Phase 2 时创建。
- `reports/`：本地派生报告，不作为事实源，不提交 Git。

## 自动检查

GitHub Actions 会运行以下无外部依赖检查：

```powershell
python project/scripts/project_audit.py
python -m unittest discover -s project/tests -v
```

新增第三方依赖后，再把依赖安装与相关测试加入 CI，避免 CI 声称覆盖了本地才有的数据或凭据。

## Phase 过渡检查

每个 Phase 开始前检查官方文档、依赖维护状态和适用规则，记录日期、来源与决定。涉及交易接口或监管时，必须以当时的官方资料为准，并保持模拟模式直到人工审批。
