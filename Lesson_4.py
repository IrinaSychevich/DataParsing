'''
Урок 4. Система управления базами данных MongoDB в Python

Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru.
Для парсинга использовать XPath. Структура данных должна содержать:
- название источника;
- наименование новости;
- ссылку на новость;
- дата публикации.
Сложить собранные новости в БД
'''

import requests
import datetime
from lxml import html
from pymongo import MongoClient
from pprint import pprint

now = datetime.datetime.now()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0'}
response = requests.get("https://lenta.ru", headers=headers)

dom = html.fromstring(response.text)

news = []
# на странице новости можно разделить на три категории (главная новость с фото(самая большая), большие новости с фото и маленькие без фото)
news_feature = dom.xpath("//a[contains(@class,'card-feature')]")
news_big = dom.xpath("//a[contains(@class,'card-big')]")
news_mini = dom.xpath("//a[contains(@class,'card-mini')]")


categories = [news_feature, news_big, news_mini]

for category in categories:
    # теперь можно собирать данные по каждой новости по отдельным категорям
    for item in category:
        new = {}
        # заголовок
        name = item.xpath(".//h3/text()")[0]
        # ссылка (для того, чтобы все были кликабельными, для некоторых добавляем https://lenta.ru)
        link = item.xpath(".//@href")
        if 'http' in link[0]:
            link = link[0]
        else:
            link = f'https://lenta.ru{link[0]}'
        # время и дату публикации на главной странице брать трудно, поскольку публикации того же дня не содержат дату, а только время
        # поэтому переходим по ссылке и берем дату там (думаю, так избежим ошибки)
        # но если сайт сторонний, то дату и время все же берем с главной страницы lenta.ru, а в случае отстутствия даты, добавялем
        # сегодняшнюю с помощью datetime
        item_response = requests.get(link, headers=headers)
        item_dom = html.fromstring(item_response.text)
        time_date = item_dom.xpath("//a[contains(@class,'topic-header__time')]//text()")
        if len(time_date) == 0:
            time_date = item.xpath(".//time/text()")
            if len(time_date[0]) == 5:
                time_date = now.strftime(f'{time_date[0]}, %d %B %Y')
        else:
            time_date = time_date[0]
        # источник как правило это lenta.ru, в случае когда статья партнера, то  на странице lenta.ru указывается логотип,
        # из которого и извлекаем само название источника
        source = item.xpath(".//use/attribute::*")
        if len(source) == 0:
            source = 'lenta'
        else:
            source = source[0]
            source = source.split('-')[-1]

        new['name'] = name
        new['link'] = link
        new['time_date'] = time_date
        new['source'] = source

        news.append(new)

print(len(news))

# создаем подключение к базе данных
client = MongoClient('127.0.0.1', 27017)
# создаем БД 'lenta'
db = client['lenta']
# создаем коллекцию 'lenta_news'
lenta_news = db.lenta_news
# записываем данные
lenta_news.insert_many(news)
