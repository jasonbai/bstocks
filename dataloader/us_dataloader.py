import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import os

def fetch_usetf_data(symbol, start_date, end_date, period="daily", hdf5_path="data/us_etf.h5"):
    # 确保目录存在
    os.makedirs(os.path.dirname(hdf5_path), exist_ok=True)

    # 处理符号名称，使其符合Python标识符的命名规则
    symbol_key = f"sym_{symbol.replace('.', '_')}"

    # 尝试从HDF5文件中读取已有数据
    try:
        with pd.HDFStore(hdf5_path) as store:
            existing_data = store[symbol_key]
    except KeyError:
        existing_data = pd.DataFrame()

    # 获取本地数据的最新日期
    if not existing_data.empty:
        last_date = existing_data.index.max()
        # 如果本地数据的最新日期在请求的结束日期之前，则需要下载缺失的数据
        if last_date < pd.to_datetime(end_date):
            print(f"Fetching missing data for {symbol}...")
            local_start_date = (last_date + pd.Timedelta(days=1)).strftime('%Y%m%d')
        else:
            print(f"Local data for {symbol} is already up-to-date")
            return existing_data  # 本地数据已经是最新的，不需要下载
    else:
        local_start_date = start_date

    # 获取最新数据
    index_data = ak.stock_us_hist(symbol=symbol, period=period, start_date=local_start_date, end_date=end_date)
    new_data = pd.DataFrame(index_data)
    new_data['日期'] = pd.to_datetime(new_data['日期'])
    new_data.set_index('日期', inplace=True)

    # 合并已有数据和新数据
    if not existing_data.empty:
        combined_data = pd.concat([existing_data, new_data])
        combined_data = combined_data[~combined_data.index.duplicated(keep='last')]
    else:
        combined_data = new_data

    # 将合并后的数据写回HDF5文件
    with pd.HDFStore(hdf5_path) as store:
        store[symbol_key] = combined_data

    return combined_data

# 更新ETF池数据
def update_indices(symbols, start_date, end_date, period="daily"):
    for symbol in symbols:
        print(f"Updating data for symbol: {symbol}")
        fetch_usetf_data(symbol, start_date, end_date, period)

# 主函数
if __name__ == "__main__":
    symbols = ["107.RSP", 
               "107.IWY", 
               "107.EWJ", 
               "107.INDA",
               "107.EWQ",
               "107.EWG",
               "107.VNM",
               "107.MOAT", 
               "105.PFF", 
               "107.VNQ",
               "105.QQQ",
               "107.SPY"
            ]
    start_date = "20200101"
    yesterday = datetime.now() - timedelta(days=1)
    end_date = yesterday.strftime("%Y%m%d")

    update_indices(symbols, start_date, end_date)
    print("美股ETF数据更新完毕.")