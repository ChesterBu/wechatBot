import random
from aiohttp import ClientSession

def get_rand(num):
    s = ""
    for i in range(num):
        n = random.randint(1, 2) #n = 1  生成数字  n=2  生成字母
        if n == 1:
            numb = random.randint(0, 9)
            s += str(numb)
        else:
            nn = random.randint(1, 2)
            cc = random.randint(1, 26)
            if nn == 1:
                numb = chr(64+cc)
                s += numb
            else:
                numb = chr(96+cc)
                s += numb
    return s


# 获取资源如文件，图片
async def fetch_res(url):
    async with ClientSession(cookies=dict(ci='42')) as session:
        async with session.get(url) as response:
            return await response.read()


# 获取文本
async def fetch(url):
    async with ClientSession(cookies=dict(ci='42')) as session:
        async with session.get(url) as response:
            return await response.text()
