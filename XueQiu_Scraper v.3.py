# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 12:28:47 2021

@author: angus
"""
import streamlit as st
import pandas as pd
import xueqiu_formulas as xf
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
        elif statement == 'Top 10 Shareholders':   
            ### this is for gathering data on the top 10 largest shareholders            
            tables = pd.DataFrame()
            for ticker in tickers:
                if len(ticker) == 8:
                    tables0 = xf.infinite_query(ticker, "/detail#/SDGD",2)
                    ### Clean data
                    tables0 = tables0 [0:2]
                    table0 = pd.DataFrame()
                    for table in tables0:
                        table = table.iloc [:,0:4]
                        report = table.columns
                        report = report [2]
                        report = report [0]
                        table.columns = table.columns.droplevel()
                        abc = table ['持股数量']
                        abc2 = abc.str[-1]
                        abc = abc.str[:-1]   
                        abc2 = '一' + abc2
                        a = []
                        for numbers in abc2:
                            b = xf.convert (numbers)
                            a.append(b)
                        a = pd.DataFrame(a, columns = ['持股数量'])
                        abc = pd.DataFrame(abc)
                        abc = abc.astype(float)
                        df3 = a.mul(abc.values)
                        df3 = df3.round(0)
                        table ['持股数量'] = df3
                        table = table.T.reset_index(drop=False).T
                        table = table.T.reset_index(drop=False).T
                        table.iloc[0] = ticker
                        table = table.reset_index(drop = True)
                        table = table.T.reset_index(drop=False).T
                        table.iloc[0] = report
                        table0 = pd.concat([table0, table])
                    table0 = table0.reset_index(drop = True)
                    tables = pd.concat([tables,table0], ignore_index=False, axis = 1)
                else:
                    pass
        elif statement == 'Top 10 Traded Shareholders':
            tables = pd.DataFrame()
            ### this is for gathering data on the top 10 most selling or buying holders
            for ticker in tickers:
                if len(ticker) == 8:
                    tables0 = xf.infinite_query(ticker,"/detail#/LTGD", 2)
                    ### Clean data
                    tables0 = tables0 [0:2]
                    table0 = pd.DataFrame()
                    for table in tables0:
                        table = table.iloc [:,0:4]
                        report = table.columns
                        report = report [2]
                        report = report [0]
                        table.columns = table.columns.droplevel()
                        abc = table ['持股数量']
                        abc2 = abc.str[-1]
                        abc = abc.str[:-1]   
                        abc2 = '一' + abc2
                        a = []
                        for numbers in abc2:
                            b = xf.convert (numbers)
                            a.append(b)
                        a = pd.DataFrame(a, columns = ['持股数量'])
                        abc = pd.DataFrame(abc)
                        abc = abc.astype(float)
                        df3 = a.mul(abc.values)
                        df3 = df3.round(0)
                        table ['持股数量'] = df3
                        table = table.T.reset_index(drop=False).T
                        table = table.T.reset_index(drop=False).T
                        table.iloc[0] = ticker
                        table = table.reset_index(drop = True)
                        table = table.T.reset_index(drop=False).T
                        table.iloc[0] = report
                        table0 = pd.concat([table0, table])
                    table0 = table0.reset_index(drop = True)
                    tables = pd.concat([tables,table0], ignore_index=False, axis = 1)
                else:
                    pass
        elif statement == 'Income Statement':
            tables = pd.DataFrame()
            ### this is for gathering data on the income statement
            for ticker in tickers:
                table = xf.infinite_query(ticker,"/detail#/GSLRB", 1, freq = freq, statement = True)
                ### Clean data

                table = table.T.reset_index(drop=False).T
                # table = table.set_index(table.columns [0]) ### sets an index so that the data is merged rather than directly concated
                table = table.T.reset_index(drop=False).T
                table.iloc[0] = ticker
                tables = pd.concat([tables,table], ignore_index=False, axis = 1)
        elif statement == 'Balance Sheet':
            tables = pd.DataFrame()
            ### this is for gathering data on the balance sheet
            for ticker in tickers:
                table = xf.infinite_query(ticker,"/detail#/ZCFZB", 1, freq = freq, statement = True)
                ### Clean data
                table = table.T.reset_index(drop=False).T
                # table = table.set_index(table.columns [0]) ### sets an index so that the data is merged rather than directly concated
                table = table.T.reset_index(drop=False).T
                table.iloc[0] = ticker
                tables = pd.concat([tables,table], ignore_index=False, axis = 1)
        else:     
            tables = pd.DataFrame()
            ### this is for gathering data on the Cash Flow Statement
            for ticker in tickers:
                table = xf.infinite_query(ticker,"/detail#/XJLLB", 1, freq = freq, statement = True)
                ### Clean data
                table = table.T.reset_index(drop=False).T
                # table = table.set_index(table.columns [0]) ### sets an index so that the data is merged rather than directly concated
                table = table.T.reset_index(drop=False).T
                table.iloc[0] = ticker
                tables = pd.concat([tables,table], ignore_index=False, axis = 1)
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
            tables2 = pd.DataFrame()
            ### this is for gathering key stock and valuation
            for ticker2 in tickers2:
                table = xf.infinite_query(ticker2,"", .5, stock_data= True)
                ### clean data
                table = table [0]
                table = table.stack().reset_index()
                table = table.iloc[:,-1]
                table = table.str.split('：', expand = True)
                table = table.set_index(table.columns [0]) ### sets an index so that the data is merged rather than directly concated
                table = table.T.reset_index(drop=False).T
                table.iloc[0] = ticker2
                tables2 = pd.concat([tables2,table], ignore_index=False, axis = 1)
        else:
            tables2 = pd.DataFrame()
            ### this is for gathering company introduction
            for ticker2 in tickers2:
                table = xf.infinite_query(ticker2,"/detail#/GSJJ", .5)
                ### clean data
                table = table [0]
                table = table.iloc [:,0:2]
                table = table.set_index(table.columns [0]) ### sets an index so that the data is merged rather than directly concated
                table = table.T.reset_index(drop=False).T
                table.iloc[0] = ticker2
                tables2 = pd.concat([tables2,table], ignore_index=False, axis = 1)
        return tables2
    tables2 = download_various(tickers2, statement2) 
    tables2
    st.markdown(xf.get_table_download_link(tables2), unsafe_allow_html=True)