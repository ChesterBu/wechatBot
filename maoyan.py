import requests
import re
from bs4 import BeautifulSoup
from fontTools.ttLib import TTFont
import os
import time
import asyncio
from aiohttp import ClientSession

os.makedirs('font', exist_ok=True)
regex_woff = re.compile("(?<=url\(').*\.woff(?='\))")
regex_font = re.compile(r'(?<=\\u).{4}')

basefont = TTFont('base.woff')
fontdict = {'uniF30D': '0', 'uniE6A2': '8', 'uniEA94': '9', 'uniE9B1': '2', 'uniF620': '6',
            'uniEA56': '3', 'uniEF24': '1', 'uniF53E': '4', 'uniF170': '5', 'uniEE37': '7'}


async def fetch_res(url):
    async with ClientSession(cookies=dict(ci='42')) as session:
        async with session.get(url) as response:
            return await response.read()


async def fetch(url):
    async with ClientSession(cookies=dict(ci='42')) as session:
        async with session.get(url) as response:
            return await response.text()


class MaoYan:
    """
    movie 电影名称，电影评分，电影简介
        {
            'name': '地久天长',
            'type': '剧情',
            'country': '中国大陆',
            'length': '175分钟',
            'release-time': '2019-03-22',
            'synopsis': '年轻的刘耀军（王景春 饰）和沈英明（徐程 饰）两家人本是挚友，两家儿子沈浩和刘星在郊外嬉戏中，耀军的儿子刘星，隐藏的真相终将因为年轻一代人的坦荡而揭开。岁月流逝，生命滚滚向前……',
            'cinema': [
                {'name': '香港未来主题影院', 'address': '地址：碑林区长安立交东北角香港未来影院二楼', 'price': '¥36起'},
                {'name': 'CGV影城(万象城店)', 'address': '地址：未央区三桥新街1076号华润万象城4层', 'price': '¥41起'},
                {'name': '万达影城(李家村店)', 'address': '地址：碑林区雁塔路北段8号万达商业广场4楼', 'price': '¥60起'},
                {'name': 'CGV影城(印象城IMAX店)', 'address': '地址：未央区未央路33号龙首村未央印象城3楼（万龙广场，盛龙广场，未央区政府）', 'price': '¥39起'},
                {'name': '奥斯卡国际影城(长安城南新天地店)', 'address': '地址：长安区西长安街与府东一路交叉口东南角城南新天地南区负一层（长安新区政府斜对面）', 'price': '¥34起'},
                {'name': '派啦萌巨幕影城(卜蜂莲花店)', 'address': '地址：未央区凤城八路与渭滨路十字西北角卜蜂莲花4F', 'price': '¥33起'},
                {'name': 'CGV影城(胡家庙店)', 'address': '地址：新城区长缨西路1号华东万和城6层（胡家庙十字）', 'price': '¥40起'},
                {'name': '中影星美国际影城(韩森寨店)', 'address': '地址：新城区幸福路与韩森路十字东南角4F', 'price': '¥33起'},
                {'name': '中影国际影城(大唐西市店)', 'address': '地址：莲湖区劳动南路大唐西市购物中心三楼（近西工大）', 'price': '¥39起'},
                {'name': '太平洋影城(西安曲江店)', 'address': '地址：雁塔区雁塔南路与雁南一路十字口大唐不夜城东南角（近雁南一路）', 'price': '¥33起'},
                {'name': '太平洋影城(西安临潼店)', 'address': '地址：临潼区大唐华清城西面负一层', 'price': '¥33起'},
                {'name': '米格国际影城(时代广场店)', 'address': '地址：碑林区南门外珠江时代广场4楼（南门外）', 'price': '¥66起'}
            ]
        }

    """

    def __init__(self):
        self.movies = []
        self.href_list = []
        self._DOMAIN = 'https://maoyan.com'
        self.cookies = dict(ci='42')  # 改变城市
        loop = asyncio.get_event_loop()
        a = time.perf_counter()
        loop.run_until_complete(self.get_hot_movies())
        print("Time 1 used:", time.perf_counter() - a)
        a = time.perf_counter()
        loop.run_until_complete(self.get_info())
        print("Time 2 used:", time.perf_counter() - a)
        a = time.perf_counter()
        tasks = [asyncio.ensure_future(self.get_img()), asyncio.ensure_future(self.get_encode_info())]
        loop.run_until_complete(asyncio.wait(tasks))
        print("Time 3 used:", time.perf_counter() - a)
        loop.close()

    # 1
    async def get_hot_movies(self):
        url = 'https://maoyan.com/films?showType=1'
        rs = await fetch(url)
        html = BeautifulSoup(rs, 'html.parser')
        hot_list = html.find_all(attrs={'class': 'movie-item'})
        for child in hot_list:
            href = child.contents[1].get('href')
            if child.text.find('购票') != -1:
                self.href_list.append(self._DOMAIN + href)


    # 2
    async def get_info(self):
        for url in self.href_list:
            rs = await fetch(url)
            html = BeautifulSoup(rs, 'html.parser')
            film = html.find(attrs={'class': 'btn buy'})
            msg = dict()
            msg['name'] = html.find(class_='name').text
            msg['synopsis'] = html.find(attrs={'class': 'dra'}).string
            msg['img_url'] = html.find(attrs={'class': 'avatar'})['src']
            ell = html.find_all('li', {'class': 'ellipsis'})
            msg['type'] = ell[0].text
            msg['country'] = ell[1].text.split('/')[0].strip()
            msg['length'] = ell[1].text.split('/')[1].strip()
            msg['release-time'] = ell[2].text[:10]
            msg['film_url'] = self._DOMAIN + film['href']
            self.movies.append(msg)

    # 3
    async def get_img(self):
        pattern = re.compile('464w_644h')
        urls = []
        for m in self.movies:
            url = re.sub(pattern, '160w_220h', m['img_url'])
            name = m['name']
            urls.append(dict(url=url, name=name), )
            m.pop('img_url')
        for d in urls:
            rs = await fetch_res(d['url'])
            open('imgs/' + d['name'] + '.png', 'wb').write(rs)

    # 3
    async def get_encode_info(self):
        urls = [a['film_url'] for a in self.movies]
        for url in urls:
            index = urls.index(url)
            dhtml = await fetch(url)
            soup = BeautifulSoup(dhtml.encode('utf-8'), "html.parser")
            woff = regex_woff.search(dhtml).group()
            wofflink = 'http:' + woff
            localname = 'font/' + os.path.basename(wofflink)
            if not os.path.exists(localname):
                rs = await fetch_res(wofflink)
                with open(localname, 'wb+') as sw:
                    sw.write(rs)
            font = TTFont(localname)
            tag = soup.find_all(attrs={'class': 'cinema-cell'})
            cinema_list = []
            if len(tag) > 0:
                for cell in tag:
                    cinema = dict()
                    cinema['name'] = cell.find('a', attrs={'class': 'cinema-name'}).get_text()
                    cinema['address'] = cell.find('p', attrs={'class': 'cinema-address'}).get_text()
                    price = cell.find('span', {'class': 'stonefont'}).get_text()
                    cinema['price'] = '¥' + self.get_font(font, price) + '起'
                    cinema_list.append(cinema)
            self.movies[index]['cinema'] = cinema_list if len(cinema_list) > 0 else '暂无影院信息'
            self.movies[index].pop('film_url')

    def get_font(self, newfont, text):
        text = repr(text)
        ms = regex_font.findall(text)
        for m in ms:
            text = text.replace(fr'\u{m}', self.get_num(newfont, f'uni{m.upper()}'))
        return eval(text)

    def get_num(self, newfont, name):
        uni = newfont['glyf'][name]
        for k, v in fontdict.items():
            if uni == basefont['glyf'][k]:
                return v


if __name__ == '__main__':
    start = time.perf_counter()
    my = MaoYan()
    for m in my.movies:
        print(m)
    print(len(my.movies))
    elapsed = (time.perf_counter() - start)
    print("Time used:", elapsed)
