# Phase 1 - Week 2 - Day 6: 面向对象重构与数据管道总结

## 1. 为什么要从面条代码升级到 OOP？

前 5 天你写的都是"从上到下一路执行"的脚本——每个 `.py` 文件里变量散落各处，想复用某一段逻辑（比如 ffill 填充）就得整段复制粘贴。这种代码叫做**面条代码 (Spaghetti Code)**，特征是：

- 改一处就崩一片（变量名冲突）
- 无法被其他脚本 `import` 复用
- 测试困难（没有明确的输入输出边界）

OOP 的核心目标不是"用了 class 就高级"，而是**把状态（数据）和行为（方法）打包在一起**，形成一个有明确边界的"黑盒"。外部调用者只需要知道接口（`load_raw`、`clean`、`save_feature`），不需要知道内部实现细节。

## 2. DataHandler 设计中的关键模式

### 链式调用 (Method Chaining)

```python
handler.load_raw().clean().add_features()
```

每个方法最后 `return self`，让调用者可以一口气串联多个操作。这不是花哨的语法糖——它强制你把每个方法设计成**无副作用的阶段转换**：输入是当前状态，输出是新状态。这种思维在后面用 Polars 的 LazyFrame 时会大量用到。

### 守卫方法 (Guard Clause)

```python
def _check_loaded(self):
    if self.df is None:
        raise RuntimeError("请先调用 load_raw() 加载数据！")
```

在每个方法入口处检查前置条件是否满足。这避免了"忘记先加载数据就开始清洗"时产生的诡异 `NoneType` 错误——直接告诉你哪一步漏了，而不是让你对着 traceback 猜半天。

### `__name__ == "__main__"` 双重身份

```python
if __name__ == "__main__":
    handler = DataHandler(db_path)
    handler.run(output_path)
```

这行代码让 `data_pipeline.py` 同时扮演两个角色：

- **作为脚本直接运行**：`python data_pipeline.py` 会执行测试逻辑
- **作为模块被 import**：`from day6_data_pipeline import DataHandler` 只导入类，不执行测试

这意味着明天 Day 7 的压力测试脚本可以直接 `import DataHandler`，不需要复制粘贴任何代码。

### Type Hints + Docstrings

```python
def load_raw(self, etf_symbol: str = "sh510300", index_table: Optional[str] = "szzs") -> "DataHandler":
```

类型标注让编辑器（Pylance）在你打 `.` 的时候就能推断出返回值类型和参数类型，悬停 Alt 看到完整的参数文档。这不是强类型检查（Python 运行时不会报错），而是给**人和工具**看的"合同"。

## 3. 四阶段管道架构

```
load_raw()  →  clean()  →  add_features()  →  save_feature()
  DuckDB读取     ffill填充    SMA/EMA/收益率     Parquet落盘
  LEFT JOIN      NaN统计      超额收益            Snappy压缩
```

每个阶段只做一件事，阶段之间通过 `self.df` 这个共享状态传递数据。这种设计叫做 **Pipeline 模式**——工业级的数据工程框架（如 Apache Airflow、Prefect）本质上就是把这种阶段化的思想做到了极致。

## 4. Week 2 全周回顾

| Day   | 技能点                | 在 DataHandler 中的对应                               |
| ----- | --------------------- | ----------------------------------------------------- |
| Day 1 | DatetimeIndex + ffill | `clean(fill_method="ffill")`                        |
| Day 2 | rolling + shift       | `add_features(sma_windows=[5,20])`                  |
| Day 3 | 对数收益率            | `add_features(add_returns=True)`                    |
| Day 4 | LEFT JOIN + Alpha     | `load_raw(index_table="szzs")` + `annual_alpha()` |
| Day 5 | Parquet 存储          | `save_feature(compression="snappy")`                |
| Day 6 | OOP 封装              | `DataHandler` 类本身                                |

**前 5 天的每一天都变成了 DataHandler 的一个方法。** 这就是 OOP 重构的本质——不是写新代码，而是把已有代码重新组织成可复用、可测试、可维护的结构。

## 5. Day 7 预告

明天是 Week 2 的压力测试日（5小时大满贯）：循环抓取/生成 50 只股票的数据，用 DataHandler 批量跑管道，引入 `tqdm` 进度条监控。核心考验两个：**内存控制**和**Pipeline 的健壮性**。
