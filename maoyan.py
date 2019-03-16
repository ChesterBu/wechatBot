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
          {'name': '夏目友人帐',
          'type': '剧情,动画,奇幻',
          'country': '日本',
          'length': '105分钟',
          'release-time': '2019-03-07',
          'synopsis': '夏目（神谷浩史 配音）.....',
          'film_url': 'https://maoyan.com/cinemas?movieId=1250341'
          }
    }}}
    """
    def __init__(self):
        self.movies = []
        self.href_list = []
        self._DOMAIN = 'https://maoyan.com'
        self.cookies = dict(ci='42')  # 改变城市
        self.get_hot_movies()
        self.get_info()
        #self.get_img()
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
                open('imgs/'+urls[k][rs.url]+'.png', 'wb').write(rs.content)

    def get_encode_info(self):
        response_list = grequests.map((grequests.get(a['film_url'], cookies=self.cookies) for a in self.movies))
        #for rs in response_list:
        rs = response_list[0]
        dhtml = rs.text
        soup = BeautifulSoup(dhtml.encode('utf-8'), "lxml")
        tag = soup.find(attrs={'class': 'cinemas-list'}).find_all('span', {'class': 'stonefont'})
        tag = [tag[x].get_text() for x in range(len(tag))]
        woff = regex_woff.search(dhtml).group()
        wofflink = 'http:' + woff
        localname = 'font\\' + os.path.basename(wofflink)
        if not os.path.exists(localname):
            self.downloads(wofflink, localname)
        font = TTFont(localname)
        print([self.get_font(font, i) for i in tag])

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




