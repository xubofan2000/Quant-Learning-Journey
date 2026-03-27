# Week 1 代码闪卡 (Flashcards)

> 每张卡片包含一个**问题 (Q)** 和一个**答案 (A)**。用手遮住答案部分，尝试自己回忆或口述，然后翻开核对。

---

## 🟢 Day 1-2: DuckDB 基建与向量化造数

### 卡片 1: 持久化 vs 内存数据库
**Q:** `duckdb.connect('market.duckdb')` 和 `duckdb.connect(':memory:')` 的本质区别是什么？什么场景用哪个？
<details><summary>🔑 答案</summary>

前者在磁盘上创建物理文件，数据持久保存，关闭程序后数据仍在；后者纯内存临时库，进程结束即销毁。
- **持久化**：存储历史行情等需要长期积累的数据
- **内存**：做一次性的临时中间计算（如清洗后丢弃的过渡表）
</details>

---

### 卡片 2: 向量化 vs for 循环
**Q:** 生成 10 万行随机数据，为什么 `np.random.choice(tickers, size=100000)` 比 `for i in range(100000): list.append(random.choice(tickers))` 快百倍？
<details><summary>🔑 答案</summary>

`np.random.choice` 调用的是 NumPy 底层用 C 语言编写的连续内存分配数组操作，绕过了 Python 解释器逐行执行的巨大开销。`for` 循环每次迭代都要经过 Python 的类型检查、内存碎片分配和解释器调度，在大批量数据面前极其低效。
</details>

---

### 卡片 3: 随机种子
**Q:** `np.random.seed(42)` 在量化研发中为什么是强制纪律？不设会怎样？
<details><summary>🔑 答案</summary>

保证**可复现性 (Reproducibility)**。不设种子，每次运行生成的数据都不同，导致：
- Bug 无法复现和排查
- 回测结果无法被同事验证
- 回归测试 (Regression Test) 失去意义
</details>

---

### 卡片 4: 动态寻址
**Q:** 写出用 `__file__` 从当前脚本定位到项目根目录的标准代码（脚本在 `Week1/` 下，根目录在上三级）。
<details><summary>🔑 答案</summary>

```python
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
```
配合 `os.makedirs(target_dir, exist_ok=True)` 实现防御性目录创建。
</details>

---

## 🔵 Day 3: DuckDB 零拷贝查询

### 卡片 5: FROM 文件路径
**Q:** DuckDB 的 `SELECT * FROM 'path/to/file.csv'` 为什么叫"零拷贝查询"？它跟 `pd.read_csv()` 的内存模型有什么本质区别？
<details><summary>🔑 答案</summary>

- **DuckDB**：不把 CSV 全量加载进内存，而是像扫描仪一样在磁盘上按需读取所选列，边扫边聚合，内存消耗极低。
- **Pandas**：`read_csv()` 必须把整个文件反序列化全部塞入内存后才能操作，面对超大文件容易 OOM 崩溃。
</details>

---

### 卡片 6: .df() 桥接
**Q:** `duckdb.query(sql).df()` 中的 `.df()` 做了什么？除了 `.df()` 还有哪些输出格式？
<details><summary>🔑 答案</summary>

`.df()` 将 DuckDB 的查询结果转为 **Pandas DataFrame**。其他选项：
- `.pl()` → Polars DataFrame
- `.arrow()` → PyArrow Table
- `.fetchall()` → 原生 Python 元组列表
</details>

---

## 🟡 Day 4: SQL → Pandas 映射

### 卡片 7: WHERE → 布尔掩码
**Q:** 把 `SELECT * FROM df WHERE price > 480` 翻译成 Pandas 代码，并解释底层发生了什么。
<details><summary>🔑 答案</summary>

```python
df[df['price'] > 480]
```
底层：`df['price'] > 480` 生成一个与原表等长的布尔数组（10万个 True/False），然后将这个布尔数组当作"遮罩面具"反向盖到 `df` 上，`False` 对应的行被过滤掉。
</details>

---

### 卡片 8: reset_index() 救命操作
**Q:** 执行 `df.groupby('ticker')['volume'].sum()` 后，如果不加 `.reset_index()` 会导致什么后果？
<details><summary>🔑 答案</summary>

`ticker` 列会被 Pandas 从普通数据列"提拔"为特殊的行索引 (Index)。后续如果尝试 `df['ticker']` 访问或做 `merge` 操作，会直接报 **KeyError**，因为它已经不在正常的列空间里了。`.reset_index()` 把它拍回普通列。
</details>

---

### 卡片 9: 链式调用的内存优势
**Q:** 以下两种写法在内存层面有何区别？
```python
# 写法A：中间变量
df1 = df[df['volume'] > 900000]
df2 = df1.groupby('ticker')['price'].max()
df3 = df2.reset_index()

# 写法B：链式调用
result = (
    df[df['volume'] > 900000]
    .groupby('ticker')['price']
    .max()
    .reset_index()
)
```
<details><summary>🔑 答案</summary>

写法A 创建了 `df1`、`df2`、`df3` 三个中间变量，它们各自占用独立内存空间，直到函数结束或手动 `del` 才释放。写法B 的链式调用中，每一步的中间结果在传递给下一步后立即被垃圾回收器销毁，内存峰值更低。
</details>

---

## 🟣 Day 5: Polars 惰性计算

### 卡片 10: scan_csv vs read_csv
**Q:** `pl.scan_csv()` 和 `pl.read_csv()` 的核心区别是什么？`scan_csv` 执行完后内存里有数据吗？
<details><summary>🔑 答案</summary>

- `read_csv()`：立即全量加载到内存（类似 Pandas 的急切模式）
- `scan_csv()`：**不加载任何数据**，只读取文件的 Schema（列名和类型），返回一个 LazyFrame（查询计划）

内存里没有实际数据，直到你调用 `.collect()` 才真正执行。
</details>

---

### 卡片 11: 谓词下推与列裁剪
**Q:** Polars 的查询优化器在你写了 `.filter(pl.col('volume') > 900000)` 后做了什么优化？用 `.explain()` 能看到什么？
<details><summary>🔑 答案</summary>

两大优化：
1. **谓词下推 (Predicate Pushdown)**：把 `volume > 900000` 的过滤条件推到磁盘读取层，不符合条件的行根本不进内存。
2. **列裁剪 (Projection Pushdown)**：只读取用到的 `ticker`、`volume`、`price` 三列，跳过其他列。

`.explain()` 会打印出类似 SQL `EXPLAIN` 的物理执行计划树，展示这些优化。
</details>

---

### 卡片 12: .collect() 的含义
**Q:** 在 Polars 的惰性模式下，`.filter()`、`.group_by()`、`.agg()` 实际上做了什么？`.collect()` 做了什么？
<details><summary>🔑 答案</summary>

前面的操作**只是在构建一张蓝图（查询计划）**，没有任何数据被处理。`.collect()` 是真正"扣动扳机"的命令——Polars 的 Rust 多线程引擎此时才会按照优化后的计划，压榨所有 CPU 核心并行执行计算，返回最终的 DataFrame。
</details>

---

## 🔴 Day 6-7: 真实数据管道与双引擎对账

### 卡片 13: 水位线 (Watermark)
**Q:** 在 ETL 管道中，为什么每次运行前要先执行 `SELECT MAX(trade_date)` 查询？不查会怎样？
<details><summary>🔑 答案</summary>

查询水位线决定了是**全量抓取**还是**增量补齐**。不查的话，每次运行都会暴力请求最近 5 年全量数据，导致：
- 浪费带宽和时间
- 触发第三方 API 的频率限制，IP 被封禁
</details>

---

### 卡片 14: 幂等写入
**Q:** 为什么在列式数据库中用 `DELETE + INSERT` 而不是 `UPSERT` 来处理重叠数据？如果脚本运行了 3 遍，数据会重复 3 倍吗？
<details><summary>🔑 答案</summary>

列式数据库（DuckDB/ClickHouse）底层按列块连续压缩存储，逐行比对主键再更新（UPSERT）会触发"写放大"，性能极差。`DELETE` 先快速删掉重叠时间段的旧数据，再 `INSERT` 整块追加新数据，效率高得多。
由于先删后插，**无论运行多少遍，数据永远只有一份**——这就是幂等性 (Idempotency)。
</details>

---

### 卡片 15: 事务保护
**Q:** `BEGIN TRANSACTION` + `COMMIT` / `ROLLBACK` 在批量写入中解决了什么问题？
<details><summary>🔑 答案</summary>

保证**原子性 (Atomicity)**。如果在 INSERT 到一半时断电或程序崩溃：
- **有事务**：数据库自动回滚，恢复到写入前的干净状态
- **无事务**：数据库里残留一半新、一半旧的脏数据，后续所有分析结果都不可信
</details>

---

### 卡片 16: read_only 连接
**Q:** `duckdb.connect(db_path, read_only=True)` 比普通连接多了什么保护？什么时候必须用？
<details><summary>🔑 答案</summary>

物理层面禁止任何写操作（INSERT/UPDATE/DELETE/DROP 全部报错）。在只做查询分析、画图展示、对账校验时**必须用**，杜绝误操作破坏历史数据的风险。
</details>

---

### 卡片 17: 浮点容差断言
**Q:** 为什么在双引擎对账时，`pd.testing.assert_series_equal` 需要设置 `atol=1e-3` 而不是 `check_exact=True`？
<details><summary>🔑 答案</summary>

DuckDB（C++引擎）和 Pandas（Python引擎）在浮点运算中使用不同的截断和舍入策略，计算同一个平均值时最后几位小数会有微小差异（这是 IEEE 754 浮点数标准的固有特性）。`atol=1e-3` 设置了绝对容差，允许 0.001 以内的偏差。如果用 `check_exact=True` 会误报"对账失败"。
</details>
