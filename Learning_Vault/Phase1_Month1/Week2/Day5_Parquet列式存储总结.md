# Phase 1 - Week 2 - Day 5: Parquet 列式存储与性能基准总结

## 1. 为什么量化圈抛弃 CSV 拥抱 Parquet？

| 维度               | CSV                                  | Parquet                                               |
| ------------------ | ------------------------------------ | ----------------------------------------------------- |
| **存储方式** | 行式（逐行逐字段的纯文本）           | 列式（同一列的数据连续聚在一起）                      |
| **类型信息** | 无（读取时 Pandas 要逐列猜测 dtype） | 自描述（列名、类型、压缩方式全部写在文件尾部 Footer） |
| **压缩**     | 不压缩                               | 内置 Snappy/Gzip/Zstd 压缩                            |
| **体积**     | 基准                                 | 小 3~5 倍                                             |
| **读取速度** | 基准                                 | 快 5~20 倍                                            |
| **列裁剪**   | 不支持（必须读全部列再丢弃）         | 原生支持（只读你 SELECT 的列，其他列不碰磁盘）        |

## 2. Snappy 压缩：为什么是默认选择？

Parquet 支持多种压缩算法，但 Snappy 是量化场景的最佳平衡点：

- **压缩比**：中等（约 3~5x），不如 Gzip 极致但够用
- **解压速度**：极快（Snappy 的设计目标就是"解压几乎不花时间"）
- **CPU 开销**：极低，不会成为回测管道的瓶颈

在量化回测中，你要反复读取同一份历史数据上百次（参数搜索、因子调优），解压速度远比压缩比重要。

## 3. DuckDB 直接查询 Parquet 文件

```python
conn.sql(f"SELECT AVG(etf_close) FROM '{parquet_path}'")
```

这行代码的底层发生了什么：

1. DuckDB 只读取 Parquet 文件尾部的 **Footer**（几十字节），获取列的元数据和偏移量
2. 根据 SQL 中用到的列名（`etf_close`），直接跳到该列在文件中的物理位置
3. 只解压和读取 `etf_close` 这一列的数据块，其他列**完全不碰**
4. 在 DuckDB 的向量化引擎里完成 AVG 聚合，返回结果

整个过程**不经过 Pandas**，没有 DataFrame 的内存开销。这就是为什么 DuckDB + Parquet 的组合在处理 GB 级历史行情数据时能保持秒级响应。

## 4. Parquet 的自描述性（vs CSV 的类型推断地狱）

用 `pyarrow.parquet.read_schema()` 可以直接读取 Parquet 文件的 Schema：

```
[0] etf_close: double
[1] etf_volume: int64
[2] index_close: double
[3] SMA_5: double
[4] etf_log_ret: double
...
```

**CSV 的痛点**：`pd.read_csv()` 读取时会逐列扫描内容来"猜"类型。日期列经常被猜成字符串，整数列如果有 NaN 会被升级为 float64，前导零的编码（如股票代码 `000001`）会被吞掉变成 `1`。你需要手动传 `dtype={}` 和 `parse_dates=[]` 来纠正，极其繁琐。

**Parquet 的方案**：写入时就把类型"焊死"在文件里。下次读取时，`pd.read_parquet()` 不猜不推断，直接按记录好的类型还原——零歧义、零意外。

## 5. 今天的全流程串联

今天的脚本是 Week 2 前四天的**大集成**：

```
Day 1 ffill填充 → Day 2 SMA滚动窗口 → Day 3 对数收益率 → Day 4 LEFT JOIN → Day 5 Parquet落盘
```

最终产出了一份 `clean_data.parquet` 特征宽表文件，它包含原始价格、技术指标、收益率、超额收益——这正是后面做策略回测和因子分析时直接 `read_parquet()` 就能用的标准化输入。

## 6. Day 6 预告

明天进入面向对象重构 (OOP)——把这五天写的散装代码封装成一个 `DataHandler` 类，暴露 `load_raw()`、`clean()`、`save_feature()` 等标准方法。从"面条代码"升级为可复用的工程化模块。
