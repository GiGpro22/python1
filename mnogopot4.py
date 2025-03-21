import threading
import json
import time
from datetime import datetime

class ExpenseManager:
    def __init__(self, filename="expenses.json"):
        self.filename = filename
        self.expenses = self.load_expenses()
        self.lock = threading.Lock()

    def load_expenses(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print("Ошибка: файл расходов поврежден. Начинаем с чистого листа.")
            return []

    def save_expenses(self):
        with self.lock: 
            with open(self.filename, 'w') as f:
                json.dump(self.expenses, f, indent=4)
                print(f"Расходы сохранены в файл: {self.filename}")

    def add_expense(self, amount, category, description=""):
        with self.lock:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.expenses.append({
                "amount": amount,
                "category": category,
                "description": description,
                "timestamp": timestamp
            })
            print(f"Добавлен расход: {amount} ({category}) - {description}")
            threading.Thread(target=self.save_expenses).start()

    def generate_report(self):
        report = {}
        for expense in self.expenses:
            category = expense["category"]
            amount = expense["amount"]
            if category in report:
                report[category] += amount
            else:
                report[category] = amount

        print("\n--- Отчет по расходам ---")
        total_spending = 0
        for category, total in report.items():
            print(f"{category}: {total}")
            total_spending += total
        print(f"----\nВсего потрачено: {total_spending}")

    def display_expenses(self):
        print("\n--- Список расходов ---")
        for i, expense in enumerate(self.expenses):
            print(f"{i+1}. {expense['timestamp']} - {expense['amount']} ({expense['category']}) - {expense['description']}")
        if not self.expenses:
            print("Расходы отсутствуют.")

def main():
    expense_manager = ExpenseManager()

    while True:
        print("\n--- Менеджер Расходов ---")
        print("1. Добавить расход")
        print("2. Показать расходы")
        print("3. Сгенерировать отчет")
        print("4. Выход")

        choice = input("Выберите действие: ")

        if choice == '1':
            try:
                amount = float(input("Сумма: "))
                category = input("Категория: ")
                description = input("Описание (необязательно): ")
                expense_manager.add_expense(amount, category, description)
            except ValueError:
                print("Ошибка: Некорректный формат суммы.")
        elif choice == '2':
            expense_manager.display_expenses()
        elif choice == '3':
            expense_manager.generate_report()
        elif choice == '4':
            print("Выход из программы.")
            break
        else:
            print("Некорректный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()