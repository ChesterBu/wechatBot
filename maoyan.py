import grequests
import re
from bs4 import BeautifulSoup
from fontTools.ttLib import TTFont
import os

os.makedirs('font', exist_ok=True)
regex_woff = re.compile("(?<=url\(').*\.woff(?='\))")
regex_font = re.compile(r'(?<=\\u).{4}')

basefont = TTFont('base.woff')
fontdict = {'uniF30D': '0', 'uniE6A2': '8', 'uniEA94': '9', 'uniE9B1': '2', 'uniF620': '6',
            'uniEA56': '3', 'uniEF24': '1', 'uniF53E': '4', 'uniF170': '5', 'uniEE37': '7'}


class MaoYan:
    """
    movie 电影名称，电影评分，电影简介
          {
          'name': '比悲伤更悲伤的故事',
          'type': '剧情,爱情',
          'country': '中国台湾',
          'length': '107分钟',
          'release-time': '2019-03-14',
          'synopsis': '唱片制作人张哲）和王牌作词人宋媛媛',
          'cinema': [
            {'name': '香港未来主题影院', 'address': '地址：碑林区长安立交东北角香港未来影院二楼', 'price': '¥33起'},
            {'name': '中影飞尚国际影城', 'address': '地址：新城区长乐西路益田假日世界7层（地铁1号线朝阳门站B出口）', 'price': '¥28起'},
            {'name': 'CGV影城(万象城店)', 'address': '地址：未央区三桥新街1076号华润万象城4层', 'price': '¥37起'},
            {'name': '金逸影城(西安澳堡店)', 'address': '地址：长安区西长安街澳堡时代广场', 'price': '¥29起'},
            {'name': '首映国际影城(通化门店)', 'address': '地址：新城区金花路十字苏宁东侧西北国际茶城4楼', 'price': '¥35起'},
            {'name': '万达影城(李家村店)', 'address': '地址：碑林区雁塔路北段8号万达商业广场4楼', 'price': '¥40起'},
            {'name': '万达影城(大明宫店)', 'address': '地址：未央区太华北路369号万达广场', 'price': '¥35起'},
            {'name': 'CGV影城(印象城IMAX店)', 'address': '地址：未央区未央路33号龙首村未央印象城3楼（万龙广场，盛龙广场，未央区政府）', 'price': '¥37起'},
            {'name': '万达影城(解放路店)', 'address': '地址：新城区解放路111号五路口东南角万达广场南区1号门4层', 'price': '¥25起'},
            {'name': '奥斯卡国际影城(长安城南新天地店)', 'address': '地址：长安区西长安街与府东一路交叉口东南角城南新天地南区负一层（长安新区政府斜对面）', 'price': '¥29起'},
            {'name': '大明宫IMAX影院(自强东路店)', 'address': '地址：新城区自强东路585号（西安大明宫国家遗址公园内御道广场东侧）', 'price': '¥30起'},
            {'name': '珠江影城(西安店)', 'address': '地址：新城区五路口十字E`love欢乐城', 'price': '¥23起'}
          ]
        }

    """

    def __init__(self):
        self.movies = []
        self.href_list = []
        self._DOMAIN = 'https://maoyan.com'
        self.cookies = dict(ci='42')  # 改变城市
        self.get_hot_movies()
        self.get_info()
        self.get_img()
        self.get_encode_info()

    def get_hot_movies(self):
        urls = ['https://maoyan.com/films?showType=1']
        rs = grequests.map((grequests.get(u, cookies=self.cookies) for u in urls))[0]
        html = BeautifulSoup(rs.text, 'html.parser')
        hot_list = html.find_all(attrs={'class': 'channel-detail movie-item-title'})
        for child in hot_list:
            a = child.contents[1]
            self.href_list.append(self._DOMAIN + a.get('href'))
        rs.close()

    def get_info(self):
        response_list = grequests.map((grequests.get(u, cookies=self.cookies) for u in self.href_list))
        for rs in response_list:
            html = BeautifulSoup(rs.text, 'html.parser')
            film = html.find(attrs={'class': 'btn buy'})
            if film:
                msg = dict()
                msg['name'] = html.find(class_='name').text
                ell = html.find_all('li', {'class': 'ellipsis'})
                msg['type'] = ell[0].text
                msg['country'] = ell[1].text.split('/')[0].strip()
                msg['length'] = ell[1].text.split('/')[1].strip()
                msg['release-time'] = ell[2].text[:10]
                msg['synopsis'] = html.find(attrs={'class': 'dra'}).string
                msg['img_url'] = html.find(attrs={'class': 'avatar'})['src']
                msg['film_url'] = self._DOMAIN + film['href']
                self.movies.append(msg)
            rs.close()

    def get_img(self):
        pattern = re.compile('464w_644h')
        urls = []
        for m in self.movies:
            url = re.sub(pattern, '160w_220h', m['img_url'])
            name = m['name']
            urls.append(dict(((url, name),)))
            m.pop('img_url')
        response_list = grequests.map((grequests.get(k, cookies=self.cookies) for a in urls for k in a))
        for k, rs in enumerate(response_list):
            if rs.status_code == 200:
                open('imgs/' + urls[k][rs.url] + '.png', 'wb').write(rs.content)

    def get_encode_info(self):
        response_list = grequests.map((grequests.get(a['film_url'], cookies=self.cookies) for a in self.movies))
        for rs in response_list:
            index = response_list.index(rs)
            dhtml = rs.text
            soup = BeautifulSoup(dhtml.encode('utf-8'), "html.parser")
            woff = regex_woff.search(dhtml).group()
            wofflink = 'http:' + woff
            localname = 'font\\' + os.path.basename(wofflink)
            if not os.path.exists(localname):
                self.downloads(wofflink, localname)
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
            rs.close()

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

    def downloads(self, url, localfn):
        url = [url, ]
        with open(localfn, 'wb+') as sw:
            rs = grequests.map((grequests.get(u, cookies=self.cookies) for u in url))[0]
            sw.write(rs.content)


if __name__ == '__main__':
    my = MaoYan()
    for m in my.movies:
        print(m)
