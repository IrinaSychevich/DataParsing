'''
Урок 5. Парсинг данных. Scrapy. Начало
2) Написать программу, которая собирает товары «В тренде» с сайта техники mvideo и складывает данные в БД.
Сайт можно выбрать и свой. Главный критерий выбора: динамически загружаемые товары'''
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
from pprint import pprint

# скачаем chrome-драйвер и поместим в папку проекта
# создадим сервисный объект, в котором указан путь к chrome-драйверу
s = Service('./chromedriver.exe')
# добавим опцию открытия полноэкранного режима браузера
chromeOptions = Options()
chromeOptions.add_argument('start-maximized')
# создадим объект драйвера на основании браузера
driver = webdriver.Chrome(service=s, options=chromeOptions)
# добавим время ожидания, на случай медленной прогрузки страницы
driver.implicitly_wait(20)
# указываем страницу
driver.get("https://www.mvideo.ru")
# прокрутим страницу до товаров, относящихся к группе "Хиты продаж", через шаг у = 500
premium = []
while len(premium) != 1:
    try:
        category = driver.find_element(By.XPATH, '//h2[text()="Хиты продаж"]/parent::*//mvid-product-cards-group')
        premium.append(category)
    except:
        actions = ActionChains(driver)
        actions.scroll_by_amount(0, 500).perform()
        time.sleep(2)

# не знаю почему, но у меня не открывались ссылки на товары, окно появлялось, но в нем была ошибка(блокировка)
# либо страница не прогружалась, даже если поставить значительный time.sleep
# поэтому информацию извлекала с главной страницы
products_name = category.find_elements(By.CLASS_NAME, 'product-mini-card__name')
products_price = category.find_elements(By.CLASS_NAME, 'price__main-value')
products_info = []
for i in range(len(products_name)):
    info = {}
    name = products_name[i].find_element(By.XPATH, './/a').text
    price = products_price[i].text
    info['name'] = name
    info['price'] = price
    products_info.append(info)
print(products_info)
# создаем подключение к базе данных
client = MongoClient('127.0.0.1', 27017)
# создаем БД 'mvideo'
db = client['mvideo']
# создаем коллекцию 'products'
products = db.products
# записываем данные
products.insert_many(products_info)
for product in products.find({}):
    pprint(product)