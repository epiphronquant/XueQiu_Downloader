# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 12:28:47 2021

@author: angus
"""
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
import base64
from io import BytesIO
### configure page
st.set_page_config(layout="wide")
st.title('XueQiu Downloader')
def infinite_query(ticker, xq_exten, sleep_time, freq):### function that refreshes page until it can gather the needed data
    driver = webdriver.Chrome(chrome_options=chrome_options) ### use google chrome
    driver.get("https://xueqiu.com/snowman/S/" + ticker + xq_exten) ### go to website
    # time.sleep(sleep_time) ### gives time for page to load. This is a xueqiu specific solution

    if freq == '全部':
        pass
    else:
        path = "//span[contains(@class,'btn') and contains(text(), '"+ freq +"')]"
        button= driver.find_element_by_xpath(path)### selects button 
        button.click()
    time.sleep(sleep_time) ### gives time for page to load. This is a xueqiu specific solution
    html = driver.page_source ## gather and read HTML    
    table = None
    while table is None:
        try: 
            table = pd.read_html(html)
        except ValueError:
            driver.refresh()
            time.sleep(4)
            html = driver.page_source## gather and read HTML
            try: 
                table = pd.read_html(html)
            except ValueError:
                table = None
    driver.delete_all_cookies()
    driver.quit()   
    return table
def convert(chinese): ### converts Chinese numbers to int
    numbers = {'零':0, '一':1, '二':2, '三':3, '四':4, '五':5, '六':6, '七':7, '八':8, '九':9, '壹':1, '贰':2, '叁':3, '肆':4, '伍':5, '陆':6, '柒':7, '捌':8, '玖':9, '两':2, '廿':20, '卅':30, '卌':40, '虚':50, '圆':60, '近':70, '枯':80, '无':90}
    units = {'个':1, '十':10, '百':100, '千':1000, '万':10000, '亿':100000000, '拾':10, '佰':100, '仟':1000}
    number, pureNumber = 0, True
    for i in range(len(chinese)):
        if chinese[i] in units or chinese[i] in ['廿', '卅', '卌', '虚', '圆', '近', '枯', '无']:
            pureNumber = False
            break
        if chinese[i] in numbers:
            number = number * 10 + numbers[chinese[i]]
    if pureNumber:
        return number
    number = 0
    for i in range(len(chinese)):
        if chinese[i] in numbers or chinese[i] == '十' and (i == 0 or  chinese[i - 1] not in numbers or chinese[i - 1] == '零'):
            base, currentUnit = 10 if chinese[i] == '十' and (i == 0 or chinese[i] == '十' and chinese[i - 1] not in numbers or chinese[i - 1] == '零') else numbers[chinese[i]], '个'
            for j in range(i + 1, len(chinese)):
                if chinese[j] in units:
                    if units[chinese[j]] >= units[currentUnit]:
                        base, currentUnit = base * units[chinese[j]], chinese[j]
            number = number + base
    return number
def to_excel(df): ### converts a dataframe to excel
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', index = False, header = False)
        writer.save()
        processed_data = output.getvalue()
        return processed_data
def get_table_download_link(df): ### Hack that allows you to download the dataframe
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="extract.xlsx">Download xlsx</a>' # decode b'abc' => abc    
### Options that allow chrome to run in streamlit
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

column_1, column_2 = st.beta_columns(2) ### Divides page into 2 columns
with column_1:### ### Download Statements chart
    st.header ('Download Statements')
    tickers = st.text_input("Type in Chinese ticker/tickers in the format 12345, SH123456, SZ123456 for HKEX, SHSE and SZSE stocks respectively. Shareholder information only exists for stocks listed in Mainland China.")
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
    st.write('You selected:', statement)
    @st.cache
    def download(tickers, statement, freq):
        if tickers == ['']:### Makes function not run if there is no input
            tables = pd.DataFrame()
        elif statement == 'Top 10 Shareholders':   
            ### this is for gathering data on the top 10 largest shareholders
            tables = pd.DataFrame()
            for ticker in tickers:
                table = infinite_query(ticker, "/detail#/SDGD",2, '全部')
                ### Clean data
                table = table [0]
                table = table.iloc [:,0:4]
                table.columns = table.columns.droplevel()
                abc = table ['持股数量']
                abc2 = abc.str[-1]
                abc = abc.str[:-1]   
                abc2 = '一' + abc2
                a = []
                for numbers in abc2:
                    b = convert (numbers)
                    a.append(b)
                a = pd.DataFrame(a, columns = ['持股数量'])
                abc = pd.DataFrame(abc)
                abc = abc.astype(float)
                df3 = a.mul(abc.values)
                table ['持股数量'] = df3
                table = table.T.reset_index(drop=False).T
                table = table.T.reset_index(drop=False).T
                table.iloc[0] = ticker
                tables = pd.concat([tables,table], ignore_index=False, axis = 1)
        elif statement == 'Top 10 Traded Shareholders':
            tables = pd.DataFrame()
            ### this is for gathering data on the top 10 most selling or buying holders
            for ticker in tickers:
                table = infinite_query(ticker,"/detail#/LTGD", 2, '全部')
                ### Clean data
                table = table [0]
                table = table.iloc [:,0:4]
                table.columns = table.columns.droplevel()
                abc = table ['持股数量']
                abc2 = abc.str[-1]
                abc = abc.str[:-1]   
                abc2 = '一' + abc2
                a = []
                for numbers in abc2:
                    b = convert (numbers)
                    a.append(b)
                a = pd.DataFrame(a, columns = ['持股数量'])
                abc = pd.DataFrame(abc)
                abc = abc.astype(float)
                df3 = a.mul(abc.values)
                table ['持股数量'] = df3
                table = table.T.reset_index(drop=False).T
                table = table.T.reset_index(drop=False).T
                table.iloc[0] = ticker
                tables = pd.concat([tables,table], ignore_index=False, axis = 1)
        elif statement == 'Income Statement':
            tables = pd.DataFrame()
            ### this is for gathering data on the income statement
            for ticker in tickers:
                table = infinite_query(ticker,"/detail#/GSLRB", 1, freq)
                ### Clean data
                table = table [0]
                table = table.iloc[:,1:]
                table = table.T.reset_index(drop=False).T
                table = table.T.reset_index(drop=False).T
                table.iloc[0] = ticker
                tables = pd.concat([tables,table], ignore_index=False, axis = 1)
        elif statement == 'Balance Sheet':
            tables = pd.DataFrame()
            ### this is for gathering data on the balance sheet
            for ticker in tickers:
                table = infinite_query(ticker,"/detail#/ZCFZB", 1, freq)
                ### Clean data
                table = table [0]
                table = table.iloc[:,1:]
                table = table.T.reset_index(drop=False).T
                table = table.T.reset_index(drop=False).T
                table.iloc[0] = ticker
                tables = pd.concat([tables,table], ignore_index=False, axis = 1)
        else:     
            tables = pd.DataFrame()
            ### this is for gathering data on the Cash Flow Statement
            for ticker in tickers:
                table = infinite_query(ticker,"/detail#/XJLLB", 1, freq)
                ### Clean data
                table = table [0]
                table = table.iloc[:,1:]
                table = table.T.reset_index(drop=False).T
                table = table.T.reset_index(drop=False).T
                table.iloc[0] = ticker
                tables = pd.concat([tables,table], ignore_index=False, axis = 1)
        return tables
    tables = download(tickers, statement, freq)
    e = tables.astype(str) 
    st.dataframe(e)
    st.markdown(get_table_download_link(tables), unsafe_allow_html=True)
with column_2:##### Download various information chart
    st.header ('Download Various Other Information')
    tickers2 = st.text_input("Type in Chinese tickers but NOT HKEX tickers for stock data")
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
                table = infinite_query(ticker2,"", .5, '全部')
                ### clean data
                table = table [0]
                table = table.stack().reset_index()
                table = table.iloc[:,-1]
                table = table.str.split('：', expand = True)
                table = table.T.reset_index(drop=False).T
                table.iloc[0] = ticker2
                tables2 = pd.concat([tables2,table], ignore_index=False, axis = 1)
        else:
            tables2 = pd.DataFrame()
            ### this is for gathering company introduction
            for ticker2 in tickers2:
                table = infinite_query(ticker2,"/detail#/GSJJ", .5, '全部')
                ### clean data
                table = table [0]
                table = table.iloc [:,0:2]
                table = table.T.reset_index(drop=False).T
                table.iloc[0] = ticker2
                tables2 = pd.concat([tables2,table], ignore_index=False, axis = 1)
        return tables2
    tables2 = download_various(tickers2, statement2) 
    tables2
    st.markdown(get_table_download_link(tables2), unsafe_allow_html=True)