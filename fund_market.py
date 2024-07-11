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
    
    
    def fund_plots(self,symbol, hdf5_path="data/fund_human.h5"):
        import altair as alt

        # 处理符号名称，使其符合Python标识符的命名规则
        symbol_key = f"sym_{symbol}"

        # 从HDF5文件中读取指数数据
        with pd.HDFStore(hdf5_path) as store:
            index_df = store[symbol_key]
        index_df.index = index_df.index.astype(str)
        
        # 计算移动平均线
        index_df['MA20'] = index_df['单位净值'].rolling(window=20).mean()
        index_df['MA50'] = index_df['单位净值'].rolling(window=50).mean()
        index_df['MA200'] = index_df['单位净值'].rolling(window=200).mean()


        # 选择日期
        options = index_df.index.tolist()
        date = st.select_slider("请选择想要查询的日期", options=options, value=options[-240], key=symbol)
        st.write("当前选择的起始日期是：", date)

        # 筛选数据
        pro_df = index_df.loc[date:, :].reset_index()

        # 绘制指数折线图
        line = alt.Chart(pro_df).mark_line(color='red',size=3).encode(
            x='净值日期',
            y=alt.Y('单位净值', scale=alt.Scale(domain=[pro_df['单位净值'].min(), pro_df['单位净值'].max()]))
        ).properties(
            width=1200,  # 设置图表宽度
            height=400  # 设置图表高度
        )
        ma20_line = alt.Chart(pro_df).mark_line(color='#4793AF').encode(
            x='净值日期',
            y=alt.Y('MA20', scale=alt.Scale(domain=[pro_df['单位净值'].min(), pro_df['单位净值'].max()]))
        )
        ma50_line = alt.Chart(pro_df).mark_line(color='#DD5746').encode(
            x='净值日期',
            y=alt.Y('MA50', scale=alt.Scale(domain=[pro_df['单位净值'].min(), pro_df['单位净值'].max()]))
        )
        ma200_line = alt.Chart(pro_df).mark_line(color='#8B322C').encode(
            x='净值日期',
            y=alt.Y('MA200', scale=alt.Scale(domain=[pro_df['单位净值'].min(), pro_df['单位净值'].max()]))
        )
        index_chart = alt.layer(line, ma20_line, ma50_line, ma200_line).resolve_scale(y='shared')

        

        # 将两个图表上下排列
        combined_chart = (line + ma20_line + ma50_line + ma200_line) 
        st.altair_chart(combined_chart, use_container_width=True)
    
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
                    - 简要总结数据情况，组合中持仓有的数量，今年来上涨的的数量，下跌的数量，近3月上涨的的数量，下跌的数量，同时特别分析在'近1周', '近1月', '近3月','今年来'的情况，结合日增长率，观察是否有可能反转，不用一一列举，说明整个组合的情况及其中特殊的情况即可。

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

    def summarize_fund_data(self, symbol, hdf5_path="data/fund_human.h5"):
            from openai import OpenAI   
            from dotenv import load_dotenv
            # 将DataFrame转换为字符串格式
            # 处理符号名称，使其符合Python标识符的命名规则
            # 处理符号名称，使其符合Python标识符的命名规则
            symbol_key = f"sym_{symbol}"

            # 从HDF5文件中读取指数数据
            with pd.HDFStore(hdf5_path) as store:
                index_df = store[symbol_key]
            index_df.index = index_df.index.astype(str)
            
            # 计算移动平均线
            index_df['MA20'] = index_df['单位净值'].rolling(window=20).mean()
            index_df['MA50'] = index_df['单位净值'].rolling(window=50).mean()
            index_df['MA200'] = index_df['单位净值'].rolling(window=200).mean()

            # 筛选数据
            pro_df = index_df.iloc[-240:].reset_index()
            df_str = pro_df.to_string()
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
                        ### 角色 
                        你是基金投资专家。根据用户提供的基金历史净值数据，简要分析该基金最近240个净值走势的情况，特别关注当前价格的位置在整体里的情况，同时结合MA20，MA50，MA200，三个均线指标近期变化，确认后续是否买入卖出或持有，并给出基于数据特点的提醒和后续操作建议，特别要关注最近一个月的表现情况。
                        ## 技能 
                        ### 技能 1：市场总结 
                        - 分析用户提供的数据，识别股票的主要趋势和变化。
                        - 用简明的语言总结市场情况，确保普通投资者能理解。
                        - 根据均线理论：20日均线、50日均线和200日均线是技术分析中常用的移动平均线指标，它们分别代表不同时间周期的市场平均成本，帮助投资者判断市场趋势和交易时机。以下是这些均线的一些常见交易理论：

                            20日均线（短期趋势）：

                            短期趋势判断：20日均线通常用于判断短期市场的趋势。当股价位于20日均线之上时，表明短期市场趋势偏多；反之，则偏空。

                            交易信号：股价上穿20日均线可能被视为买入信号，而下穿则可能被视为卖出信号。

                            50日均线（中期趋势）：

                            中期趋势判断：50日均线用于判断中期市场的趋势。股价位于50日均线之上，通常表明中期市场趋势偏多；反之，则偏空。

                            交易信号：股价上穿50日均线可能被视为较强的买入信号，而下穿则可能被视为较强的卖出信号。

                            200日均线（长期趋势）：

                            长期趋势判断：200日均线用于判断长期市场的趋势。股价位于200日均线之上，通常表明长期市场趋势偏多；反之，则偏空。

                            交易信号：股价上穿200日均线可能被视为非常强的买入信号，而下穿则可能被视为非常强的卖出信号。

                            综合应用：

                            金叉与死叉：当短期均线（如20日均线）上穿长期均线（如50日或200日均线）时，形成“金叉”，通常被视为买入信号；反之，短期均线下穿长期均线形成“死叉”，通常被视为卖出信号。

                            支撑与阻力：均线也可以作为支撑和阻力的参考。例如，股价在下跌过程中遇到200日均线可能会反弹，而在上涨过程中遇到200日均线可能会回落。

                            注意事项：

                            市场环境：不同的市场环境（如牛市、熊市、震荡市）对均线的反应可能不同，因此需要结合其他技术指标和市场信息综合判断。

                            风险管理：均线交易理论并非绝对准确，实际操作中应结合风险管理策略，如设置止损点，以控制潜在的亏损。

                            这些交易理论在实际应用中需要结合个人的交易策略和市场分析，灵活运用。
                        

                        ### 技能 2：投资提醒 
                        - 根据市场总结，给出在投资时需注意的要点和潜在风险。
                        - 提供具体的提醒，帮助投资者做出明智决定。

                        ### 技能 3：操作建议
                        - 根据均线理论及自身走势，给出后续的投资操作建议。
                        - 确保建议有实际操作性，适合不同风险偏好的投资者。

                        ## 限制
                        - 只回答与市场总结、投资提醒和操作建议相关的问题。
                        - 内容使用markdown格式，标题只需要文本加粗即可。
                        - 遵循用户提供的数据和语言，请勿添加不相关的信息。
                        - 确保总结和建议简洁明了。
                        '''
                        },
                {"role": "user", "content": f"这是名为{symbol} 基金的净值情况，最近240日净值数据如下:\n\n{df_str}"}
            ]
                # 发送请求
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=True,
                temperature=0.7,
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

    choose = option_menu(None, ["公募基金排行", "我关注的基金", "我的组合","单个基金分析"], 
    icons=['house', 'list-task', "list-task", "list-task"], 
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
        myfund_list = ["008114","006228","161907","013308","163406","220670","001593","163407","008763","040046","003547","000369","006048","164824","007994","015016","000893","007721","010349","005996","019858","164701","006282","007380","160416","162411","000043","001668","006105","016630","009617","007769","005613","206011"]
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
        st.header("全球视野相信人类组合")
        myfund_list = ["040046","164701","007721","007380","006282","160416","162411","015016","008763","013308","000043","000893","001668","000369","006105","016630","006105","016630","005613","164824","206011"]
        stock_market = StockMarket_fund()
        df_fund = stock_market.my_fund_list()

        def filter_funds(df_fund, myfund_list):
            filtered_df = df_fund[df_fund['基金代码'].isin(myfund_list)]
            return filtered_df
        filtered_df = filter_funds(df_fund, myfund_list)
        filtered_df =filtered_df[['基金代码', '基金简称', '日期', '单位净值', '日增长率', '近1周', '近1月', '近3月',
       '近6月', '近1年', '近2年', '近3年', '今年来', '成立来', '手续费']]
        st.dataframe(filtered_df, hide_index=True)
        if st.button("AI自动生成 分析报告"):
            stock_market.summarize_market_data(filtered_df.drop(columns=['基金代码']))
        else:
            st.info("点击按钮 AI助力")


    elif choose == '单个基金分析':
        stock_market = StockMarket_fund()
        st.markdown("### 重点基金净值走势")
        myfund_dic ={"016630":"中证1000",
                     "040046":"纳斯达克100",
                    "164701":"黄金贵金属",
                    "007380":"上证50",
                    "006282":"摩根欧洲动力策略股票",
                    "160416":"华安标普全球石油指数",
                    "162411":"华宝标普油气上游股票",
                    "015016":"华安德国（DAX）联接C",
                    "000369":"广发全球医疗保健",
                    "001668":"汇添富全球移动互联网",
                    "000043":"嘉实美国成长股",
                    "013308":"易方达恒生科技ETF联接",
                    "006105":"宏利印度股票",
                    "000893":"工银创新动力股票"
                    }
        for key, value in myfund_dic.items():
            st.title(f"{key} - {value}")
            st.info("净值走势")
            stock_market.fund_plots(key)
            if st.button("AI自动生成-分析报告", key=f"button_{key}"):
                stock_market.summarize_fund_data(key)
            else:
                st.info("点击按钮 - AI助力")



    