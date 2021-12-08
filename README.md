# XueQiu_Downloader

Go to https://share.streamlit.io/epiphronquant/xueqiu_downloader/main/XueQiu_Scraper.py to use the app

XueQiu only has data on HKEX, Chinese stocks, American stocks. Yahoo Finance has data on almost all stocks but Yahoo Downloader lacks in the quality of XueQiu Downloader.

In contrast to Yahoo Downloader, I personally had to develop a solution to scrape data from XueQiu. 
This involved using "selenium" which opens a google chrome window to the url, and uses "pandas" to scrape and clean tables from the open chrome window. Options then click the window to select the correspoding reports and scrapes them accordingly. 

The design of the XueQiu website is different from Yahoo Finance so it is slower to gather data. Gathering data on a statement can range from 1 second to 5 seconds to even half a minute. This is because even if you personally go to the XueQiu website, occasionally, no data is shown. To workaround this issue, the program would wait 1 second for the data to load then refresh the page every 4 seconds until the data is shown and "pandas" can scrape the data. If there isn't data or XueQiu never shows the data, it is advisable to stop the program and refresh the page.

Data from XueQiu is much more accurate than Yahoo Downloader and is in Chinese. Their statement data has a much longer timespan.
