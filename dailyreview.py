def statement_func():
    import streamlit as st
    import pandas as pd
    from streamlit_option_menu import option_menu
    import os
    

    st.title("每日复盘")
    st.write("本站用于个人爱好量化分析的项目，数据有可能不准确，请谨慎使用。")

    # 读取 CSV 文件
    # 读取index_statistics
    index_statistics = pd.read_csv("data/index_statistics.csv", usecols=lambda x: x not in pd.read_csv("data/index_statistics.csv", nrows=0).columns[:1])
    index_statistics['指数代码'] = index_statistics['指数代码'].astype(str).str.zfill(6)
    # 读取etf_statistics1
    etf_statistics1 = pd.read_csv("data/etf_statistics1.csv", usecols=lambda x: x not in pd.read_csv("data/etf_statistics1.csv", nrows=0).columns[:1])
    etf_statistics1['ETF代码'] = etf_statistics1['ETF代码'].astype(str).str.zfill(6)
    # 读取etf_statistics2
    etf_statistics2 = pd.read_csv("data/etf_statistics2.csv", usecols=lambda x: x not in pd.read_csv("data/etf_statistics2.csv", nrows=0).columns[:1])
    etf_statistics2['ETF代码'] = etf_statistics2['ETF代码'].astype(str).str.zfill(6)
    # 读取etf_statistics3
    etf_statistics3 = pd.read_csv("data/etf_statistics3.csv", usecols=lambda x: x not in pd.read_csv("data/etf_statistics3.csv", nrows=0).columns[:1])
    etf_statistics3['ETF代码'] = etf_statistics3['ETF代码'].astype(str).str.zfill(6)

    

    # 人工智能自动生成市场总结
    def summarize_market_data(df):
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
                    ### 角色 
                    你是投资专家。根据用户提供的数据，简要总结市场情况，并给出基于数据特点的提醒和后续操作建议。
                    ## 技能 
                    ### 技能 1：市场总结 
                    - 分析用户提供的数据，识别市场的主要趋势和变化。
                    - 用简明的语言总结市场情况，确保普通投资者能理解。

                    ### 技能 2：投资提醒 
                    - 根据市场总结，给出在投资时需注意的要点和潜在风险。
                    - 提供具体的提醒，帮助投资者做出明智决定。

                    ### 技能 3：操作建议
                    - 根据数据特点，给出后续的投资操作建议。
                    - 确保建议有实际操作性，适合不同风险偏好的投资者。

                    ## 限制
                    - 只回答与市场总结、投资提醒和操作建议相关的问题。
                    - 内容使用markdown格式，标题只需要文本加粗即可。
                    - 遵循用户提供的数据和语言，请勿添加不相关的信息。
                    - 确保总结和建议简洁明了。
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
    # 导航栏
    choose = option_menu(None, ["大盘情况", "ETF专题", "全球主要ETF"], 
    icons=['house', 'list-task', "list-task"], 
    menu_icon="cast", default_index=0, orientation="horizontal")
    if choose == '大盘情况':
        # 大盘情况
        st.header("一、重要指数表现情况")
        st.dataframe(index_statistics, hide_index=True)
        
        if st.button("AI自动生成 分析报告"):
            summarize_market_data(index_statistics)
        else:
            st.info("点击按钮 AI助力")

    elif choose == 'ETF专题':
        st.header("二、ETF 专题")
        st.write("以最近一周涨跌排序")

        st.markdown("### 国内宽基跟踪")
        st.dataframe(etf_statistics1, hide_index=True)


        if st.button("AI自动生成 分析报告"):
            summarize_market_data(etf_statistics1)
        else:
            st.info("点击按钮 AI助力")

        st.markdown("### 行业主要ETF")
        st.dataframe(etf_statistics3, hide_index=True)
        st.info("AI自动生成市场总结")
        summarize_market_data(etf_statistics3)
    elif choose == '全球主要ETF':
        st.header("全球主要ETF")
        st.dataframe(etf_statistics2, hide_index=True)
        st.info("AI自动生成市场总结")
        summarize_market_data(etf_statistics2)

    return