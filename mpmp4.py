import threading
import json
import os
from datetime import datetime
import hashlib
import time

class Logger:
    def __init__(self, username):
        self.username = username
        self.log_file = f"{username}_log.log"
        self.log_queue = []
        self.lock = threading.Lock()
        self.running = True
        self.start_logging()

    def log(self, level, message):
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        log_entry = f"[{level}] [{timestamp}] [{self.username}] – {message}\n"
        with self.lock:
            self.log_queue.append(log_entry)

    def start_logging(self):
        def write_logs():
            while self.running:
                if self.log_queue:
                    with self.lock:
                        with open(self.log_file, 'a') as f:
                            for entry in self.log_queue:
                                f.write(entry)
                        self.log_queue.clear()
                time.sleep(1) 
        self.log_thread = threading.Thread(target=write_logs, daemon=True)
        self.log_thread.start()

    def stop_logging(self):
        self.running = False
        if self.log_thread:
            self.log_thread.join()


class UserManager:
    def __init__(self, users_file="users.json"):
        self.users_file = users_file
        self.users = self.load_users()

    def load_users(self):
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print("Ошибка: файл пользователей поврежден. Начинаем с чистого листа.")
            return {}

    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=4)

    def register(self, username, password):
        if username in self.users:
            print("Ошибка: Пользователь с таким именем уже существует.")
            return False
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.users[username] = {"password": hashed_password}
        self.save_users()
        print("Регистрация прошла успешно.")
        return True

    def login(self, username, password):
        if username not in self.users:
            print("Ошибка: Пользователь не найден.")
            return False
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if self.users[username]["password"] == hashed_password:
            print("Авторизация прошла успешно.")
            return True
        print("Ошибка: Неверный пароль.")
        return False


class ExpenseManager:
    def __init__(self, username, logger):
        self.username = username
        self.filename = f"{username}_expenses.json"
        self.expenses = self.load_expenses()
        self.lock = threading.Lock()
        self.save_thread = None
        self.running = True
        self.logger = logger
        self.start_autosave()

    def load_expenses(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            self.logger.log("ERROR", "Файл расходов поврежден. Начинаем с чистого листа.")
            return []

    def save_expenses(self):
        with self.lock:
            with open(self.filename, 'w') as f:
                json.dump(self.expenses, f, indent=4)
            self.logger.log("INFO", f"Расходы сохранены в файл: {self.filename}")

    def start_autosave(self):
        def autosave():
            while self.running:
                time.sleep(5)  
                self.save_expenses()
        self.save_thread = threading.Thread(target=autosave, daemon=True)
        self.save_thread.start()

    def stop_autosave(self):
        self.running = False
        if self.save_thread:
            self.save_thread.join()

    def add_expense(self, amount, category, description=""):
        try:
            with self.lock:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.expenses.append({
                    "amount": amount,
                    "category": category,
                    "description": description,
                    "timestamp": timestamp
                })
                self.logger.log("INFO", f"Добавлен расход: {amount} ({category}) - {description}")
        except Exception as e:
            self.logger.log("ERROR", f"Ошибка при добавлении расхода: {str(e)}")

    def obc_report(self):
        try:
            report = {}
            for expense in self.expenses:
                category = expense["category"]
                amount = expense["amount"]
                if category in report:
                    report[category] += amount
                else:
                    report[category] = amount

            self.logger.log("INFO", "Итоги отчет по расходам.")
            print("\n--- Отчет по расходам ---")
            total_spending = 0
            for category, total in report.items():
                print(f"{category}: {total}")
                total_spending += total
            print(f"----\nВсего потрачено: {total_spending}")
        except Exception as e:
            self.logger.log("ERROR", f"Ошибка при генерации отчета: {str(e)}")

    def display_expenses(self):
        try:
            self.logger.log("INFO", "Просмотр списка расходов.")
            print("\n--- Список расходов ---")
            for i, expense in enumerate(self.expenses):
                print(f"{i+1}. {expense['timestamp']} - {expense['amount']} ({expense['category']}) - {expense['description']}")
            if not self.expenses:
                print("Расходы отсутствуют.")
        except Exception as e:
            self.logger.log("ERROR", f"Ошибка при отображении расходов: {str(e)}")


def main():
    user_manager = UserManager()

    while True:
        print("\n--- Менеджер Расходов ---")
        print("1. Регистрация")
        print("2. Авторизация")
        print("3. Выход")

        choice = input("Выберите действие: ")

        if choice == '1':
            username = input("Введите имя пользователя: ")
            password = input("Введите пароль: ")
            if user_manager.register(username, password):
                logger = Logger(username)
                logger.log("INFO", "Пользователь зарегистрирован.")
        elif choice == '2':
            username = input("Введите имя пользователя: ")
            password = input("Введите пароль: ")
            if user_manager.login(username, password):
                logger = Logger(username)
                logger.log("INFO", "Пользователь авторизован.")
                expense_manager = ExpenseManager(username, logger)
                user_menu(expense_manager, logger)
        elif choice == '3':
            print("Выход из программы.")
            break
        else:
            print("Некорректный выбор. Попробуйте снова.")


def user_menu(expense_manager, logger):
    while True:
        print("\n--- Меню пользователя ---")
        print("1. Добавить расход")
        print("2. Показать расходы")
        print("3. Итоги расходов")
        print("4. Выход")

        choice = input("Выберите действие: ")

        if choice == '1':
            try:
                amount = float(input("Сумма: "))
                category = input("Категория: ")
                description = input("Описание (необязательно): ")
                expense_manager.add_expense(amount, category, description)
            except ValueError:
                logger.log("ERROR", "Некорректный формат суммы.")
                print("Ошибка: Некорректный формат суммы.")
        elif choice == '2':
            expense_manager.display_expenses()
        elif choice == '3':
            expense_manager.obc_report()
        elif choice == '4':
            expense_manager.stop_autosave()
            logger.log("INFO", "Пользователь вышел из системы.")
            print("Выход из меню пользователя.")
            break
        else:
            print("Некорректный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()