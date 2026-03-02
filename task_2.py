import sqlite3

conn = sqlite3.connect('resourse/drink_shop.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    quantity REAL NOT NULL,
    unit TEXT NOT NULL,
    alcohol_percent REAL DEFAULT 0,
    min_quantity REAL DEFAULT 0,
    price_per_unit REAL DEFAULT 0
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS drinks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    alcohol_percent REAL DEFAULT 0,
    price REAL DEFAULT 0,
    volume REAL DEFAULT 0
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS cocktails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    price REAL DEFAULT 0
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS cocktail_ingredients (
    cocktail_id INTEGER,
    drink_id INTEGER,
    quantity REAL NOT NULL,
    FOREIGN KEY (cocktail_id) REFERENCES cocktails (id),
    FOREIGN KEY (drink_id) REFERENCES drinks (id),
    PRIMARY KEY (cocktail_id, drink_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_type TEXT NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    total_price REAL NOT NULL,
    date TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_id INTEGER,
    quantity REAL NOT NULL,
    movement_type TEXT NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients (id)
)
''')

conn.commit()

def add_ingredient():
    name = input("Название: ")
    qty = int(input("Количество: "))
    unit = input("Ед.изм: ")
    alc = int(input("Крепость: ") or 0)
    min_qty = int(input("Мин.остаток: ") or 0)
    price = int(input("Цена: ") or 0)
    cursor.execute("INSERT INTO ingredients VALUES (NULL,?,?,?,?,?,?)",
                  (name, qty, unit, alc, min_qty, price))
    conn.commit()
    print("OK")

def list_ingredients():
    for row in cursor.execute("SELECT * FROM ingredients"):
        print(row)

def restock_ingredient():
    name = input("Название: ")
    qty = int(input("Количество: "))
    cursor.execute("UPDATE ingredients SET quantity = quantity + ? WHERE name = ?", (qty, name))
    cursor.execute("INSERT INTO stock_movements (ingredient_id, quantity, movement_type, date) SELECT id,"
                   " ?, 'приход', datetime('now') FROM ingredients WHERE name = ?", (qty, name))
    conn.commit()
    print("OK")

def add_drink():
    name = input("Название: ")
    alc = int(input("Крепость: "))
    price = int(input("Цена: "))
    vol = int(input("Объем(мл): "))
    cursor.execute("INSERT INTO drinks VALUES (NULL,?,?,?,?)",
                  (name, alc, price, vol))
    conn.commit()
    print("OK")

def list_drinks():
    for row in cursor.execute("SELECT * FROM drinks"):
        print(row)

def add_cocktail():
    name = input("Название: ")
    price = int(input("Цена: "))
    cursor.execute("INSERT INTO cocktails VALUES (NULL,?,?)", (name, price))
    cid = cursor.lastrowid
    while True:
        did = input("ID напитка (0-стоп): ")
        if did == "0":
            break
        qty = int(input("Количество(мл): "))
        cursor.execute("INSERT INTO cocktail_ingredients VALUES (?,?,?)",
                      (cid, int(did), qty))
    conn.commit()
    print("OK")

def list_cocktails():
    for c in cursor.execute("SELECT * FROM cocktails"):
        print(c)
        for i in cursor.execute("SELECT d.name, ci.quantity FROM cocktail_ingredients ci JOIN drinks d ON"
                                " ci.drink_id = d.id WHERE ci.cocktail_id = ?", (c[0],)):
            print(f"  {i[0]} {i[1]}мл")

def calc_cocktail_strength():
    name = input("Название коктейля: ")
    cid = cursor.execute("SELECT id FROM cocktails WHERE name = ?", (name,)).fetchone()
    if cid:
        total_alc = 0
        total_vol = 0
        for i in cursor.execute("SELECT d.alcohol_percent, ci.quantity FROM cocktail_ingredients ci JOIN drinks"
                                " d ON ci.drink_id = d.id WHERE ci.cocktail_id = ?", (cid[0],)):
            total_alc += i[0] * i[1]
            total_vol += i[1]
        if total_vol:
            print(f"Крепость: {total_alc/total_vol:.1f}%")

def sell_item():
    print("1. Напиток")
    print("2. Коктейль")
    typ = input("Выберите: ")

    if typ == "1":
        name = input("Название: ")
        qty = int(input("Количество: "))
        price = cursor.execute("SELECT price FROM drinks WHERE name = ?", (name,)).fetchone()
        if price:
            total = price[0] * qty
            cursor.execute("INSERT INTO sales (item_type, item_name, quantity, total_price, date) VALUES"
                           " (?,?,?,?, datetime('now'))", ('drink', name, qty, total))
            conn.commit()
            print(f"Сумма: {total}")
    elif typ == "2":
        name = input("Название: ")
        qty = int(input("Количество: "))
        price = cursor.execute("SELECT price FROM cocktails WHERE name = ?", (name,)).fetchone()
        if price:
            total = price[0] * qty
            cursor.execute("INSERT INTO sales (item_type, item_name, quantity, total_price, date)"
                           " VALUES (?,?,?,?, datetime('now'))", ('cocktail', name, qty, total))
            conn.commit()
            print(f"Сумма: {total}")

def sales_history():
    for s in cursor.execute("SELECT * FROM sales ORDER BY date DESC LIMIT 10"):
        print(s)

while True:
    print("1. Ингредиенты")
    print("2. Напитки")
    print("3. Коктейли")
    print("4. Продажи")
    print("5. Выход")

    choice = input("Выберите действие: ")

    if choice == "1":
        print("\n1. Добавить")
        print("2. Список")
        print("3. Пополнить")
        sub = input("Выберите: ")

        if sub == "1":
            add_ingredient()
        elif sub == "2":
            list_ingredients()
        elif sub == "3":
            restock_ingredient()
    elif choice == "2":
        print("\n1. Добавить")
        print("2. Список")
        sub = input("Выберите: ")

        if sub == "1":
            add_drink()
        elif sub == "2":
            list_drinks()
    elif choice == "3":
        print("\n1. Создать")
        print("2. Список")
        print("3. Крепость")
        sub = input("Выберите: ")

        if sub == "1":
            add_cocktail()
        elif sub == "2":
            list_cocktails()
        elif sub == "3":
            calc_cocktail_strength()
    elif choice == "4":
        print("\n1. Продажа")
        print("2. История")
        sub = input("Выберите: ")

        if sub == "1":
            sell_item()
        elif sub == "2":
            sales_history()
    elif choice == "5":
        break
    else:
        print("Ошибка: введите 1, 2, 3, 4 или 5!")
conn.close()