def get_fields():
    name = input("Введи имя, которое хочешь заполнить в веб-форму: ")
    phone = input(
        "Введи номер телефона, который хочешь заполнить в веб-форму: ")
    flag = input("Введи 1, чтобы кнопка Отправить нажалась автоматически: ")

    with open("fields.txt", 'w') as f:
        f.write(name)
        f.write('\n')
        f.write(phone)
        f.write('\n')
        f.write('automate' if flag == 1 else 'manually')


if __name__ == '__main__':
    get_fields()
