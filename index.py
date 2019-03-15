from maoyan import MaoYan
from turing import get_response
from weather import get_forecast
from package import get_package


func_dict = {
    '正在热映': MaoYan,
    '图灵机器人': get_response,
    '天气查询': get_forecast,
    '快递查询': get_package
}

illustration_dict = {
    '正在热映': '输入正在热映即可查看',
    '图灵机器人': '输入图灵机器人+消息',
    '天气查询': '输入天气查询+城市名',
    '快递查询': '输入快递查询+包裹号',
    '定时发送消息': '定时发送+时间+消息+姓名'
}

