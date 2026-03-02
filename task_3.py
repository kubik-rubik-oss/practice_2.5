import requests
import sqlite3

conn = sqlite3.connect('resourse/currency_groups.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS group_currencies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        code TEXT NOT NULL,
        name TEXT NOT NULL,
        nominal INTEGER,
        value REAL,
        FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
        UNIQUE(group_id, code)
    )
''')

conn.commit()

url = "https://www.cbr-xml-daily.ru/daily_json.js"
response = requests.get(url, timeout = 5)
response.encoding = 'utf-8'
data = response.json()

def viewing_all_currencies(data):
    print("\nКод, Имя, Номинал, Стоимость")
    for code, info in data['Valute'].items():
        print(f"{code}, {info['Name']}, {info['Nominal']}, {info['Value']} руб.")

def viewing_specific_currency(data):
    choice_id = input("Введите код валюты: ").upper()
    if choice_id in data['Valute']:
        info = data['Valute'][choice_id]
        print(f"{choice_id}, {info['Name']}, {info['Nominal']}, {info['Value']} руб.")
    else:
        print("Ошибка: валюта не найдена!")

def create_group_currency():
    name = input("Введите название группы: ").lower()

    cursor.execute("SELECT id FROM groups WHERE name = ?", (name,))
    if cursor.fetchone():
        print(f"Группа '{name}' уже существует!")
        return

    cursor.execute("INSERT INTO groups (name) VALUES (?)", (name,))
    conn.commit()
    print(f"Группа '{name}' создана")

    show_groups_list()

    choice = input("\nХотите добавить валюты в группу сейчас? (да/нет): ").lower()
    if choice == 'да':
        add_currencies_to_group(name)

def show_groups_list():
    cursor.execute("SELECT id, name FROM groups ORDER BY name")
    groups = cursor.fetchall()

    if not groups:
        print("\n(нет групп)")
        return

    print("\nДоступные группы:")
    for g in groups:
        cursor.execute("SELECT COUNT(*) FROM group_currencies WHERE group_id = ?", (g[0],))
        count = cursor.fetchone()[0]
        print(f"{g[1]} ({count} валют)")

def add_currencies_to_group(group_name):
    cursor.execute("SELECT id FROM groups WHERE name = ?", (group_name,))
    group = cursor.fetchone()
    if not group:
        print("Ошибка: группа не найдена")
        return

    group_id = group[0]

    print(f"\nДобавление валют в группу '{group_name}'")

    while True:
        code = input("Введите код валюты (или 'стоп'): ").upper()
        if code == 'СТОП':
            break

        if code not in data['Valute']:
            print("Ошибка: валюта не найдена")
            continue

        cursor.execute(
            "SELECT id FROM group_currencies WHERE group_id = ? AND code = ?",
            (group_id, code)
        )
        if cursor.fetchone():
            print(f"Валюта {code} уже есть в группе!")
            continue

        info = data['Valute'][code]
        cursor.execute('''
            INSERT INTO group_currencies (group_id, code, name, nominal, value)
            VALUES (?, ?, ?, ?, ?)
        ''', (group_id, code, info['Name'], info['Nominal'], info['Value']))
        conn.commit()
        print(f"Валюта {code} ({info['Name']}) добавлена")

def viewing_list_groups():
    cursor.execute("SELECT id, name FROM groups ORDER BY name")
    groups = cursor.fetchall()

    if not groups:
        print("Нет созданных групп")
        return

    for group in groups:
        print(f"\n{group[1]}:")

        cursor.execute('''
            SELECT code, name, nominal, value FROM group_currencies 
            WHERE group_id = ? ORDER BY code
        ''', (group[0],))

        currencies = cursor.fetchall()
        if currencies:
            for c in currencies:
                print(f"{c[0]}: {c[1]} - {c[3]} руб.")
        else:
            print("(группа пуста)")

def change_list_groups():
    cursor.execute("SELECT id, name FROM groups ORDER BY name")
    groups = cursor.fetchall()

    if not groups:
        print("Ошибка: нет созданных групп")
        return

    print("\nДоступные группы:")
    for g in groups:
        print(f"{g[1]}")

    name = input("\nВыберите группу: ").lower()

    cursor.execute("SELECT id, name FROM groups WHERE name = ?", (name,))
    group = cursor.fetchone()

    if not group:
        print("Ошибка: группа не найдена")
        return

    group_id, group_name = group

    print(f"\nГруппа '{group_name}':")
    cursor.execute("SELECT code, name FROM group_currencies WHERE group_id = ? ORDER BY code", (group_id,))
    currencies = cursor.fetchall()

    if currencies:
        for c in currencies:
            print(f"{c[0]}: {c[1]}")
    else:
        print("(группа пуста)")

    print("\nДействия:")
    print("1. Добавить валюту")
    print("2. Удалить валюту")
    print("3. Удалить группу")
    print("4. Отмена")

    action = input("Выберите действие: ")

    if action == "1":
        code = input("Код валюты: ").upper()
        if code not in data['Valute']:
            print("Ошибка: валюта не найдена")
            return

        cursor.execute(
            "SELECT id FROM group_currencies WHERE group_id = ? AND code = ?",
            (group_id, code)
        )
        if cursor.fetchone():
            print("Ошибка: валюта уже есть в группе")
            return

        info = data['Valute'][code]
        cursor.execute('''
            INSERT INTO group_currencies (group_id, code, name, nominal, value)
            VALUES (?, ?, ?, ?, ?)
        ''', (group_id, code, info['Name'], info['Nominal'], info['Value']))
        conn.commit()
        print(f"Валюта {code} добавлена")

    elif action == "2":
        if not currencies:
            print("Ошибка: группа пуста")
            return

        code = input("Код валюты для удаления: ").upper()
        cursor.execute(
            "DELETE FROM group_currencies WHERE group_id = ? AND code = ?",
            (group_id, code)
        )
        if cursor.rowcount > 0:
            conn.commit()
            print(f"Валюта {code} удалена")
        else:
            print("Ошибка: валюта не найдена в группе")

    elif action == "3":
        confirm = input(f"Удалить группу '{group_name}'? (да/нет): ").lower()
        if confirm == 'да':
            cursor.execute("DELETE FROM groups WHERE id = ?", (group_id,))
            conn.commit()
            print("Группа удалена")

    elif action == "4":
        print("Отмена")

def show_db_info():
    print("\nИнформация о базе данных:")
    print(f"Файл БД: currency_groups.db")

    cursor.execute("SELECT COUNT(*) FROM groups")
    groups_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM group_currencies")
    currencies_count = cursor.fetchone()[0]

    print(f"Групп: {groups_count}")

while True:
    print("1. Текущий курс всех валют")
    print("2. Просмотр отдельной валюты")
    print("3. Создание группы")
    print("4. Просмотр групп")
    print("5. Изменение групп")
    print("6. Информация о базе данных")
    print("7. Выход")

    choice = input("\nВыберите действие: ")

    if choice == "1":
        viewing_all_currencies(data)
    elif choice == "2":
        viewing_specific_currency(data)
    elif choice == "3":
        create_group_currency()
    elif choice == "4":
        viewing_list_groups()
    elif choice == "5":
        change_list_groups()
    elif choice == "6":
        show_db_info()
    elif choice == "7":
        print("Вы вышли")
        conn.close()
        break
    else:
        print("Ошибка: введите 1, 2, 3, 4, 5, 6 или 7!")