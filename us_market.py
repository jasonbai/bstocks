import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import os

class StockMarket_us:

    def combined_plots(self, symbol, index_hdf5_path="data/us_etf.h5"):

        # 处理符号名称，使其符合Python标识符的命名规则
        symbol_key = f"sym_{symbol.replace('.', '_')}"

        # 从HDF5文件中读取指数数据
        with pd.HDFStore(index_hdf5_path) as store:
            index_df = store[symbol_key]
        index_df.index = index_df.index.astype(str)
        
        # 计算移动平均线
        index_df['MA20'] = index_df['收盘'].rolling(window=20).mean()
        index_df['MA50'] = index_df['收盘'].rolling(window=50).mean()
        index_df['MA200'] = index_df['收盘'].rolling(window=200).mean()


        # 选择日期
        options = index_df.index.tolist()
        date = st.select_slider("请选择想要查询的日期", options=options, value=options[-240], key=symbol)
        st.write("当前选择的起始日期是：", date)

        # 筛选数据
        pro_df = index_df.loc[date:, :].reset_index()

        # 绘制指数折线图
        line = alt.Chart(pro_df).mark_line(color='red',size=3).encode(
            x='日期',
            y=alt.Y('收盘', scale=alt.Scale(domain=[pro_df['收盘'].min(), pro_df['收盘'].max()]))
        ).properties(
            width=1200,  # 设置图表宽度
            height=400  # 设置图表高度
        )
        ma20_line = alt.Chart(pro_df).mark_line(color='#4793AF').encode(
            x='日期',
            y=alt.Y('MA20', scale=alt.Scale(domain=[pro_df['收盘'].min(), pro_df['收盘'].max()]))
        )
        ma50_line = alt.Chart(pro_df).mark_line(color='#DD5746').encode(
            x='日期',
            y=alt.Y('MA50', scale=alt.Scale(domain=[pro_df['收盘'].min(), pro_df['收盘'].max()]))
        )
        ma200_line = alt.Chart(pro_df).mark_line(color='#8B322C').encode(
            x='日期',
            y=alt.Y('MA200', scale=alt.Scale(domain=[pro_df['收盘'].min(), pro_df['收盘'].max()]))
        )
        index_chart = alt.layer(line, ma20_line, ma50_line, ma200_line).resolve_scale(y='shared')

        combined_chart = (line + ma20_line + ma50_line + ma200_line) 
        st.altair_chart(combined_chart, use_container_width=True)

    # 人工智能自动分析
    def summarize_market_data(self, symbol, index_hdf5_path="data/us_etf.h5"):
        from openai import OpenAI   
        from dotenv import load_dotenv
        # 将DataFrame转换为字符串格式
        # 处理符号名称，使其符合Python标识符的命名规则
        symbol_key = f"sym_{symbol.replace('.', '_')}"

        # 从HDF5文件中读取指数数据
        with pd.HDFStore(index_hdf5_path) as store:
            index_df = store[symbol_key]
        index_df.index = index_df.index.astype(str)
        
        # 计算移动平均线
        index_df['MA20'] = index_df['收盘'].rolling(window=20).mean()
        index_df['MA50'] = index_df['收盘'].rolling(window=50).mean()
        index_df['MA200'] = index_df['收盘'].rolling(window=200).mean()

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
                    你是投资专家。根据用户提供的数据，简要分析该ETF最近240个交易日的情况，特别关注当前价格的位置在整体里的情况，同时结合MA20，MA50，MA200，三个均线指标以及成交量分析近期变化，确认后续是否买入卖出或持有，并给出基于数据特点的提醒和后续操作建议，特别要关注最近一个月的表现情况。
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
                    - 结合成交量来分析20日均线、50日均线和200日均线的交易理论。成交量是衡量市场活跃度和趋势强度的关键指标，与均线结合使用时，根据用户提供的数据提供更全面的市场分析。以下是一些结合成交量的交易理论：

                        1. **成交量确认趋势**：
                        - **上涨趋势**：当股价位于20日、50日或200日均线之上，并且成交量逐渐放大，表明上涨趋势得到成交量的支持，趋势可能更加可靠。
                        - **下跌趋势**：当股价位于20日、50日或200日均线之下，并且成交量逐渐放大，表明下跌趋势得到成交量的支持，趋势可能更加可靠。

                        2. **成交量确认突破**：
                        - **均线突破**：当股价突破20日、50日或200日均线时，如果伴随着成交量的显著增加，突破信号的可靠性更高。例如，股价上穿200日均线且成交量放大，可能预示着长期上涨趋势的开始。
                        - **均线回踩**：在股价回踩均线时，如果成交量减少，可能表明卖压减弱，股价有可能再次上涨。

                        3. **成交量与均线交叉**：
                        - **金叉**：当20日均线上穿50日或200日均线时，如果伴随着成交量的增加，金叉信号的强度和可靠性更高。
                        - **死叉**：当20日均线下穿50日或200日均线时，如果伴随着成交量的增加，死叉信号的强度和可靠性更高。

                        4. **成交量与均线支撑/阻力**：
                        - **支撑**：当股价在下跌过程中遇到20日、50日或200日均线并反弹时，如果成交量增加，支撑的有效性更高。
                        - **阻力**：当股价在上涨过程中遇到20日、50日或200日均线并回落时，如果成交量增加，阻力的有效性更高。

                        **注意事项**：
                        - **成交量的一致性**：在分析成交量时，应关注其与价格变动的一致性。例如，价格上涨时成交量应增加，价格下跌时成交量应减少。
                        - **成交量的高低**：成交量的绝对值也很重要。高成交量通常表明市场参与度高，趋势可能更持久；低成交量可能表明市场参与度低，趋势可能较弱。

                        结合成交量和均线进行交易决策时，应综合考虑多个因素，包括市场环境、其他技术指标和基本面分析，以制定更全面和稳健的交易策略。

                    ### 技能 2：投资提醒 
                    - 根据市场总结，给出在投资时需注意的要点和潜在风险。
                    - 提供具体的提醒，帮助投资者做出明智决定。

                    ### 技能 3：操作建议
                    - 根据均线理论和结合成交量情况，给出后续的投资操作建议。
                    - 确保建议有实际操作性，适合不同风险偏好的投资者。

                    ## 限制
                    - 只回答与市场总结、投资提醒和操作建议相关的问题。
                    - 内容使用markdown格式，标题只需要文本加粗即可。
                    - 遵循用户提供的数据和语言，请勿添加不相关的信息。
                    - 确保总结和建议简洁明了。
                    '''
                    },
            {"role": "user", "content": f"这是名为{symbol} etf情况，最近240个交易日数据如下:\n\n{df_str}"}
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



def us_etf_analysis():
    symbols = { "105.QQQ":"NASDAQ-100指数",
                "107.SPY":"标普500指数",
               "107.EWJ":"日本ETF",
               "107.INDA":"印度ETF",
               "107.VNM":"越南ETF",
               "107.EWQ":"法国ETF",
                "107.EWG":"德国ETF",
               "107.RSP":"标普500 等权重",
               "107.IWY":"罗素领先200成长指数",
               "107.MOAT":"晨星宽护城河指数",
               "105.PFF":"美国优先股，美国市场上规模最大流动性最好的优先股前500",
               "107.VNQ":"房地产信托指数ETF",               
            }
    stock_market = StockMarket_us()

    count = 0
    for key, value in symbols.items():
        cleaned_key = key.split('.')[1]
        st.title(f"{cleaned_key} - {value}")
        stock_market.combined_plots(key)
        if count < 1:
            st.info("AI自动生成市场总结")
            stock_market.summarize_market_data(key)
            count += 3
