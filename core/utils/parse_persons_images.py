import os
import asyncio
import time

import requests
from environs import Env
from selenium.webdriver import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from core.utils.database import get_connector, get_persons

env = Env()
env.read_env()
images = set(os.listdir('../static'))
persons = {}
caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "eager"
options = webdriver.ChromeOptions()
# options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


async def load_persons():
    global persons
    conn = await get_connector()
    persons.update(await get_persons(conn))


asyncio.run(load_persons())
for hero in persons.values():
    if hero + '.jpg' not in images:
        driver.get(f'https://yandex.ru/images/search?from=tabbar&text={hero}+персонаж')
        n = int(input())
        image = driver.find_elements(By.CLASS_NAME, value='SerpItem')[n]
        link = image.find_element(By.TAG_NAME, value='img').get_property('src')
        img = requests.get(link)
        with open(f'../static/{hero}.jpg', 'wb') as f:
            f.write(img.content)
