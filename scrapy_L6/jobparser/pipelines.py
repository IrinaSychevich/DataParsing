# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from pymongo import MongoClient

class JobparserPipeline:
    def __init__(self):
        client = MongoClient(host='localhost', port=27017)
        self.mongo_base = client.vacancy27017
    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        item = self.salary_item(item)
        collection.insert_one(item)
        return item

    def salary_item(self, item):
        # информативными будут данные содержащие более 1 элемента (Например, "по договоренности" не несет никакой конкретики и равно ничему)
        if len(item['salary']) > 1:
            # Из списка удалим лишние пробелы,  которые попали в него, как отдельные элементы (например,
            # ['от', '200000',' ', 'до', ' ', '500000'] --> ['от','200000', 'до', '500000']
            item['salary'] = [elem for elem in item['salary'] if elem.strip()]
            # Для элементов списка удалим лишние пробелы (например, 'от' вместо 'от ').
            new_salary_list = []
            for el in item['salary']:
                el = el.replace(' ', '')
                new_salary_list.append(el)
            item['salary'] = new_salary_list
            # удалим из списка слово 'месяц', как само собой разумеющееся
            if 'месяц' in item['salary']:
                item['salary'].remove('месяц')
            new_salary = []
            # Удалим элементы '\xa0'
            if '\xa0' in item:
                item['salary'].remove('\xa0')
            # В случае склеивания элементов посредством '\xa0' разобьем один элемент на три
            # (например, '180\xa0000\xa0₽' --> '180\xa0000', '\xa0', '₽')
            for el in item['salary']:
                if '\xa0' in el:
                    el = el.split('\xa0')
                    new_el = []
                    cur = ''
                    for i in el:
                        try:
                            int(i)
                            new_el.append(i)
                        except:
                            cur = i
                    el = ''.join(map(str, new_el))
                    new_salary.append(el)
                    if len(cur) != 0:
                        new_salary.append(cur)
                else:
                    new_salary.append(el)
            item['salary'] = new_salary
            # Сделаем разбивку элементов в зависимомти от наличия следующих слов: до, от
            if ('от' in item['salary']) and ('до' in item['salary']):
                salary_min = int(item['salary'][item['salary'].index('от') + 1])
                salary_max = int(item['salary'][item['salary'].index('до') + 1])
                currency = item['salary'][-1]
            elif ('от' in item['salary']) and ('до' not in item['salary']):
                salary_min = int(item['salary'][item['salary'].index('от') + 1])
                salary_max = None
                currency = item['salary'][-1]
            elif ('от' not in item['salary']) and ('до' in item['salary']):
                salary_min = None
                salary_max = int(item['salary'][item['salary'].index('до') + 1])
                currency = item['salary'][-1]
            elif '—' in item['salary']:
                salary_min = int(item['salary'][item['salary'].index('—') - 1])
                salary_max = int(item['salary'][item['salary'].index('—') + 1])
                currency = item['salary'][-1]
        else:
            salary_min = None
            salary_max = None
            currency = None
        item['salary_min'] = salary_min
        item['salary_max'] = salary_max
        item['salary_cur'] = currency
        del item['salary']
        return item

