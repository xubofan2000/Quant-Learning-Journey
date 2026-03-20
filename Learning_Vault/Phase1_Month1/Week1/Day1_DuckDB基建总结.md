# Phase 1 - Week 1 - Day 1: DuckDB 初始化基建知识点总结

## 1. 为什么量化环境首选 DuckDB 而不是 SQLite？
在你产出的 `day1_duckdb_init.py` 脚本中，你成功在本地创建了 `.duckdb` 物理数据库文件。相比于老牌稳健的 SQLite，DuckDB 在金融数据界备受推崇的原因主要有两点核心差异：

* **行式存储 (SQLite) vs 列式存储 (DuckDB)**：
  * **行式 (Row-oriented)**：数据在磁盘上按行连着存。如果要查询某个月某个股票的收盘价，SQLite 依然需要把那一行的日期、开盘、高低点甚至用不到的列全拿出来，适合高频零星读取（例如记账本、网站后台）。
  * **列式 (Columnar)**：同列的数据在磁盘和内存中是在一起的。量化聚合计算（如：全系列股票的 `close_price` 算移动平均），DuckDB 只扫描这单纯的一列，并且原生自带 CPU SIMD（单指令多数据流）底层极速向量化加成，读取与计算速度直接碾压 SQLite。
* **零成本的 Pandas/Polars 映射桥梁**：
  * DuckDB 在查询时能将底层二进制结果顺滑地直接吐成 `Pandas DataFrame`，就像你脚本里写的 `.df()`。

## 2. 核心 Python API 语法复查
结合你成功运行的代码，以下几个 API 是你未来几周最高频调用的基石：

* `conn = duckdb.connect(db_path)`
  - **知识点**：用于建立**持久化**连接。如果不填路径而是传入 `':memory:'`，DuckDB 会创建一个完全在内存中的临时数据库（处理完一波临时丢弃的数据时非常实用且极快）。
* `conn.execute("CREATE TABLE ...")`
  - **知识点**：标准 SQL 支持。它的方言（Dialect）高度兼容 PostgreSQL。无需专门学一套 Python 函数库，你之前所有的 SQL 查询/建表/联合经验可以 100% 顺滑平移。
* `.df()` 转换柄
  - **知识点**：对于查询返回的 Relation 对象，可以直接加上 `.df()`（Pandas DataFrame），`.pl()`（Polars DataFrame）或 `.arrow()`（PyArrow Table）。
* `conn.close()`
  - **知识点**：对于物理 `duckdb` 文件，同时只能有一个进程获得写入锁。记得关闭连接以解除文件锁定。

## 3. 迈向 Day 2
Day 1 你已经搭好了一座极简、极速的量化数据仓储地基（以及包含 date, ticker, close_price, volume 的骨架表）。

下一步 (Day 2) 就是用 Python 的随机手段或 Faker 工具生成 10 万行高质量的 mock 数据。用庞大的数据将这座“空城”填满！
