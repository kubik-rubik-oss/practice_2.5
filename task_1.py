import sqlite3

class Student:
    def __init__(self, first_name, last_name, middle_name, group_name, mark):
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.group_name = group_name
        self.mark = mark

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name} {self.group_name} {self.mark}"

def init_db():
    conn = sqlite3.connect("resourse/students.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            middle_name TEXT NOT NULL,
            group_name TEXT NOT NULL,
            mark TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn, cursor

def add_student(cursor, conn):
    last_name = input("Фамилия: ")
    first_name = input("Имя: ")
    middle_name = input("Отчество: ")
    group_name = input("Группа: ")
    mark = input("Оценки (4 оценки, через пробел): ")
    marks = []
    for x in mark.split():
        try:
            marks.append(int(x))
        except ValueError:
            print(f"Ошибка: введите число!")
            return
    marks_str = " ".join(str(m) for m in marks)

    if not all([last_name, first_name, middle_name, group_name, mark]):
        print("Ошибка: все поля должны быть заполнены!")
        return

    student = Student(first_name, last_name, middle_name, group_name, marks_str)
    cursor.execute("""
            INSERT INTO students (first_name, last_name, middle_name, group_name, mark) 
            VALUES (?, ?, ?, ?, ?)
        """, (student.first_name, student.last_name, student.middle_name, student.group_name, student.mark))
    conn.commit()
    print("Студент добавлен")

def view_students(cursor):
    cursor.execute("SELECT id, last_name, first_name, middle_name, group_name, mark FROM students")
    students = cursor.fetchall()

    if not students:
        print("\nСписок студентов пуст")
        return

    print("\nСписок студентов")
    for s in students:
        print(f"{s[0]}. {s[1]} {s[2]} {s[3]}, Группа: {s[4]}, Оценки: {s[5]}")
    print("\n")

def view_specific_student(cursor, conn):
    view_students(cursor)

    id_view = int(input("\nВведите ID студента для просмотра: "))

    cursor.execute("SELECT * FROM students WHERE id = ?", (id_view,))
    student = cursor.fetchone()

    if student:
        marks_str = student[5]
        if marks_str:
            marks = list(map(int, marks_str.split()))
            avg = sum(marks) / len(marks)
        else:
            avg = 0

        print(f"ID: {student[0]}")
        print(f"Фамилия: {student[1]}")
        print(f"Имя: {student[2]}")
        print(f"Отчество: {student[3]}")
        print(f"Группа: {student[4]}")
        print(f"Оценки: {student[5]}")
        print(f"Средний балл: {avg}\n")

def update_student(cursor, conn):
    view_students(cursor)

    try:
        id_up = int(input("\nВведите ID студента для редактирования: "))
        cursor.execute("SELECT * FROM students WHERE id = ?", (id_up,))
        student = cursor.fetchone()

        if student:
            print("\nДанные студента:")
            print(f"1. Фамилия: {student[1]}")
            print(f"2. Имя: {student[2]}")
            print(f"3. Отчество: {student[3]}")
            print(f"4. Группа: {student[4]}")
            print(f"5. Оценки: {student[5]}")

            print("\nЧто хотите изменить?")
            print("1 - Фамилию")
            print("2 - Имя")
            print("3 - Отчество")
            print("4 - Группу")
            print("5 - Оценки")
            print("6 - Отмена")

            choice = input("Ваш выбор: ")

            if choice == "1":
                new_value = input("Введите новую фамилию: ")
                cursor.execute("UPDATE students SET last_name = ? WHERE id = ?", (new_value, id_up))
                print("Фамилия обновлена")

            elif choice == "2":
                new_value = input("Введите новое имя: ")
                cursor.execute("UPDATE students SET first_name = ? WHERE id = ?", (new_value, id_up))
                print("Имя обновлено")

            elif choice == "3":
                new_value = input("Введите новое отчество: ")
                cursor.execute("UPDATE students SET middle_name = ? WHERE id = ?", (new_value, id_up))
                print("Отчество обновлено")

            elif choice == "4":
                new_value = input("Введите новую группу: ")
                cursor.execute("UPDATE students SET group_name = ? WHERE id = ?", (new_value, id_up))
                print("Группа обновлена")

            elif choice == "5":
                new_value = input("Введите новые оценки (через пробел): ")
                cursor.execute("UPDATE students SET mark = ? WHERE id = ?", (new_value, id_up))
                print("Оценки обновлены")

            elif choice == "6":
                print("Редактирование отменено")
                return
            else:
                print("Ошибка: неверный выбор!")
                return
            conn.commit()

        else:
            print("Ошибка: студент с таким ID не найден!")
    except ValueError:
        print("Ошибка: введите корректный ID!")

def delete_student(cursor, conn):
    view_students(cursor)

    try:
        id_del = int(input("\nВведите ID студента для удаления: "))
        cursor.execute("DELETE FROM students WHERE id=?", (id_del,))
        if cursor.rowcount > 0:
            conn.commit()
            print("Студент удален")
        else:
            print("Ошибка: студент с таким ID не найден!")
    except ValueError:
        print("Ошибка: введите корректный ID!")

def average_mark_group(cursor, conn):
    view_students(cursor)

    group = input("Введите название группы: ")

    cursor.execute("SELECT mark FROM students WHERE group_name = ?", (group,))
    students = cursor.fetchall()

    if not students:
        print("Ошибка: группа не найдена!")
        return

    marks = []
    for s in students:
        if s[0]:
            marks.extend(map(int, s[0].split()))

    if marks:
        print(f"Средний балл: {sum(marks) / len(marks)}\n")
    else:
        print("Нет оценок\n")

conn, cursor = init_db()

while True:
    print("1. Добавить студента")
    print("2. Показать всех")
    print("3. Показать конкретного студента")
    print("4. Редактирование студента")
    print("5. Удалить студента")
    print("6. Показать средний балл конкретной группы")
    print("7. Выход")

    choice = input("Выберите действие: ")

    if choice == "1":
        add_student(cursor, conn)
    elif choice == "2":
        view_students(cursor)
    elif choice == "3":
        view_specific_student(cursor, conn)
    elif choice == "4":
        update_student(cursor, conn)
    elif choice == "5":
        delete_student(cursor, conn)
    elif choice == "6":
        average_mark_group(cursor, conn)
    elif choice == "7":
        print("Вы вышли")
        break
    else:
        print("Ошибка: неверный выбор!")

conn.close()