import csv
from datetime import datetime
from random import random
from time import sleep
import random
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import sys

input_dateformat = '%m-%d %H:%M'
output_dateformat = '%Y-%m-%d %H:%M'

cur_year = 2024 # 今夕是何年
cur_month = 12

def get_url(idx: int) -> str:
    # "example : https://guba.eastmoney.com/list,zssh000001,f_1.html"
    url = f"https://guba.eastmoney.com/list,zssh000001,f_{idx}.html"
    return url

def date_convert(date: str) -> str:
    # 加一个年份信息
    # 输入格式： '06-13 10:40'
    # 输出格式： '2017-03-30 09:29'
    global cur_month, cur_year
    date = "2024-" + date # 防闰年
    dt = datetime.strptime(date, output_dateformat)
    if dt.month == 12 and cur_month == 1:
        cur_year -= 1 # 这意味着我们已经跨越了一年
    cur_month = dt.month
    dt = dt.replace(year=cur_year)
    formatted_datetime_str = dt.strftime(output_dateformat)
    return formatted_datetime_str


def get_news(start_page, end_date):
    '''
    @ args
    start_page: 从第几页开始爬取(方便因为莫名其妙的故障导致重来)
    end_date: 最早爬取到哪一天(最晚日期默认为今日，你也可通过修改start_page来间接修改最晚日期)
    '''
    '''
    资讯页
    '''
    if sys.platform.startswith('linux'):  # linux下启动，使用linux chromedriver
        from pyvirtualdisplay import Display
        driver_path = r"chromedriver/chromedriver"
        display = Display(visible=0, size=(1920, 1080))  # 打开虚拟展示界面以避免图形界面启动Chrome的错误
        display.start()
    else:  # windows下启动
        driver_path = r"chromedriver/chromedriver.exe"

    # create local csv (warning: old records will be overwritten)
    with open('comments.csv', 'w', newline='', encoding='utf-8') as f:
        headers = ["date", 'content', 'author']
        writer = csv.writer(f)
        writer.writerow(headers)
        f.close()

    page_idx = start_page
    while True:
        url = get_url(page_idx)

        option = webdriver.ChromeOptions()
        option.add_argument('headless')

        if sys.platform.startswith('linux'):  # linux下用no-sandbox模式
            option.add_argument("--no-sandbox")

        browser = webdriver.Chrome(executable_path=driver_path, options=option)  # 打开浏览器

        print(page_idx, url)

        browser.get(url)  # 访问相对应链接
        sleep(random.uniform(1, 3))

        html = browser.page_source  # 网页代码含有汉字的地方可以直接输出汉字
        soup = BeautifulSoup(html, "html.parser")  # 指定解析html的解析器为"html.parser",可以把网络中标签值提取出来

        if "上证指数吧" not in html:
            print("Your IP is banned")
            exit(0)

        table = soup.find("table", {'class': "default_list"})
        news_list = table.find("tbody", {'class': 'listbody'})
        read_list = news_list.find_all("div", {'class': 'read'})
        comment_list = news_list.find_all("div", {'class': 'reply'})
        title_list = news_list.find_all("div", {'class': 'title'})
        author_list = news_list.find_all("div", {'class': 'author cl'})
        renew_list = news_list.find_all("div", {'class': 'update pub_time'})
        print(len(news_list), len(read_list), len(comment_list), len(title_list), len(author_list), len(renew_list))
        '''
        正文页
        '''

        ls = []
        for i in range(len(renew_list)):
            ls.append([date_convert(renew_list[i].text.strip()), title_list[i].text.strip(), author_list[i].text.strip()])

        print(ls)
        with open('comments.csv', 'a', newline='', encoding='utf-8') as f:
            print("write", len(ls), "comments to file")
            writer = csv.writer(f)
            writer.writerows(ls)
            f.close()

        browser.quit()
        if sys.platform.startswith('linux'):
            display.stop()

        # 判断是否已经到终止时间
        dt_str = date_convert(renew_list[-1].text.strip())
        dt = datetime.strptime(dt_str, output_dateformat)
        if dt < end_date:
            print("search ends")
            return
        sleep(1)
        page_idx += 1


if __name__ == "__main__":
    # start_page, end_date定义在最上面，需要可以修改
    start_page = 0
    end_date = datetime(2023, 6, 13, 0, 30)
    get_news(start_page, end_date)
    print("运行完成")

# http://guba.eastmoney.com/news,300314,1418288636.html 查不出内容
