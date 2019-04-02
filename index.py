import itchat
import re
from itchat.content import TEXT
from turing import get_response
from weather import get_forecast
from package import get_package
from apscheduler.schedulers.background import BackgroundScheduler
from maoyan import MaoYan

# class WeChatBot:
#
#     def __init__(self, user):
#         self.user = user
#         self.schedule_status = 0
#     def schedule(self):
#         stage={
#             '1': '请输入年，如：2019',
#             '2': '请输入月，如：2',
#             '3': '请输入日，如：18',
#             '4': '请输入时(24小时制)，如：21',
#             '5': '请输入分，如：50',
#             '6': '请输入秒，如：6'
#         }

def main():
    schedule = BackgroundScheduler()

    def send_msg(msg, name):
        user = itchat.search_friends(name=name)
        if len(user) > 0:
            user_name = user[0]['UserName']
            itchat.send_msg(msg, toUserName=user_name)

    @itchat.msg_register(TEXT)
    def text_reply(msg):
        m = MaoYan()
        user = msg['FromUserName']
        text = msg['Text']
        if re.search(r"天气查询", text) or re.search(r"气温", text):
            reply = '''查询今日天气请输入今日天气+城市名，如:今日天气+西安.\n查询七日天气请输入七日天气+城市名，如:七日天气+西安。'''
        elif re.search(r"今日天气", text):
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
        elif re.search(r"快递", text):
            try:
                pack_num = re.search(r"(快递)(\+)([0-9]+)", text).group(3)
                reply = get_package(pack_num)
            except:
                reply = "查询快递请输入：快递+运单号，如：快递+12345"
        elif re.search(r"电影", text) or re.search(r"正在热映", text):
            try:
                reply = m.movies[0]['name']
            except:
                reply = "查询电影请输入:电影或正在热映"
        elif re.search(r"定时", text):
            try:
                temp = text.split('+')[1:]
                time = temp[0]
                msg = temp[1]
                name = temp[2]
                print(temp)
                schedule.add_job(send_msg, 'date', run_date=time, kwargs={"msg": msg, "name": name})
                reply = '设置成功'
                schedule.start()
            except:
                reply = "设置定时任务请输入:定时发送+时间+msg+姓名,如：定时发送+2019-2-16 21:51:00+晚上好+filehelper"
        elif re.search(r"功能", text):
            reply = "本机器人有如下功能:[快递查询],[天气查询],[院线热映],[设定定时任务]"

        else:
            reply = '机器人自动回复:'+get_response(text)
        itchat.send(reply, toUserName='filehelper')

    itchat.auto_login(exitCallback=schedule.shutdown)
    itchat.run()


if __name__ == '__main__':
    main()
