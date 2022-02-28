import requests
import numpy as np
from bs4 import BeautifulSoup
import time
import random
import asyncio
from aiohttp import ClientSession
from connection import Connection

UA_List = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60',
    'Opera/8.0 (Windows NT 5.1; U; en)',
    'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0'
]

connection = Connection()
headers = {'User-Agent': random.choice(UA_List)}
category_links = []
recipe_links = []

async def getCategoryLinks():
    resp = requests.get("https://icook.tw/categories", headers=headers)
    soup = BeautifulSoup(resp.text,"html.parser")
    links = soup.find_all('a', class_='categories-all-child-link')
    for link in links:
        category_links.append("https://icook.tw" + link.get('href'))
        
    async with ClientSession() as session:
        tasks = [asyncio.create_task(getRecipeLinks(link, session)) for link in category_links]
        await asyncio.wait(tasks)

async def getRecipeLinks(link, session):
    page_num = 1
    while True:
        param = {'page': page_num}
        async with session.get(link, headers=headers, params=param) as response:
            resp = await response.text()
            if response.status == requests.codes.ok:
                soup = BeautifulSoup(resp, "html.parser")
                recipe_IDs = soup.find_all('article', class_='browse-recipe-card')

                for ID in recipe_IDs:
                    recipe_url = "https://icook.tw/recipes/" + ID.get('data-recipe-id')
                    if recipe_url not in recipe_links:
                        recipe_links.append(recipe_url)
                        connection.recordRecipeURL(recipe_url)
                        print(str(len(recipe_links)) + '\t' + recipe_url)
                        asyncio.sleep(0.1)
                page_num += 1
            else:
                break

start_time = time.time()
loop = asyncio.get_event_loop()
loop.run_until_complete(getCategoryLinks())
print("花費:" + str(time.time() - start_time) + "秒")