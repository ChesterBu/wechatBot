"""
爬取猫眼电影

"""

import os
import re
import requests
from fontTools.ttLib import TTFont
from bs4 import BeautifulSoup

host = 'http://maoyan.com'

os.makedirs('font', exist_ok=True)
regex_woff = re.compile("(?<=url\(').*\.woff(?='\))")
regex_text = re.compile('(?<=<span class="stonefont">).*?(?=</span>)')
regex_font = re.compile('(?<=&#x).{4}(?=;)')

basefont = TTFont('base.woff')
fontdict = {'uniF30D': '0', 'uniE6A2': '8', 'uniEA94': '9', 'uniE9B1': '2', 'uniF620': '6',
            'uniEA56': '3', 'uniEF24': '1', 'uniF53E': '4', 'uniF170': '5', 'uniEE37': '7'}

link = 'https://maoyan.com/cinemas?movieId=1250341'


def decode_font():

    """
    link:
    :return:
    {
        'name': '夏目友人帐',
        'type': '剧情,动画,奇幻',
        'country': '日本',
        'length': '105分钟',
        'release-time': '2019-03-07',
        'score': '9.1',
        'score-num': '88440',
        'box-office': '1.00亿',
        'price': ['23', '23']
    }
    """

    dhtml = requests.get(link).text
    msg = {}
    dsoup = BeautifulSoup(dhtml, 'lxml')
    # 下载字体文件
    woff = regex_woff.search(dhtml).group()
    wofflink = 'http:' + woff
    localname = 'font\\' + os.path.basename(wofflink)
    if not os.path.exists(localname):
        downloads(wofflink, localname)
    font = TTFont(localname)

    # 其中含有 unicode 字符，BeautifulSoup 无法正常显示，只能用原始文本通过正则获取
    ms = regex_text.findall(dhtml)
    if len(ms) < 3:
        msg['score'] = '0'
        msg['score-num'] = '0'
        msg['box-office'] = '0'
    else:
        msg['score'] = get_font(font, ms[0])
        msg['score-num'] = get_font(font, ms[1])
        msg['box-office'] = get_font(font, ms[2]) + dsoup.find('span', class_='unit').text
        msg['price'] = [get_font(font, i) for i in ms[3:]]
    print(msg)


def get_font(newfont, text):
    ms = regex_font.findall(text)
    for m in ms:
        text = text.replace(f'&#x{m};', get_num(newfont, f'uni{m.upper()}'))
    return text


def get_num(newfont, name):
    uni = newfont['glyf'][name]
    for k, v in fontdict.items():
        if uni == basefont['glyf'][k]:
            return v


def downloads(url, localfn):
    with open(localfn, 'wb+') as sw:
        sw.write(requests.get(url).content)


decode_font()