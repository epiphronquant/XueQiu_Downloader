# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 12:28:47 2021

@author: angus
"""

import streamlit as st
from selenium import webdriver
import pandas as pd
import time

st.set_page_config(layout="wide")
st.title('Xueqiu Downloader')

def infinite_query(html):
    table = None
    while table is None:
        try: 
            table = pd.read_html(html)
        except ValueError:
            driver.refresh()
            time.sleep(4)
            ## gather and read HTML
            html = driver.page_source
            try: 
                table = pd.read_html(html)
            except ValueError:
                table = None
    return table
def convert(chinese):
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

column_1, column_2 = st.beta_columns(2) ### Divides page into 2 columns

with column_1:### ### Download Statements chart
    st.header ('Download Statements')
    tickers = st.text_input("Type in Chinese tickers in the format 12345, SH123456, SZ123456 for HKEX, SHSE and SZSE stocks respectively")
    tickers = tickers.split(',')
    tickers = map(str.strip, tickers)
    tickers = list(tickers)
    
    # tickers = ['SH603392', 'SZ000858', 'SH601318','SZ000422']
    
    
    #### This is for gathering data on the top 10 largest shareholders
    statement = st.selectbox(
             'What would you like to download?',
             ('Income Statement','Balance Sheet', 'Cash Flow', 'Top 10 Shareholders', 'Top 10 Traded Shareholders'))
    st.write('You selected:', statement)

    if tickers == ['']:
        tables = pd.DataFrame()
    elif statement == 'Top 10 Shareholders':   
        tables = pd.DataFrame()
        for ticker in tickers:
            driver = webdriver.Chrome() ### use google chrome
            driver.get("https://xueqiu.com/snowman/S/" + ticker + "/detail#/SDGD") ### go to website
            time.sleep(2) ### gives time for page to load. This is a xueqiu specific solution
            html = driver.page_source ## gather and read HTML    
            ###refresh web page until chart shows up
            table = infinite_query(html)
            ### Clean data
            table = table [0]
            table = table.iloc [:,0:3]
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
            driver.delete_all_cookies()
            driver.quit()

        
    elif statement == 'Top 10 Traded Shareholders':
        tables = pd.DataFrame()
        ### this is for gathering data on the top 10 most selling or buying holders
        for ticker in tickers:
            driver = webdriver.Chrome() ### use google chrome
            driver.get("https://xueqiu.com/snowman/S/" + ticker + "/detail#/LTGD") ### go to website
            time.sleep(2) ### gives time for page to load. This is a xueqiu specific solution
            html = driver.page_source ## gather and read HTML    
            ###refresh web page until chart shows up
            table = infinite_query(html)
            ### Clean data
            table = table [0]
            table = table.iloc [:,0:3]
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
            driver.delete_all_cookies()
            driver.quit()
    elif statement == 'Income Statement':
        tables = pd.DataFrame()
        ### this is for gathering data on the income statement
        for ticker in tickers:
            driver = webdriver.Chrome() ### use google chrome
            driver.get("https://xueqiu.com/snowman/S/" + ticker + "/detail#/GSLRB") ### go to website
            time.sleep(1) ### gives time for page to load. This is a xueqiu specific solution
            html = driver.page_source ## gather and read HTML    
            ###refresh web page until chart shows up
            table = infinite_query(html)
            ### Clean data
            table = table [0]
            table = table.iloc[:,1:]
            table = table.T.reset_index(drop=False).T
            table = table.T.reset_index(drop=False).T
            table.iloc[0] = ticker
            tables = pd.concat([tables,table], ignore_index=False, axis = 1)
            driver.delete_all_cookies()
            driver.quit()
    
    elif statement == 'Balance Sheet':
        tables = pd.DataFrame()
        ### this is for gathering data on the balance sheet
        for ticker in tickers:
            driver = webdriver.Chrome() ### use google chrome
            driver.get("https://xueqiu.com/snowman/S/" + ticker + "/detail#/ZCFZB") ### go to website
            time.sleep(1) ### gives time for page to load. This is a xueqiu specific solution
            html = driver.page_source ## gather and read HTML    
            ###refresh web page until chart shows up
            table = infinite_query(html)
            ### Clean data
            table = table [0]
            table = table.iloc[:,1:]
            table = table.T.reset_index(drop=False).T
            table = table.T.reset_index(drop=False).T
            table.iloc[0] = ticker
            tables = pd.concat([tables,table], ignore_index=False, axis = 1)
            driver.delete_all_cookies()
            driver.quit()
    else:     
        tables = pd.DataFrame()
        ### this is for gathering data on the Cash Flow Statement
        for ticker in tickers:
            driver = webdriver.Chrome() ### use google chrome
            driver.get("https://xueqiu.com/snowman/S/" + ticker + "/detail#/XJLLB") ### go to website
            time.sleep(1) ### gives time for page to load. This is a xueqiu specific solution
            html = driver.page_source ## gather and read HTML    
            ###refresh web page until chart shows up
            table = infinite_query(html)
            ### Clean data
            table = table [0]
            table = table.iloc[:,1:]
            table = table.T.reset_index(drop=False).T
            table = table.T.reset_index(drop=False).T
            table.iloc[0] = ticker
            tables = pd.concat([tables,table], ignore_index=False, axis = 1)
            driver.delete_all_cookies()
            driver.quit()
    e = tables.astype(str) 
    # e = e.T.reset_index(drop=True).T
    st.dataframe(e)



with column_2:##### Download various information chart
    st.header ('Download Various Other Information')
    tickers2 = st.text_input("Type in Chinese tickers")
    tickers2 = tickers2.split(',') 
    tickers2 = map(str.strip, tickers2)
    tickers2 = list(tickers2)
    
    statement2 = st.selectbox(
             'What would you like to download?',
             ('Stock Data', 'Company data'))
    st.write('You selected:', statement2)
    if tickers2 == ['']:
        tables2 = pd.DataFrame()
    elif statement2 == 'Stock Data':
        tables2 = pd.DataFrame()
        ### this is for gathering key stock and valuation
        for ticker2 in tickers2:
            driver = webdriver.Chrome() ### use google chrome
            driver.get("https://xueqiu.com/S/" + ticker2 ) ### go to website
            # time.sleep(1) ### gives time for page to load. This is a xueqiu specific solution
            html = driver.page_source ## gather and read HTML    
            ###refresh web page until chart shows up
            table = infinite_query(html)
            table = table [0]
            table = table.stack().reset_index()
            table = table.iloc[:,-1]
            table = table.str.split('：', expand = True)
            table = table.T.reset_index(drop=False).T
            table.iloc[0] = ticker
            tables2 = pd.concat([tables2,table], ignore_index=False, axis = 1)
            driver.delete_all_cookies()
            driver.quit()
            
    else:
        tables2 = pd.DataFrame()
        ### this is for gathering company introduction
        for ticker2 in tickers2:
            driver = webdriver.Chrome() ### use google chrome
            driver.get("https://xueqiu.com/S/" + ticker2+ "/detail#/GSJJ") ### go to website
            time.sleep(.5) ### gives time for page to load. This is a xueqiu specific solution
            html = driver.page_source ## gather and read HTML    
            ###refresh web page until chart shows up
            table = infinite_query(html)
            table = table [0]
            table = table.iloc [:,0:2]
            table = table.T.reset_index(drop=False).T
            table.iloc[0] = ticker
            tables2 = pd.concat([tables2,table], ignore_index=False, axis = 1)
            driver.delete_all_cookies()
            driver.quit()
    tables2 