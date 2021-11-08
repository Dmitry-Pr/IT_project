import pymysql
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, CardTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.base import EventLoop
from kivy.storage.jsonstore import JsonStore
from pymysql import OperationalError, InterfaceError
from kivy.utils import platform

from data import DataScreen
from enter import EnterScreen
from settings import SettingsScreen
from registration import RegScreen
from info import InfoScreen
from ege import EGEScreen
from learning import LearningScreen
from guess import GuessScreen
from match import MatchScreen
from description import DescScreen
from add_objects import AddObjScreen
from loading import LoadingScreen
from config import host, user, passwd, port, database

Window.clearcolor = (1, 1, 1, 1)
Window.softinput_mode = "below_target"


class MainScreen(MDScreen):
    """Class that contains all the screens except enter and registration screens."""
    main_manager = ObjectProperty(None)
    main_toolbar = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)


class Manager(ScreenManager):
    """Class that helps to switch between enter, registration and main screens."""
    enter_screen = ObjectProperty(None)
    reg_screen = ObjectProperty(None)
    main_screen = ObjectProperty(None)


class User:
    """Class of user."""

    def __init__(self, user_id, name, email, settings):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.settings = settings


class MainApp(MDApp):
    """Main class of the application."""
    screens = []
    theme = 'light'
    obj_id = ''
    connected = False
    settings_shown = False
    store = JsonStore('users.json')
    user = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def connect_db(self):
        """A method that creates a connection to the database."""
        try:
            self.con = pymysql.connect(
                host=host,
                user=user,
                port=port,
                passwd=passwd,
                database=database,
                cursorclass=pymysql.cursors.DictCursor,
                read_timeout=2
            )
            self.connected = True
        except OperationalError:
            self.connected = False
        except InterfaceError:
            self.connected = False

    def on_stop(self):
        """A method that works when user leaves the application.
        It saves all the settings of the application
        that user made and closes the connection to database.
        """
        if self.connected:
            try:
                MDApp.get_running_app().con.ping(True)
                with MDApp.get_running_app().con.cursor() as cursor:
                    cursor.execute(f'''UPDATE settings
                                       SET theme="{self.user.settings['theme']}",
                                       data_length="{self.user.settings['data_length']}",
                                       learning_level="{self.user.settings['learning_level']}",
                                       guess_level="{self.user.settings['guess_level']}",
                                       match_level="{self.user.settings['match_level']}",
                                       match_length="{self.user.settings['match_length']}"
                                       WHERE user_id="{self.user.user_id}"''')
                    self.con.commit()

            except OperationalError:
                pass
            except InterfaceError:
                pass
            except AttributeError:
                pass
            self.con.close()

    def build(self):
        """A method that starts the application."""
        self.scr_manager = Manager(transition=CardTransition(duration=0.3, direction='up', mode='pop'))
        self.theme_cls.theme_style = "Light"
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)
        self.connect_db()
        try:
            if self.store.get('UserInfo')['name'] != '':
                self.create_user(self.store.get('UserInfo')['id'])
                if not self.user:
                    self.scr_manager.current = 'enter'
                else:
                    self.scr_manager.main_screen.ids.data_screen.enter()
                    self.scr_manager.main_screen.ids.sm.current = 'data'
                    self.scr_manager.current = 'main'
            else:
                self.scr_manager.current = 'enter'
        except KeyError:
            self.scr_manager.current = 'enter'
        except TypeError:
            self.scr_manager.current = 'enter'
        if platform == 'android':  # asking for a permission to access devises storage
            from android.permissions import Permission, request_permissions

            def callback(permission, results):
                if all([res for res in results]):
                    print("Got all permissions")
                else:
                    print("Did not get all permissions")

            request_permissions([Permission.READ_EXTERNAL_STORAGE,
                                 Permission.WRITE_EXTERNAL_STORAGE], callback)

        return self.scr_manager

    def create_user(self, user_id, registration=False):
        """A method creates users account if he has just passed registration.
        It also gets information about user.
        """
        settings = {'theme': 'light', 'data_length': 10,
                    'learning_level': 4, 'guess_level': 4,
                    'guess_length': 4, 'match_level': 4,
                    'match_length': 4}
        if self.connected:
            try:
                if registration:

                    MDApp.get_running_app().con.ping(True)
                    with MDApp.get_running_app().con.cursor() as cursor:
                        cursor.execute(f'''INSERT INTO settings (user_id, theme, data_length,
                                           learning_level, guess_level, guess_length, match_level, match_length)
                                           VALUES ("{user_id}", "{settings["theme"]}", "{settings["data_length"]}",
                                           "{settings["learning_level"]}", "{settings["guess_level"]}",
                                           "{settings["guess_length"]}", "{settings["match_level"]}",
                                           "{settings["match_length"]}")''')
                        self.con.commit()
                else:
                    MDApp.get_running_app().con.ping(True)
                    with MDApp.get_running_app().con.cursor() as cursor:
                        cursor.execute(f'''SELECT * FROM settings
                                           WHERE user_id="{user_id}"''')
                        settings = cursor.fetchone()

            except OperationalError:
                pass
            except InterfaceError:
                pass
            try:
                MDApp.get_running_app().con.ping(True)
                with MDApp.get_running_app().con.cursor() as cursor:
                    cursor.execute(f'''SELECT * FROM users
                                       WHERE id="{user_id}"''')
                    user_data = cursor.fetchone()
                self.scr_manager.main_screen.ids.data_screen.clear_data_screen()
                self.user = User(user_id, user_data['name'], user_data['email'], settings)
                self.change_theme(self.user.settings['theme'])

            except OperationalError:
                self.user = None
            except InterfaceError:
                pass

    def login_check(self, instance):
        """A method that checks if user passed enter screen
        and saves them locally so they will not have
        to enter the account the next time.
        """
        self.connect_db()
        if self.scr_manager.ids.enter_screen.check():
            self.store.put('UserInfo', id=self.user.user_id, name=self.user.name, email=self.user.email)
            self.scr_manager.main_screen.ids.data_screen.enter()
            self.change_screen(self.scr_manager, 'main')

    def reg_check(self, instance):
        """A method that checks if user passed registration screen
        and saves them locally so they will not have
        to enter the account the next time.
        """
        self.connect_db()
        if self.scr_manager.ids.reg_screen.check():
            self.store.put('UserInfo', id=self.user.user_id, name=self.user.name, email=self.user.email)
            self.scr_manager.main_screen.ids.data_screen.enter()
            self.change_screen(self.scr_manager, 'main')

    def hook_keyboard(self, window, key, *args):
        """A method that changes the current screen
        if user clicked 'Back' button on his devise.
        (Escape on PC)
        """

        if key == 27:
            if len(self.screens):
                sm, screen = self.screens[-1]
                self.screens = self.screens[:-1]
                sm.current = screen
                return True
            else:
                pass

    def change_screen(self, sm, screen):
        """A method that changes screen to screen, given as argument."""
        if not self.screens or sm.current != screen:
            if sm.current == 'add_obj' and screen != 'loading':
                self.scr_manager.main_screen.ids.add_obj.loading = False
            if sm.current == 'match' and screen != 'loading':
                self.scr_manager.main_screen.ids.match.loading = False
            if screen != 'loading' and sm.current != 'loading':
                self.screens.append([sm, sm.current])
            sm.current = screen

    def change_theme(self, t):
        """A method that changes the application theme."""
        if t == 'light':
            self.theme = "light"
            self.theme_cls.theme_style = "Light"
        else:
            self.theme = 'dark'
            self.theme_cls.theme_style = "Dark"
        self.user.settings['theme'] = t


if __name__ == '__main__':
    app = MainApp()
    app.run()
