'''
Урок 5. Парсинг данных. Scrapy. Начало
Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить данные о письмах
в базу данных (от кого, дата отправки, тема письма, текст письма полный)
Логин тестового ящика: study.ai_172@mail.ru
Пароль тестового ящика: NextPassword172#'''

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from pymongo import MongoClient
from pprint import pprint

# скачаем chrome-драйвер и поместим в папку проекта
# создадим сервисный объект, в котором указан путь к chrome-драйверу
s = Service('./chromedriver.exe')
# добавим опцию открытия полноэкранного режима браузера
chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_argument('--start-maximized')
# создадим объект драйвера на основании браузера
driver = webdriver.Chrome(service=s, options=chromeOptions)
# добавим время ожидания, на случай медленной прогрузки страницы
driver.implicitly_wait(10)
# указываем страницу
driver.get("https://account.mail.ru")
# найдем на странице элемент для ввода логина и зададим значение, затем нажмем Enter, затем то же самое для пароля
elem = driver.find_element(By.NAME, 'username')
elem.send_keys("study.ai_172@mail.ru")
elem.send_keys(Keys.ENTER)
elem = driver.find_element(By.NAME, 'password')
elem.send_keys("NextPassword172#")
elem.send_keys(Keys.ENTER)
# найдем общее количество входящих писем, для этого нажмем на кнопку "Выделить все", на месте кнопки появится текст с количеством всех писем
elem = driver.find_element(By.XPATH, '//span[contains(@class,"button2_select-all")]')
elem.click()
num = driver.find_element(By.XPATH, '//span[contains(@class,"button2_select-all")]//div').text
num = int(num)
# создадим список, куда будем вносить новые письма (как объекты). В дальнейшем будем переходить на новые вкладки,
# поэтому необходимо зафиксировать информацию о полученных объектах в данный список
# и создадим список, в который будем записывать информацию о письмах
all_letters = []
letter_info = []
# скролить страницу будем до тех пор, пока не соберем информацию по всем письмам
while len(all_letters) != num:
    # найдем отдельные письма
    letters = driver.find_elements(By.XPATH, '//a[contains(@class,"js-tooltip-direction_letter-bottom")]')
    # обозначим текущую страницу как главную
    main_window = driver.current_window_handle
    # будем открывать в новом окне каждое письмо. Из-за того, что подгружается больше писем, чем есть, (а скролит по последнему, что есть на странице,
    # а не тому, что подгрузил) ставим условие уникальности.
    for letter in letters:
        if letter not in all_letters:
            all_letters.append(letter)
            letter.send_keys(Keys.CONTROL + Keys.RETURN)
    # переходим к каждому открытому письму и собираем информацию (одновременно открыто около 10-20 писем), затем закрываем страницу
    for window_handle in driver.window_handles:
        if window_handle != main_window:
            info = {}
            driver.switch_to.window(window_handle)
            date_letter = driver.find_element(By.CLASS_NAME, 'letter__date').text
            name_letter = driver.find_element(By.CLASS_NAME, 'thread__subject-line').text
            sender_letter = driver.find_element(By.CLASS_NAME, 'letter-contact').text
            text_letter = driver.find_element(By.CLASS_NAME, 'letter__body').text

            info['date_letter'] = date_letter
            info['name_letter'] = name_letter
            info['sender_letter'] = sender_letter
            info['text_letter'] = text_letter
            letter_info.append(info)
            driver.close()
    # обозначаем, что вернулись на главную страницу
    driver.switch_to.window(main_window)
    # пролистываем вниз до последнего элемента занесенного в список и повторяем цикл
    actions = ActionChains(driver)
    actions.move_to_element(all_letters[-1])
    actions.perform()

# создаем подключение к базе данных
client = MongoClient('127.0.0.1', 27017)
# создаем БД 'mail_ru'
db = client['mail_ru']
# создаем коллекцию 'incoming_emails'
incoming_emails = db.incoming_emails
# записываем данные
incoming_emails.insert_many(letter_info)
for letter in incoming_emails.find({}):
    pprint(letter)
