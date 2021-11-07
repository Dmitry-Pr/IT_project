from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from pymysql import OperationalError, InterfaceError

from buttons import ImageBtn


class DataScreen(MDScreen):
    """Class of showing objects screen"""
    manager = ObjectProperty()
    data = []
    data_type = 'architecture'
    person_added = False
    stamp_added = False
    drawing_added = False
    marked_added = False
    arch_added = False
    obj_id = ''

    def __init__(self, **kwargs):
        super(DataScreen, self).__init__(**kwargs)

    def enter(self, *args):
        """A method called when the screen is entered or is going to be entered."""
        self.add_data()

    def add_data(self, marked=False):
        """A method gets data that will be shown from the database."""
        try:
            data_length = MDApp.get_running_app().user.settings['data_length']
        except AttributeError:
            return
        if MDApp.get_running_app().connected:
            try:
                MDApp.get_running_app().con.ping(True)
                with MDApp.get_running_app().con.cursor() as cursor:
                    if marked:
                        cursor.execute(f'''SELECT * FROM marked_objects
                                                   WHERE user_id="{MDApp.get_running_app().user.user_id}"''')
                        tmp = cursor.fetchall()
                        if tmp:
                            ids = ', '.join([str(tmp[i]['obj_id']) for i in range(len(tmp))])
                            cursor.execute(f'''SELECT * FROM objects
                                                       WHERE id IN ({ids})''')
                            self.data = cursor.fetchall()
                        else:
                            self.data = {}
                    else:

                        cursor.execute(f'''SELECT * FROM objects
                                                   WHERE type="{self.data_type}"
                                                   AND (user_id = "0" 
                                                   OR user_id="{MDApp.get_running_app().user.user_id}")
                                                   ORDER BY RAND() LIMIT {data_length}''')
                        self.data = cursor.fetchall()
                    # print(self.data)
            except OperationalError:
                self.data = {}
                # self.banner = True
                # self.ids.banner.show()
                self.create_dialog('Подключение к сети потерянно')
            except InterfaceError:
                self.data = {}

        self.clone()

    def clear_data_screen(self):
        """A method that deletes the whole data from the screen."""
        self.ids.bottom_nav.switch_tab('architecture')
        self.ids.bottom_nav.refresh_tabs()
        self.ids.marked_scroll.ids.inf.clear_widgets()
        self.ids.arch_scroll.ids.inf.clear_widgets()
        self.ids.person_scroll.ids.inf.clear_widgets()
        self.ids.stamp_scroll.ids.inf.clear_widgets()
        self.ids.drawing_scroll.ids.inf.clear_widgets()
        self.person_added = False
        self.stamp_added = False
        self.drawing_added = False
        self.marked_added = False

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

    def change_data(self, instance):
        """A method that checks what type of the data was chosen by user."""
        if instance.name == 'marked':
            self.data_type = 'marked'
            self.add_data(marked=True)
        elif instance.name == 'person':
            self.data_type = 'person'
            if not self.person_added:
                self.person_added = True
                self.add_data()
        elif instance.name == 'stamp':
            self.data_type = 'stamp'
            if not self.stamp_added:
                self.stamp_added = True
                self.add_data()
        elif instance.name == 'drawing':
            self.data_type = 'drawing'
            if not self.drawing_added:
                self.drawing_added = True
                self.add_data()
        elif instance.name == 'architecture':
            self.data_type = 'architecture'
            if not self.arch_added:
                self.arch_added = True
                self.add_data()

    def clone(self):
        """A method that shows objects on the screen."""
        if self.data_type == 'architecture':
            inf = self.ids.arch_scroll.ids.inf
            scr = self.ids.arch_scroll.ids.refresh_layout
        elif self.data_type == 'person':
            inf = self.ids.person_scroll.ids.inf
            scr = self.ids.person_scroll.ids.refresh_layout
        elif self.data_type == 'stamp':
            inf = self.ids.stamp_scroll.ids.inf
            scr = self.ids.stamp_scroll.ids.refresh_layout
        elif self.data_type == 'drawing':
            inf = self.ids.drawing_scroll.ids.inf
            scr = self.ids.drawing_scroll.ids.refresh_layout
        else:
            inf = self.ids.marked_scroll.ids.inf
            scr = self.ids.marked_scroll.ids.refresh_layout
        data = self.data
        if not data:
            return
        inf.clear_widgets()
        inf.size_hint_y = len(data) / 2
        inf.rows = len(data)
        for i in range(len(data)):
            color = Color(1.0, 0.0, 0.0, 0.5)
            box_layout = BoxLayout(orientation='vertical', padding=10)
            card = MDCard(size_hint=(0.9, 0.9),
                          pos_hint={'center_y': 0.5, 'center_x': 0.5},
                          padding=10,
                          radius=[25, 25, 25, 25],
                          elevation=5)
            card.canvas.before.add(color)
            im = ImageBtn(source=data[i]['image'],
                          obj_id=data[i]['id'],
                          size_hint=(0.9, 0.9),
                          pos_hint={'center_y': 0.5, 'center_x': 0.5})
            im.bind(on_release=self.get_info)
            card.add_widget(im)
            box_layout.add_widget(card)
            inf.add_widget(box_layout)
            scr.update_from_scroll()

    def refresh_callback(self, *args):
        """A method that updates data
        while the spinner remains on the screen."""

        def refresh_callback(interval):
            if self.data_type == 'architecture':
                refresh_layout = self.ids.arch_scroll.ids.refresh_layout
                inf = self.ids.arch_scroll.ids.inf
            elif self.data_type == 'person':
                refresh_layout = self.ids.person_scroll.ids.refresh_layout
                inf = self.ids.person_scroll.ids.inf
            elif self.data_type == 'stamp':
                refresh_layout = self.ids.stamp_scroll.ids.refresh_layout
                inf = self.ids.stamp_scroll.ids.inf
            elif self.data_type == 'drawing':
                refresh_layout = self.ids.drawing_scroll.ids.refresh_layout
                inf = self.ids.drawing_scroll.ids.inf
            elif self.data_type == 'marked':
                refresh_layout = self.ids.marked_scroll.ids.refresh_layout
                inf = self.ids.marked_scroll.ids.inf
            inf.clear_widgets()
            self.add_data(marked=(self.data_type == 'marked'))
            refresh_layout.update_from_scroll()
            refresh_layout.refresh_done()
            self.tick = 0

        Clock.schedule_once(refresh_callback, 1)

    def get_info(self, instance):
        """A method changes the current screen
        to screen with information about the chosen object."""
        MDApp.get_running_app().obj_id = instance.obj_id
        manager = MDApp.get_running_app().scr_manager.main_screen.ids.sm
        MDApp.get_running_app().change_screen(manager, 'info')
