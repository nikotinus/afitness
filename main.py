# main.py
#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Предназначена для заполнения формы на сайте фитнес-клуба с использованием selenium
    Предполагается запуск по расписанию программы средствами операционной системы.
    Требуется наличие установленного браузера Chrome и скачанного вебдрайвера.

    Краткое описание:
    - проверяет наличие файла fields.txt - содержит информацию о том, что надо будет
    вводить в вебформу
    - при отсутствии - просит пользователя внести данные, создает файл
    - открывает браузер, находит последовательного заданные элементы, заполняет соответсвующие поля.

    !!!ВНИМАНИЕ!!!
    Если третья строка в файле "fields.txt" содержит 'automate', то на последнем шаге будет нажата
    кнопка ОТПРАВИТЬ.
    Если строка незаполнена или содержит любое другое слово, то программа работает в тестовом режиме:
    - откроет зал баскетбол в  воскресенье
    - кнопка ОТправить активна, но автоматически не нажата
"""
import logging
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import random as rnd
import os
from name_input import get_fields


logging.basicConfig(
    format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level=logging.DEBUG, filename='logs.log')


def main():
    # задаем файл с данными для заполнения
    fields = "fields.txt"
    # проверяем наличие файла в папке с файлом программы
    try:
        if not os.path.isfile(fields):
            msg = "Отсутствует файл с именем и телефоном (файл с данными)"
            logging.debug(msg)

            if get_fields(fields):
                msg = "Данные для заполнения внесены пользователем"
                logging.info(msg)
            else:
                msg = "Функция get_fileds вернула False"
                logging.error(msg)
                return False, False
        else:
            msg = "Файл с данными существует"
            logging.info(msg)
    except Exception:
        msg = "Ошибка при заполнении данных пользователем"
        logging.error(msg)

    try:
        # читаем поля из файла
        with open(fields, 'r') as f:
            name_ = f.readline().split('\n')[0]
            phone = f.readline().split('\n')[0]
            activity = f.readline().split('\n')[0]
            flag = f.readline().split('\n')[0]
        msg = f"Прочитали параметры: \nИмя: {name_}\nТелефон: {phone}\nСпортзал: {activity}\nФлаг: {flag}"
        logging.info(msg)
    except Exception:
        msg = "Проблемы с открытием файла. Возможно, требуется повторно запустить name_input.py"
        logging.error(msg)
        return False, flag
    try:
        driver = webdriver.Chrome()
        msg = "Найден файл с драйвером"
        logging.debug(msg)
    except Exception:
        msg = "Не удалось найти драйвер Chrome - надо разместить его в папке с основным файлом"
        logging.error(msg)

    url = "https://spb.afitness.ru/dalnevostochniy/timetable"
    desires_title = "Расписание занятий в A-Fitness Дальневосточный в Санкт-Петербурге"
    try:
        driver.get(url)
        attempt = 0
        max_attempt = 2
        while driver.title != desires_title and attempt <= max_attempt:
            sleep(5)
            driver.get(url)
            attempt += 1
        msg = f"Предпринято {attempt} попыток для открытия url."
        logging.debug(msg)
        if attempt > max_attempt:
            msg = f"Количество попыток {attempt} превысило максимально допустимое {max_attempt}"
            logging.error(msg)
            raise Exception
        msg = f'Открыт заданный url: {url}'
        logging.info(msg)
    except Exception:
        msg = f'Проблемы при открытии целевого url: {url}'
        logging.error(msg)
        driver.close()
        return False, flag

    try:
        driver.switch_to.window(driver.window_handles[0])
        msg = "Переключились в активное окно"
        logging.info(msg)

    except Exception:
        msg = "Не смогли переключитьcя в окно"
        logging.error(msg)
        driver.close()
        return False, flag

    # Переключаемся на основную рамку
    try:
        iframe = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.TAG_NAME, 'iframe')))
        driver.switch_to.frame(iframe)
        msg = "Переключились на нужный фрейм"
        logging.info(msg)
    except Exception:
        msg = "Не смогли переключиться в искомый фрейм"
        logging.error(msg)
        driver.close()
        return False, flag

    # задаем путь до элементов с залом бадминтона и волейбола
    path_badminton = '//*[@id="fitness-widget-club-tab-0"]/div[6]/table/tbody/tr[15]/td[5]/div'
    # path_voleyboll = '//*[@id="fitness-widget-club-tab-0"]/div[6]/table/tbody/tr[14]/td[6]/div[3]'
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
        logging.error(msg)
        driver.close()
        return False, flag

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
        logging.error(msg)
        driver.close()
        return False, flag

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
        return False, flag
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
        logging.error(msg)
        driver.close()
        return False, flag
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
        return False, flag

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
            logging.error(msg)
            driver.close()
            return False, flag
        try:
            # находим кнопку отправить
            send_button = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.ID, 'preentry_appl_submit')))
            send_button.click()
            msg = "Нажата кнопка Отправить"
            logging.info(msg)
        except Exception:
            msg = "Не смогли нажать кнопку Отправить"
            logging.error(msg)
            driver.close()
            return False, flag
        try:
            # переименовываем файл с полями
            old_name = os.path.normpath(os.path.join(
                os.path.abspath(os.path.dirname(__file__)), fields))
            new_name = os.path.normpath(os.path.join(
                os.path.abspath(os.path.dirname(__file__)), 'send_' & fields))
            os.rename(old_name, new_name)
            msg = "Переименован файл с данными"
            logging.error(msg)
        except Exception:
            msg = " Не смогли переименовать файл с данными"
            logging.error(msg)
            return False, flag
    else:
        timeout = 10
        msg = "Флаг установлен в ручной режим. У пользователя есть {timeout} секунд на нажатие кнопки Отправить"
        logging.info(msg)
        sleep(timeout)
        msg = "{timeout} секунд истекли. Закрываем браузер"
        logging.info(msg)
    driver.close()
    return True, flag


if __name__ == '__main__':
    main_attempt = 0
    main_max_attempt = 3
    result = False
    while not result and main_attempt < main_max_attempt:
        main_attempt += 1
        msg = "______________________________________________________________________________________________\n"
        msg += f"Начата попытка №{main_attempt}"
        logging.info(msg)
        result, flag = main()

    if main_attempt > main_max_attempt:
        msg = f"За заданные {main_max_attempt} попытки не удалось заполнить форму"
        logging.error(msg)
    if result:
        msg = f'Форма успешно заполнена. Флаг на отправку установлен: {flag}'
        logging.info(msg)
    else:
        msg = f'На каком-то из этапов произошла ошибка'
        logging.critical(msg)
