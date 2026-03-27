# Phase 1 Week 1: 核心知识点总结与闪卡题库 (Spaced Repetition)

这份总结提取了 Week 1 从 SQL 到 Python (Pandas/DuckDB/Polars) 迁移的最核心、最容易遗忘的知识点。专门为 NotebookLM 生成 Flashcards 优化。

## 1. 相对路径与环境定位
- **痛点**: 在不同终端运行 Python 脚本时，简单的相对路径 `./data.csv` 容易随工作目录变化而报错。
- **最佳实践**: 使用 `__file__` 动态寻址。`os.path.join(os.path.dirname(__file__), 'data.csv')`。

## 2. DuckDB 与 Pandas 的工程边界
- **DuckDB 的定位**: 负责底层存储、I/O 降维、列修剪（Column Pruning）。它最大的优势是极其快速的零拷贝（Zero-copy）直接查询外部文件（如 CSV/Parquet）。
- **Pandas 的定位**: 负责内存中的复杂矩阵运算和数据整理。Pandas 的 `read_csv` 具有极高的反序列化和内存膨胀成本。
- **黄金组合**: `DuckDB(I/O & 聚合过滤) -> .df() -> Pandas(复杂处理)`。

## 3. SQL 到 Pandas 的思维/代码映射
- **SELECT**: SQL: `SELECT col_a, col_b` -> Pandas: `df[['col_a', 'col_b']]`
- **WHERE**: SQL: `WHERE price > 100` -> Pandas: `df.loc[df['price'] > 100]`
- **GROUP BY**: SQL: `GROUP BY ticker` -> Pandas: `df.groupby('ticker').agg(...)`
- **ORDER BY**: SQL: `ORDER BY date DESC` -> Pandas: `df.sort_values('date', ascending=False)`

## 4. Polars 的懒加载与查询优化
- **Lazy Evaluation (懒加载)**: 使用 `pl.scan_csv()` 而不是 `pl.read_csv()`。只有在最后调用 `.collect()` 时才会物理执行计算。
- **谓词下推 (Predicate Pushdown)**: Polars 引擎会自动将后置的 `.filter()` 条件提前到数据读取层，极大地节约了内存。

## 5. 本地数据流转架构：覆盖更新 (Upsert)
- **痛点**: MySQL 的行级 UPSERT 处理海量时序数据极慢且容易锁表。
- **降维解法**: 使用数据仓库经典的 **查询水位线 (High-Water Mark) + DELETE & INSERT 幂等覆盖** 架构保障本地日线数据更新。即先查已存在的最新日期，然后删除冲突时间段数据，最后批量 INSERT 新拉取的数据。

## 6. Pandas 降采样对账 (Resampling)
- 当需要校验按月聚合的 DuckDB 结果时，Pandas 的杀手锏是时序重采样：`df.resample('M').mean()`（注意最新版本推荐使用 `ME` 作为 Month End 别名）。这比先提取 date 里的月份再 GroupBy 要优雅高效得多。
