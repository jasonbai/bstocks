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

    def my_fund_list(self):
        file_path = "data/fund_rank_全部.csv"
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None, None
        
        df_fund = pd.read_csv(file_path)
        df_fund['基金代码'] = df_fund['基金代码'].astype(str).str.zfill(6)
        # 确保所有数字列都是 int 型
        numeric_columns = ['单位净值', '日增长率', '近1周', '近1月', '近3月', '近6月', '近1年', '近2年', '近3年', '今年来', '成立来']
        for col in numeric_columns:
            df_fund[col] = pd.to_numeric(df_fund[col], errors='coerce').fillna(0).astype(float)

        return df_fund
    
    # 人工智能自动生成市场总结
    def summarize_market_data(self,df):
        from openai import OpenAI   
        from dotenv import load_dotenv
        # 将DataFrame转换为字符串格式
        df_str = df.to_string()
        # DeepSeek API的配置
        load_dotenv()  # 加载 .env 文件中的环境变量
        api_key = os.getenv("OPENAI_API_KEY_stocks")
        if not api_key:
            st.error("API 密钥未设置。请设置 OPENAI_API_KEY_stocks 环境变量。")
            return

        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        # 设置请求消息
        messages = [
            {"role": "system", "content": 
                    '''
                    # 角色
                    你是投资专家，擅长分析投资组合，并给出建议。你能够简要总结基金数据情况，并基于数据提供后续操作建议。

                    ## 技能
                    ### 技能 1: 总结数据情况
                    - 读取用户提供的基金数据。
                    - 简要总结数据情况，组合中持仓有的数量，今年来上涨的的数量，下跌的数量，近3月上涨的的数量，下跌的数量，同时特别分析在'近1周', '近1月', '近3月','今年来'的情况，不用一一列举，说明整个组合的情况及其中特殊的情况即可。

                    ### 技能 2: 基于数据的操作建议
                    - 分析总结后的数据，识别所有异常数据（例如，显著的增长或亏损）。
                    - 针对这些异常情况，建议适当的投资组合调整或操作策略。
                    - 格式例子:
                    =====
                    -  组合操作建议：
                    - 操作有：增持，减持，清仓
                    -  建议将 <基金代码> 进行 <操作>，因为 <原因>。
                    -  <其他操作建议，原因，同上>
                    =====

                    ## 限制:
                    - 格式要尽量简明扼要。
                    - 内容使用markdown格式，标题只需要文本加粗即可。
                    - 仅回答与基金数据总结和投资建议相关的问题。如果遇到其他领域的提问，不予回答。
                    '''
                    },
            {"role": "user", "content": f"这是最新的股票或ETF情况:\n\n{df_str}"}
        ]

        # 发送请求
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=True,
            temperature=0.7
        )

        full_response = ""
        message_placeholder = st.empty()
        for chunk in response:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

        return full_response
    
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
        myfund_list = ["008114","006228","161907","013308","163406","220670","001593","163407","008763","040046","003547","000369","006048","164824","007994","015016","000893","007721","010349","005996","019858","164701","006282","007380","160416","162411","519191","000043","001668","006105","016630","009617","007769","005613","206011"]
        stock_market = StockMarket_fund()
        df_fund = stock_market.my_fund_list()

        def filter_funds(df_fund, myfund_list):
            filtered_df = df_fund[df_fund['基金代码'].isin(myfund_list)]
            return filtered_df
        filtered_df = filter_funds(df_fund, myfund_list)
        filtered_df =filtered_df[['基金代码', '基金简称', '日期', '单位净值', '日增长率', '近1周', '近1月', '近3月',
       '近6月', '近1年', '近2年', '近3年', '今年来', '成立来', '手续费']]
        st.dataframe(filtered_df, hide_index=True)
        st.info("AI自动生成市场总结")
        stock_market.summarize_market_data(filtered_df.drop(columns=['基金代码']))

    elif choose == '我的组合':
        st.header("待新增")
        myfund_list = ["040046","163701","007721","007380","006282","160416","162411","015016","519191","008763","013308","000043","000893","001668","000369","006105","016630","006105","016630","005613","164824","206011"]
        stock_market = StockMarket_fund()
        df_fund = stock_market.my_fund_list()

        def filter_funds(df_fund, myfund_list):
            filtered_df = df_fund[df_fund['基金代码'].isin(myfund_list)]
            return filtered_df
        filtered_df = filter_funds(df_fund, myfund_list)
        filtered_df =filtered_df[['基金代码', '基金简称', '日期', '单位净值', '日增长率', '近1周', '近1月', '近3月',
       '近6月', '近1年', '近2年', '近3年', '今年来', '成立来', '手续费']]
        st.dataframe(filtered_df, hide_index=True)
        st.info("AI自动生成市场总结")
        stock_market.summarize_market_data(filtered_df.drop(columns=['基金代码']))


    