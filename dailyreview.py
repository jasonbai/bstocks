def statement_func():
    import streamlit as st
    import pandas as pd
    

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

    # 大盘情况
    st.header("一、重要指数表现情况")
    st.dataframe(index_statistics, hide_index=True)
    # ETF 表现情况
    st.header("二、ETF 专题")
    st.write("以最近一周涨跌排序")
    st.markdown("### 1. 国内宽基跟踪")
    st.dataframe(etf_statistics1, hide_index=True)
    st.markdown("### 2. 全球主要ETF")
    st.dataframe(etf_statistics2, hide_index=True)
    st.markdown("### 3. 行业主要ETF")
    st.dataframe(etf_statistics3, hide_index=True)


    return