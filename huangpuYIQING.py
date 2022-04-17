import requests
from bs4 import BeautifulSoup
import datetime
import re
from selenium import webdriver
import time
import xlwings as xw
from selenium.webdriver.chrome.service import Service
s = Service(executable_path=r"C:\Users\admin\AppData\Roaming\Python\Python38\site-packages\selenium\webdriver\chrome\chromedriver.exe")
driver = webdriver.Chrome(service=s)

def get_huangpu_data(url):
    """
    读取上海市卫健委中黄浦区相关数据
    :param url: 卫健委新闻发布网站
    :return huangpuquezhen, huangpuyisi: 黄浦区新增确诊病例以及新增无症状病例
    """
    r = requests.get(url=url, headers=huangpu_headers)
    #huangpu_dict = {}
    soup = BeautifulSoup(r.text, 'lxml')
    print(soup.text)
    # print(new_text)
    style = r'黄浦区新增(\d+)例本土确诊病例，新增(\d+)例本土无症状感染者，分别居住于'
    print(style)
    huangpuquezhen = int(re.search(style, soup.text).group(1))
    print(huangpuquezhen)
    huangpuyisi = int(re.search(style, soup.text).group(2))
    print(huangpuyisi)
    return huangpuquezhen, huangpuyisi

def get_huangpu_today_news():
    """
    读取上海市卫健委中黄浦相关新闻
    :return sh_dict: 返回一个字典，包括黄浦新增确诊、新增无症状病例数量
    """
    url = 'http://wsjkw.sh.gov.cn/xwfb/index.html'
    r = requests.get(url=url, headers=sh_headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    today_format = datetime.datetime.today().strftime('%Y-%m-%d')
    #today_format = datetime.datetime(2022, 4, 7).strftime('%Y-%m-%d')
    print(today_format)
    today_sh_news = soup.find_all(name='span', text=today_format)
    today_counts = len(today_sh_news)
    for i in range(today_counts - 1, -1, -1):
        title = today_sh_news[i].find_previous_sibling(
            name='a').attrs['title']  # 标题
        # print(title)
        href = today_sh_news[i].find_previous_sibling(name='a').attrs['href']  # 网址
        if re.findall('本市各区确诊病例、无症状感染者居住地信息', title):
            print(title)
            print(href)
            huangpuquezhen, huangpuyisi = get_huangpu_data(href)
            huangpu_dict = {}
            huangpu_dict['日期'] = today_format
            huangpu_dict['黄浦新增确诊'] = huangpuquezhen
            huangpu_dict['黄浦新增无症状'] = huangpuyisi
            print(huangpu_dict)
            return huangpu_dict

def get_cookie(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(3)
    cookies = driver.get_cookies()
    driver.quit()
    items = []
    for i in range(len(cookies)):
        cookie_value = cookies[i]
        item = cookie_value['name'] + '=' + cookie_value['value']
        items.append(item)
    cookiestr = '; '.join(a for a in items)
    return cookiestr

def get_into_excel():
    '''把数据贴到excel里'''
    app = xw.App()
    wb = app.books.open('shanghaicoviddata .xlsx')
    ws = wb.sheets['march']
    ws1 = wb.sheets['huangpu']
    max_row = ws1.range('A1').expand('table').rows.count + 1
    ws1_max_row = ws1.range('A1').expand('table').rows.count + 1
    ws1.range('A' + str(max_row)).value = huangpu_dict['日期']
    ws1.range('B' + str(max_row)).value = ws1_max_row - 1
    ws1.range('C' + str(max_row)).value = huangpu_dict['黄浦新增确诊']
    ws1.range('D' + str(max_row)).value = huangpu_dict['黄浦新增无症状']
    wb.save()
    wb.close()
    app.quit()

if __name__ == "__main__":
    sh_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Cookie': get_cookie('http://wsjkw.sh.gov.cn/xwfb/index.html'),
        # 'Cookie': 'zh_choose=s; zh_choose=s; _gscu_2010802395=80620430ie0po683; yd_cookie=12f170fc-e368-4a662db5220af2d434160e259b2e31585efb; _ydclearance=2cd0a8873fd311efcda1c1aa-05fc-4001-a108-0e86b80b3fee-1580700296; _gscbrs_2010802395=1; _pk_ref.30.0806=%5B%22%22%2C%22%22%2C1580693101%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DDVUbOETLyMZLC5c_V7RJRbAYPvyqaU3f2PCBi2-E6KC2QEFltdrKWGmhgA5NbC3c%26wd%3D%26eqid%3Df38b30250015e1c5000000045e365a8d%22%5D; _pk_ses.30.0806=*; _pk_id.30.0806=35b481da38abb562.1580620431.6.1580694952.1580693101.; _gscs_2010802395=80693100qds57e17|pv:6; AlteonP=ALa1BGHbHKyWUqcNUGRETw$$',
        'Host': 'wsjkw.sh.gov.cn'
    }
    huangpu_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Cookie': get_cookie('https://mp.weixin.qq.com/s/8bljTUplPh1q4MXb6wd_gg'),
        # 'Cookie': 'zh_choose=s; zh_choose=s; _gscu_2010802395=80620430ie0po683; yd_cookie=12f170fc-e368-4a662db5220af2d434160e259b2e31585efb; _ydclearance=2cd0a8873fd311efcda1c1aa-05fc-4001-a108-0e86b80b3fee-1580700296; _gscbrs_2010802395=1; _pk_ref.30.0806=%5B%22%22%2C%22%22%2C1580693101%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DDVUbOETLyMZLC5c_V7RJRbAYPvyqaU3f2PCBi2-E6KC2QEFltdrKWGmhgA5NbC3c%26wd%3D%26eqid%3Df38b30250015e1c5000000045e365a8d%22%5D; _pk_ses.30.0806=*; _pk_id.30.0806=35b481da38abb562.1580620431.6.1580694952.1580693101.; _gscs_2010802395=80693100qds57e17|pv:6; AlteonP=ALa1BGHbHKyWUqcNUGRETw$$',
        'Host': 'https://mp.weixin.qq.com'
    }

    try:
        huangpu_dict = get_huangpu_today_news()
        print('黄浦数据：{}'.format(huangpu_dict))
        print(huangpu_dict)
    except BaseException:
        print('黄浦数据未更新')

    # 三、导出到excel里
    if huangpu_dict != None:
        get_into_excel()
        print('Excel刷新成功！')
