'''
Задание 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для
конкретного пользователя, сохранить JSON-вывод в файле *.json.
'''

import requests
import json

# Имя пользователя github
username = input("Введите имя пользователя github: ")
# url для запроса
url = f"https://api.github.com/users/{username}/repos"
# делаем запрос и возвращаем json
user_repos = requests.get(url).json()
# выводим список репозиториев (только наименования) для пользователя
for repos in user_repos:
    print(repos['name'])
# сохраняем данные в документ JSON
with open('user_repos.json', 'w') as f:
    json.dump(user_repos, f)

'''
Задание 2.  Изучить список открытых API (https://www.programmableweb.com/category/all/apis). 
Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к нему, пройдя авторизацию. 
Ответ сервера записать в файл.
Если нет желания заморачиваться с поиском, возьмите API вконтакте (https://vk.com/dev/first_guide). 
Сделайте запрос, чтобы получить список всех сообществ, на которые вы подписаны.
'''
''' проходим авторизацию в VK:
    - входим в свой аккаунт
    - создаем приложение и настраиваем следующим образом:
        - в графе «Платформа» выбираем «Standalone-приложение»
        - в строке «Состояние» выбираем «Приложение включено и видно всем»
        - в строке «Open API» выбираем «Включён»
        - добавляем «Адрес сайта» - любой, например: http://example.com
        - также указываем "Домен" в соответствии с указанным адресом сайта: example.com
        - сохраняем изменения и копируем ID приложения
    - в адрессной строке делаем запрос:
        https://oauth.vk.com/authorize?client_id=***&display=page&redirect_uri=http://example.com&scope=groups&response_type=token
        где client_id=*** - ID созданного приложения,
            redirect_uri - указанный в настройках приложения сайт
            scope=groups - то, к чему разрешается доступ приложению, по заданию нужно найти список групп(сообществ)
    - получаем токен в адрессной строке: access_token=****, копируем
    - делаем запрос:
'''
import requests
import json
from pprint import pprint
user_id = input('Введите ID пользователя: ')
token = input('Введите access_token: ')
# url для запроса
url = f'https://api.vk.com/method/groups.get?user_id={user_id}&extended=1&access_token={token}&v=5.131 HTTP/1.1'
user_groups = requests.get(url).json()
# сохраняем данные в документ JSON
with open('user_groups.json', 'w') as groups_f:
    json.dump(user_groups, groups_f)
# выводим список сообществ
for user_group in user_groups['response']['items']:
    print(user_group['name'])