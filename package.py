import json
import requests


def get_package(package):
    try:
        url1 = 'http://www.kuaidi100.com/autonumber/autoComNum?resultv2=1&text=' + package
        companyName = json.loads(requests.get(url1).text)['auto'][0]['comCode']
        url2 = 'http://www.kuaidi100.com/query?type=' + companyName + '&postid=' + package
        details = "时间↓--地点和跟踪进度↓\n"
        for item in json.loads(requests.get(url2).text)['data']:
            details += item['time']+item['context']+'\n'
        return details
    except Exception as e:
        details = "运单号码有误"+repr(e)
    finally:
        return details or '查无此单'


if __name__ == "__main__":
    print(get_package(package='75127612798169'))
