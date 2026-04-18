import sqlite3
import ctypes

dll = ctypes.CDLL("./asm/db_wrapper.dll")

dll.check_rowcount_wrapper.argtypes = [ctypes.c_longlong]
dll.check_rowcount_wrapper.restype = ctypes.c_int
dll.choose_field_wrapper.argtypes = [ctypes.c_longlong]
dll.choose_field_wrapper.restype = ctypes.c_int


class CapitalRepository:
    def __init__(self, db_file='database/capitals.db'):
        """Инициализация подключения к SQLite"""
        self.db_file = db_file
        self.connection = None
        self.connect()
        self.create_table()

    def connect(self):
        """Подключение к БД"""
        self.connection = sqlite3.connect(self.db_file)
        self.connection.row_factory = sqlite3.Row  # Чтобы возвращать данные как словари
        print(f"Подключение к БД {self.db_file}")

    def create_table(self):
        """Создание таблицы capitals если она не существует"""
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS capitals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country TEXT NOT NULL UNIQUE,
                capital TEXT NOT NULL
            )
        """)
        self.connection.commit()
        cursor.close()

    def add_capital(self, country, capital):
        """Добавление новой столицы"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("INSERT INTO capitals (country, capital) VALUES (?, ?)", (country, capital))
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Ошибка: Страна '{country}' уже существует")
            return None
        finally:
            cursor.close()

    def delete_capital(self, identifier):
        """Удаление записи по ID или стране"""
        cursor = self.connection.cursor()
        try:
            if isinstance(identifier, int):
                cursor.execute("DELETE FROM capitals WHERE id = ?", (identifier,))
            else:
                cursor.execute("DELETE FROM capitals WHERE country = ?", (identifier,))

            self.connection.commit()

            # ASM
            return bool(dll.check_rowcount_wrapper(cursor.rowcount))
        finally:
            cursor.close()

    def update_capital(self, identifier, new_country=None, new_capital=None):
        cursor = self.connection.cursor()
        try:
            if new_country and new_capital:
                query = "UPDATE capitals SET country = ?, capital = ? WHERE "
                params = [new_country, new_capital]
            elif new_country:
                query = "UPDATE capitals SET country = ? WHERE "
                params = [new_country]
            elif new_capital:
                query = "UPDATE capitals SET capital = ? WHERE "
                params = [new_capital]
            else:
                return False

            is_int = isinstance(identifier, int)

            # ASM
            result = dll.choose_field_wrapper(1 if is_int else 0)

            if result == 1:
                query += "id = ?"
            else:
                query += "country = ?"

            params.append(identifier)

            cursor.execute(query, params)
            self.connection.commit()

            # ASM
            return bool(dll.check_rowcount_wrapper(cursor.rowcount))

        finally:
            cursor.close()

    def search(self, keyword):
        """Поиск по стране или столице (частичное совпадение)"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM capitals 
            WHERE country LIKE ? OR capital LIKE ?
        """, (f'%{keyword}%', f'%{keyword}%'))

        results = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return results

    def filter_by_country(self, country):
        """Фильтрация по стране (точное совпадение)"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM capitals WHERE country = ?", (country,))
        results = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return results

    def filter_by_capital(self, capital):
        """Фильтрация по столице (точное совпадение)"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM capitals WHERE capital = ?", (capital,))
        results = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return results

    def get_all_capitals(self):
        """Получение всех записей"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM capitals ORDER BY country")
        results = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return results

    def close(self):
        """Закрытие соединения с БД"""
        if self.connection:
            self.connection.close()
        print("Соединение с БД закрыто")
