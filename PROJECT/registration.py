import hashlib

from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from pymysql import OperationalError, InterfaceError


class RegScreen(MDScreen):
    """Class of registration screen."""
    email_exist = False
    login_exist = False

    def __init__(self, **kwargs):
        self.login = ObjectProperty('')
        self.password = ObjectProperty('')
        self.password_2 = ObjectProperty('')
        self.email = ObjectProperty('')
        super(RegScreen, self).__init__(**kwargs)

    def check(self):
        """A method that checks if all the fields are filled in correctly."""
        if self.login.text == '':
            self.create_dialog("Введите логин")
            return False
        elif self.password.ids.text_field.text == '':
            self.create_dialog("Введите пароль")
            return False
        elif self.password_2.ids.text_field.text == '':
            self.create_dialog("Введите пароль ещё раз")
            return False
        elif self.password.ids.text_field.text != self.password_2.ids.text_field.text:
            self.create_dialog("Пароли не совпадают")
            return False
        elif self.email.text == '':
            self.create_dialog('Введите email')
        elif len(self.email.text) == 1 or '@' not in self.email.text:
            self.create_dialog('Введен некорректный email, введите другой email')
        elif self.email.text.index('@') == 0 or self.email.text.index('@') == len(self.email.text) - 1:
            self.create_dialog('Введен некорректный email, введите другой email')
        elif len(self.password.ids.text_field.text) < 6:
            self.create_dialog("Пароль должен содержать не менее 6 символов")
            return False
        else:
            completed = self.user_reg(self.login.text, self.password.ids.text_field.text, self.email.text)
            if completed == -1:
                self.create_dialog("Подключение к сети потерянно")
                return False
            elif completed:
                return True
            else:
                if self.email_exist:
                    self.email_exist = False
                    self.create_dialog("Данный email уже используется, введите другой email")
                elif self.login_exist:
                    self.login_exist = False
                    self.create_dialog("Пользователь с таким именем уже существует, введите другое имя")
                return False

    def create_dialog(self, text):
        self.dialog = MDDialog(
            text=text,
            buttons=[
                MDRaisedButton(
                    text='Ок',
                    font_style='Button',
                    on_release=self.close_dialog
                )
            ],
        )
        self.dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss()

    def user_reg(self, log, pas, email):
        """A method that checks that there is no user with the same login and email.
        It also creates a user in the database."""
        pwd = hashlib.md5(pas.encode()).hexdigest()
        if MDApp.get_running_app().connected:
            try:
                MDApp.get_running_app().con.ping(True)
                with MDApp.get_running_app().con.cursor() as cursor:
                    cursor.execute(f"SELECT id FROM users WHERE name='{log}'")
                    try_user = cursor.fetchone()
                    if try_user:
                        self.login_exist = True
                        return False
                    cursor.execute(f"SELECT id FROM users WHERE email='{email}'")
                    try_email = cursor.fetchone()
                    if try_email:
                        self.email_exist = True
                        return False
                    cursor.execute(f"INSERT INTO users (name, password, email)"
                                   f" VALUES ('{log}', '{pwd}', '{email}')")
                    MDApp.get_running_app().con.commit()
                    cursor.execute(f"SELECT id FROM users WHERE name='{log}' AND password='{pwd}'")
                    user_id = cursor.fetchone()
                    MDApp.get_running_app().create_user(user_id['id'], True)
                    return user_id
            except OperationalError:
                return -1
            except InterfaceError:
                return -1
        return -1
