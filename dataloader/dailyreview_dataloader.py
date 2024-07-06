import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

class IndexAnalyzer:
    def __init__(self, period, start_date, end_date, index_codes, index_names):
        self.period = period
        self.start_date = start_date
        self.end_date = end_date
        self.index_codes = index_codes
        self.index_names = index_names

    def get_index_data(self, symbol):
        index_data = ak.index_zh_a_hist(symbol, self.period, self.start_date, self.end_date)
        return index_data

    def calculate_statistics(self, data):
        if data.empty or len(data) < 2:
            return data

        data["涨跌幅"] = (data["收盘"].pct_change() * 100).round(2).astype(str) + '%'
        data["近30日均值"] = data["收盘"].rolling(window=30).mean()

        # 计算boll轨 MA20 P= 2
        data["近20日均值"] = data["收盘"].rolling(window=20).mean()
        data['20日移动标准差'] = data['收盘'].rolling(window=20).std()
        # 计算布林轨区间
        data['布林轨下轨'] = data['近20日均值'] - 1.3 * data['20日移动标准差']
        data['布林轨上轨'] = data['近20日均值'] + 1.3 * data['20日移动标准差']
        data['布林轨区间'] = list(zip((data['布林轨下轨']).round(2), (data['布林轨上轨']).round(2)))
        # 操作提示
        data["预警"] = data.apply(
            lambda row: "突破上轨" if row["收盘"] > row['布林轨上轨'] else "突破下轨" if row["收盘"] < row[
                '布林轨下轨'] else '震荡', axis=1)

        return data

    def get_observation_statistics(self, index_name, index_code, data):
        if data.empty or len(data) < 3:
            return {}

        latest_data = data.iloc[-1]
        statistics = {
            "观察日期": data.iloc[-1]['日期'],
            "观察指数": index_name,
            "指数代码": index_code,
            "当日数值": latest_data['收盘'],
            "涨跌幅": latest_data['涨跌幅'],
            "昨日数值": data.iloc[-2]['收盘'],
            "前日数值": data.iloc[-3]['收盘'],
            "近30日均值": latest_data['近30日均值'],
            "布林轨区间": latest_data['布林轨区间'],
            "预警": latest_data['预警']
        }
        return statistics

    def get_index_statistics(self, start_date, end_date):
        # 初始化结果 DataFrame
        result_df = pd.DataFrame(
            columns=["观察日期","观察指数", "指数代码", "当日数值", "涨跌幅", "昨日数值", "前日数值", "近30日均值", "布林轨区间",
                     "预警"])

        # 获取指数数据并计算统计信息
        for index_name, index_code in zip(self.index_names, self.index_codes):
            index_data = self.get_index_data(index_code)
            index_data = self.calculate_statistics(index_data)
            statistics = self.get_observation_statistics(index_name, index_code, index_data)
            # 将字典转换为DataFrame
            if statistics:
                statistics_df = pd.DataFrame([statistics])
                # 将statistics_df添加到result_df
                result_df = pd.concat([result_df, statistics_df], ignore_index=True)

        return result_df
    

# 主函数
if __name__ == "__main__":
    index_codes = ["000001", "399001", "399006", "000688"]
    index_names = ["上证指数", "深圳指数", "创业板", "科创板"]
    start_date = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")
    end_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    analyzer = IndexAnalyzer("daily", start_date, end_date, index_codes, index_names)
    result = analyzer.get_index_statistics(start_date, end_date)
    result.to_csv("data/index_statistics.csv")