import re
import time
import datetime
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
# 设置页面布局为 "wide"
st.set_page_config(layout="wide")

# 添加自定义 CSS
def add_custom_css():
    custom_css = """
    <style>
    .main  {
        padding-right: 20rem;
    }
    """
    st.markdown(custom_css, unsafe_allow_html=True)


if __name__ == "__main__":
    add_custom_css()
    st.sidebar.markdown("# 尾灯白的量化分析")
    st.sidebar.markdown("作者：尾灯白（GitHub：jasonbai）")
    st.sidebar.markdown("项目介绍：[stockdashboard](https://github.com/jasonbai)")
    selection = st.sidebar.radio("当前支持的分析图表：",
                                 ["复盘日报","国内市场宽度", "海外市场","基金专题", "模型专题", "开发测试"])
    if  selection == "复盘日报":
        from dailyreview import statement_func
        statement_func()
    if selection == "国内市场宽度":
        from stockwidth import stock_market_analysis
        stock_market_analysis()
    if selection == "海外市场":
        from us_market import us_etf_analysis
        us_etf_analysis()
    elif selection == "基金专题":
        from test import test_func
        test_func()
    elif selection == "模型专题":
        from test import test_func
        test_func()
    elif selection == "开发测试":
        from test import test_func
        test_func()
