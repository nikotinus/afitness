import os


def get_fields(file_name: str) -> bool:
    name = input("Введи имя, которое хочешь заполнить в веб-форму: ")
    phone = input(
        "Введи номер телефона, который хочешь заполнить в веб-форму: ")
    badminton = input("Введи 1, чтобы Записаться на Бадминтон: ")
    flag = input("Введи 1, чтобы кнопка Отправить нажалась автоматически: ")

    try:
        with open(file_name, 'w') as f:
            f.write(name)
            f.write('\n')
            f.write(phone)
            f.write('\n')
            f.write('badminton' if badminton == "1" else 'basketball')
            f.write('\n')
            f.write('automate' if flag == "1" else 'manually')
        return True
    except Exception:
        file_name = os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), file_name))
        os.remove(file_name)
        return False


if __name__ == '__main__':
    get_fields()
