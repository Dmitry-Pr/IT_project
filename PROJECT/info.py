import webbrowser

from kivy.event import EventDispatcher
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFloatingActionButton, MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from pymysql import OperationalError, InterfaceError

from buttons import ScrollLabel


class InfoScreen(MDScreen, EventDispatcher):
    """CLass of screen with information about an object."""
    box = ObjectProperty()
    scr = ObjectProperty()
    more_inf = ObjectProperty()
    add_btn = ObjectProperty()
    obj_pict = StringProperty()
    obj_name = StringProperty()
    obj_user_id = 0
    obj_id = 0
    obj_info = ''
    delete_btn = None
    add_pressed = False
    more_pressed = False

    def __init__(self, **kwargs):
        super(InfoScreen, self).__init__(**kwargs)

    def on_pre_enter(self):
        """A method that works when user enters the screen."""
        self.obj_id = MDApp.get_running_app().obj_id
        if self.delete_btn:
            self.remove_widget(self.delete_btn)
            self.delete_btn = None
        self.get_object()
        if self.more_pressed:
            self.get_information()

    def get_information(self, instance=None):
        """A method that changes information shown on the screen
        if 'Больше информации' has been pressed or unpressed."""
        if not self.more_pressed:
            self.more_pressed = True
            self.more_inf.text = 'Меньше информации'
            self.txt_box = MDBoxLayout(orientation='vertical',
                                       size_hint=[0.9, 0.9],
                                       pos_hint={'center_x': 0.5, 'center_y': 0.5})
            scr_label = ScrollLabel(text=self.obj_info)
            wid = Widget(size_hint_y=0.05)
            self.link = MDLabel(size_hint_y=0.1,
                                markup=True,
                                theme_text_color="Custom",
                                text_color=[54 / 255, 63 / 255, 183 / 255, .9],
                                text='[ref=]Искать в Интернете[/ref]',
                                on_ref_press=self.open_url)
            self.txt_box.add_widget(self.link)
            self.txt_box.add_widget(wid)
            self.txt_box.add_widget(scr_label)
            self.box.size_hint_y = 2
            self.box.add_widget(self.txt_box)
            self.scr.update_from_scroll()
            self.scr.scroll_y = 0.5
        else:
            self.more_pressed = False
            self.box.size_hint_y = 1
            self.more_inf.text = 'Больше информации'
            self.box.remove_widget(self.txt_box)

    def open_url(self, *args):
        """A method that searches a name of the object in the Internet."""
        webbrowser.open('https://yandex.ru/search/?text=' + self.obj_name)

    def get_object(self):
        """A method that gets information about the chosen object."""
        try:
            MDApp.get_running_app().con.ping(True)
            with MDApp.get_running_app().con.cursor() as cursor:
                cursor.execute(f'''SELECT * FROM objects WHERE id="{self.obj_id}"''')
                obj = cursor.fetchone()
                self.obj_id = obj['id']
                self.obj_pict = obj['image']
                self.obj_name = obj['name']
                self.obj_info = obj['information']
                self.obj_user_id = obj['user_id']
                cursor.execute(f'''SELECT * FROM marked_objects
                                           WHERE user_id="{MDApp.get_running_app().user.user_id}"
                                           AND obj_id="{self.obj_id}"''')
                obj_marked = cursor.fetchone()
                if obj_marked:
                    self.add_pressed = True
                    self.add_btn.text = 'Удалить\nиз помеченных'
                else:
                    self.add_pressed = False
                    self.add_btn.text = 'Добавить\nв помеченные'
                if self.obj_user_id:
                    self.delete_btn = MDFloatingActionButton(icon='trash-can',
                                                             pos_hint={'center_x': .85, 'center_y': .9},
                                                             on_release=self.delete)
                    self.add_widget(self.delete_btn)
        except InterfaceError as e:
            # print(e)
            return
        except OperationalError:
            self.clear_widgets()
            self.create_dialog('Подключение к сети потерянно')
            return

    def delete(self, instance):
        self.create_delete_dialog('Вы уверены, что хотите удалить этот объект?')

    def create_delete_dialog(self, text):
        self.delete_dialog = MDDialog(
            text=text,
            buttons=[
                MDFlatButton(
                    text='Подтвердить',
                    font_style='Button',
                    theme_text_color="Error",
                    on_release=self.delete_obj
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

    def delete_obj(self, instance):
        """A method that deletes the object from the database
        if the object is added by this user."""
        self.close_delete_dialog(None)
        if MDApp.get_running_app().connected:
            try:
                MDApp.get_running_app().con.ping(True)
                with MDApp.get_running_app().con.cursor() as cursor:
                    cursor.execute(f'''DELETE FROM objects WHERE id="{self.obj_id}"''')
                    cursor.execute(f'''DELETE FROM marked_objects WHERE obj_id="{self.obj_id}"''')
                    MDApp.get_running_app().con.commit()
                    MDApp.get_running_app().scr_manager.main_screen.ids.data_screen.clear_data_screen()
                    MDApp.get_running_app().scr_manager.main_screen.ids.data_screen.enter()
                    MDApp.get_running_app().change_screen(self.manager, 'data')
            except OperationalError:
                self.create_dialog('Подключение к сети потерянно')
            except InterfaceError:
                pass

    def add_to_marked(self, instance):
        """A method that adds the object to marked objects for this user."""
        if not self.add_pressed:
            self.add_pressed = True
            self.add_btn.text = 'Удалить\nиз помеченных'
            if MDApp.get_running_app().connected:
                try:
                    MDApp.get_running_app().con.ping(True)
                    with MDApp.get_running_app().con.cursor() as cursor:
                        cursor.execute(f'''INSERT INTO marked_objects (user_id, obj_id)
                                           VALUES ("{MDApp.get_running_app().user.user_id}", "{self.obj_id}")''')
                        MDApp.get_running_app().con.commit()
                except OperationalError:
                    self.create_dialog('Подключение к сети потерянно')
                except InterfaceError:
                    pass
        else:
            self.add_pressed = False
            self.add_btn.text = 'Добавить\nв помеченные'
            if MDApp.get_running_app().connected:
                try:
                    MDApp.get_running_app().con.ping(True)
                    with MDApp.get_running_app().con.cursor() as cursor:
                        cursor.execute(f'''DELETE FROM marked_objects
                                           WHERE user_id="{MDApp.get_running_app().user.user_id}"
                                           AND obj_id="{self.obj_id}"''')
                        MDApp.get_running_app().con.commit()
                except OperationalError:
                    self.create_dialog('Подключение к сети потерянно')
                except InterfaceError:
                    pass
