from _socket import gaierror
from threading import Thread
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.imagelist import SmartTileWithLabel
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget
from kivymd.uix.screen import MDScreen
from kivy.utils import platform
from ftplib import FTP
from pymysql import OperationalError, InterfaceError
import os
import datetime

from config import host, ftp_login, ftp_passwd


class AddObjScreen(MDScreen):
    """Class of adding objects to database screen."""
    fold = ''
    img = ''
    loading = False
    finished = False
    saving_image_finished = False
    saving_object_finished = False
    data = []

    def __init__(self, **kwargs):
        super(AddObjScreen, self).__init__(**kwargs)

    def on_pre_enter(self):
        """A method that works when user enters the screen."""
        self.data = []
        self.finished = False
        self.saving_image_finished = False
        self.saving_object_finished = False
        if self.loading:
            self.loading = False
            return
        try:
            self.clear_widgets()
            scr = ScrollView()
            lst = MDList()
            if platform == 'android':
                self.fold = '/storage/emulated/0/DCIM/'
            else:  # needed for debugging application on PC.
                self.fold = 'C:/Users/User/PycharmProjects/IVR/'  # change it to the path you need
            for directory in os.listdir(self.fold):
                icon = IconLeftWidget(icon='folder')
                item = OneLineIconListItem(text=directory, on_release=self.show_images)
                item.add_widget(icon)
                lst.add_widget(item)
            scr.add_widget(lst)
            self.add_widget(scr)
        except PermissionError:
            toast('Ошибка')
            self.clear_widgets()
            self.add_widget(MDLabel(text='Ошибка, нет доступа к хранилищу',
                                    halign='center'))

    def show_images(self, instance):
        """A method that works after user chose path to an image they want to add to the database."""
        self.fold += instance.text
        thread = Thread(target=self.find_images())
        thread.start()
        self.show_loading()
        Clock.schedule_interval(self.loading_finished, 0.2)

    def loading_finished(self, dt):
        """A method that checks if the loading of images finished."""
        if self.finished:
            self.finished = False
            if self.data:
                self.show_folder()
            MDApp.get_running_app().change_screen(self.manager, self.name)
            return False

    def show_loading(self):
        """A method that shows loading screen."""
        self.loading = True
        MDApp.get_running_app().change_screen(self.manager, 'loading')

    def find_images(self):
        """A method that finds images on user's devise."""
        try:
            self.data = os.listdir(self.fold + '/')
            self.data.sort(key=lambda x: datetime.datetime.fromtimestamp(os.path.getctime(
                self.fold + '/' + x)),
                           reverse=True)
        except NotADirectoryError:
            self.fold = '/'.join(self.fold.split('/')[:-1]) + '/'
            self.create_dialog('Выберете другую папку')
        self.finished = True

    def show_folder(self):
        """A method that shows some images from the chosen path."""
        self.clear_widgets()
        img_list = ScrollView()
        data = self.data
        if len(data) > 20:
            n = 20
        else:
            n = len(data)
        grid = MDGridLayout(cols=2, size_hint_y=(n / 4))
        for i in range(n):
            if data[i].endswith('.jpg') or data[i].endswith('.png') or data[i].endswith('.jpeg'):
                grid.add_widget(SmartTileWithLabel(source=self.fold + '/' + data[i],
                                                   text=self.fold + '/' + data[i],
                                                   on_press=self.add_image))
        img_list.add_widget(grid)
        self.add_widget(img_list)

    def add_image(self, instance):
        """A method that shows settings of an object user wants to make"""
        self.clear_widgets()
        self.img = instance.text
        toast(instance.text)
        sets = ObjectsSets(image=self.img)
        self.ids['sets'] = sets
        sets.ids.up.bind(on_press=self.change_type_up)
        sets.ids.down.bind(on_press=self.change_type_down)
        sets.ids.conf.bind(on_press=self.confirm)
        self.add_widget(sets)

    def change_type_up(self, instance):
        """A method that changes type of the object if the corresponding button is pressed."""
        types = ['архитектура', 'личность', 'марка', 'картина']
        i = types.index(self.ids.sets.ids.type.text)
        if i - 1 >= 0:
            i -= 1
            self.ids.sets.ids.type.text = types[i]

    def change_type_down(self, instance):
        """A method that changes type of the object if the corresponding button is pressed."""
        types = ['архитектура', 'личность', 'марка', 'картина']
        i = types.index(self.ids.sets.ids.type.text)
        if i + 1 < len(types):
            i += 1
            self.ids.sets.ids.type.text = types[i]

    def confirm(self, instance):
        """A method that checks if all the fields are filled in correctly."""
        name = self.ids.sets.ids.name_inp.text
        if len(name) > 35:
            name = name[:35]
        if len(name.strip()) == 0:
            self.create_dialog('Введите название')
            return
        info = self.ids.sets.ids.info_inp.text
        if len(info) > 663:
            info = info[:663]
        if len(info.strip()) == 0:
            self.create_dialog('Введите описание')
            return
        info = ' '.join(info.split('\n'))
        types = ['архитектура', 'личность', 'марка', 'картина']
        i = types.index(self.ids.sets.ids.type.text)
        types_eng = ['architecture', 'person', 'stamp', 'drawing']
        self.saving_image(name, info, types_eng[i], self.img)

    def saving_image(self, name, info, t, img):
        """A method that creates loading and starts loading image to the database."""
        thread1 = Thread(target=self.save_image(img))
        thread1.start()
        thread2 = Thread(target=self.save_object(name, info, t, img))
        thread2.start()
        self.show_loading()
        Clock.schedule_interval(self.saving_finished, 0.5)

    def saving_finished(self, dt):
        """A method that checks if the loading has been finished."""
        if self.saving_image_finished and self.saving_object_finished:
            self.saving_image_finished = False
            self.saving_object_finished = False
            MDApp.get_running_app().scr_manager.main_screen.ids.data_screen.refresh_callback()
            MDApp.get_running_app().change_screen(self.manager, self.name)
            self.on_pre_enter()
            return False

    def save_image(self, file):
        """A method that saves the user's image to the hosting file storage."""
        try:
            ftp = FTP(host, ftp_login, ftp_passwd)
            ftp.cwd(host + '/public_html/images')
            ftp.storbinary('STOR ' + file.split('/')[-1], open(file, 'rb'))
            ftp.quit()
        except gaierror:
            self.clear_widgets()
            self.create_dialog('Проверьте подключение к интернету')
        self.saving_image_finished = True

    def save_object(self, name, info, t, image):
        """A method that saves the object to the database."""
        if MDApp.get_running_app().connected:
            try:
                MDApp.get_running_app().con.ping(True)
                with MDApp.get_running_app().con.cursor() as cursor:
                    cursor.execute(f'''INSERT INTO objects (name, type, image,
                                       information, user_id)
                                       VALUES ("{name}", "{t}",
                                       "{'http://'+ host + '/images/' + image.split('/')[-1]}",
                                       "{info}", "{MDApp.get_running_app().user.user_id}")''')
                    MDApp.get_running_app().con.commit()

            except OperationalError:
                toast("Ошибка")
            except InterfaceError:
                pass
            except AttributeError:
                toast("Ошибка")
        self.saving_object_finished = True

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


class ObjectsSets(MDScreen):
    """Class of an object setting's template."""
    image = StringProperty()
    """Image that user chose."""

    def __init__(self, **kwargs):
        super(ObjectsSets, self).__init__(**kwargs)
