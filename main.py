"""
    Предназначена для заполнения формы на сайте фитнес-клуба с использованием selenium
    Предполагается запуск по расписанию программы средствами операционной системы.
    Требуется наличие установленного браузера Chrome и скачанного вебдрайвера.

    Краткое описание:
    - проверяет наличие файла fields.txt - содержит информацию о том, что надо будет
    вводить в вебформу
    - при отсутствии - просит пользователя внести данные, созадет файл
    - открывает браузер, находит последовательного заданные элементы, заполняет соответсвующие поля.

    !!!ВНИМАНИЕ!!!
    Если третья строка в файле "fields.txt" содержит 'automate', то на последнем шаге будет нажата
    кнопка ОТПРАВИТЬ.
    Если строка незаполнена или содержит любое другое слово, то программа работает в тестовом режиме:
    - откроет зал баскетбол в  воскресенье
    - кнопка ОТправить активна, но автоматически не нажата
"""

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import random as rnd
import os.path
from name_input import get_fields


def main():
    if not os.path.isfile("fields.txt"):
        get_fields()

    try:
        # читаем поля из файла
        with open('fields.txt', 'r') as f:
            name_ = f.readline()
            phone = f.readline()
            flag = f.readline()
    except Exception:
        print("Проблемы с открытием файла. Возможно, требуется повторно запустить name_input.py")

    driver = webdriver.Chrome()
    url = "https://spb.afitness.ru/dalnevostochniy/timetable"
    desires_title = "Расписание занятий в A-Fitness Дальневосточный в Санкт-Петербурге"
    driver.get(url)
    attempt = 1
    while driver.title != desires_title and attempt < 5:
        sleep(5)
        driver.get(url)
        attempt += 1
    if attempt > 5:
        driver.close()
        raise Exception(
            f'I tried {attempt} times to get the desired url. All of them where failed.')

    driver.switch_to.window(driver.window_handles[0])

    # Переключаемся на основную рамку
    iframe = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.TAG_NAME, 'iframe')))
    driver.switch_to.frame(iframe)

    # задаем путь до элементов с залом бадминтона и волейбола
    path_badminton = '//*[@id="fitness-widget-club-tab-0"]/div[6]/table/tbody/tr[15]/td[5]/div'
    path_voleyboll = '//*[@id="fitness-widget-club-tab-0"]/div[6]/table/tbody/tr[14]/td[6]/div[3]'
    path_basketball = '//*[@id="fitness-widget-club-tab-0"]/div[6]/table/tbody/tr[13]/td[8]/div'

    main_path = path_badminton if flag == 'automate' else path_basketball

    sportzal = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, main_path)))
    sportzal.click()

    # находим путь до полей с именем и номером телефона
    path_name = '//input[@id="preentry_appl_name"]'
    path_phone = '//input[@id="preentry_appl_phone"]'

    # определяем поле с именем
    sportzal = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, path_name)))
    sportzal.click()
    sleep(1)

    # заполняем имя
    for letter in name_:
        sleep(rnd.random())
        sportzal.send_keys(letter)

    # определяем поле с номером телефона
    sportzal = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, path_phone)))
    sportzal.click()
    sleep(1)

    # заполняем теле]н
    for letter in phone:
        sleep(rnd.random())
        sportzal.send_keys(letter)

    if flag == 'automate':
        print("Сейчас!")
        # находим чекбокс с правилами
        checkbox = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'popup-rules-state')))
        checkbox.click()

        # находим кнопку отправить
        send_button = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, 'preentry_appl_submit')))
        send_button.click()
        sleep(1)
        driver.close()


if __name__ == '__main__':
    main()
