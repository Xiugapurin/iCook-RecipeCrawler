import random
import time
import asyncio
from bs4 import BeautifulSoup
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
record_list = []

async def getRecipeLinks():
    task_counter = 0
    recipe_URL_list = connection.getAllRecipeURL()
    while True:
        task_list = recipe_URL_list[task_counter*25 : task_counter*25 + 25]
        task_counter += 1
        async with ClientSession() as session:
            tasks = [asyncio.create_task(getRecipeInfo(URL, session)) for URL in task_list]
            await asyncio.wait(tasks)

async def getRecipeInfo(URL, session):
    try:
        async with session.get(URL, headers=headers) as response:
            resp = await response.text()
            soup = BeautifulSoup(resp, "html.parser")
            is_continue = soup.select_one('div.ingredient-groups-open-btn-inner')

            if is_continue == None:
                title = soup.find('h1', class_='title').text.strip()
                auther = soup.find('a', class_='author-name-link').text
                try:
                    image = soup.select_one('div.recipe-cover > a').get('href')
                except:
                    image = ''
                try:
                    description = soup.select_one('div.recipe-details-header.recipe-details-block > section > p').text
                except:
                    description = ''
                try:
                    serving = soup.select_one('div.servings > span.num').text
                except:
                    serving = 0
                try:
                    time_needed = soup.select_one('div.info-content > span.num').text
                except:
                    time_needed = 0

                # 抓食材
                ingredients_list = []
                ingredients = soup.select('div.ingredient')
                for ingredient in ingredients:
                    ingredient_type = '食材'
                    ingredient_name = ingredient.select_one('a.ingredient-search').get('data-name')
                    if ingredient_name[0] == '[' and ']' in ingredient_name:
                        index = ingredient_name.find(']')
                        ingredient_type = ingredient_name[1:index]
                        ingredient_name = ingredient_name[index+2:]
                    ingredient_unit = ingredient.select_one('div.ingredient-unit').text

                    ingredients_list.append(
                        {
                            'type': ingredient_type,
                            'name': ingredient_name,
                            'unit': ingredient_unit
                        }
                    )
                
                # 抓步驟
                step_counter = 1
                step_list = []
                steps = soup.select('figure.recipe-step-instruction')
                for step in steps:
                    try:
                        step_image = step.select_one('a.recipe-step-cover.ratio-container.ratio-container-4-3.glightbox').get('href')
                    except:
                        step_image = ''
                    try:
                        step_description = step.select_one('figcaption.recipe-step-description > p').text
                    except:
                        step_description = ''
                    step_list.append(
                        {
                            'step': step_counter,
                            'image': step_image,
                            'description': step_description
                        }
                    )
                    step_counter += 1

                # 小撇步
                tip_str = ''
                tips = soup.select('blockquote.recipe-details-tip p')
                for tip in tips:
                    try:
                        tip_str += (tip.text + '\n')
                    except:
                        tip_str = ''

                # 發布時間
                release_time = soup.select_one('div.recipe-detail-metas time').get('datetime')

                info = {
                    'URL': URL,
                    'title': title,
                    'author': auther,
                    'image': image,
                    'description': description,
                    'serving': serving,
                    'time_needed': time_needed,
                    'ingredients': ingredients_list,
                    'steps': step_list,
                    'tip': tip_str,
                    'release_time': release_time
                }

                connection.insertRecipe(info)
                record_list.append(1)
                print('No. ' + str(len(record_list)) + '\tURL:' + URL)
            else:
                print('Insert failed\tURL:' + URL + '\n')
    except Exception as e:
        print('Insert failed\tURL:' + URL + '\t' , type(e), e + '\n')

start_time = time.time()
loop = asyncio.get_event_loop()
loop.run_until_complete(getRecipeLinks())
print("花費:" + str(time.time() - start_time) + "秒")
print('共紀錄 ' + len(record_list) + ' 筆')