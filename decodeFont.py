from fontTools.ttLib import TTFont
from util import fetch_res
import os
import re

os.makedirs('font', exist_ok=True)
regex_woff = re.compile("(?<=url\(').*\.woff(?='\))")
regex_font = re.compile(r'(?<=\\u).{4}')

basefont = TTFont('base.woff')
fontdict = {'uniF30D': '0', 'uniE6A2': '8', 'uniEA94': '9', 'uniE9B1': '2', 'uniF620': '6',
            'uniEA56': '3', 'uniEF24': '1', 'uniF53E': '4', 'uniF170': '5', 'uniEE37': '7'}


def decode_font(newfont, text):
    text = repr(text)
    ms = regex_font.findall(text)
    for m in ms:
        text = text.replace(fr'\u{m}', get_num(newfont, f'uni{m.upper()}'))
    return eval(text)


def get_num(newfont, name):
    uni = newfont['glyf'][name]
    for k, v in fontdict.items():
        if uni == basefont['glyf'][k]:
            return v


async def download_font(html):
    woff = regex_woff.search(html).group()
    woff_link = 'http:' + woff
    local_name = 'font/' + os.path.basename(woff_link)
    if not os.path.exists(local_name):
        rs = await fetch_res(woff_link)
        with open(local_name, 'wb+') as sw:
            sw.write(rs)
    return TTFont(local_name)

