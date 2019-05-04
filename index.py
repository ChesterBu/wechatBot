from apscheduler.schedulers.background import BackgroundScheduler
from maoyan import MaoYan
from itchatUtils import text_handler, login, run
from wechatbot import WeChatBot

def main():
    memo = {}
    init_scheduler = BackgroundScheduler()
    init_scheduler.add_job(MaoYan, 'interval', days=1)

    def clear_memo():
        memo.clear()
        init_scheduler.shutdown()

    @text_handler
    def text_reply(msg):
        user = msg['FromUserName']
        text = msg['Text']
        if memo.__contains__(user):
            memo[user].entry(text)
        else:
            memo[user] = WeChatBot(user)
            memo[user].entry(text)

    login(clear_memo)
    run()


if __name__ == '__main__':
    main()
