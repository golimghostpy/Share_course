import sys
import socket
import json

from PyQt5.QtWidgets import ( # подключение всех необходимых виджетов для интерфейса
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
    QCalendarWidget,
    QDialog,
    QDialogButtonBox,
    QInputDialog,
    QFormLayout,
    QDateEdit
)
from PyQt5.QtCore import Qt, QDate, QPoint
from PyQt5.QtGui import QPainter, QColor

clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # привязка сокета

def send_to_server(message): # отправка сообщения на сервер и получение ответа
    try:
        clientSock.sendall(message.encode())
        response = clientSock.recv(65536)
        return response.decode()
    except Exception as e:
        print(f"Error communicating with server: {e}")

class CustomCalendarWidget(QCalendarWidget): # модифицируем календарь для отображения событий
    def __init__(self, parent=None):
        super().__init__(parent)
        self.events = {}

    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)
        if date in self.events:
            painter.setBrush(QColor(255, 0, 0))
            painter.drawEllipse(rect.topLeft() + QPoint(3, 3), 3, 3) # нарисуем красные точки в углу, если есть данные

    def setEvent(self, date, event):
        if date not in self.events:
            self.events[date] = []
        self.events[date].append(event)
        self.updateCell(date)

    def getEvents(self, date):
        return self.events.get(date, [])

    def removeEvent(self, date, event):
        if date in self.events:
            self.events[date].remove(event)
            if not self.events[date]:
                del self.events[date]
            self.updateCell(date)

def check_sql_injection(to_check, what_to_check): # ограничение используемых символов в полях ввода
    for i in to_check:
        if what_to_check == 'login' and not (i.isalnum() or i == '_'):
            return True
        elif what_to_check == 'password' and not(i.isalnum() or i in '!#$%&()*+-:;<=>?@[]^_{|}~'):
            return True
        elif what_to_check == 'word' and not(i.isalpha()):
            return True
        elif what_to_check == 'number' and not(i.isdigit()):
            return True
        elif what_to_check == 'number+word' and not(i.isalnum()):
            return True
        elif what_to_check == 'simple lable' and not(i.isalnum() or i in ' :-_'):
            return True

current_login = None

class LoginWindow(QWidget): # окно авторизации
    def __init__(self, switch_to_register, switch_to_main):
        super().__init__()
        self.switch_to_register = switch_to_register
        self.switch_to_main = switch_to_main
        self.initUI()

    def initUI(self): # отрисовка интерфейса
        self.setWindowTitle('Login')

        self.label_username = QLabel('Имя пользователя:', self)
        self.entry_username = QLineEdit(self)
        self.label_password = QLabel('Пароль:', self)
        self.entry_password = QLineEdit(self)
        self.entry_password.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton('Войти', self)
        self.register_button = QPushButton('Регистрация', self)

        self.login_button.clicked.connect(self.login_user)
        self.register_button.clicked.connect(self.switch_to_register)

        layout = QVBoxLayout()
        layout.addWidget(self.label_username)
        layout.addWidget(self.entry_username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.entry_password)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)
        self.setStyleSheet(self.get_stylesheet()) # подключаем стиль

    def login_user(self): # авторизация
        global current_login
        username = self.entry_username.text()
        password = self.entry_password.text()

        if not username or not password:
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')
            return

        if len(username) > 32:
            QMessageBox.warning(self, 'Ошибка логина', 'Имя пользователя слишком длинное\nМаксимум 32 символа')
            return
        if len(password) > 32:
            QMessageBox.warning(self, 'Ошибка пароля', 'Пароль слишком длинный\nМаксимум 32 символа')
            return

        if check_sql_injection(username, 'login'):
            QMessageBox.warning(self, 'Ошибка логина', 'Запрещенные символы в логине (могут быть только буквы, цифры и _)')
            return
        if check_sql_injection(password, 'password'):
            QMessageBox.warning(self, 'Ошибка пароля', 'Запрещенные символы в пароле (могут быть только буквы, цифры и !#$%&()*+-:;<=>?@[]^_{|}~)')
            return

        answer = send_to_server(f"login {username} {password}") # пробуем войти

        if answer == "wrong login": # нет пользователя
            QMessageBox.warning(self, 'Ошибка логина', 'Несуществующее имя пользователя')
        elif answer == "wrong password": # неверный пароль
            QMessageBox.warning(self, 'Ошибка пароля', 'Неверный пароль')
        else:
            current_login = username
            self.switch_to_main() # переключение на окно контактов

    def get_stylesheet(self): # стиль
        return """
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
                font-size: 14px;
                color: black;
            }
            QLabel {
                margin: 10px 0;
                color: black;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                color: black;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

class RegistrationWindow(QWidget): # окно регистрации
    def __init__(self, switch_to_login):
        super().__init__()
        self.switch_to_login = switch_to_login
        self.initUI()

    def initUI(self): # отрисовка интерфейса
        self.setWindowTitle('Registration')

        self.label_username = QLabel('Имя пользователя:', self)
        self.entry_username = QLineEdit(self)
        self.label_password = QLabel('Пароль:', self)
        self.entry_password = QLineEdit(self)
        self.entry_password.setEchoMode(QLineEdit.Password)
        self.label_confirm_password = QLabel('Подтверждение пароля:', self)
        self.entry_confirm_password = QLineEdit(self)
        self.entry_confirm_password.setEchoMode(QLineEdit.Password)
        self.register_button = QPushButton('Зарегистрироваться', self)
        self.back_button = QPushButton('Вход', self)

        self.register_button.clicked.connect(self.register_user)
        self.back_button.clicked.connect(self.switch_to_login)

        layout = QVBoxLayout()
        layout.addWidget(self.label_username)
        layout.addWidget(self.entry_username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.entry_password)
        layout.addWidget(self.label_confirm_password)
        layout.addWidget(self.entry_confirm_password)
        layout.addWidget(self.register_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)
        self.setStyleSheet(self.get_stylesheet()) # подключение стиля

    def register_user(self): # регистрация пользователя
        username = self.entry_username.text()
        password = self.entry_password.text()
        confirm_password = self.entry_confirm_password.text()

        if not(username and password and confirm_password):
            QMessageBox.warning(self, 'Ошибка ввода', 'Заполните все поля')
            return

        if password != confirm_password:
            QMessageBox.warning(self, 'Ошибка ввода', 'Пароли не совпадают, повторите попытку')
            return

        if len(username) > 32:
            QMessageBox.warning(self, 'Ошибка логина', 'Имя пользователя слишком длинное\nМаксимум 32 символа')
            return
        if len(password) > 32:
            QMessageBox.warning(self, 'Ошибка пароля', 'Пароль слишком длинный\nМаксимум 32 символа')
            return

        if check_sql_injection(username, 'login'):
            QMessageBox.warning(self, 'Ошибка логина', 'Запрещенные символы в логине (могут быть только буквы, цифры и _)')
            return
        if check_sql_injection(password, 'password'):
            QMessageBox.warning(self, 'Ошибка пароля', 'Запрещенные символы в пароле (могут быть только буквы, цифры и !#$%&()*+-:;<=>?@[]^_{|}~)')
            return

        answer = send_to_server(f"register {username} {password} {confirm_password}") # пробуем зарегистрировать

        if answer == "login already exists": # пользователь уже существует
            QMessageBox.warning(self, 'Ошибка логина', 'Пользователь с таким именем уже существует')
            return

        QMessageBox.information(self, 'Регистрация', f'Пользователь {username} успешно зарегистрирован') # выводим оповещение
        self.entry_username.clear()
        self.entry_password.clear()
        self.entry_confirm_password.clear()
        switch_to_login() # переключаемся на меню входа

    def get_stylesheet(self): # стиль
        return """
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
                font-size: 14px;
                color: black;
            }
            QLabel {
                margin: 10px 0;
                color: black;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                color: black;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

class ChangePasswordWindow(QWidget): # окно смены пароля
    def __init__(self, switch_to_contacts, switch_to_events):
        super().__init__()
        self.switch_to_contacts = switch_to_contacts
        self.switch_to_events = switch_to_events
        self.initUI()

    def initUI(self): # отрисовка интерфейса
        self.setWindowTitle('Change password')

        self.label_change_password = QLabel('Сменить пароль:', self)
        self.label_old_password = QLabel('Старый пароль:', self)
        self.entry_old_password = QLineEdit(self)
        self.entry_old_password.setEchoMode(QLineEdit.Password)
        self.label_new_password = QLabel('Новый пароль:', self)
        self.entry_new_password = QLineEdit(self)
        self.entry_new_password.setEchoMode(QLineEdit.Password)
        self.label_confirm_new_password = QLabel('Подтвердите новый пароль:', self)
        self.entry_confirm_new_password = QLineEdit(self)
        self.entry_confirm_new_password.setEchoMode(QLineEdit.Password)
        self.change_password_button = QPushButton('Сменить пароль', self)
        self.contacts_button = QPushButton('Контакты', self)
        self.events_button = QPushButton('Мероприятия', self)

        layout = QVBoxLayout()
        layout.addWidget(self.label_change_password)
        layout.addWidget(self.label_old_password)
        layout.addWidget(self.entry_old_password)
        layout.addWidget(self.label_new_password)
        layout.addWidget(self.entry_new_password)
        layout.addWidget(self.label_confirm_new_password)
        layout.addWidget(self.entry_confirm_new_password)
        layout.addWidget(self.change_password_button)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.contacts_button)
        button_layout.addWidget(self.events_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setStyleSheet(self.get_stylesheet()) # подключение стиля

        self.change_password_button.clicked.connect(self.change_password)
        self.contacts_button.clicked.connect(self.switch_to_contacts)
        self.events_button.clicked.connect(self.switch_to_events)

    def change_password(self): # смена пароля
        global current_login
        old_password = self.entry_old_password.text()
        new_password = self.entry_new_password.text()
        confirm_new_password = self.entry_confirm_new_password.text()

        if not(old_password and new_password and confirm_new_password):
            QMessageBox.warning(self, 'Ошибка ввода', 'Заполните все поля')
            return

        check_old = send_to_server(f'login {current_login} {old_password}') # проверяем, точно ли пользователь знает прежний пароль
        if check_old == 'wrong password':
            QMessageBox.warning(self, 'Ошибка пароля', 'Старый пароль неверный')
            return

        if len(new_password) > 32:
            QMessageBox.warning(self, 'Ошибка пароля', 'Новый пароль слишком длинный\nМаксимум 32 символа')
            return

        if new_password != confirm_new_password:
            QMessageBox.warning(self, 'Ошибка пароля', 'Пароли не совпадают, попробуйте еще раз')
            return

        if check_sql_injection(new_password, 'password'):
            QMessageBox.warning(self, 'Ошибка пароля', 'Запрещенные символы в пароле (могут быть только буквы, цифры и !#$%&()*+-:;<=>?@[]^_{|}~)')
            return

        if old_password == new_password:
            QMessageBox.warning(self, 'Ошибка пароля', 'Нельзя оставить старый пароль')
            return

        answer = send_to_server(f"change_password {current_login} {new_password}") # отправляем запрос на смену пароля

        QMessageBox.information(self, 'Смена пароля', f'Пароль успешно изменен') # оповещение

        # очищаем формы
        self.entry_old_password.clear()
        self.entry_new_password.clear()
        self.entry_confirm_new_password.clear()

    def get_stylesheet(self): # стиль
        return """
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
                font-size: 14px;
                color: black;
            }
            QLabel {
                margin: 10px 0;
                color: black;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                color: black;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

contacts = []
class ContactsWindow(QWidget): # окно контактов
    def __init__(self, switch_to_events, switch_to_main, switch_to_login):
        super().__init__()
        self.switch_to_events = switch_to_events
        self.switch_to_main = switch_to_main
        self.switch_to_login = switch_to_login
        self.initUI()
        self.load_contacts()

    def load_contacts(self): # прогрузка контактов из бд
        global contacts, current_login

        answer = send_to_server(f'get_contacts {current_login}')

        if answer == 'no contacts':
            return

        contact_matrix = [[j for j in i.split(',')] for i in answer[:-1].split(';')]
        for contact in contact_matrix:
            contacts.append({ # добавление в список
                'surname': contact[0],
                'name': contact[1],
                'patronymic': contact[2],
                'birth_date': contact[3],
                'city': contact[4],
                'street': contact[5],
                'house_number': contact[6],
                'apartment_number': contact[7],
                'phone': contact[8]
            })

            self.list_widget.addItem(QListWidgetItem(f"{contact[0]} {contact[1]} {contact[8]}")) # добавление отображения

    def initUI(self): # отрисовка интерфейса
        self.setWindowTitle('Contacts')

        self.list_widget = QListWidget(self)
        self.list_widget.itemDoubleClicked.connect(self.change_contact)

        self.add_button = QPushButton('Добавить', self)
        self.remove_button = QPushButton('Удалить', self)
        self.events_button = QPushButton('Мероприятия', self)
        self.change_password_button = QPushButton('Сменить пароль', self)
        self.logout_button = QPushButton('Выйти', self)

        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.events_button)
        button_layout.addWidget(self.change_password_button)

        layout.addLayout(button_layout)

        logout_layout = QHBoxLayout()
        logout_layout.addStretch()
        logout_layout.addWidget(self.logout_button)

        layout.addLayout(logout_layout)

        self.setLayout(layout)
        self.setStyleSheet(self.get_stylesheet()) # подключение стиля

        self.add_button.clicked.connect(self.add_contact)
        self.remove_button.clicked.connect(self.remove_contact)
        self.events_button.clicked.connect(self.switch_to_events)
        self.change_password_button.clicked.connect(self.switch_to_main)
        self.logout_button.clicked.connect(self.logout)

    def add_contact(self): # добавление контакта
        global contacts, current_login
        dialog = AddContactDialog(self) # создаем окно добавление контакта
        if dialog.exec_():
            contact = dialog.get_contact() # считывание данных с формы
            if contact:
                request = f'add_contact {current_login} '
                for i in contact.values():
                    request += i + ' '

                answer = send_to_server(request.strip())

                if answer == 'contact with this phone number is already exists': # нельзя добавить контакт с уже существующим номером
                    QMessageBox.warning(self, 'Ошибка контакта', 'Контакт с таким номером уже существует')
                    return

                contacts.append(contact) # добавляем контакт
                self.list_widget.addItem(QListWidgetItem(f"{contact['surname']} {contact['name']} {contact['phone']}")) # отображаем
            else:
                self.add_contact()

    def remove_contact(self): # удаление контакта
        global contacts, current_login
        selected_items = self.list_widget.selectedItems() # берем выбранный элемент
        if not selected_items:
            return
        for item in selected_items:
            index = self.list_widget.row(item)
            self.list_widget.takeItem(index)

            request = f'remove_contact {current_login} {contacts[index]['phone']}' # удаляем контакт
            send_to_server(request)

            del contacts[index]

    def change_contact(self, item): # изменить контакт
        global contacts
        index = self.list_widget.row(item)
        contact = contacts[index]
        dialog = EditContactDialog(contact, self) # выводим окно изменения контакта
        if dialog.exec_():
            updated_contact = dialog.get_contact()
            if updated_contact:
                request = f'change_contact {current_login} {contacts[index]['phone']} '
                contacts[index] = updated_contact
                for i in updated_contact.values():
                    request += i + ' '

                send_to_server(request.strip()) # отправляем запрос на изменение

                QMessageBox.information(self, 'Изменение контакта', f'Контакт успешно изменен') # оповещение
                item.setText(f"{updated_contact['surname']} {updated_contact['name']} {updated_contact['phone']}")

    def logout(self): # выход из аккаунта
        reply = QMessageBox.question(self, 'Выход', 'Вы уверены, что хотите выйти?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.switch_to_login()

    def get_stylesheet(self): # стиль
        return """
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
                font-size: 14px;
                color: black;
            }
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #ffffff;
                padding: 10px;
                color: black;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ddd;
                color: black;
            }
            QListWidget::item:selected {
                background-color: #007BFF;
                color: white;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

class PhoneInput(QLineEdit): # поле ввода номера телефона
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setInputMask("+00000000000;_") # маска

def check_contact(self): # проверка полей контакта на соответствие формату
    if check_sql_injection(self.surname_entry.text(), 'word'):
        QMessageBox.warning(self, 'Ошибка фамилии', 'Фамилия - одно слово')
        return None

    if check_sql_injection(self.name_entry.text(), 'word'):
        QMessageBox.warning(self, 'Ошибка имени', 'Имя - одно слово')
        return None

    if check_sql_injection(self.patronymic_entry.text(), 'word'):
        QMessageBox.warning(self, 'Ошибка отчества', 'Отчество - одно слово')
        return None

    if check_sql_injection(self.city_entry.text(), 'word'):
        QMessageBox.warning(self, 'Ошибка города', 'Город - одно слово\nЕсли ваш город имеет в названии более одного слова -> разделите их символом \'-\'')
        return None

    if check_sql_injection(self.street_entry.text(), 'word'):
        QMessageBox.warning(self, 'Ошибка улицы', 'Улица - одно слово\nЕсли ваша улица имеет в названии более одного слова -> разделите их символом \'-\'')
        return None

    if check_sql_injection(self.house_number_entry.text(), 'number+word'):
        QMessageBox.warning(self, 'Ошибка номера дома', 'Номер дома может быть только число+буква')
        return None

    if check_sql_injection(self.apartment_number_entry.text(), 'number'):
        QMessageBox.warning(self, 'Ошибка номера квартиры', 'Номер квартиры это число')
        return None

    return 'ok'

class AddContactDialog(QDialog): # окно добавления контакта
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self): # отрисовка интерфейса
        self.setWindowTitle('Add Contact')

        self.form_layout = QFormLayout()

        self.surname_label = QLabel('Фамилия:*', self)
        self.surname_entry = QLineEdit(self)
        self.form_layout.addRow(self.surname_label, self.surname_entry)

        self.name_label = QLabel('Имя:*', self)
        self.name_entry = QLineEdit(self)
        self.form_layout.addRow(self.name_label, self.name_entry)

        self.patronymic_label = QLabel('Отчество:', self)
        self.patronymic_entry = QLineEdit(self)
        self.form_layout.addRow(self.patronymic_label, self.patronymic_entry)

        self.birth_date_label = QLabel('Дата рождения:', self)
        self.birth_date_entry = QDateEdit(self)
        self.birth_date_entry.setCalendarPopup(True)
        self.form_layout.addRow(self.birth_date_label, self.birth_date_entry)

        self.city_label = QLabel('Город:', self)
        self.city_entry = QLineEdit(self)
        self.form_layout.addRow(self.city_label, self.city_entry)

        self.street_label = QLabel('Улица:', self)
        self.street_entry = QLineEdit(self)
        self.form_layout.addRow(self.street_label, self.street_entry)

        self.house_number_label = QLabel('Номер дома:', self)
        self.house_number_entry = QLineEdit(self)
        self.form_layout.addRow(self.house_number_label, self.house_number_entry)

        self.apartment_number_label = QLabel('Номер квартиры:', self)
        self.apartment_number_entry = QLineEdit(self)
        self.form_layout.addRow(self.apartment_number_label, self.apartment_number_entry)

        self.phone_label = QLabel('Номер телефона:*', self)
        self.phone_entry = PhoneInput(self)
        self.form_layout.addRow(self.phone_label, self.phone_entry)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(self.form_layout)
        layout.addWidget(self.button_box)

        self.setLayout(layout)
        self.setStyleSheet(self.get_stylesheet()) # подключение стиля

    def get_contact(self): # получение контакта из формы
        last_name = self.surname_entry.text()
        first_name = self.name_entry.text()
        phone = self.phone_entry.text()

        if not last_name or not first_name or not phone:
            QMessageBox.warning(self, 'Ошибка ввода', 'Заполните все поля')
            return None

        if not(check_contact(self)):
            return None

        if (len(last_name) > 64 or len(first_name) > 64 or len(self.patronymic_entry.text()) > 64 or
                len(self.city_entry.text()) > 64 or len(self.street_entry.text()) > 64 or
                len(self.house_number_entry.text()) > 64 or len(self.apartment_number_entry.text()) > 64): # проверка длины
            QMessageBox.warning(self, 'Ошибка ввода', 'Слишком много данных на 1 поле, максимальная длина - 64 символа')
            return None


        if len(phone) != 12:
            QMessageBox.warning(self, 'Phone Error', 'Длина номера телефона - 11 символов')
            return None

        return {
            'surname': last_name.capitalize(),
            'name': first_name.capitalize(),
            'patronymic': self.patronymic_entry.text().capitalize(),
            'birth_date': self.birth_date_entry.date().toString('yyyy-MM-dd'),
            'city': self.city_entry.text(),
            'street': self.street_entry.text(),
            'house_number': self.house_number_entry.text(),
            'apartment_number': self.apartment_number_entry.text(),
            'phone': phone
        }

    def get_stylesheet(self): # стиль
        return """
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
                font-size: 14px;
                color: black;
            }
            QLabel {
                margin: 10px 0;
                color: black;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                color: black;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

class EditContactDialog(QDialog): # окно изменение контакта
    def __init__(self, contact, parent=None):
        super().__init__(parent)
        self.contact = contact
        self.original_contact = contact.copy()
        self.initUI()

    def initUI(self): # отрисовка интерфейса
        self.setWindowTitle('Edit Contact')

        self.form_layout = QFormLayout()

        self.surname_label = QLabel('Фамилия:*', self)
        self.surname_entry = QLineEdit(self)
        self.surname_entry.setText(self.contact.get('surname', ''))
        self.surname_entry.textChanged.connect(self.check_changes)
        self.form_layout.addRow(self.surname_label, self.surname_entry)

        self.name_label = QLabel('Имя:*', self)
        self.name_entry = QLineEdit(self)
        self.name_entry.setText(self.contact.get('name', ''))
        self.name_entry.textChanged.connect(self.check_changes)
        self.form_layout.addRow(self.name_label, self.name_entry)

        self.patronymic_label = QLabel('Отчество:', self)
        self.patronymic_entry = QLineEdit(self)
        self.patronymic_entry.setText(self.contact.get('patronymic', ''))
        self.patronymic_entry.textChanged.connect(self.check_changes)
        self.form_layout.addRow(self.patronymic_label, self.patronymic_entry)

        self.birth_date_label = QLabel('Дата рождения:', self)
        self.birth_date_entry = QDateEdit(self)
        self.birth_date_entry.setCalendarPopup(True)
        birth_date = QDate.fromString(self.contact.get('birth_date', ''), 'yyyy-MM-dd')
        self.birth_date_entry.setDate(birth_date)
        self.birth_date_entry.dateChanged.connect(self.check_changes)
        self.form_layout.addRow(self.birth_date_label, self.birth_date_entry)

        self.city_label = QLabel('Город:', self)
        self.city_entry = QLineEdit(self)
        self.city_entry.setText(self.contact.get('city', ''))
        self.city_entry.textChanged.connect(self.check_changes)
        self.form_layout.addRow(self.city_label, self.city_entry)

        self.street_label = QLabel('Улица:', self)
        self.street_entry = QLineEdit(self)
        self.street_entry.setText(self.contact.get('street', ''))
        self.street_entry.textChanged.connect(self.check_changes)
        self.form_layout.addRow(self.street_label, self.street_entry)

        self.house_number_label = QLabel('Номер дома:', self)
        self.house_number_entry = QLineEdit(self)
        self.house_number_entry.setText(self.contact.get('house_number', ''))
        self.house_number_entry.textChanged.connect(self.check_changes)
        self.form_layout.addRow(self.house_number_label, self.house_number_entry)

        self.apartment_number_label = QLabel('Номер квартиры:', self)
        self.apartment_number_entry = QLineEdit(self)
        self.apartment_number_entry.setText(self.contact.get('apartment_number', ''))
        self.apartment_number_entry.textChanged.connect(self.check_changes)
        self.form_layout.addRow(self.apartment_number_label, self.apartment_number_entry)

        self.phone_label = QLabel('Номер телефона:*', self)
        self.phone_entry = PhoneInput(self)
        self.phone_entry.setText(self.contact.get('phone', ''))
        self.phone_entry.textChanged.connect(self.check_changes)
        self.form_layout.addRow(self.phone_label, self.phone_entry)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Save).setEnabled(False)
        self.button_box.accepted.connect(self.save_contact)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(self.form_layout)
        layout.addWidget(self.button_box)

        self.setLayout(layout)
        self.setStyleSheet(self.get_stylesheet()) # подключение стиля

    def check_changes(self): # проверка изменений
        current_contact = self.get_contact()
        if current_contact != self.original_contact:
            self.button_box.button(QDialogButtonBox.Save).setEnabled(True)
        else:
            self.button_box.button(QDialogButtonBox.Save).setEnabled(False)

    def save_contact(self): # сохранение изменений
        current_contact = self.get_contact()
        if current_contact == self.original_contact:
            QMessageBox.warning(self, 'Нет изменений', 'Никаких изменений не произведено.')
        elif not current_contact:
            QMessageBox.warning(self, 'Ошибка ввода', 'Заполните или исправьте все поля')
        else:
            self.accept()

    def get_contact(self): # получение контакта из формы
        surname = self.surname_entry.text()
        name = self.name_entry.text()
        phone = self.phone_entry.text()

        if not (surname and name and phone):
            return None

        if not(check_contact(self)):
            return None

        return {
            'surname': surname,
            'name': name,
            'patronymic': self.patronymic_entry.text(),
            'birth_date': self.birth_date_entry.date().toString('yyyy-MM-dd'),
            'city': self.city_entry.text(),
            'street': self.street_entry.text(),
            'house_number': self.house_number_entry.text(),
            'apartment_number': self.apartment_number_entry.text(),
            'phone': phone
        }

    def get_stylesheet(self): # стиль
        return """
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
                font-size: 14px;
                color: black;
            }
            QLabel {
                margin: 10px 0;
                color: black;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                color: black;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

class EventsWindow(QWidget): # окно событий
    def __init__(self, switch_to_contacts, switch_to_main, switch_to_login):
        super().__init__()
        self.switch_to_contacts = switch_to_contacts
        self.switch_to_main = switch_to_main
        self.switch_to_login = switch_to_login
        self.initUI()
        self.load_events()

    def initUI(self): # отрисовка интерфейса
        self.setWindowTitle('Events')

        self.calendar = CustomCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.show_events_for_date)

        self.contacts_button = QPushButton('Контакты', self)
        self.change_password_button = QPushButton('Сменить пароль', self)
        self.logout_button = QPushButton('Выйти', self)

        layout = QVBoxLayout()
        layout.addWidget(self.calendar)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.contacts_button)
        button_layout.addWidget(self.change_password_button)

        layout.addLayout(button_layout)

        logout_layout = QHBoxLayout()
        logout_layout.addStretch()
        logout_layout.addWidget(self.logout_button)

        layout.addLayout(logout_layout)

        self.setLayout(layout)
        self.setStyleSheet(self.get_stylesheet()) # подключение стиля

        self.contacts_button.clicked.connect(self.switch_to_contacts)
        self.change_password_button.clicked.connect(self.switch_to_main)
        self.logout_button.clicked.connect(self.logout)

    def load_events(self): # загрузка событий из бд
        global current_login
        answer = send_to_server(f"get_events {current_login}")

        if answer == "no events":
            return

        event_matrix = [[j for j in i.split(',')[:-1]] for i in answer[:-1].split(';')]
        for event in event_matrix:
            if len(event) >= 2:
                date_str = event[0]
                events = event[1:]
                date = QDate.fromString(date_str, 'yyyy-MM-dd')
                if date.isValid():
                    for i in events:
                        self.calendar.setEvent(date, ' '.join(i.split('_')))

    def show_events_for_date(self, date): # показать события на дату
        dialog = EventListDialog(date, self.calendar, self) # создаем окно со списком событий
        dialog.exec_()

    def logout(self): # выйти из аккаунта
        reply = QMessageBox.question(self, 'Выход', 'Вы уверены, что хотите выйти?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.switch_to_login()

    def get_stylesheet(self): # стиль
        return """
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
                font-size: 14px;
                color: black;
            }
            QCalendarWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: white;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

class EventListDialog(QDialog): # список событий
    def __init__(self, date, calendar, parent=None):
        super().__init__(parent)
        self.date = date
        self.calendar = calendar
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f'Events for {self.date.toString("MMMM d, yyyy")}')

        self.list_widget = QListWidget(self)
        events = self.calendar.getEvents(self.date)
        for event in events:
            self.list_widget.addItem(QListWidgetItem(event))
        self.list_widget.itemDoubleClicked.connect(self.change_event)

        self.add_button = QPushButton('Добавить', self)
        self.remove_button = QPushButton('Удалить', self)
        self.close_button = QPushButton('Закрыть', self)

        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setStyleSheet(self.get_stylesheet())

        self.add_button.clicked.connect(self.add_event)
        self.remove_button.clicked.connect(self.remove_event)
        self.close_button.clicked.connect(self.close)

    def change_event(self, item): # изменение события
        old_event_name = item.text()
        new_event_name, ok = QInputDialog.getText(self, 'Смена мероприятия', 'Введите название мероприятия:', text=old_event_name)

        if check_sql_injection(new_event_name, 'simple lable'): # проверка символов
            QMessageBox.warning(self, 'Ошибка изменения', 'Вы можете писать только слова, числа и знаки :-_')
            return

        if ok and new_event_name:
            answer = send_to_server(f"change_event {current_login} {self.date.toString('yyyy-MM-dd')} {'_'.join(old_event_name.strip().split())} {'_'.join(new_event_name.strip().split())}")
            if answer == "successful change_event": # успешное изменение
                self.calendar.removeEvent(self.date, old_event_name)
                self.calendar.setEvent(self.date, new_event_name)
                item.setText(new_event_name)

    def add_event(self): # добавление события
        event_name, ok = QInputDialog.getText(self, 'Добавить', 'Введите название мероприятия:')

        if check_sql_injection(event_name, 'simple lable'):
            QMessageBox.warning(self, 'Ошибка добавления', 'Вы можете писать только слова, числа и знаки :-_')
            return

        if len(event_name) > 256:
            QMessageBox.warning(self, 'Ошибка ввода', 'Слишком длинное мероприятие, максимум - 256 символов')
            return None

        if ok and event_name:
            answer = send_to_server(f"add_event {current_login} {self.date.toString('yyyy-MM-dd')} {'_'.join(event_name.strip().split())}") # отправка запроса на добавление
            if answer == "successful add_event":
                self.list_widget.addItem(QListWidgetItem(event_name))
                self.calendar.setEvent(self.date, event_name)

    def remove_event(self): # удаление события
        selected_items = self.list_widget.selectedItems()
        if not selected_items: # если ничего не выбрано
            return
        for item in selected_items:
            event_name = item.text()
            answer = send_to_server(f"remove_event {current_login} {self.date.toString('yyyy-MM-dd')} {'_'.join(event_name.strip().split())}") # запрос на удаление
            if answer == "successful remove_event":
                self.calendar.removeEvent(self.date, event_name)
                self.list_widget.takeItem(self.list_widget.row(item))

    def get_stylesheet(self): # стиль
        return """
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
                font-size: 14px;
                color: black;
            }
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #ffffff;
                padding: 10px;
                color: black;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ddd;
                color: black;
            }
            QListWidget::item:selected {
                background-color: #007BFF;
                color: white;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

login_window = None
registration_window = None
change_password_window = None
contacts_window = None
events_window = None

def show_login_window(): # открыть окно авторизации
    global login_window
    login_window = LoginWindow(switch_to_registration, switch_to_contacts)
    login_window.resize(300, 300)
    login_window.show()

def show_registration_window(): # открыть окно регистрации
    global registration_window
    registration_window = RegistrationWindow(switch_to_login)
    registration_window.resize(300, 300)
    registration_window.show()

def show_change_password_window(): # открыть окно смены пароля
    global change_password_window
    change_password_window = ChangePasswordWindow(switch_to_contacts, switch_to_events)
    change_password_window.resize(300, 400)
    change_password_window.show()

def show_contacts_window(): # открыть окно контактов
    global contacts_window
    contacts_window = ContactsWindow(switch_to_events, switch_to_change_password, switch_to_login)
    contacts_window.resize(300, 400)
    contacts_window.show()

def show_events_window(): # открыть окно событий
    global events_window
    events_window = EventsWindow(switch_to_contacts, switch_to_change_password, switch_to_login)
    events_window.resize(300, 400)
    events_window.show()

def switch_to_registration(): # переключиться на регистрацию
    global login_window, registration_window
    if login_window:
        login_window.close()
    show_registration_window()

def switch_to_login(): # переключиться на вход
    global registration_window, login_window, contacts_window, events_window, contacts, current_login
    if registration_window:
        registration_window.close()
    if contacts_window:
        contacts, current_login = [], None
        contacts_window.close()
    if events_window:
        contacts, current_login = [], None
        events_window.close()
    show_login_window()

def switch_to_change_password(): # переключиться на смену пароля
    global change_password_window, contacts_window, events_window

    if contacts_window:
        contacts_window.close()
    if events_window:
        events_window.close()
    show_change_password_window()

def switch_to_contacts(): # переключиться на окно контактов
    global change_password_window, contacts_window, login_window
    if change_password_window:
        change_password_window.close()
    if events_window:
        events_window.close()
    if login_window:
        login_window.close()
    show_contacts_window()

def switch_to_events(): # переключиться на окно событий
    global change_password_window, events_window
    if change_password_window:
        change_password_window.close()
    if contacts_window:
        contacts_window.close()
    show_events_window()

if __name__ == '__main__':
    with open('clientConfig.json', 'r') as config:
        info = json.loads(config.read())
        dbPort, dbIP = info['dbPort'], info['dbIP']

    serverAddr = (str(dbIP), int(dbPort))
    clientSock.connect(serverAddr)

    app = QApplication(sys.argv)
    show_login_window()
    sys.exit(app.exec_())
