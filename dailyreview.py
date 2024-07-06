def statement_func():
    import streamlit as st
    import pandas as pd
    

    st.title("这里是说明")
    st.write("本站用于个人爱好量化分析的项目，数据有可能不准确，请谨慎使用。")

    # 读取 CSV 文件
    df = pd.read_csv("data/index_statistics.csv", usecols=lambda x: x not in pd.read_csv("data/index_statistics.csv", nrows=0).columns[:1])
    df['指数代码'] = df['指数代码'].astype(str).str.zfill(6)
    # 大盘情况
    st.header("一、重要指数表现情况")
    st.dataframe(df, hide_index=True)
    return