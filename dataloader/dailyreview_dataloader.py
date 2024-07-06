import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

# 指数数据下载器
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
    
# ETF数据下载器
class ETFAnalyzer:
    def __init__(self, etf_list, start_date, end_date):
        self.etf_list = etf_list
        self.start_date = start_date
        self.end_date = end_date
        self.result_df = pd.DataFrame(columns=["ETF名称", "ETF代码", "最新价", "今日涨幅", "近1周涨幅", "近30天涨幅"])

    def get_etf_data(self, etf_code):
        etf_data = ak.fund_etf_hist_em(symbol=etf_code, start_date=self.start_date, end_date=self.end_date)
        return etf_data

    def calculate_percentage_change(self, data, column_name):
        data[column_name] = (data[column_name].pct_change() * 100).round(2)
        return data

    def get_etf_statistics(self, etf_name, etf_code, data):
        latest_data = data.iloc[-1]
        statistics = {
            "ETF名称": etf_name,
            "ETF代码": etf_code,
            "最新价": latest_data['收盘'],
            "今日涨幅": latest_data['涨跌幅'].astype(str) + '%',
            "近1周涨幅": data['涨跌幅'].tail(5).sum().round(2).astype(str) + '%',
            "近30天涨幅": data['涨跌幅'].tail(30).sum().round(2).astype(str) + '%',
        }
        return statistics

    def get_combined_etf_statistics(self):
        for etf_name, etf_code in self.etf_list.items():
            etf_data = self.get_etf_data(etf_code)
            statistics = self.get_etf_statistics(etf_name, etf_code, etf_data)
            statistics_df = pd.DataFrame([statistics])
            self.result_df = pd.concat([self.result_df, statistics_df], ignore_index=True)
        return self.result_df
    
# 主函数
if __name__ == "__main__":
    # 指数数据下载器测试
    index_codes = ["000001", "399001", "399006", "000688"]
    index_names = ["上证指数", "深圳指数", "创业板", "科创板"]
    start_date = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")
    end_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    analyzer = IndexAnalyzer("daily", start_date, end_date, index_codes, index_names)
    result = analyzer.get_index_statistics(start_date, end_date)
    result.to_csv("data/index_statistics.csv")

    # 国内宽基ETF数据下载器
    etf_list1 = {
    "上证50ETF": "510050",
    "中证500ETF": "159922",
    "沪深300": "510300",
    "红利ETF": "510880",
    "创业板ETF": "159915",
    "恒生ETF": "159920"
    }
    analyzer = ETFAnalyzer(etf_list1, start_date, end_date)
    etf_stat_1 = analyzer.get_combined_etf_statistics()
    etf_stat_1['近1周涨幅'] = etf_stat_1['近1周涨幅'].str.rstrip('%').astype('float')
    etf_stat_1 = etf_stat_1.sort_values(by='近1周涨幅', ascending=False)
    etf_stat_1['近1周涨幅'] = (etf_stat_1['近1周涨幅']).round(2).astype(str) + '%'
    etf_stat_1.to_csv("data/etf_statistics1.csv")

    # 全球主要ETF数据下载器
    etf_list2 = {
    "日经ETF": "513520",
    "上证50ETF": "510050",
    "沪深300": "510300",
    "德国ETF": "513030",
    "法国CAC40ETF": "513080",
    "恒生ETF": "159920",
    "标普500ETF": "513500",
    "纳斯达克ETF": "159632",
    "黄金ETF": "518880",
    "石油ETF": "561360"
    }
    analyzer = ETFAnalyzer(etf_list2, start_date, end_date)
    etf_stat_2 = analyzer.get_combined_etf_statistics()
    etf_stat_2['近1周涨幅'] = etf_stat_2['近1周涨幅'].str.rstrip('%').astype('float')  # 将字符串转换为数值
    etf_stat_2 = etf_stat_2.sort_values(by='近1周涨幅', ascending=False)
    etf_stat_2['近1周涨幅'] = (etf_stat_2['近1周涨幅']).round(2).astype(str) + '%'
    etf_stat_2.to_csv("data/etf_statistics2.csv")

    # 行业ETF数据下载器
    etf_list3 = {
    "电力ETF": "159611",
    "中概互联网ETF": "513050",
    "证券ETF": "512880",
    "医疗ETF": "512170",
    "芯片ETF": "159995",
    "半导体ETF": "512480",
    "黄金ETF": "518880",
    "光伏ETF": "515790",
    "酒ETF": "512690",
    "消费ETF": "159928",
    "军工ETF": "512660",
    "新能源车ETF": "515030",
    "创新药ETF": "159992",
    "游戏ETF": "159869",
    "养殖ETF": "159865",
    "有色金属ETF": "512400",
    "房地产ETF": "512200",
    "传媒ETF": "512980",
    "旅游ETF": "159766",
    "光伏ETF": "159857",
    "煤炭ETF": "515220",
    "通信ETF": "515880",
    "传媒ETF": "512980"
    }
    analyzer = ETFAnalyzer(etf_list3, start_date, end_date)
    etf_stat_3 = analyzer.get_combined_etf_statistics()
    etf_stat_3['近1周涨幅'] = etf_stat_3['近1周涨幅'].str.rstrip('%').astype('float')  # 将字符串转换为数值
    etf_stat_3 = etf_stat_3.sort_values(by='近1周涨幅', ascending=False)
    etf_stat_3['近1周涨幅'] = (etf_stat_3['近1周涨幅']).round(2).astype(str) + '%'
    etf_stat_3.to_csv("data/etf_statistics3.csv")