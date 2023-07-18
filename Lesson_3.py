'''
Урок 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
которая будет добавлять только новые вакансии в вашу базу.
'''

import pymongo
import json
from pymongo import MongoClient
from pprint import pprint
from pymongo.errors import DuplicateKeyError

# создаем подключение к базе данных
client = MongoClient('127.0.0.1', 27017)
# для создания БД берем данные из домашней работы к Уроку 2
with open('job_listing.json') as json_file:
    job_listing = json.load(json_file)
# pprint(job_listing)
# создаем БД 'job'
db = client['job']
# создаем коллекцию 'vacancies'
vacancies = db.vacancies
# записываем в коллекцию данные из документа 'job_listing.json' по одному,
# пропуская вакансии с с одинаковыми данными
# создаем список 'error_vacancies', куда будем помещать дубликаты
error_vacancies = []
# на случай перезагрузки удаляем предыдущие данные
# db.drop_collection('vacancies')
# создаем уникальный индекс по трем полям: название вакансии, фирма (работодатель), местоположение работодателя
vacancies.create_index([('name', pymongo.ASCENDING), ('employer_name', pymongo.ASCENDING), ('employer_address', pymongo.ASCENDING)], unique=True)
for vacancy in job_listing:
    # удалим ID, если он есть, чтобы он заменился на сгенерированный автоматически
    if '_id' in vacancy:
        del vacancy['_id']
    try:
        vacancies.insert_one(vacancy)
    except DuplicateKeyError:
        print('Document with the same information already exists')
        # записываем в список 'error_vacancies' дубликаты
        del vacancy['_id']
        error_vacancies.append(vacancy)
# pprint(error_vacancies)
# помещаем список дубликатов в документ json
with open('error_copy_vacancies.json', 'w') as errors_f:
    json.dump(error_vacancies, errors_f)
# печатаем коллекцию 'vacancies'
for doc in vacancies.find({}):
    pprint(doc)
# считаем количество элементов в коллекции
count_db = 0
for doc in vacancies.find({}):
    count_db += 1
print(f'Количество вакансий в коллекции: {count_db}') # 683
# считаем количество повторяющихся элементов
count_dupl = len(error_vacancies) 
print(f'Количество повторяющихся вакансий: {count_dupl}') # 17
'''
Урок 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше 
введённой суммы (необходимо анализировать оба поля зарплаты, то есть цифра вводится одна, а запрос проверяет оба поля)
'''
sal = input('Введите желаемую заработную плату. От ')
vacancy = input('Введите вакансию, профессию: ') # Например: 'Аналитик маркетплейсов' (в моем БД собраны только аналитики)
def suitable_vacancy(name_vacancy, salary, collection):
# Ищем совпадение наименования вакасии и зп: минимальная больше желаемой или если не указана минимальная, то максимальная больше желаемой, или желаемая меньше максимальной, но больше минимальной
    for doc in collection.find({'$and': [{'name': name_vacancy}, {'$or': [{'salary.salary_min': {'$gt': int(salary)}}, {'$and': [{'salary.salary_min': None}, {'salary.salary_max': {'$gt': int(salary)}}]}, {'$and': [{'salary.salary_min': {'$lt': int(salary)}}, {'salary.salary_max': {'$gt': int(salary)}}]}]}]}):
        pprint(doc)
suitable_vacancy(vacancy, sal, vacancies)
