import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# def parse_info(data):
#     info = data.split('\n')
#     line = info[3] if info[2].count('Режиссёр') == 0 else info[2]
#     style = line[line.find('•')+2: line.find('Режиссёр')-2]
#     country = line[: line.find('•')-1]
#     line = info[2][2:] if info[2][0] == ',' else info[1]
#     year = int(line[: line.find(',')])
#     return {'id': kino_id, 'name': info[0], 'style': style, 'country': country, 'year': year}


options = webdriver.ChromeOptions()
# options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


# kino_id = 10000
# for i in range(1, 31):
#     driver.get(f'https://www.kinopoisk.ru/lists/movies/genre--animation/?sort=votes&b=films&page={i}')
#     time.sleep(0.3)
#
#     table = driver.find_elements(By.CLASS_NAME, value='styles_main__Y8zDm')
#
#     for e in table:
#         try:
#             kino = parse_info(e.text)
#             db.add_kino(kino)
#         except Exception as e:
#             print(e)
#         finally:
#             kino_id += 1
#
#     print(i)

for i0, a in enumerate([]):
    try:
        os.mkdir(f'images_kinopoisk/{a["id"]}')
    except:
        print(end='.')
        continue
    driver.get(f'https://yandex.ru/images/search?from=tabbar&text={a["name"]}+мультфильм')
    img_list = driver.find_elements(By.CLASS_NAME, value='serp-item__link')[:5]
    for i, el in enumerate(img_list):
        link = el.find_element(By.TAG_NAME, value='img').get_property('src')
        img = requests.get(link)
        with open(f'{a["id"]}/{i + 1}.jpg', 'wb') as f:
            f.write(img.content)
    print(i0)