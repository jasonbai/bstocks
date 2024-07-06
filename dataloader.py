import os
import pandas as pd
import akshare as ak
from datetime import datetime, timedelta
import copy

print("开始更新数据...")

def fetch_index_data(symbol, start_date, end_date, period="daily", hdf5_path="data/index_data.h5"):
    # 确保目录存在
    os.makedirs(os.path.dirname(hdf5_path), exist_ok=True)

    # 处理符号名称，使其符合Python标识符的命名规则
    symbol_key = f"sym_{symbol}"

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
    index_data = ak.index_zh_a_hist(symbol=symbol, period=period, start_date=local_start_date, end_date=end_date)
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

def fetch_index_all(symbol, start_date, end_date, period="daily", hdf5_path="data/index_all.h5"):
    # 确保目录存在
    os.makedirs(os.path.dirname(hdf5_path), exist_ok=True)

    # 处理符号名称，使其符合Python标识符的命名规则
    symbol_key = f"sym_{symbol}"

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

    # 指数成份股
    hs300_stocks = ak.index_stock_cons(symbol=symbol)
    stock_list = hs300_stocks['品种代码'].tolist()

    # 获取所有成份股的历史数据
    all_stock_data = pd.DataFrame()
    for stock in stock_list:
        stock_data = ak.stock_zh_a_hist(symbol=stock, period=period, start_date=local_start_date, end_date=end_date)
        stock_data['日期'] = pd.to_datetime(stock_data['日期'])
        stock_data.set_index('日期', inplace=True)
        stock_data['股票代码'] = stock
        all_stock_data = pd.concat([all_stock_data, stock_data])

    # 检查并删除重复的股票代码和日期
    all_stock_data = all_stock_data.reset_index().drop_duplicates(subset=['日期', '股票代码']).set_index('日期')    

    # 确保每个股票代码和日期的组合是唯一的
    all_stock_data = all_stock_data.dropna(subset=['收盘'])

    all_data = pd.DataFrame(all_stock_data)

    # 合并已有数据和新数据
    if not existing_data.empty:
        combined_data_all = pd.concat([existing_data, all_data])
        # 确保合并后的数据中没有重复的日期和股票代码组合
        combined_data_all = combined_data_all.reset_index().drop_duplicates(subset=['日期', '股票代码']).set_index('日期')
    else:
        combined_data_all = all_data

    # 将合并后的数据写回HDF5文件
    with pd.HDFStore(hdf5_path) as store:
        store[symbol_key] = combined_data_all

    return combined_data_all

def update_indices(symbols, start_date, end_date, period="daily"):
    for symbol in symbols:
        print(f"Updating data for symbol: {symbol}")
        fetch_index_data(symbol, start_date, end_date, period)

def update_indices_all(symbols, start_date, end_date, period="daily"):
    for symbol in symbols:
        print(f"Updating data for symbol: {symbol}")
        fetch_index_all(symbol, start_date, end_date, period)

if __name__ == "__main__":
    symbols = ["000300", # 沪深300指数
               "399006", # 创业板指数
               "000016", # 上证50指数
               "399673", # 创业50指数
               "000905", # 中证500指数
            ]
    start_date = "20200101"
    yesterday = datetime.now() - timedelta(days=1)
    end_date = yesterday.strftime("%Y%m%d")
    
    # 使用深拷贝来避免原始参数被修改
    start_date_copy = copy.deepcopy(start_date)
    end_date_copy = copy.deepcopy(end_date)
    
    update_indices(symbols, start_date_copy, end_date_copy)
    update_indices_all(symbols, start_date_copy, end_date_copy)
    print("数据更新完毕.")