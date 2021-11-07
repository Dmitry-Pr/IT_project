from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
import hashlib

from pymysql import OperationalError, InterfaceError


class EnterScreen(MDScreen):
    """Class of enter screen."""
    def __init__(self, **kwargs):
        self.login = StringProperty('')
        self.password = StringProperty('')
        super(EnterScreen, self).__init__(**kwargs)

    def check(self):
        """A method that checks if all the fields are filled in correctly
        and if there is a user with this login and this password in the database.
        """
        if self.login.text == '':
            self.create_dialog("Введите логин")
        elif self.password.ids.text_field.text == '':
            self.create_dialog("Введите пароль")
        else:
            completed = self.user_check(self.login.text, self.password.ids.text_field.text)
            if completed == -1:
                self.create_dialog("Подключение к сети потерянно")
            elif completed:
                return True
            else:
                self.create_dialog("Неправильный логин или пароль")

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

    def user_check(self, log, pas):
        """A method that checks if there is a user user
        with this login and this password in the database.
        """
        pwd = hashlib.md5(pas.encode()).hexdigest()
        if MDApp.get_running_app().connected:
            try:
                MDApp.get_running_app().con.ping(True)
                with MDApp.get_running_app().con.cursor() as cursor:
                    cursor.execute(f"SELECT id FROM users WHERE name='{log}' AND password='{pwd}'")
                    user_id = cursor.fetchone()
                    if user_id:
                        MDApp.get_running_app().create_user(user_id['id'])
                        return user_id
                    return 0
            except OperationalError:
                return -1
            except InterfaceError:
                pass
        return -1


class ClickableTextField(MDRelativeLayout):
    """Class of a textfield with clickable icon in it."""
    text = StringProperty()
    """Text of the textfield."""
    hint_text = StringProperty()
    """Hint text of the textfield."""
