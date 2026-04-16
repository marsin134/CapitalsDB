from repository.repository import CapitalRepository


def print_separator():
    print("-" * 55)


def print_capitals(capitals_list):
    """Вспомогательная функция для вывода списка столиц"""
    if not capitals_list:
        print("  Нет данных")
        return

    print(f"{'ID':<5} {'Страна':<25} {'Столица':<25}")
    print_separator()
    for item in capitals_list:
        print(f"{item['id']:<5} {item['country']:<25} {item['capital']:<25}")
    print_separator()


def main():
    # Создаем репозиторий
    repo = CapitalRepository('database/capitals.db')

    print("ДОБАВЛЕНИЕ ЗАПИСЕЙ:")
    repo.add_capital("Россия", "Москва")
    repo.add_capital("Франция", "Париж")
    repo.add_capital("Германия", "Берлин")
    repo.add_capital("Италия", "Рим")
    repo.add_capital("Испания", "Мадрид")
    repo.add_capital("Великобритания", "Лондон")
    repo.add_capital("Япония", "Токио")
    repo.add_capital("Китай", "Пекин")
    print()

    print("ВСЕ ЗАПИСИ:")
    print_capitals(repo.get_all_capitals())
    print()

    print("ПОИСК (поиск 'ри'):")
    results = repo.search("ри")
    print_capitals(results)
    print()

    print("ФИЛЬТРАЦИЯ ПО СТРАНЕ (Франция):")
    print_capitals(repo.filter_by_country("Франция"))
    print()

    print("ФИЛЬТРАЦИЯ ПО СТОЛИЦЕ (Рим):")
    print_capitals(repo.filter_by_capital("Рим"))
    print()

    print("РЕДАКТИРОВАНИЕ (меняем столицу Германии):")
    repo.update_capital("Германия", new_capital="Бонн")
    print("   После обновления:")
    print_capitals(repo.filter_by_country("Германия"))
    print("   Возвращаем обратно:")
    repo.update_capital("Германия", new_capital="Берлин")
    print_capitals(repo.filter_by_country("Германия"))
    print()

    print("РЕДАКТИРОВАНИЕ ПО ID (меняем страну с ID=5):")
    all_before = repo.get_all_capitals()
    print("   До изменения:")
    print_capitals([all_before[4]])
    repo.update_capital(5, new_country="Испания (Королевство)")
    print("   После изменения:")
    print_capitals(repo.filter_by_country("Испания (Королевство)"))
    print()

    print("УДАЛЕНИЕ ПО НАЗВАНИЮ (удаляем Италию):")
    repo.delete_capital("Италия")
    print("   Все записи после удаления:")
    print_capitals(repo.get_all_capitals())
    print()

    print("УДАЛЕНИЕ ПО ID (удаляем ID=7 - Япония):")
    repo.delete_capital(7)
    print("   Все записи после удаления:")
    print_capitals(repo.get_all_capitals())
    print()

    print("ПОИСК СТОЛИЦ НА 'М':")
    print_capitals(repo.search("М"))
    print()

    print("ПОПЫТКА ДОБАВИТЬ ДУБЛИКАТ (Россия):")
    repo.add_capital("Россия", "Санкт-Петербург")
    print()

    print("ДОБАВЛЯЕМ ЕЩЕ НЕСКОЛЬКО СТРАН:")
    repo.add_capital("Канада", "Оттава")
    repo.add_capital("Бразилия", "Бразилиа")
    repo.add_capital("Австралия", "Канберра")
    print()

    print("   ИТОГОВАЯ БАЗА ДАННЫХ:")
    print_capitals(repo.get_all_capitals())

    # Закрываем соединение
    repo.close()

    print("\nФайл БД 'capitals.db' создан в папке проекта.")


if __name__ == "__main__":
    main()