'''
Урок 2. Парсинг данных.HTML, DOM, XPath
Необходимо собрать информацию о вакансиях на вводимую должность(используем input или через аргументы получаем должность) с
сайта HH.Приложение должно анализировать все страницы сайта. Получившийся список должен содержать в себе минимум:
- Наименование вакансии.
- Предлагаемую зарплату(разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
- Ссылку на саму вакансию.
- Сайт, откуда собрана вакансия.
По желанию можно добавить ещё параметры вакансии(например, работодателя и расположение).
Общий результат можно вывести с помощью dataFrame через pandas. Сохраните в json либо csv.
'''

from bs4 import BeautifulSoup
import requests
from pprint import pprint

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 OPR/99.0.0.0'}
params = {'page': 0, 'items_on_page': 20}
url = "https://hh.ru/search/vacancy"
vacancy = input('Введите профессию или должность: ')
session = requests.Session()
articles_list = []

while True:
    response = session.get(url + f'?text={vacancy}', headers=headers, params=params)
    soup = BeautifulSoup(response.text, "html.parser")
    # найдем блок кода со списком вакансий
    articles = soup.find_all('div', {'class': 'serp-item'})
    if not articles:
        break
    # для каждой вакансии будем искать нужную информацию
    for article in articles:
        article_info = {}
        # вся нужная инфомация для выполнения задания хранится в следующем блоке
        info = article.find('div', {'class': 'vacancy-serp-item-body__main-info'})
        # выделим название вакансии и ссылку на саму вакансию
        info_name = info.find('a')
        name = info_name.text
        link = info_name.get('href')
        # найдем информацию о зарплате
        salary_info = info.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        # инфомацию будем разбивать на блоки: минимальная и максимальная зп и валюта. Записывать будем в словарь
        salary = {}
        # если информации нет, то все поля будут None
        if salary_info is None:
            salary_min = None
            salary_max = None
            currency = None
        # если информация есть, то извлечем текст в виде списка.
        else:
            salary_info = salary_info.contents
            # Из списка удалим лишние пробелы,  которые попали в него, как отдельные элементы (например,
            # ['200000',' ', ' ', '-', ' ','500000'] --> ['200000', '-', '500000']
            salary_info = [elem for elem in salary_info if elem.strip()]
            new_salary = []
            # В случае склеивания элементов в один посредством тире разобьем один элемент на три
            # (например, '50000-80000' --> '50000', '-', '80000')
            for el in salary_info:
                if '–' in el:
                    el = el.split('–')
                    el.insert(1, '–')
                    for i in el:
                        new_salary.append(i)
                else:
                    new_salary.append(el)
            # Для элементов списка удалим лишние пробелы (например, 'от  ' вместо 'от').
            new_salary_list = []
            for el in new_salary:
                el = el.replace(' ', '')
                new_salary_list.append(el)
            salary_info = new_salary_list
            # Сделаем разбивку элементов в зависимомти от содержимого (наличия следующих слов и символо: до, от, -)
            if '–' in salary_info:
                salary_min = int(salary_info[salary_info.index('–') - 1].replace(u"\u202F", ""))
                salary_max = int(salary_info[salary_info.index('–') + 1].replace(u"\u202F", ""))
                currency = salary_info[-1]
            elif 'от' in salary_info:
                salary_min = int(salary_info[salary_info.index('от') + 1].replace(u"\u202F", ""))
                salary_max = None
                currency = salary_info[-1]
            elif 'до' in salary_info:
                salary_max = int(salary_info[salary_info.index('до') + 1].replace(u"\u202F", ""))
                salary_min = None
                currency = salary_info[-1]
            else:
                salary_min = int(salary_info[0].replace(u"\u202F", ""))
                salary_max = int(salary_info[0].replace(u"\u202F", ""))
                currency = salary_info[-1]
        salary['salary_min'] = salary_min
        salary['salary_max'] = salary_max
        salary['currency'] = currency

        # Информацию по фирме найдем следующим образом
        employer_info = info.find('div', {'class': 'vacancy-serp-item__meta-info-company'})
        employer_name = employer_info.text.replace(u'\xa0', ' ')
        employer_address = info.find('div', {'data-qa': 'vacancy-serp__vacancy-address'}).text.replace(u'\xa0', ' ')

        article_info['name'] = name
        article_info['link'] = link
        article_info['salary'] = salary
        article_info['employer_name'] = employer_name
        article_info['employer_address'] = employer_address
        articles_list.append(article_info)
    params['page'] += 1
pprint(articles_list)
print(len(articles_list))
print(params['page'])


# не нашла 'Сайт, откуда собрана вакансия'