# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 14:53:06 2021

@author: angus
"""
import numpy as np
from time import sleep
import base64
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd

### Options that allow chrome to run in streamlit
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

def infinite_query(ticker, xq_exten, sleep_time, freq = '全部',  stock_data = False, statement = False):
    '''Heavily Xueqiu customized function that refreshes page until it can gather the needed data
    in: str, str, int, str, bool, bool
    out: dataframe or list of dataframes
    '''
    driver = webdriver.Chrome(options=chrome_options) ### use google chrome
    driver.get("https://xueqiu.com/snowman/S/" + ticker + xq_exten) ### go to website
    sleep(1) ### gives time for page to load. This is a xueqiu specific solution
    # time.sleep(sleep_time) ### gives time for page to load. This is a xueqiu specific solution
    
    if stock_data == True: ### This is for gathering HKEX stock data
        try:
            int(ticker) ### only HKEX stocks get caught up in this logic
            sleep(1) ### gives time for page to load. This is a xueqiu specific solution
            button= driver.find_element_by_xpath('/html/body/div/div[2]/div[2]/div[5]/a')### selects button 
            button.click()
        except ValueError:
            pass
    else:
        pass
    
    if freq == '全部': ### selects the frequency
        pass
    else:
        path = "//span[contains(@class,'btn') and contains(text(), '"+ freq +"')]"
        button= driver.find_element_by_xpath(path)### selects button 
        button.click()
    sleep(sleep_time) ### gives time for page to load. This is a xueqiu specific solution
    html = driver.page_source ## gather and read HTML       
    if statement == True:
            ### initialize dataframe
        statements = pd.DataFrame()
        ### gathers first chart
        html = driver.page_source ## gather and read HTML    
        statement1 = None
        while statement1 is None:
            try: 
                statement1 = pd.read_html(html)
            except ValueError:
                driver.refresh()
                sleep(4)
                html = driver.page_source## gather and read HTML
                try: 
                    statement1 = pd.read_html(html) 
                except ValueError:
                    statement1 = None
        
        statement1 = statement1 [0]
        statement1 = statement1.set_index(statement1.columns [0]) ### sets an index so that the data is merged rather than directly concated
        # statement1 = statement1.iloc [:,1:]
        
        statements = pd.concat([statements,statement1], ignore_index=False, axis = 1)
        statements = statements.set_index(statements.columns [0]) ### sets an index so that the data is merged rather than directly concated
        # statements = statements.iloc [:,1:]
        
        statement1l = statement1.values.tolist()
        
        ### press button to gather next chart
        path = "/html/body/div/div[2]/div[2]/div/div[1]/div[2]/span[2]" ## this presses the 下一页 button. It uses copy x-path from chrome inspect
        button= driver.find_element_by_xpath(path)### selects button 
        button.click() 
        sleep(.5)
        
        html = driver.page_source ## gather and read HTML    
        statement2 = pd.read_html(html)
        statement2 = statement2 [0]
        statement2 = statement2.set_index(statement2.columns [0]) ### sets an index so that the data is merged rather than directly concated
        
        statement2l = statement2.values.tolist()
        
        ### compare first chart with second chart
        comparison = statement1l == statement2l
        
        while comparison is False:
            statement2_edit = statement2.iloc [:,2:]
            statements = pd.concat([statements,statement2_edit], ignore_index=False, axis = 1)
            ### gathers first chart
            statement1 = statement2
            statement1l = statement1.values.tolist()        
            ### press button to gather next chart
            path = "/html/body/div/div[2]/div[2]/div/div[1]/div[2]/span[2]" ## this presses the 下一页 button. It uses copy x-path from chrome inspect
            button= driver.find_element_by_xpath(path)### selects button 
            button.click() 
            sleep(1)    
            html = driver.page_source ## gather and read HTML    
            statement2 = pd.read_html(html)
            statement2 = statement2 [0]
            statement2 = statement2.set_index(statement2.columns [0]) ### sets an index so that the data is merged rather than directly concated
            # statement2 = statement2.iloc [:,1:]
        
            statement2l = statement2.values.tolist()
            comparison = statement1l == statement2l
        statements = statements.reset_index()
        statements = convert_table(statements)
        table = statements
    else:
        table = None
        while table is None:
            try: 
                table = pd.read_html(html)
            except ValueError:
                driver.refresh()
                sleep(4)
                html = driver.page_source## gather and read HTML
                try: 
                    table = pd.read_html(html)
                except ValueError:
                    table = None
    driver.delete_all_cookies()
    driver.quit()   
    return table
def convert(chinese): 
    """converts Chinese numbers to int
    in: string
    out: string
    """
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
def convert_table(table):
    """coverts everything beyond the first column with chinese numbers to raw int number
    in: dataframe 
    out: dataframe
    """
    columns = table.columns [1:]
    for column in columns:
        abc = table [column]
        abc2 = abc.str[-1]
        abc = abc.str[:-1]   
        abc2 = '一' + abc2
        abc2 = abc2.astype(str)
        a = []
        for numbers in abc2:
            b = convert (numbers)
            a.append(b)
        a = pd.DataFrame(a, columns = [column])
        abc = pd.DataFrame(abc)
        abc = abc.replace(r'^\s*$', np.nan, regex=True)
        abc = abc.astype(float)
        df3 = a.mul(abc.values)
        df3 = df3.round(2)
        table [column] = df3
    return table
def to_excel(df):
    """"converts a dataframe to excel
    in: dataframe
    out: processed_data
    """
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index = True, header = False)
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