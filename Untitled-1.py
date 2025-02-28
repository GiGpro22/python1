import json
import bcrypt
import os  


class User:
    def __init__(self, username, password, role="user"):
        self._username = username
        self._password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        )
        self._role = role

    def get_username(self):
        return self._username

    def set_username(self, new_username):
        self._username = new_username

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self._password_hash)

    def get_role(self):
        return self._role

    def set_role(self, role):
        self._role = role

    def update_password(self, old_password, new_password):
        if self.check_password(old_password):
            self._password_hash = bcrypt.hashpw(
                new_password.encode("utf-8"), bcrypt.gensalt()
            )
            return True
        else:
            return False

    def display_info(self):
        print(f"Username: {self._username}, Role: {self._role}")

    def to_dict(self):
        return {
            "username": self._username,
            "password_hash": self._password_hash.decode("utf-8"),
            "role": self._role,
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(data["username"], "dummy_password", data["role"])  # Фиктивный пароль
        user._password_hash = data["password_hash"].encode("utf-8")
        return user


class Admin(User):
    def __init__(self, username, password):
        super().__init__(username, password, role="admin")

    def display_info(self):
        print(f"Admin Username: {self._username}")


class Pet:
    def __init__(
        self, pet_id, animal_type, gender, age, color, nickname, owner_phone
    ):
        self._pet_id = pet_id
        self._animal_type = animal_type
        self._gender = gender
        self._age = age
        self._color = color
        self._nickname = nickname
        self._owner_phone = owner_phone

    def get_id(self):
        return self._pet_id

    def get_animal_type(self):
        return self._animal_type

    def get_gender(self):
        return self._gender

    def get_age(self):
        return self._age

    def get_color(self):
        return self._color

    def get_nickname(self):
        return self._nickname

    def get_owner_phone(self):
        return self._owner_phone

    def set_animal_type(self, animal_type):
        self._animal_type = animal_type

    def set_gender(self, gender):
        self._gender = gender

    def set_age(self, age):
        self._age = age

    def set_color(self, color):
        self._color = color

    def set_nickname(self, nickname):
        self._nickname = nickname

    def set_owner_phone(self, owner_phone):
        self._owner_phone = owner_phone

    def display_info(self):
        print(
            f"ID: {self._pet_id}, Тип: {self._animal_type}, Пол: {self._gender}, "
            f"Возраст: {self._age} лет, Цвет: {self._color}, "
            f"Кличка: {self._nickname}, Телефон владельца: {self._owner_phone}"
        )

    def __str__(self):
        return f"ID: {self._pet_id}, Тип: {self._animal_type}, Кличка: {self._nickname}"

    def to_dict(self):
        return {
            "pet_id": self._pet_id,
            "animal_type": self._animal_type,
            "gender": self._gender,
            "age": self._age,
            "color": self._color,
            "nickname": self._nickname,
            "owner_phone": self._owner_phone,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["pet_id"],
            data["animal_type"],
            data["gender"],
            data["age"],
            data["color"],
            data["nickname"],
            data["owner_phone"],
        )


class PetManagementSystem:
    def __init__(self):
        self._users = []
        self._pets = []
        self.data_file = "pet_data.json"  # Имя файла для хранения данных
        self.load_data()  # Загружаем данные при инициализации

    def load_data(self):
        """Загружает данные из файла."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                self._users = [User.from_dict(user_data) for user_data in data.get("users", [])]
                self._pets = [Pet.from_dict(pet_data) for pet_data in data.get("pets", [])]

            except FileNotFoundError:
                print(f"Файл {self.data_file} не найден.  Создается новый файл.")
            except json.JSONDecodeError:
                print(f"Ошибка: Некорректный формат JSON в файле {self.data_file}.")
                #  Можно предусмотреть создание нового файла или загрузку значений по умолчанию
            except Exception as e:
                print(f"Произошла ошибка при загрузке данных: {e}")
        else:
            self.load_default_data() # Если файл не существует, загружаем дефолтные данные
            self.save_data()  # И сразу сохраняем, чтобы создать файл

    def save_data(self):
        """Сохраняет данные в файл."""
        data = {
            "users": [user.to_dict() for user in self._users],
            "pets": [pet.to_dict() for pet in self._pets],
        }
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)  # Красивый JSON
        except Exception as e:
            print(f"Произошла ошибка при сохранении данных: {e}")

    def load_default_data(self):
        """Загружает дефолтные данные"""
        self._users.append(Admin("admin", "123"))
        self._users.append(User("user", "123"))
        self._pets.append(
            Pet(1, "Собака", "Самец", 3, "Чёрный", "Шарик", "+7 999 123-45-67")
        )
        self._pets.append(
            Pet(2, "Кошка", "Самка", 2, "Белый", "Сакура", "+7 999 987-65-43")
        )
        self._pets.append(
            Pet(3, "Попугай", "Самец", 1, "Зелёный", "Кеша", "+7 999 456-78-90")
        )
        self._pets.append(
            Pet(4, "Кролик", "Самка", 4, "Серый", "Бан", "+7 999 321-09-87")
        )

    def register(self):
        username = input("Введите имя пользователя: ")
        if self.find_user(username):
            print("Пользователь уже существует. Пожалуйста, выберите другое имя.")
            return

        password = input("Введите пароль: ")
        new_user = User(username, password)
        self._users.append(new_user)
        self.save_data()  # Сохраняем данные после регистрации
        print("Регистрация прошла успешно!")

    def login(self):
        username = input("Введите имя пользователя: ")
        password = input("Введите пароль: ")

        user = self.find_user(username)
        if user and user.check_password(password):
            print(f"Добро пожаловать, {username}!")
            return user

        print("Неверное имя пользователя или пароль.")
        return None

    def find_user(self, username):
        for user in self._users:
            if user.get_username() == username:
                return user
        return None

    def show_pets(self):
        for pet in self._pets:
            pet.display_info()

    def sort_pets(self, criterion):
        try:
            sorted_pets = sorted(
                self._pets, key=lambda pet: getattr(pet, f"get_{criterion}")()
            )
            for pet in sorted_pets:
                pet.display_info()
        except AttributeError:
            print("Неверный критерий сортировки.")

    def add_pet(self):
        try:
            new_pet_id = max(pet.get_id() for pet in self._pets) + 1 if self._pets else 1
            animal_type = input("Введите тип животного: ")
            gender = input("Введите пол животного (Самец/Самка): ")
            age = int(input("Введите возраст животного: "))
            color = input("Введите цвет животного: ")
            nickname = input("Введите кличку животного: ")
            owner_phone = input("Введите телефон владельца: ")

            new_pet = Pet(
                new_pet_id, animal_type, gender, age, color, nickname, owner_phone
            )
            self._pets.append(new_pet)
            self.save_data()  # Сохраняем данные после добавления питомца
            print("Питомец успешно добавлен!")
            return True
        except ValueError:
            print("Ошибка: Неверный формат введенных данных.")
            return False
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return False

    def delete_pet(self):
        try:
            pet_id_to_delete = int(input("Введите ID питомца для удаления: "))
            original_length = len(self._pets)
            self._pets[:] = [
                pet for pet in self._pets if pet.get_id() != pet_id_to_delete
            ]

            if len(self._pets) < original_length:
                self.save_data()  # Сохраняем данные после удаления
                print(f"Питомец с ID {pet_id_to_delete} успешно удален!")
                return True
            else:
                print(f"Питомец с ID {pet_id_to_delete} не найден.")
                return False

        except ValueError:
            print("Ошибка: Неверный формат ID.")
            return False
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return False

    def update_pet(self):
        try:
            pet_id_to_update = int(input("Введите ID питомца для изменения: "))
            for pet in self._pets:
                if pet.get_id() == pet_id_to_update:
                    print("Текущие характеристики:")
                    pet.display_info()

                    pet.set_animal_type(
                        input(
                            f"Введите новый тип животного ({pet.get_animal_type()}): "
                        )
                        or pet.get_animal_type()
                    )
                    pet.set_gender(
                        input(f"Введите новый пол ({pet.get_gender()}): ")
                        or pet.get_gender()
                    )
                    try:
                        age = int(input(f"Введите новый возраст ({pet.get_age()}): "))
                        pet.set_age(age)
                    except ValueError:
                        print("Неверный формат возраста. Возраст не изменён.")
                    pet.set_color(
                        input(f"Введите новый цвет ({pet.get_color()}): ")
                        or pet.get_color()
                    )
                    pet.set_nickname(
                        input(f"Введите новую кличку ({pet.get_nickname()}): ")
                        or pet.get_nickname()
                    )
                    pet.set_owner_phone(
                        input(
                            f"Введите новый телефон ({pet.get_owner_phone()}): "
                        )
                        or pet.get_owner_phone()
                    )

                    self.save_data()  # Сохраняем данные после обновления
                    print("Характеристики питомца успешно обновлены!")
                    return True
            print(f"Питомец с ID {pet_id_to_update} не найден.")
            return False
        except ValueError:
            print("Ошибка: Неверный формат ID.")
            return False
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return False

    def search_pet_by_name(self, a):
        a = a.lower()
        results = []
        for pet in self._pets:
            if (
                a in pet.get_animal_type().lower()
                or a in pet.get_gender().lower()
                or a in str(pet.get_age()).lower()
                or a in pet.get_color().lower()
                or a in pet.get_nickname().lower()
                or a in pet.get_owner_phone().lower()
            ):
                results.append(pet)
        return results

    def change_user_credentials(self, username, new_login=None, new_password=None):
        user = self.find_user(username)
        if user:
            if new_login:
                user.set_username(new_login)
            if new_password:
                user.update_password(
                    user.check_password(new_password), new_password
                )  # Обновляем хеш пароля
            self.save_data()  # Сохраняем данные после изменения данных пользователя
            return f"Данные о пользователе '{username}' были обновлены!."
        return f"Пользователь '{username}' не найден."

    def user_menu(self, user):
        while True:
            action = input(
                "Выберите действие: [1] Просмотреть животных, [2] Сортировка по возрасту, [3] Обновление профиля, [4] Поиск животного, [0] Выйти: "
            )

            if action == "1":
                self.show_pets()
            elif action == "2":
                self.sort_pets("age")
            elif action == "3":
                old_password = input("Введите старый пароль: ")
                new_password = input("Введите новый пароль: ")
                if user.update_password(old_password, new_password):
                    self.save_data()  # Сохраняем данные после изменения пароля
                    print("Данные пользователя обновлены")
            elif action == "4":
                a = input("Введите имя питомца, которого хотите найти:")
                results = self.search_pet_by_name(a)
                if results:
                    print(f"\nРезультаты поиска по запросу {a}")
                    print(
                        f"{'Вид':<10} {'Пол':<10} {'Возраст':<10} {'Цвет':<15} {'Кличка':<15} {'Телефон владельца':<15}"
                    )
                    print("_" * 90)
                    for pet in results:
                        print(
                            f"{pet.get_animal_type():<10} {pet.get_gender():<10} {pet.get_age():<10} {pet.get_color():<15} {pet.get_nickname():<15} {pet.get_owner_phone():<15}"
                        )
                else:
                    print("Питомцы не найдены.")
            elif action == "0":
                break
            else:
                print("Неверное действие.")

    def admin_menu(self):
        while True:
            action = input(
                "Выберите действие: [1] Добавить животное, [2] Удалить животное, [3] Изменить критерии, [4] Поиск животного, [5] Изменить данные пользователя, [6] Сортировка по возрасту, [7] Импорт данных, [8] Экспорт данных, [0] Выйти: "
            )

            if action == "1":
                self.add_pet()
            elif action == "2":
                self.delete_pet()
            elif action == "3":
                self.update_pet()
            elif action == "4":
                a = input("Введите имя питомца, которого хотите найти:")
                results = self.search_pet_by_name(a)
                if results:
                    print(f"\nРезультаты поиска по запросу {a}")
                    print(
                        f"{'Вид':<10} {'Пол':<10} {'Возраст':<10} {'Цвет':<15} {'Кличка':<15} {'Телефон владельца':<15}"
                    )
                    print("_" * 90)
                    for pet in results:
                        print(
                            f"{pet.get_animal_type():<10} {pet.get_gender():<10} {pet.get_age():<10} {pet.get_color():<15} {pet.get_nickname():<15} {pet.get_owner_phone():<15}"
                        )
                else:
                    print("Питомцы не найдены.")
            elif action == "5":
                username = input("Введите текущее имя пользователя: ")
                new_login = input(
                    "Введите новое имя пользователя (оставьте пустым, если не хотите менять): "
                )
                new_password = input(
                    "Введите новый пароль (оставьте пустым, если не хотите менять): "
                )

                result = self.change_user_credentials(username, new_login, new_password)
                print(result)
                print("Обновленные пользователи:")
                for user in self._users:
                    user.display_info()
            elif action == "6":
                self.sort_pets("age")
            elif action == "7":
                filename = input("Введите имя файла для импорта: ")
                try:
                    self.import_data(filename)
                    print("Импорт данных успешно завершен!")
                except Exception as e:
                    print(f"Ошибка при импорте данных: {e}")
            elif action == "8":
                filename = input("Введите имя файла для экспорта: ")
                try:
                    self.export_data(filename)
                    print("Экспорт данных успешно завершен!")
                except Exception as e:
                    print(f"Ошибка при экспорте данных: {e}")
            elif action == "0":
                break
            else:
                print("Неверное действие.")

    def export_data(self, filename):
        data = {
            "users": [user.to_dict() for user in self._users],
            "pets": [pet.to_dict() for pet in self._pets],
        }

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)  # Красивый JSON
            print(f"Данные успешно экспортированы в JSON файл: {filename}")

        except FileNotFoundError:
            print(f"Файл {filename} не найден.")
        except Exception as e:
            print(f"Произошла ошибка при экспорте: {e}")

    def import_data(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Очищаем текущие данные, чтобы не было дубликатов
            self._users = []
            self._pets = []

            for user_data in data["users"]:
                self._users.append(User.from_dict(user_data))

            for pet_data in data["pets"]:
                self._pets.append(Pet.from_dict(pet_data))
            self.save_data() #Сохраняем данные после импорта
            print(f"Данные успешно импортированы из JSON файла: {filename}")

        except FileNotFoundError:
            print(f"Файл {filename} не найден.")
        except json.JSONDecodeError:
            print(f"Ошибка: Некорректный формат JSON в файле {filename}.")
        except KeyError as e:
            print(f"Ошибка: Отсутствует ключ '{e}' в JSON файле.")
        except Exception as e:
            print(f"Произошла ошибка при импорте: {e}")


if __name__ == "__main__":
    system = PetManagementSystem()

    while True:
        action = input(
            "Выберите действие: [1] Регистрация, [2] Авторизация, [0] Выйти: "
        )

        if action == "1":
            system.register()
        elif action == "2":
            user = system.login()
            if user:
                if user.get_role() == "admin":
                    system.admin_menu()
                else:
                    system.user_menu(user)
        elif action == "0":
            print("Вы вышли из программы.")
            break
        else:
            print("Неверное действие.")


