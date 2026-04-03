"""
data_pipeline.py - 量化数据管道 (OOP 重构版)

将 Week 1~2 的散装脚本封装为面向对象的 DataHandler 类。
暴露标准接口：load_raw → clean → add_features → save_feature

用法：
    handler = DataHandler(db_path="path/to/market_data.duckdb")
    handler.load_raw(etf_symbol="sh510300", index_table="szzs")
    handler.clean()
    handler.add_features(sma_windows=[5, 20])
    handler.save_feature("output/clean_data.parquet")
    
    # 或者一行搞定：
    handler.run(output_path="output/clean_data.parquet")
"""

import duckdb
import pandas as pd
import numpy as np
import os
import time
from typing import Optional


class DataHandler:
    """量化数据管道核心类：从原始数据到特征宽表的全流程封装。"""

    def __init__(self, db_path: str):
        """
        初始化数据管道。

        Args:
            db_path: DuckDB 数据库文件的绝对路径
        """
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"数据库文件不存在: {db_path}")
        
        self.db_path = db_path
        self.df: Optional[pd.DataFrame] = None  # 主数据表
        self._is_loaded = False
        self._is_cleaned = False
        self._is_featured = False

    # ==========================================
    # 📂 Stage 1: 数据加载
    # ==========================================
    def load_raw(
        self,
        etf_symbol: str = "sh510300",
        index_table: Optional[str] = "szzs"
    ) -> "DataHandler":
        """
        从 DuckDB 加载原始数据。

        Args:
            etf_symbol: ETF 代码
            index_table: 基准指数表名（None 则跳过 JOIN）
        
        Returns:
            self（支持链式调用）
        """
        conn = duckdb.connect(self.db_path, read_only=True)

        # 读取 ETF 数据
        df_etf = conn.sql(f"""
            SELECT trade_date, close_price, volume
            FROM etf_daily_kline 
            WHERE symbol = '{etf_symbol}'
            ORDER BY trade_date
        """).df()

        df_etf['trade_date'] = pd.to_datetime(df_etf['trade_date'])
        df_etf.rename(columns={
            'close_price': 'etf_close',
            'volume': 'etf_volume'
        }, inplace=True)

        # 尝试 LEFT JOIN 基准指数
        if index_table:
            try:
                df_index = conn.sql(f"""
                    SELECT date AS trade_date, close AS index_close
                    FROM {index_table}
                    ORDER BY date
                """).df()
                df_index['trade_date'] = pd.to_datetime(df_index['trade_date'])
                
                self.df = pd.merge(df_etf, df_index, on='trade_date', how='left')
                assert len(self.df) == len(df_etf), "LEFT JOIN 行数膨胀！"
                print(f"  ✅ 已加载 ETF({etf_symbol}) + 基准指数({index_table})")
            except Exception as e:
                print(f"  ⚠️ 基准指数表 {index_table} 不可用 ({e})，仅加载 ETF")
                self.df = df_etf
        else:
            self.df = df_etf

        conn.close()

        # 设置时间索引
        self.df = self.df.set_index('trade_date').sort_index()
        self._is_loaded = True
        
        print(f"  📊 数据范围: {self.df.index.min().date()} ~ {self.df.index.max().date()}, {len(self.df)} 行")
        return self

    # ==========================================
    # 🧹 Stage 2: 数据清洗
    # ==========================================
    def clean(self, fill_method: str = "ffill") -> "DataHandler":
        """
        清洗缺失值。

        Args:
            fill_method: 填充方法 ("ffill"=前向填充, "bfill"=后向填充, "drop"=直接丢弃)
        
        Returns:
            self（支持链式调用）
        """
        self._check_loaded()

        nan_before = self.df.isna().sum().sum()

        if fill_method == "ffill":
            self.df = self.df.ffill()
        elif fill_method == "bfill":
            self.df = self.df.bfill()
        elif fill_method == "drop":
            self.df = self.df.dropna()
        else:
            raise ValueError(f"不支持的填充方法: {fill_method}")

        nan_after = self.df.isna().sum().sum()
        self._is_cleaned = True

        print(f"  🧹 清洗完成: NaN {nan_before} → {nan_after} (方法: {fill_method})")
        return self

    # ==========================================
    # ⚙️ Stage 3: 特征工程
    # ==========================================
    def add_features(
        self,
        sma_windows: list[int] = [5, 20],
        add_returns: bool = True,
        add_excess: bool = True
    ) -> "DataHandler":
        """
        添加技术指标和收益率特征。

        Args:
            sma_windows: SMA 窗口列表，如 [5, 20, 60]
            add_returns: 是否添加收益率列
            add_excess: 是否添加超额收益列（需要 index_close 列存在）
        
        Returns:
            self（支持链式调用）
        """
        self._check_loaded()

        # SMA 移动平均线
        for w in sma_windows:
            self.df[f'SMA_{w}'] = self.df['etf_close'].rolling(w).mean()

        # EMA 指数移动平均
        for w in sma_windows:
            self.df[f'EMA_{w}'] = self.df['etf_close'].ewm(span=w, adjust=False).mean()

        if add_returns:
            # 简单收益率 + 对数收益率
            self.df['etf_return'] = self.df['etf_close'].pct_change()
            self.df['etf_log_ret'] = np.log(
                self.df['etf_close'] / self.df['etf_close'].shift(1)
            )

        if add_excess and 'index_close' in self.df.columns:
            self.df['index_return'] = self.df['index_close'].pct_change()
            self.df['index_log_ret'] = np.log(
                self.df['index_close'] / self.df['index_close'].shift(1)
            )
            self.df['excess_return'] = self.df['etf_return'] - self.df['index_return']
            self.df['excess_log_ret'] = self.df['etf_log_ret'] - self.df['index_log_ret']

        # 去掉最大窗口的预热期 NaN
        warmup = max(sma_windows) if sma_windows else 0
        self.df = self.df.iloc[warmup:]
        self._is_featured = True

        print(f"  ⚙️ 特征工程完成: {self.df.shape[1]} 列, 去掉 {warmup} 行预热期")
        return self

    # ==========================================
    # 💾 Stage 4: 持久化输出
    # ==========================================
    def save_feature(
        self,
        output_path: str,
        compression: str = "snappy"
    ) -> str:
        """
        保存特征宽表为 Parquet 格式。

        Args:
            output_path: 输出路径（.parquet）
            compression: 压缩算法 ("snappy", "gzip", "zstd")
        
        Returns:
            保存的文件绝对路径
        """
        self._check_loaded()

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        self.df.to_parquet(output_path, engine='pyarrow', compression=compression)
        
        size_kb = os.path.getsize(output_path) / 1024
        print(f"  💾 已保存: {output_path} ({size_kb:.1f} KB, {compression}压缩)")
        return os.path.abspath(output_path)

    # ==========================================
    # 🚀 一键 Pipeline
    # ==========================================
    def run(
        self,
        output_path: str,
        etf_symbol: str = "sh510300",
        index_table: Optional[str] = "szzs",
        sma_windows: list[int] = [5, 20],
    ) -> str:
        """
        一键执行全流程管道：加载 → 清洗 → 特征 → 保存。

        Returns:
            保存的文件绝对路径
        """
        print("🚀 启动数据管道...")
        t0 = time.perf_counter()

        self.load_raw(etf_symbol=etf_symbol, index_table=index_table)
        self.clean()
        self.add_features(sma_windows=sma_windows)
        path = self.save_feature(output_path)

        elapsed = time.perf_counter() - t0
        print(f"✅ 管道完成！耗时 {elapsed:.2f}s, 输出 {self.df.shape[0]}行 × {self.df.shape[1]}列")
        return path

    # ==========================================
    # 📊 辅助方法
    # ==========================================
    def summary(self) -> pd.DataFrame:
        """返回 DataFrame 的 describe() 统计摘要。"""
        self._check_loaded()
        return self.df.describe()

    def annual_alpha(self) -> pd.Series:
        """
        计算年度超额收益（基于对数收益率严谨聚合）。
        
        Returns:
            年度超额收益百分比 Series
        """
        self._check_loaded()
        if 'excess_log_ret' not in self.df.columns:
            raise ValueError("需要先 add_features(add_excess=True)")
        
        log_sum = self.df['excess_log_ret'].dropna().resample('YE').sum()
        return (np.exp(log_sum) - 1) * 100

    def _check_loaded(self):
        """内部守卫：确保数据已加载。"""
        if self.df is None:
            raise RuntimeError("请先调用 load_raw() 加载数据！")

    def __repr__(self) -> str:
        if self.df is None:
            return "DataHandler(未加载)"
        return (
            f"DataHandler("
            f"{self.df.shape[0]}行×{self.df.shape[1]}列, "
            f"{self.df.index.min().date()}~{self.df.index.max().date()})"
        )


# ==========================================
# 🎯 直接运行测试
# ==========================================
if __name__ == "__main__":
    # 动态寻址
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
    db_path = os.path.join(project_root, 'Database', 'files', 'market_data.duckdb')
    output_path = os.path.join(project_root, 'Database', 'files', 'clean_data_v2.parquet')

    # 方式1：一键 Pipeline
    handler = DataHandler(db_path)
    handler.run(output_path)

    # 打印年度 Alpha
    print("\n--- 年度超额收益 (对数聚合) ---")
    for year, alpha in handler.annual_alpha().items():
        emoji = "📈" if alpha > 0 else "📉"
        print(f"  {emoji} {year.year}年: {alpha:+.2f}%")

    # 方式2：链式调用（灵活控制每一步）
    print("\n--- 链式调用演示 ---")
    handler2 = DataHandler(db_path)
    handler2.load_raw(etf_symbol="sh510300", index_table="szzs") \
            .clean(fill_method="ffill") \
            .add_features(sma_windows=[5, 10, 20, 60])
    
    print(f"\n  {handler2}")
    print(f"  列名: {handler2.df.columns.tolist()}")
