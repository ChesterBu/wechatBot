import itchat
from itchat.content import TEXT

text_handler = itchat.msg_register(TEXT)


def login(cb):
    itchat.auto_login(exitCallback=cb)


run = itchat.run


def send_msg(msg, name):
    itchat.send_msg(msg, toUserName=name)


def send_img(path, name):
    itchat.send_image(path, toUserName=name)

