import requests
import json


def get_response(msg):
    api = 'http://openapi.tuling123.com/openapi/api/v2'
    KEY = '6921bf7230204d0b812fa528efb302bc'
    dat = {
        "perception": {
            "inputText": {
                "text": msg
            }
        },
        "userInfo": {
            "apiKey": KEY,
            "userId": "391806"
        }
    }
    dat = json.dumps(dat)
    r = requests.post(api, data=dat).json()
    return r['results'][0]['values']['text']


if __name__ == '__main__':
    print(get_response('haha'))
