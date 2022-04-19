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


def get_sh_data(url):
    """
    读取上海市卫健委数据
    :param url: 卫健委新闻发布网站
    :return zhuangui, guankongquezhen, guankongyisi: 转归确诊、管控中新增确诊病例以及管控中新增无症状病例
    """
    r = requests.get(url=url, headers=sh_headers)
    sh_dict = {}
    soup = BeautifulSoup(r.text, 'lxml')
    # print(soup)
    ivs_content = soup.find(
        name='div',
        attrs={
            'id': 'ivs_content',
            'class': 'Article_content'})
    new_text = ivs_content.get_text()
    #style = r'其中(\d+)例确诊病例为此前无症状感染者转归，(\d+)例确诊病例和(\d+)例无症状感染者在隔离管控中发现'
    style = r'含既往无症状感染者转为确诊病例(\d+)例）和无症状感染者17332例，实际新增本土阳性感染者19442例，其中(\d+)例确诊病例和(\d+)例无症状感染者在隔离管控中发现'
    zhuangui = int(re.search(style, new_text).group(1))
    print(zhuangui)
    guankongquezhen = int(re.search(style, new_text).group(2))
    print(guankongquezhen)
    guankongyisi = int(re.search(style, new_text).group(3))
    print(guankongyisi)
    return zhuangui, guankongquezhen, guankongyisi

def get_sh_today_news():
    """
    读取上海市卫健委新闻
    :return sh_dict: 返回一个字典，包括新增确诊、新增无症状以及转归确诊、管控中新增确诊病例、管控中新增无症状病例数量
    """
    url = 'http://wsjkw.sh.gov.cn/xwfb/index.html'
    r = requests.get(url=url, headers=sh_headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    # print(soup)
    today_format = datetime.datetime.today().strftime('%Y-%m-%d')
    #today_format = datetime.datetime(2022, 4, 7).strftime('%Y-%m-%d')
    print(today_format)
    today_sh_news = soup.find_all(name='span', text=today_format)
    today_counts = len(today_sh_news)
    for i in range(today_counts - 1, -1, -1):
        title = today_sh_news[i].find_previous_sibling(
            name='a').attrs['title']  # 标题
        print(title)
        href = 'http://wsjkw.sh.gov.cn' + \
            today_sh_news[i].find_previous_sibling(name='a').attrs['href']  # 网址
        print(href)
        if title.startswith('昨日新增') or '上海新增' in title:
            # print(title)
            print(href)
            zhuangui, guankongquezhen, guankongyisi = get_sh_data(href)
            print(zhuangui)
            sh_dict = {}
            sh_dict['日期'] = today_format
            sh_dict['新增确诊'] = re.findall(r"(?<=\新增本土新冠肺炎确诊病例)\d+", title)
            sh_dict['新增无症状'] = re.findall(r"(?<=\本土无症状感染者)\d+", title)
            sh_dict['转归'] = zhuangui
            sh_dict['管控确诊'] = guankongquezhen
            sh_dict['管控无症状'] = guankongyisi
            print(sh_dict)
            return sh_dict

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
    wb = app.books.open('shanghaicoviddata.xlsx')
    ws = wb.sheets['march']
    ws1 = wb.sheets['huangpu']
    max_row = ws.range('A1').expand('table').rows.count + 1
    ws.range('A' + str(max_row)).value = sh_dict['日期']
    ws.range('B' + str(max_row)).value = max_row - 1
    ws.range('C' + str(max_row)).value = sh_dict['新增确诊']
    ws.range('D' + str(max_row)).value = sh_dict['新增无症状']
    ws.range('F' + str(max_row)).value = sh_dict['转归']
    ws.range('G' + str(max_row)).value = sh_dict['管控确诊']
    ws.range('H' + str(max_row)).value = sh_dict['管控无症状']
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

    try:
        sh_dict = get_sh_today_news()
        print('上海数据：{}'.format(sh_dict))
        print(sh_dict)
    except BaseException:
        print('上海数据未更新')

    #huangpu_dict = get_huangpu_today_news()
    #print(huangpu_dict)
    # 三、导出到excel里
    if sh_dict != None:
        get_into_excel()
        print('Excel刷新成功！')
