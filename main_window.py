import sys
from PyQt5.QtWidgets import (QMainWindow, QTableWidgetItem, QMessageBox,
                             QInputDialog, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
from repository.repository import CapitalRepository


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Загружаем UI
        loadUi('ui/main_window.ui', self)

        # Инициализируем репозиторий
        self.repo = CapitalRepository('database/capitals.db')

        # Настраиваем таблицу
        self.setup_table()

        # Подключаем сигналы
        self.setup_signals()

        # Загружаем данные
        self.refresh_table()

        # Показываем окно
        self.show()

    def setup_table(self):
        """Настройка таблицы"""
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Страна', 'Столица'])
        self.tableWidget.setColumnWidth(0, 85)
        self.tableWidget.setColumnWidth(1, 375)
        self.tableWidget.setColumnWidth(2, 375)
        self.tableWidget.setSelectionBehavior(self.tableWidget.SelectRows)
        self.tableWidget.setEditTriggers(self.tableWidget.NoEditTriggers)

    def setup_signals(self):
        """Подключение сигналов к слотам"""
        self.addButton.clicked.connect(self.add_capital)
        self.searchButton.clicked.connect(self.search_capitals)
        self.filterButton.clicked.connect(self.filter_capitals)
        self.resetButton.clicked.connect(self.refresh_table)
        self.editButton.clicked.connect(self.edit_capital)
        self.deleteButton.clicked.connect(self.delete_capital)
        self.refreshButton.clicked.connect(self.refresh_table)

        # Обработка нажатия Enter в полях поиска
        self.searchLineEdit.returnPressed.connect(self.search_capitals)
        self.filterLineEdit.returnPressed.connect(self.filter_capitals)

    def refresh_table(self):
        """Обновление таблицы со всеми данными"""
        capitals = self.repo.get_all_capitals()
        self.display_capitals(capitals)
        self.infoLabel.setText(f"Всего записей: {len(capitals)}")

        # Очищаем поля поиска и фильтрации
        self.searchLineEdit.clear()
        self.filterLineEdit.clear()

    def display_capitals(self, capitals_list):
        """Отображение данных в таблице"""
        self.tableWidget.setRowCount(0)  # Очищаем таблицу

        for row, capital in enumerate(capitals_list):
            self.tableWidget.insertRow(row)
            self.tableWidget.setItem(row, 0, QTableWidgetItem(str(capital['id'])))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(capital['country']))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(capital['capital']))

    def add_capital(self):
        """Добавление новой столицы"""
        country = self.countryAddLineEdit.text().strip()
        capital = self.capitalAddLineEdit.text().strip()

        if not country or not capital:
            QMessageBox.warning(self, "Ошибка", "Заполните оба поля!")
            return

        result = self.repo.add_capital(country, capital)
        if result:
            msgBox = QMessageBox(self)
            msgBox.information(self, "Успех", f"Добавлено: {country} - {capital}")
            msgBox.setText("The document has been modified.")
            self.countryAddLineEdit.clear()
            self.capitalAddLineEdit.clear()
            self.refresh_table()
        else:
            QMessageBox.warning(self, "Ошибка", f"Страна '{country}' уже существует!")

    def search_capitals(self):
        """Поиск по ключевому слову"""
        keyword = self.searchLineEdit.text().strip()
        if not keyword:
            QMessageBox.warning(self, "Ошибка", "Введите текст для поиска!")
            return

        results = self.repo.search(keyword)
        self.display_capitals(results)

        if results:
            self.infoLabel.setText(f"🔍 Найдено записей: {len(results)}")
        else:
            self.infoLabel.setText(f"❌ Ничего не найдено по запросу '{keyword}'")
            QMessageBox.information(self, "Результат", f"По запросу '{keyword}' ничего не найдено")

    def filter_capitals(self):
        """Фильтрация по точному значению"""
        filter_value = self.filterLineEdit.text().strip()
        if not filter_value:
            QMessageBox.warning(self, "Ошибка", "Введите значение для фильтрации!")
            return

        filter_type = self.filterComboBox.currentText()

        if filter_type == "Стране":
            results = self.repo.filter_by_country(filter_value)
            filter_text = f"стране '{filter_value}'"
        else:
            results = self.repo.filter_by_capital(filter_value)
            filter_text = f"столице '{filter_value}'"

        self.display_capitals(results)

        if results:
            self.infoLabel.setText(f"🎯 Отфильтровано по {filter_text}: {len(results)} записей")
        else:
            self.infoLabel.setText(f"❌ Не найдено по {filter_text}")
            QMessageBox.information(self, "Результат", f"По {filter_text} ничего не найдено")

    def edit_capital(self):
        """Редактирование выбранной записи"""
        current_row = self.tableWidget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования!")
            return

        # Получаем данные выбранной записи
        record_id = int(self.tableWidget.item(current_row, 0).text())
        current_country = self.tableWidget.item(current_row, 1).text()
        current_capital = self.tableWidget.item(current_row, 2).text()

        # Диалог для выбора что редактировать
        items = ["Страну", "Столицу", "И страну, и столицу"]
        choice, ok = QInputDialog.getItem(self, "Редактирование",
                                          "Что вы хотите изменить?",
                                          items, 0, False)

        if not ok:
            return

        new_country = None
        new_capital = None

        if choice == "Страну":
            new_country, ok = QInputDialog.getText(self, "Редактирование",
                                                   f"Введите новое название страны (было: {current_country}):")
            if ok and new_country:
                new_country = new_country.strip()

        elif choice == "Столицу":
            new_capital, ok = QInputDialog.getText(self, "Редактирование",
                                                   f"Введите новую столицу (было: {current_capital}):")
            if ok and new_capital:
                new_capital = new_capital.strip()

        else:  # И страну, и столицу
            new_country, ok1 = QInputDialog.getText(self, "Редактирование",
                                                    f"Введите новое название страны (было: {current_country}):")
            if ok1 and new_country:
                new_country = new_country.strip()

            new_capital, ok2 = QInputDialog.getText(self, "Редактирование",
                                                    f"Введите новую столицу (было: {current_capital}):")
            if ok2 and new_capital:
                new_capital = new_capital.strip()

        # Обновляем запись
        if self.repo.update_capital(record_id, new_country, new_capital):
            QMessageBox.information(self, "Успех", "Запись успешно обновлена!")
            self.refresh_table()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось обновить запись!")

    def delete_capital(self):
        """Удаление выбранной записи"""
        current_row = self.tableWidget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления!")
            return

        record_id = int(self.tableWidget.item(current_row, 0).text())
        country = self.tableWidget.item(current_row, 1).text()
        capital = self.tableWidget.item(current_row, 2).text()

        # Подтверждение удаления
        reply = QMessageBox.question(self, "Подтверждение",
                                     f"Вы уверены, что хотите удалить запись:\n{country} - {capital}?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.repo.delete_capital(record_id):
                QMessageBox.information(self, "Успех", "Запись успешно удалена!")
                self.refresh_table()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить запись!")

    def closeEvent(self, event):
        """Закрытие соединения при закрытии окна"""
        self.repo.close()
        event.accept()