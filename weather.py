import requests


def get_forecast(city_name):
    KEY = '9bdc2dd8ba279b19fb37c3c2a2e525e3'
    payload = {'format': 2, 'cityname': city_name, 'key': KEY}
    weather = requests.get('http://v.juhe.cn/weather/index', params=payload).json()
    if weather.status_code == '200':
        return weather['result']['today']
    else:
        return 404


if __name__ == '__main__':
    city = '北京'
    fc = get_forecast(city)
    string = "今日天气:{weather},气温{temperature},紫外线强度:{uv_index},穿衣建议{dressing_advice} "
    print(string.format(**fc))
