import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import os

def download_latest_fund_data(symbol, hdf5_path):
    # 确保目录存在
    os.makedirs(os.path.dirname(hdf5_path), exist_ok=True)
    # 处理符号名称，使其符合Python标识符的命名规则
    symbol_key = f"sym_{symbol}"

    # 获取最新的基金数据
    """获取基金的单位净值数据"""
    fund_data = ak.fund_open_fund_info_em(symbol=symbol, indicator="单位净值走势")
    fund_data = fund_data[['净值日期', '单位净值', '日增长率']]
    new_data = fund_data.set_index('净值日期')

    # 将新数据写回HDF5文件
    with pd.HDFStore(hdf5_path) as store:
        store[symbol_key] = new_data
    print(f"数据已成功下载并保存到 {hdf5_path} 中，符号: {symbol}")

def update_indices(symbols,hdf5_path):
    for symbol in symbols:
        print(f"Updating data for symbol: {symbol}")
        download_latest_fund_data(symbol,hdf5_path)

# 主函数
if __name__ == "__main__":
    # 基金列表(相信人类)
    symbols = ["040046","164701","007721","007380","006282","160416","162411","015016","519191","008763","013308","000043","000893","001668","000369","006105","016630","006105","016630","005613","164824","206011"]
    update_indices(symbols,hdf5_path="data/fund_human.h5")