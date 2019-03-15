import grequests
import re
from bs4 import BeautifulSoup


class MaoYan:
    """


    movie 电影名称，电影评分，电影简介
          name,score,synopsis
    }}}
    """
    def __init__(self):
        self.movies = []
        self.href_list = []
        self._DOMAIN = 'https://maoyan.com'
        self.cookies = dict(ci='42')  # 改变城市
        self.get_hot_movies()
        self.get_synopsis()
        self.get_img()

    def get_hot_movies(self):
        urls = ['https://maoyan.com/films?showType=1']
        rs = grequests.map((grequests.get(u, cookies=self.cookies) for u in urls))[0]
        html = BeautifulSoup(rs.text, 'html.parser')
        hot_list = html.find_all(attrs={'class': 'channel-detail movie-item-title'})
        for child in hot_list:
            a = child.contents[1]
            movie = dict((('name', a.text), ('href', self._DOMAIN + a.get('href'))))
            self.href_list.append(self._DOMAIN + a.get('href'))
            scoreNode = child.next_sibling.next_sibling
            movie['score'] = scoreNode.text
            self.movies.append(movie)
        rs.close()

    def get_synopsis(self):
        synopsis = []
        img_list = []
        response_list = grequests.map((grequests.get(u, cookies=self.cookies) for u in self.href_list))
        for rs in response_list:
            html = BeautifulSoup(rs.text, 'html.parser')
            s = html.find(attrs={'class': 'dra'})
            img_url = html.find(attrs={'class': 'avatar'})['src']
            if html.find(attrs={'class': 'btn buy'}):
                film_url = self._DOMAIN + html.find(attrs={'class': 'btn buy'})['href']
                synopsis.append(s.string)
                img_list.append(img_url)
            rs.close()
        for i, v in enumerate(self.movies):
            v['synopsis'] = synopsis[i]
            v['img_url'] = img_list[i]
            v['film_url'] = film_url
            v.pop('href')

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
        pass


if __name__ == '__main__':
    my = MaoYan()
    for zz in my.movies:
        print(zz)




