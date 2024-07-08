import pandas as pd
import os
import streamlit as st
from streamlit_option_menu import option_menu

class StockMarket_fund:

    def get_top_and_tail_funds(self, symbol):
        # 读取已经下载好的数据
        file_path = f"data/fund_rank_{symbol}.csv"
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None, None
        
        df_fund = pd.read_csv(file_path)
        df_fund['基金代码'] = df_fund['基金代码'].astype(str).str.zfill(6)
        
        # 将列转换为数值，并将无法转换的值转换为NaN
        df_fund['今年来'] = pd.to_numeric(df_fund['今年来'], errors='coerce')
        df_fund['近1月'] = pd.to_numeric(df_fund['近1月'], errors='coerce')
        df_fund['近3年'] = pd.to_numeric(df_fund['近3年'], errors='coerce')
        df_fund['近1年'] = pd.to_numeric(df_fund['近1年'], errors='coerce')
        df_fund['成立来'] = pd.to_numeric(df_fund['成立来'], errors='coerce')

        df_fund['今年来'] = df_fund['今年来'].fillna(0)
        
        # 剔除C类
        df_fund = df_fund[~df_fund['基金简称'].str.contains('C', case=False)]
        
        # 缩减输出列
        df_fund = df_fund[['基金代码', '基金简称', '日期', '近1月', '近1年', '近3年', '今年来', '成立来', '手续费']]
        
        # 今年来排序
        df_fund_year = df_fund.sort_values('今年来', ascending=False)
        
        # 获取top10和tail10
        df_fund_year_top = df_fund_year.head(10)
        df_fund_year_tail = df_fund_year.tail(10)
        
        return df_fund_year_top, df_fund_year_tail


def fund_analysis():

    choose = option_menu(None, ["公募基金排行", "我关注的基金", "我的组合"], 
    icons=['house', 'list-task', "list-task"], 
    menu_icon="cast", default_index=0, orientation="horizontal")
    if choose == '公募基金排行':
        # 大盘情况
        st.header("各类公募基金 前10后和10名")
        st.info("依照今年以来排序")

        symbols = ["全部", "股票型", "混合型", "债券型", "指数型", "QDII", "FOF"]
        stock_market = StockMarket_fund()
        for symbol in symbols:
            top10, tail10 = stock_market.get_top_and_tail_funds(symbol)
            if top10 is not None and tail10 is not None:
                st.markdown(f"### {symbol} ：前10名")
                st.dataframe(top10, hide_index=True)
                st.markdown(f"### {symbol} ：后十名")
                st.dataframe(tail10, hide_index=True)
    elif choose == '我关注的基金':
        st.header("待新增")
 
    elif choose == '我的组合':
        st.header("待新增")

    