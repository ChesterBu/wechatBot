from turing import get_response
from weather import get_forecast
from package import get_package
from apscheduler.schedulers.background import BackgroundScheduler
import json
import re
from const import Status
from itchatUtils import send_msg,send_img

class WeChatBot:
    def __init__(self, user):
        self.user = 'filehelper'
        self.status = Status['init']

        self.movie = json.load(open('m.json', 'r'))
        self.movie_index = 0
        self.max_movie = len(self.movie)
        self.is_send_movie_list = False

        self.schedule = BackgroundScheduler()

        self.function = {
            Status['init']: self.handle_text,
            Status['weather']: self.handle_weather,
            Status['schedule']: self.handle_schedule,
            Status['package']: self.handle_package,
            Status['movie']: self.handle_movie,
        }

    def entry(self, text):
        self.function[self.status](text)

    """
    trigger:
       功能
    """

    def handle_text(self, text):
        if re.search(r"定时", text):
            self.handle_schedule(text)
        elif re.search(r"快递", text):
            self.handle_package(text)
        elif re.search(r"天气", text) or re.search(r"气温", text):
            self.handle_weather(text)
        elif re.search(r"电影", text) or re.search(r"正在热映", text) or re.search(r"院线热映", text):
            self.handle_movie(text)
        elif re.search(r"功能", text):
            reply = "本机器人有如下功能:[快递查询],[天气查询],[院线热映],[设定定时任务]"
            send_msg(reply, self.user)
        else:
            reply = '机器人自动回复:' + get_response(text)
            send_msg(reply, self.user)

    """
    trigger:
       定时
    """

    def handle_schedule(self, text):
        try:
            temp = text.split('+')[1:]
            time = temp[0]
            msg = temp[1]
            name = temp[2]
            self.schedule.add_job(send_msg, 'date', run_date=time, kwargs={"msg": msg, "name": name})
            reply = '设置成功'
            self.schedule.start()
        except:
            reply = "设置定时任务请输入:定时发送+时间+msg+姓名,如：定时发送+2019-2-16 21:51:00+晚上好+filehelper"
        send_msg(reply, self.user)

    """
    trigger:
        快递
    """

    def handle_package(self, text):
        try:
            pack_num = re.search(r"(快递)(\+)([0-9]+)", text).group(3)
            reply = get_package(pack_num)
        except:
            reply = "查询快递请输入：快递+运单号，如：快递+12345"
        send_msg(reply, self.user)

    """
    trigger:
       天气
        今日天气，七日天气
    """

    def handle_weather(self, text):
        if re.search(r"今日天气", text):
            try:
                city_name = re.search(r"(今日天气)(\+)(.*)", text).group(3)
                reply = get_forecast('今日天气', city_name)
            except:
                reply = '查询今日天气请输入今日天气 + 城市名，如: 今日天气 + 西安.'
        elif re.search(r"七日天气", text):
            try:
                city_name = re.search(r"(七日天气)(\+)(.*)", text).group(3)
                reply = get_forecast('七日天气', city_name)
            except:
                reply = '查询七日天气请输入七日天气+城市名，如:七日天气+西安'
        else:
            reply = '''查询今日天气请输入今日天气+城市名，如:今日天气+西安.\n查询七日天气请输入七日天气+城市名，如:七日天气+西安。'''
        send_msg(reply, self.user)

    """
    trigger:
        电影，正在热映，院线热映
        in:
            \d 选择
            影院:（一个电影中）查看电影院，
            简介:（一个电影中）查看简介，
            l 展示列表
            q 退出

    """

    def send_list(self):
        temp = ''
        if not self.is_send_movie_list:
            for i, m in enumerate(self.movie):
                temp += f"{i+1}.{m['name']}\n"
            send_msg(temp, self.user)
            self.is_send_movie_list = True

    def handle_movie(self, text):
        self.status = Status['movie']
        self.send_list()
        if text.isdigit():
            try:
                index = int(text) - 1
                if 0 <= index < self.max_movie:
                    self.movie_index = index
                    reply1 = self.movie[index]['basic']
                    img = self.movie[index]['img']
                    send_img(img, self.user)
                    send_msg(reply1, self.user)
                else:
                    send_msg("请输入正确的数字范围1～" + str(self.max_movie), self.user)
            except:
                send_msg("请输入合法的数字1~" + str(self.max_movie), self.user)
        elif re.search(r'影院', text):
            reply2 = ''
            for i in self.movie[self.movie_index]['cinema']:
                reply2 += i + '\n'
            send_msg(reply2, self.user)
        elif re.search(r'简介', text):
            reply3 = self.movie[self.movie_index]['intro']
            send_msg(reply3, self.user)
        elif re.search(r'l', text):
            self.is_send_movie_list = False
            self.send_list()
        elif re.search(r'q', text):
            self.status = Status['init']
            self.movie_index = 0
            self.is_send_movie_list = False
