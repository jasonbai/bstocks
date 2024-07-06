import re
import time
import datetime
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

# 添加自定义 CSS
def add_custom_css():
    custom_css = """
    <style>
    .main  {
        padding-right: 60rem;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


if __name__ == "__main__":
    add_custom_css()
    st.sidebar.markdown("# 尾灯白的量化分析")
    st.sidebar.markdown("作者：尾灯白（GitHub：jasonbai）")
    st.sidebar.markdown("项目介绍：[stockdashboard](https://github.com/jasonbai)")
    selection = st.sidebar.radio("当前支持的分析图表：",
                                 ["使用说明","国内市场", "海外市场", "模型专题", "基金专题"
                                  , "开发测试"
                                  ])
    if  selection == "使用说明":
        from statement import statement_func
        statement_func()
    if selection == "国内市场":
        from stock import stock_market_analysis
        stock_market_analysis()
    if selection == "海外市场":
        from test import test_func
        test_func()
    elif selection == "模型专题":
        from test import test_func
        test_func()
    elif selection == "基金专题":
        from test import test_func
        test_func()
    elif selection == "开发测试":
        from test import test_func
        test_func()