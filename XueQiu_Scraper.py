# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 12:28:47 2021

@author: angus
"""
import streamlit as st
import pandas as pd
import xueqiu_formulas as xf
from time import sleep
### configure page
st.set_page_config(layout="wide")
st.title('XueQiu Downloader')

column_1, column_2 = st.beta_columns(2) ### Divides page into 2 columns
with column_1:### ### Download Statements chart
    st.header ('Download Statements')
    tickers = st.text_input("Type in ticker/tickers in the format 01234, SH123456, SZ123456, ABCD for HKEX, SHSE, SZSE and American stocks respectively. Shareholder information only exists for stocks listed in Mainland China.")
    tickers = tickers.split(',')
    tickers = map(str.strip, tickers)
    tickers = list(tickers)
    statement = st.selectbox(
              'What would you like to download?',
              ('Income Statement','Balance Sheet', 'Cash Flow', 'Top 10 Shareholders', 'Top 10 Traded Shareholders'))
    st.write('You selected:', statement)
    freq = st.selectbox(
      'What frequency would the data be? This is irrelevant for shareholder info',
      ('全部','年报', '中报', '一季报', '三季报'))
    st.write('You selected:', freq)
    @st.cache
    def download(tickers, statement, freq):
        if tickers == ['']:### Makes function not run if there is no input
            tables = pd.DataFrame()
        elif statement == 'Top 10 Shareholders': ### this is for gathering data on the top 10 largest shareholders            
            tickers =[x for x in tickers if len(x)==8]
            tables = []
            for ticker in tickers:
                xf.infinite_query_threaded_shareholder(ticker, tables, "/detail#/SDGD") ### this downloads the data but completes in different order
            while len(tables) < len(tickers): ### this must be modified for shareholder data
                sleep(0.01)
            tables = xf.org_table(tickers, tables, row = 1) ### convert list of tables to dataframe in orderly fashion
            
        elif statement == 'Top 10 Traded Shareholders':
            tickers =[x for x in tickers if len(x)==8]
            tables = []
            for ticker in tickers:
                xf.infinite_query_threaded_shareholder(ticker, tables, "/detail#/LTGD") ### this downloads the data but completes in different order
            while len(tables) < len(tickers): ### this must be modified for shareholder data
                sleep(0.01)
            tables = xf.org_table(tickers, tables, row = 1) ### convert list of tables to dataframe
            
        elif statement == 'Income Statement':
            ### this is for gathering data on the income statement
            tables = []
            for ticker in tickers:
                xf.infinite_query_threaded_statements(ticker, tables, "/detail#/GSLRB", freq = freq) ### this downloads the data but completes in different order
            while len(tables) < len(tickers):
                sleep(0.01)
            tables = xf.org_table(tickers, tables) ### convert list of tables to dataframe
            
        elif statement == 'Balance Sheet':
            tables = []
            for ticker in tickers:
                xf.infinite_query_threaded_statements(ticker, tables, "/detail#/ZCFZB", freq = freq) ### this downloads the data but completes in different order
            while len(tables) < len(tickers):
                sleep(0.01)
            tables = xf.org_table(tickers, tables) ### convert list of tables to dataframe
        
        else:     
            tables = []
            for ticker in tickers:
                xf.infinite_query_threaded_statements(ticker, tables, "/detail#/XJLLB", freq = freq) ### this downloads the data but completes in different order
            while len(tables) < len(tickers):
                sleep(0.01)
            tables = xf.org_table(tickers, tables) ### convert list of tables to dataframe
        return tables
    tables = download(tickers, statement, freq)
    e = tables.astype(str) 
    st.dataframe(e)
    st.markdown(xf.get_table_download_link(tables), unsafe_allow_html=True)

with column_2:##### Download various information chart
    st.header ('Download Various Other Information')
    tickers2 = st.text_input("Type in ticker/tickers")
    tickers2 = tickers2.split(',') 
    tickers2 = map(str.strip, tickers2)
    tickers2 = list(tickers2)
    statement2 = st.selectbox(
             'What would you like to download?',
             ('Stock Data', 'Company Data'))
    st.write('You selected:', statement2)
    @st.cache
    def download_various (tickers2, statement2):
        if tickers2 == ['']:### make sure the function doesn't run if there is no data inputted
            tables2 = pd.DataFrame()
        elif statement2 == 'Stock Data':
            tables2 = []
            for ticker2 in tickers2:
                xf.infinite_query_threaded_stockdata(ticker2, tables2) ### this downloads the data but completes in different order
            while len(tables2) < len(tickers2):
                sleep(0.01)
            tables2 = xf.org_table(tickers2, tables2) ### convert list of tables to dataframe
        else:
            ### this is for gathering company introduction
            tables2 = []
            for ticker2 in tickers2:
                xf.infinite_query_threaded_compintro(ticker2, tables2) ### this downloads the data but completes in different order
            while len(tables2) < len(tickers2):
                sleep(0.01)
            tables2 = xf.org_table(tickers2, tables2) ### convert list of tables to dataframe
        return tables2

    tables2 = download_various(tickers2, statement2) 
    tables2
    st.markdown(xf.get_table_download_link(tables2), unsafe_allow_html=True)
