from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from pymysql import OperationalError, InterfaceError


class SettingsScreen(MDScreen):
    """Class of screen with application's settings."""
    settings = {'theme': 'light', 'data_length': 4, 'learning_level': 4,
                'guess_level': 4, 'guess_length': 4, 'match_level': 4, 'match_length': 4}

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

    def on_pre_enter(self):
        """A method that works when user enters the screen.
        It gets settings from the user class.
        """
        self.user_name = MDApp.get_running_app().user.name
        self.email = MDApp.get_running_app().user.email
        self.settings = MDApp.get_running_app().user.settings
        self.ids.name.text = self.user_name
        self.ids.email.text = self.email
        self.ids.data_length.text = str(self.settings['data_length'])
        self.ids.guess.text = str(self.settings['guess_level'])
        self.ids.guess_length.text = str(self.settings['guess_length'])
        self.ids.match.text = str(self.settings['match_level'])
        self.ids.match_length.text = str(self.settings['match_length'])
        self.ids.learning.text = str(self.settings['learning_level'])
        self.ids.switch.active = self.settings['theme'] == 'dark'

    def on_pre_leave(self):
        """A method that works when user leaves the screen.
        It saves the user's settings in the database.
        """
        if MDApp.get_running_app().connected:
            try:
                MDApp.get_running_app().con.ping(True)
                with MDApp.get_running_app().con.cursor() as cursor:
                    cursor.execute(f'''UPDATE settings
                                       SET theme="{self.settings['theme']}",
                                       data_length="{self.settings['data_length']}",
                                       learning_level="{self.settings['learning_level']}",
                                       guess_level="{self.settings['guess_level']}",
                                       guess_length="{self.settings['guess_length']}",
                                       match_level="{self.settings['match_level']}",
                                       match_length="{self.settings['match_length']}"
                                       WHERE user_id="{MDApp.get_running_app().user.user_id}"''')
                    MDApp.get_running_app().con.commit()

            except OperationalError:
                pass
            except InterfaceError:
                pass
        MDApp.get_running_app().user.settings = self.settings

    def delete_pressed(self, instance):
        """A method that works if user pressed button that deletes their account.
        It asks if they are sure they want to delete their account.
        """
        self.create_delete_dialog("Удалить аккаунт?")

    def delete_data(self, instance):
        """A method that deletes the account from the database."""
        self.close_delete_dialog('')
        user_id = MDApp.get_running_app().user.user_id
        if MDApp.get_running_app().connected:
            try:
                MDApp.get_running_app().con.ping(True)
                with MDApp.get_running_app().con.cursor() as cursor:
                    cursor.execute(f'''DELETE FROM users WHERE id = "{user_id}"''')
                    cursor.execute(f'''DELETE FROM settings WHERE user_id = "{user_id}"''')
                    cursor.execute(f'''DELETE FROM marked_objects WHERE user_id = "{user_id}"''')
                    MDApp.get_running_app().con.commit()

            except OperationalError:
                self.create_dialog('Нет подключения к сети')
                return
            except InterfaceError:
                pass
        MDApp.get_running_app().store.put('UserInfo')
        self.exit('')

    def exit(self, instance):
        """A method that works when user wants to leave his account."""
        MDApp.get_running_app().screens = []
        manager = MDApp.get_running_app().scr_manager.main_screen.ids.sm
        manager.current = 'data'
        MDApp.get_running_app().scr_manager.current = 'enter'

    def create_delete_dialog(self, text):
        self.delete_dialog = MDDialog(
            text=text,
            buttons=[
                MDFlatButton(
                    text='Подтвердить',
                    font_style='Button',
                    theme_text_color="Error",
                    on_release=self.delete_data
                ),
                MDRaisedButton(
                    text='Отмена',
                    font_style='Button',
                    on_release=self.close_delete_dialog
                )

            ],
        )
        self.delete_dialog.open()

    def close_delete_dialog(self, obj):
        self.delete_dialog.dismiss()

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

    def level_up(self, instance, t):
        """A method that increases the chosen number if possible."""
        if t == 'data_length':
            if self.settings['data_length'] < 30:
                self.settings['data_length'] += 1
                self.ids.data_length.text = str(self.settings['data_length'])
        if t == 'guess':
            if self.settings['guess_level'] < 6:
                self.settings['guess_level'] += 1
                self.ids.guess.text = str(self.settings['guess_level'])
        elif t == 'guess_length':
            if self.settings['guess_length'] < 20:
                self.settings['guess_length'] += 1
                self.ids.guess_length.text = str(self.settings['guess_length'])
        elif t == 'match':
            if self.settings['match_level'] < 6:
                self.settings['match_level'] += 1
                self.ids.match.text = str(self.settings['match_level'])
        elif t == 'match_length':
            if self.settings['match_length'] < 20:
                self.settings['match_length'] += 1
                self.ids.match_length.text = str(self.settings['match_length'])
        elif t == 'learning':
            if self.settings['learning_level'] < 20:
                self.settings['learning_level'] += 1
                self.ids.learning.text = str(self.settings['learning_level'])

    def level_down(self, instance, t):
        """A method that decreases the chosen number if possible."""
        if t == 'data_length':
            if self.settings['data_length'] > 2:
                self.settings['data_length'] -= 1
                self.ids.data_length.text = str(self.settings['data_length'])
        if t == 'guess':
            if self.settings['guess_level'] > 2:
                self.settings['guess_level'] -= 1
                self.ids.guess.text = str(self.settings['guess_level'])
        elif t == 'guess_length':
            if self.settings['guess_length'] > 1:
                self.settings['guess_length'] -= 1
                self.ids.guess_length.text = str(self.settings['guess_length'])
        elif t == 'match':
            if self.settings['match_level'] > 2:
                self.settings['match_level'] -= 1
                self.ids.match.text = str(self.settings['match_level'])
        elif t == 'match_length':
            if self.settings['match_length'] > 1:
                self.settings['match_length'] -= 1
                self.ids.match_length.text = str(self.settings['match_length'])
        elif t == 'learning':
            if self.settings['learning_level'] > 2:
                self.settings['learning_level'] -= 1
                self.ids.learning.text = str(self.settings['learning_level'])
