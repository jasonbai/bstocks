import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

# 指数数据下载器
class IndexAnalyzer:
    def __init__(self, symbol):
        self.symbol = symbol

    def get_fund_rank(self):
        try:
            df_fund_rank = ak.fund_open_fund_rank_em(self.symbol)
            if df_fund_rank.empty:
                print(f"Warning: No data returned for symbol '{self.symbol}'.")
                return None
            return df_fund_rank
        except Exception as e:
            print(f"Error occurred while fetching data for symbol '{self.symbol}': {e}")
            return None

# 主函数
if __name__ == "__main__":
    # 公募基金下载器
    symbols = {"全部", "股票型", "混合型", "债券型", "指数型", "QDII", "FOF"}
    
    for symbol in symbols:
        analyzer = IndexAnalyzer(symbol)
        result = analyzer.get_fund_rank()
        if result is not None:
            result.to_csv(f"data/fund_rank_{symbol}.csv")
            print(f"{symbol} 公募基金数据下载完毕！")
        else:
            print(f"{symbol} 公募基金数据下载失败！")
    print("基金排序下载完成！")