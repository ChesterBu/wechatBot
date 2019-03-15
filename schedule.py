import itchat
from apscheduler.schedulers.blocking import BlockingScheduler


def send_msg(msg, name):
    user = itchat.search_friends(name=name)
    if len(user) > 0:
        user_name = user[0]['UserName']
        itchat.send_msg(msg, toUserName=user_name)


def schedule_run(msg, name):
    schedule = BlockingScheduler()
    schedule.add_job(send_msg, 'date', run_date="2019-2-16 21:51:00", kwargs={"msg": msg, "name": name})
    schedule.start()
    itchat.auto_login(exitCallback=schedule.shutdown)



