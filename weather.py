import requests
'''

{'resultcode': '200', 'reason': 'successed!',
 'result': {'sk': {'temp': '14', 'wind_direction': '东北风', 'wind_strength': '3级', 'humidity': '24%', 'time': '11:52'},
            'today': {'temperature': '4℃~19℃', 'weather': '晴', 'weather_id': {'fa': '00', 'fb': '00'}, 'wind': '东南风微风',
                      'week': '星期二', 'city': '北京', 'date_y': '2019年03月26日', 'dressing_index': '较冷',
                      'dressing_advice': '建议着大衣、呢外套加毛衣、卫衣等服装。体弱者宜着厚外套、厚毛衣。因昼夜温差较大，注意增减衣服。', 'uv_index': '中等',
                      'comfort_index': '', 'wash_index': '较适宜', 'travel_index': '较不宜', 'exercise_index': '较不宜',
                      'drying_index': ''}, 
            'future': [
                 {'temperature': '4℃~19℃', 'weather': '晴', 'weather_id': {'fa': '00', 'fb': '00'}, 'wind': '东南风微风',
                  'week': '星期二', 'date': '20190326'},
                 {'temperature': '5℃~21℃', 'weather': '多云', 'weather_id': {'fa': '01', 'fb': '01'}, 'wind': '东北风3-5级',
                  'week': '星期三', 'date': '20190327'},
                 {'temperature': '2℃~12℃', 'weather': '多云', 'weather_id': {'fa': '01', 'fb': '01'}, 'wind': '东南风微风',
                  'week': '星期四', 'date': '20190328'},
                 {'temperature': '5℃~16℃', 'weather': '多云', 'weather_id': {'fa': '01', 'fb': '01'}, 'wind': '西北风微风',
                  'week': '星期五', 'date': '20190329'},
                 {'temperature': '3℃~14℃', 'weather': '晴', 'weather_id': {'fa': '00', 'fb': '00'}, 'wind': '西北风4-5级',
                  'week': '星期六', 'date': '20190330'},
                 {'temperature': '2℃~12℃', 'weather': '多云', 'weather_id': {'fa': '01', 'fb': '01'}, 'wind': '东南风微风',
                  'week': '星期日', 'date': '20190331'},
                 {'temperature': '5℃~16℃', 'weather': '多云', 'weather_id': {'fa': '01', 'fb': '01'}, 'wind': '西北风微风',
                  'week': '星期一', 'date': '20190401'}
            ]}, 
 'error_code': 0
}

'''


def get_forecast(day_type, city_name):
    KEY = '9bdc2dd8ba279b19fb37c3c2a2e525e3'
    payload = {'format': 2, 'cityname': city_name, 'key': KEY}
    today = "今日天气:{weather},气温{temperature},紫外线强度:{uv_index},穿衣建议:{dressing_advice} "
    future = "{week}:气温{temperature},天气{weather},{wind}"
    url = 'http://v.juhe.cn/weather/index'
    weather = requests.get(url, params=payload).json()
    if weather['resultcode'] == '200':
        result = weather['result']
        if day_type == '今日天气':
            return today.format(**result['today'])
        elif day_type == '七日天气':
            temp = ''
            for i in result['future']:
                temp += future.format(**i)+'\n'
            return temp
        else:
            return '无此选项'
    else:
        return weather['reason']


if __name__ == '__main__':
    print(get_forecast('今日天气', '西安'))
    print(get_forecast('七日天气', '西安'))

    # fc = get_forecast(city)
    # print(fc)
    # # string = "今日天气:{weather},气温{temperature},紫外线强度:{uv_index},穿衣建议{dressing_advice} "
    # # print(string.format(**fc))
    #
    # string2 ="{week}:气温:{temperature},天气;{weather},{wind}"


