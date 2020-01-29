# main.py
#!/usr/bin/python
#-*- coding: utf - 8 - *-
version = 3.0
updates = f"""
** {version}:
- рефакторинг кода для обработки ситуации, когда пользователь отдельно открыл файл с данными до начала работы программы

** 2.3:
- исправлен блок адресации на всплывыающее окно и поиск текста о количестве свободных мест (оказалось,
  что это два разных адреса - "свободные места" и "отсутствие свободных мест")

** 2.2:
- в запись инструкции добавлена строка с версией программы
- блок контроля всплывающего окна вынесен из блока try - except
- актуализирована запись в лог под произведенные изменения

** 2.1:
- внесены мелкие правки в запись лога, форматирование, текстовка
- добавлен контроль нажатия на окно
"""
instr = f'''
    Версия программы: {version}
    Предназначена для заполнения формы на сайте фитнес-клуба с использованием selenium
    Предполагается запуск по расписанию программы средствами операционной системы.
    Требуется наличие установленного браузера Chrome и скачанного вебдрайвера.

    Краткое описание:
    - проверяет наличие файла fields.txt - содержит информацию о том, что надо будет
    вводить в вебформу
    - при отсутствии - просит пользователя внести данные, создает файл
    - открывает браузер, находит последовательного заданные элементы, заполняет соответсвующие поля.
    - если флаг установлен в автомат и кнопка Отправить нажата, то переименовывает файл fields.txt для исключения
      возможности повторной отправки
    !!!ВНИМАНИЕ!!!
    Если четвертая строка в файле "fields.txt" содержит 'automate', то на последнем шаге будет нажата
    кнопка ОТПРАВИТЬ.
    Если строка не заполнена или содержит любое другое слово, то программа работает в тестовом режиме:
    - откроет зал баскетбол в  воскресенье
    - кнопка ОТправить активна, но автоматически не нажата
'''
import logging
from multiprocessing import Queue
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import random as rnd
import os
from name_input import get_fields, rename_fields

log_format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'
log_level = logging.INFO
log_file_name = 'logs.log'
logging.basicConfig(format=log_format, level=log_level, filename=log_file_name)


def main(file: str=None, max_attempt=5):
    if file is None:
        file = 'fields.txt'

    data_exist = check_data_existance(file)

    if not data_exist:
        data_exist = create_data(filename=file)

    if not data_exist:
        msg = "Ошибка при создании файла с данными"
        logging.error(msg)
        return False

    fields = extract_data(file)
    if not fields:
        msg = f"Ошибка при извлечении данных из файла {file}"
        logging.error(msg)
        return False

    att = 1
    att_print_pattern = f'{att}-----'
    msg = f'{att_print_pattern*13}{att}'
    logging.info(msg)
    form_fullfilled = fill_form(data=fields)

    next_try = 'try again'
    while form_fullfilled == next_try and attempt <= max_attempt:
        att += 1
        msg = f'{att_print_pattern*10}{att}'
        logging.info(msg)
        form_fullfilled = fill_form(data=fields)
        if not form_fullfilled:
            msg = f"Ошибка при заполнении формы данными {fields}"
            logging.error(msg)
            return False

    if not form_fullfilled:
        msg = f"Ошибка при заполнении формы данными {fields}"
        logging.error(msg)
        return False

    if att > max_attempt:
        msg = f'Количество попыток {att} превысило допустимое: {max_attempt}.'
        logging.info(msg)

    return True


def check_data_existance(filename: str) -> bool:
    #  проверяем наличие файла в корне программы
    try:
        if not os.path.isfile(filename):
            msg = "Отсутствует файл с именем и телефоном (файл с данными)"
            logging.debug(msg)
            return False
        msg = "Файл с данными существует"
        logging.info(msg)
        return True
    except Exception:
        msg = "Ошибка при проверке наличия файла в корне программы"
        logging.error(msg)
        return False


def create_data(filename: str) -> bool:
    name = input("Введи имя, которое хочешь заполнить в веб-форму: ")
    phone = input(
        "Введи номер телефона, который хочешь заполнить в веб-форму: ")
    badminton = input("Введи 1, чтобы Записаться на Бадминтон: ")
    flag = input("Введи 1, чтобы кнопка Отправить нажалась автоматически: ")

    try:
        with open(filename, 'w') as f:
            f.write(name)
            f.write('\n')
            f.write(phone)
            f.write('\n')
            f.write('badminton' if badminton == "1" else 'basketball')
            f.write('\n')
            f.write('automate' if flag == "1" else 'manually')
        return True
    except Exception:
        filename = os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), filename))
        os.remove(filename)
        return False


def extract_data(filename: str) -> dict:
    try:
        # читаем поля из файла
        with open(filename, 'r') as f:
            name_ = f.readline().split('\n')[0]
            phone = f.readline().split('\n')[0]
            activity = f.readline().split('\n')[0]
            flag = f.readline().split('\n')[0]
        msg = f"Прочитали параметры: \nИмя: {name_}\nТелефон: {phone}\nСпортзал: {activity}\nФлаг: {flag}"
        logging.info(msg)
        return {
            'name': name_,
            'phone': phone,
            'activity': activity,
            'flag': flag,
        }
    except Exception:
        msg = f"Проблемы с открытием файла {filename}"
        logging.error(msg)
        return False


def fill_form(data: dict) -> bool or str:
    if not isinstance(data, dict):
        msg = f'На вход процедуре ожидается словарь, получен {type(data)}'
        logging.error(msg)
        return False
    check_list = ('name', 'phone', 'activity', 'flag')
    for item in check_list:
        if not (item in data):
            msg = f'В полученном на вход словаре {data} отсутствует ключ {item}'
            logging.error(msg)
            return False
    name_ = data['name']
    phone = data['phone']
    activity = data['activity']
    flag = data['flag']

    next_try = 'try again'

    try:
        driver = webdriver.Chrome()
        msg = "Найден файл с драйвером"
        logging.debug(msg)
    except Exception:
        msg = "Не удалось найти драйвер Chrome - надо разместить его в папке с основным файлом"
        logging.error(msg)
        return False

    url = "https://spb.afitness.ru/dalnevostochniy/timetable"
    desired_title = "Расписание занятий в A-Fitness Дальневосточный в Санкт-Петербурге"
    try:
        driver.get(url)
        msg = f'Открыт заданный url: {url}'
        logging.info(msg)
    except Exception:
        msg = f'Проблемы при открытии целевого url: {url}'
        logging.info(msg)
        sleep(3)
        driver.close()
        return next_try

    if driver.title != desired_title:
        msg = f"Название открытого url {driver.title} отличается от ожидаемого {desired_title}"
        logging.error(msg)
        return False

    try:
        driver.switch_to.window(driver.window_handles[0])
        msg = "Переключились в активное окно"
        logging.info(msg)
    except Exception:
        msg = "Не смогли переключитьcя в окно"
        logging.info(msg)
        driver.close()
        return next_try

    # Переключаемся на основную рамку
    try:
        iframe = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.TAG_NAME, 'iframe')))
        driver.switch_to.frame(iframe)
        msg = "Переключились на нужный фрейм"
        logging.info(msg)
    except Exception:
        msg = "Не смогли переключиться в искомый фрейм"
        logging.info(msg)
        driver.close()
        return next_try

    # задаем путь до элементов с залом бадминтона и волейбола
    path_badminton = '//*[@id="fitness-widget-club-tab-0"]/div[6]/table/tbody/tr[15]/td[5]/div'
    path_basketball = '//*[@id="fitness-widget-club-tab-0"]/div[6]/table/tbody/tr[13]/td[8]/div'

    main_path = path_badminton if activity == 'badminton' else path_basketball
    holl_name = "Бадминтон" if activity == 'badminton' else "Баскетбол"
    msg = f"Будем искать зал {holl_name}"
    logging.info(msg)

    try:
        sportzal = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, main_path)))
        sleep(1)
        sportzal.click()
        msg = f'Кликнули спортзал {holl_name}'
        logging.info(msg)
    except Exception:
        msg = f"Не смогли кликнуть в спортзал {holl_name}"
        logging.info(msg)
        driver.close()
        return next_try

    # проверяем появление открытого окна
    zal_title_path = '//*[@id="fitness-widget-popup"]/div/div[2]'
    popup_name = ""
    try:
        zal_popup = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, zal_title_path)))
        msg = f'Открылось всплывающее окно "{holl_name} клиенты"'
        logging.info(msg)
    except Exception:
        msg = "Не удалось аллоцировать всплывающее окно зала"
        logging.info(msg)

        try:
            sportzal.click()
            msg = f'Повторно кликнули спортзал {holl_name}'
            logging.info(msg)
            zal_popup = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, zal_title_path)))
            msg = f'Открылось всплывающее окно "{holl_name} клиенты"'
            logging.info(msg)
        except Exception:
            msg = f"Повторно не удалось аллоцировать всплывающее окно зала"
            logging.info(msg)
            driver.close()
            return next_try

    popup_name = zal_popup.text.split()[0].lower()
    if popup_name != holl_name.lower():
        msg = f'Имя всплывающего окна отличается от "{holl_name} клиенты"'
        logging.error(msg)
        driver.close()
        return False

    no_place_path = '//*[@id="fitness-widget-popup"]/div/div[4]/div[2]/p[7]'
    try:
        no_place = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, no_place_path)))
        msg = f"{no_place.text}"
        logging.info(msg)
        msg = "Отсутствуют свободные места"
        logging.info(msg)
        driver.close()
        return True
    except Exception:
        msg = f'Не удалось определить блок отсутствия свободных мест по адресу: {no_place_path}'
        logging.info(msg)

    available_path = '//*[@id="fitness-widget-popup"]/div/div[4]/div[2]/p[1]'
    try:
        available = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, available_path)))
        msg = f'Определили блок с указанием количества свободных мест: {available.text}'
        logging.info(msg)
    except Exception:
        msg = f'Не удалось определить блок с указанием количества свободных мест по адресу: {available_path}'
        logging.info(msg)
        driver.close()
        return next_try

    # находим путь до полей с именем и номером телефона
    path_name = '//input[@id="preentry_appl_name"]'
    path_phone = '//input[@id="preentry_appl_phone"]'

    try:
        # определяем поле с именем
        web_element_name = WebDriverWait(driver, 40).until(
            EC.visibility_of_element_located((By.XPATH, path_name)))
        web_element_name.click()
        msg = "Зашли в форму для ввода имени"
        logging.info(msg)
        sleep(1)
    except Exception:
        msg = 'Не смогли активировать поле имени'
        logging.info(msg)
        driver.close()
        return next_try

    try:
        # заполняем имя
        for letter in name_:
            sleep(0.5)
            sleep(rnd.random())
            web_element_name.send_keys(letter)
        msg = 'Заполнено поле Имя'
        logging.info(msg)
    except Exception:
        msg = 'Не смогли заполнить поле Имя'
        logging.error(msg)
        driver.close()
        return False

    # определяем поле с номером телефона
    try:
        web_element_phone = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, path_phone)))
        web_element_phone.click()
        msg = "Зашли в форму для ввода телефона"
        logging.info(msg)
        sleep(1)
    except Exception:
        msg = 'Не смогли активировать поле Телефон'
        logging.info(msg)
        driver.close()
        return next_try

    # заполняем телефон
    try:
        for letter in phone:
            sleep(0.5)
            sleep(rnd.random())
            web_element_phone.send_keys(letter)
        msg = "Заполнено поле Телефон"
        logging.info(msg)
    except Exception:
        msg = "Не смогли заполнить поле Телефон"
        logging.error(msg)
        driver.close()
        return False

    if flag == 'automate':
        msg = 'Флаг установлен в Автомат. Начали попытку нажатия кнопки Отправить'
        logging.info(msg)
        try:
            # находим чекбокс с правилами
            checkbox = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'popup-rules-state')))
            checkbox.click()
            msg = "Установлен чекбокс на Согласие"
            logging.info(msg)
        except Exception:
            msg = "Не смогли установить чекбокс на Согласие с обработкой персональных данных"
            logging.info(msg)
            driver.close()
            return next_try
        try:
            # находим кнопку отправить
            send_button = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.ID, 'preentry_appl_submit')))
            send_button.click()
            msg = "Нажата кнопка Отправить"
            logging.info(msg)
            driver.close()
            return True
        except Exception:
            msg = "Не смогли нажать кнопку Отправить"
            logging.info(msg)
            driver.close()
            return next_try
    else:
        timeout = 10
        msg = f"Флаг установлен в ручной режим. У пользователя есть {timeout} секунд на нажатие кнопки Отправить"
        logging.info(msg)
        sleep(timeout)
        msg = f"{timeout} секунд истекли. Закрываем браузер"
        logging.info(msg)
        driver.close()
        return True

    if driver:
        driver.close()
        msg = f'Драйвер остался открытым!'
        loggin.critical(msg)
        return False


def rename_data_filename(filename: str) -> bool:
    try:
        # переименовываем файл с полями
        old_name = os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), filename))
        msg = f'Прежнее имя файла: {old_name}'
        logging.info(msg)
    except Exception:
        msg = "Не смогли определить прежнее имя"
        logging.error(msg)

    try:
        new_name = os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 'send_' & filename))
        msg = f'new_name: {new_name}'
        logging.info(msg)
    except Exception:
        msg = "Не смогли задать новое имя"
        logging.error(msg)
    try:
        os.rename(old_name, new_name)
        msg = "Переименован файл с данными"
        logging.info(msg)
    except Exception:
        msg = " Не смогли переименовать файл с данными"
        logging.error(msg)


if __name__ == '__main__':
    msg = f"\n\n------------------------------------------------------------------------------------------------------------\n"
    msg += instr
    logging.info(msg)
    filename = 'fields.txt'
    try:
        result = main(file=filename, max_attempt=6)
    except Exception:
        msg = f'Что-то произошло вне основной процедуры'
        logging.critical(msg)
        result = False

    if not result:
        msg = f'На каком-то из этапов заполнения формы произошла ошибка. Смотри лог выше'
        logging.critical(msg)
    else:
        rename_data_filename(filename)

    print(f"Логи записаны в файл: {log_file_name}")
