import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup


async def fetch(url):
    async with ClientSession(cookies=dict(ci='42')) as session:
        async with session.get(url) as response:
            return await response.text()


async def main():
    href_list = []
    a = await fetch('https://maoyan.com/films?showType=1')
    html = BeautifulSoup(a, 'html.parser')
    hot_list = html.find_all(attrs={'class': 'channel-detail movie-item-title'})
    for child in hot_list:
        a = child.contents[1]
        href_list.append(a.get('href'))
    print(href_list)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


