import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt




class StockMarket:

    def combined_plots(self, symbol, index_hdf5_path="data/index_data.h5", all_hdf5_path="data/index_all.h5"):
        """
        从HDF5文件中读取特定指数的数据并绘制折线图和市场宽度图
        :param symbol: 指数代码
        :param index_hdf5_path: 指数数据的HDF5文件路径
        :param all_hdf5_path: 所有数据的HDF5文件路径
        """
        # 处理符号名称，使其符合Python标识符的命名规则
        symbol_key = f"sym_{symbol}"

        # 从HDF5文件中读取指数数据
        with pd.HDFStore(index_hdf5_path) as store:
            index_df = store[symbol_key]
        index_df.index = index_df.index.astype(str)
        
        # 计算移动平均线
        index_df['MA20'] = index_df['收盘'].rolling(window=20).mean()
        index_df['MA50'] = index_df['收盘'].rolling(window=50).mean()
        index_df['MA200'] = index_df['收盘'].rolling(window=200).mean()

        # 从HDF5文件中读取所有数据
        with pd.HDFStore(all_hdf5_path) as store:
            all_df = store[symbol_key]
        # 计算每个股票的MA20、MA50和MA200
        all_df['MA20'] = all_df.groupby('股票代码')['收盘'].transform(lambda x: x.rolling(window=20).mean())
        all_df['MA50'] = all_df.groupby('股票代码')['收盘'].transform(lambda x: x.rolling(window=50).mean())
        all_df['MA200'] = all_df.groupby('股票代码')['收盘'].transform(lambda x: x.rolling(window=200).mean())

        # 选择日期
        options = index_df.index.tolist()
        date = st.select_slider("请选择想要查询的日期", options=options, value=options[-240], key=symbol)
        st.write("当前选择的起始日期是：", date)

        # 筛选数据
        pro_df = index_df.loc[date:, :].reset_index()
        all_df_filtered = all_df.loc[date:, :].reset_index()

        # 绘制指数折线图
        line = alt.Chart(pro_df).mark_line(color='red',size=3).encode(
            x='日期',
            y=alt.Y('收盘', scale=alt.Scale(domain=[pro_df['收盘'].min(), pro_df['收盘'].max()]))
        ).properties(
            width=1000,  # 设置图表宽度
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

        # 计算市场宽度
        def calculate_market_breadth(df, ma_column):
            df['高于均线'] = df['收盘'] > df[ma_column]
            market_breadth = df.groupby('日期')['高于均线'].mean() * 100
            return market_breadth

        market_breadth_ma20 = calculate_market_breadth(all_df_filtered, 'MA20')
        market_breadth_ma50 = calculate_market_breadth(all_df_filtered, 'MA50')
        market_breadth_ma200 = calculate_market_breadth(all_df_filtered, 'MA200')

        market_breadth_df = pd.DataFrame({
            '日期': market_breadth_ma20.index,
            'MA20': market_breadth_ma20.values,
            'MA50': market_breadth_ma50.values,
            'MA200': market_breadth_ma200.values
        })
        # 自定义颜色映射
        color_mapping = {
            'MA20': '#4793AF',
            'MA50': '#DD5746',
            'MA200': '#8B322C'
        }
        # 自定义线宽映射
        size_mapping = {
            'MA20': 1,
            'MA50': 3,
            'MA200': 5
        }

        # 绘制市场宽度图
        market_breadth_chart = alt.Chart(market_breadth_df).mark_line().encode(
            x='日期:T',
            y=alt.Y('value:Q', title='百分比'),
            color=alt.Color('key:N', scale=alt.Scale(domain=list(color_mapping.keys()), range=list(color_mapping.values())), title='移动平均线'),
            size=alt.Size('key:N', scale=alt.Scale(domain=list(size_mapping.keys()), range=list(size_mapping.values()))),
            tooltip=['日期:T', 'value:Q']
        ).transform_fold(
            ['MA20', 'MA50', 'MA200'],
            as_=['key', 'value']
        ).properties(
            width=1000,  # 设置图表宽度
            height=400  # 设置图表高度
        )
        # 增加一条横线在百分比15的位置
        rule1 = alt.Chart(pd.DataFrame({'y': [15]})).mark_rule(color='black').encode(
            y='y'
        )
        rule2 = alt.Chart(pd.DataFrame({'y': [85]})).mark_rule(color='black').encode(
            y='y'
        )

        market_breadth_chart += rule1
        market_breadth_chart += rule2


        # 将两个图表上下排列
        combined_chart = (line + ma20_line + ma50_line + ma200_line) & market_breadth_chart
        st.altair_chart(combined_chart, use_container_width=True)
    


def stock_market_analysis():
    stock_market = StockMarket()
    st.title('上证50走势及市场宽度')
    stock_market.combined_plots("000016")
    st.title('沪深300走势及市场宽度')
    stock_market.combined_plots("000300")

    st.title('创业板走势及市场宽度')
    stock_market.combined_plots("399006")

    st.title('创业50走势及市场宽度')
    stock_market.combined_plots("399673")

    st.title('中证500走势及市场宽度')
    stock_market.combined_plots("000905")