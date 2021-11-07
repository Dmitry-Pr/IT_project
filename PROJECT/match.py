import random
from threading import Thread

from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.image import AsyncImage
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.behaviors import TouchBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, IconLeftWidget, OneLineIconListItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.swiper import MDSwiper, MDSwiperItem
from pymysql import OperationalError, InterfaceError


class MatchScreen(MDScreen):
    """Class of screen with a matching game."""
    data = []
    finished = False
    loading = False
    item = 0
    obj_image = ''
    obj_id = 0
    obj_type = ''
    match_level = 4
    correct = 0
    match_length = 4

    def __init__(self, **kwargs):
        super(MatchScreen, self).__init__(**kwargs)

    def on_pre_enter(self):
        """A method that works when user enters the screen.
        It shows settings of the game.
        """
        self.finished = False
        if self.loading:
            self.loading = False
            return
        self.item = 0
        self.data = []
        self.clear_widgets()
        self.obj_type = ''
        self.correct = 0
        self.match_level = MDApp.get_running_app().user.settings['match_level']
        self.match_length = MDApp.get_running_app().user.settings['match_length']
        box = MDBoxLayout(orientation='vertical',
                          size_hint=[0.8, 0.7],
                          pos_hint={'center_y': 0.5, 'center_x': 0.5},
                          padding=10)
        card = MDCard(
            pos_hint={'center_y': 0.5, 'center_x': 0.5},
            radius=[25, 25, 25, 25],
            orientation="vertical",
            padding=10)
        box1 = MDBoxLayout(orientation='vertical',
                           spacing=10)
        lst = MDList()
        arc_item = OneLineIconListItem(text='Архитектура', on_press=self.choose_item)
        arc_icon = IconLeftWidget(icon='castle', on_press=self.choose_item)
        arc_item.add_widget(arc_icon)

        stamp_item = OneLineIconListItem(text='Марки', on_press=self.choose_item)
        stamp_icon = IconLeftWidget(icon='postage-stamp', on_press=self.choose_item)
        stamp_item.add_widget(stamp_icon)

        person_item = OneLineIconListItem(text='Личности', on_press=self.choose_item)
        person_icon = IconLeftWidget(icon='horse-human', on_press=self.choose_item)
        person_item.add_widget(person_icon)

        picture_item = OneLineIconListItem(text='Картины', on_press=self.choose_item)
        picture_icon = IconLeftWidget(icon='drawing', on_press=self.choose_item)
        picture_item.add_widget(picture_icon)

        lst.add_widget(arc_item)
        lst.add_widget(stamp_item)
        lst.add_widget(person_item)
        lst.add_widget(picture_item)
        box1.add_widget(lst)
        box1.add_widget(Widget())
        card.add_widget(MDLabel(text="Что хотите поучить?",
                                font_style='H4',
                                halign='center',
                                valign='top'))
        card.add_widget(Widget())
        card.add_widget(box1)
        box.add_widget(card)
        self.add_widget(box)

    def choose_item(self, instance):
        """A method that checks what settings of the game were chosen."""
        if isinstance(instance, IconLeftWidget):
            if instance.icon == 'castle':
                text = 'Архитектура'
            elif instance.icon == 'drawing':
                text = 'Картины'
            elif instance.icon == 'horse-human':
                text = 'Личности'
            elif instance.icon == 'postage-stamp':
                text = 'Марки'
        else:
            text = instance.text
        if text == 'Архитектура':
            self.obj_type = 'architecture'
        elif text == 'Картины':
            self.obj_type = 'drawing'
        elif text == 'Личности':
            self.obj_type = 'person'
        elif text == 'Марки':
            self.obj_type = 'stamp'
        self.show_next_task()

    def get_objects(self, obj_type):
        """A method that gets data for the game."""
        if MDApp.get_running_app().connected:
            try:
                MDApp.get_running_app().con.ping(True)
                with MDApp.get_running_app().con.cursor() as cursor:
                    cursor.execute(f'''SELECT * FROM objects
                                       WHERE type="{obj_type}"
                                       AND (user_id = "0" 
                                       OR user_id="{MDApp.get_running_app().user.user_id}")
                                       ORDER BY RAND()
                                       LIMIT {self.match_level}''')
                    return cursor.fetchall()

            except OperationalError:
                self.create_dialog('Подключение к сети потерянно')
                return []
            except InterfaceError:
                pass

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

    def show_next_task(self, instance=None):
        """A method that switches to the next task of the game."""
        self.item += 1
        if self.item > self.match_length:
            self.show_result()
            return
        thread = Thread(target=self.show_task())
        thread.start()
        self.show_loading()
        Clock.schedule_interval(self.loading_finished, 0.5)

    def show_loading(self):
        """A method that shows loading on the screen
         while current task is being loaded."""
        self.loading = True
        MDApp.get_running_app().change_screen(self.manager, 'loading')

    def loading_finished(self, dt):
        """A method that checks if the loading of the level finished."""
        if self.finished:
            self.finished = False
            MDApp.get_running_app().change_screen(self.manager, self.name)
            return False

    def show_task(self):
        """A method that shows a task of the game."""
        self.clear_widgets()
        self.data = self.get_objects(self.obj_type)
        if not self.data:
            self.finished = True
            return
        obj = random.choice(self.data)
        self.obj_id = obj['id']
        self.obj_image = obj['image']
        mycard = Card(obj_image=self.obj_image)
        self.add_widget(mycard)
        self.ids['mycard'] = mycard
        card = self.ids.mycard.ids.card
        swiper = MDSwiper(width_mult=2)
        for i in range(self.match_level):
            sw_item = MDSwiperItem()
            im_card = MDCard(elevation=15,
                             radius=[25, 25, 25, 25])
            lb = MyLabel(text=self.data[i]['information'],
                         halign='center', obj_id=self.data[i]['id'],
                         on_double_press=self.show_answer)
            im_card.add_widget(lb)
            sw_item.add_widget(im_card)
            swiper.add_widget(sw_item)
        card.add_widget(swiper)
        card.add_widget(Widget(size_hint_y=0.11))
        self.finished = True

    def show_answer(self, instance):
        """A method that shows if the answer is correct or not."""
        card = self.ids.mycard.ids.card
        card.clear_widgets()
        if instance.obj_id == self.obj_id:
            self.correct += 1
            res = 'Правильно'
            color = [40 / 255, 200 / 255, 40 / 255, 1]
        else:
            res = 'Неправильно'
            color = [200 / 255, 40 / 255, 40 / 255, 1]
        for i in range(len(self.data)):
            if self.data[i]['id'] == self.obj_id:
                obj = self.data[i]
        card.add_widget(MDLabel(text=res, halign='center',
                                font_style='H4', size_hint_y=0.2,
                                theme_text_color="Custom",
                                text_color=color,
                                adaptive_height=True))
        card.add_widget(AsyncImage(source=obj['image'],
                                   size_hint_y=0.6))
        card.add_widget(MDLabel(text=obj['name'], halign='center',
                                size_hint_y=0.1, font_style='H5'))
        lb = MDLabel(text=obj['information'],
                     halign='center',
                     font_style='Caption'
                     )
        card.add_widget(lb)
        btn = MDRaisedButton(text='Следующий вопрос',
                             on_press=self.show_next_task,
                             pos_hint={'center_x': 0.5})
        card.add_widget(btn)
        card.add_widget(Widget(size_hint_y=0.01))

    def show_result(self):
        """A method that shows results of the game."""
        card = self.ids.mycard.ids.card
        card.clear_widgets()
        card.add_widget(MDLabel(text='Соответсвия закончены',
                                font_style='H4',
                                halign='center'))
        grid = MDGridLayout(rows=2, padding=10, spacing=10)
        grid.add_widget(MDLabel(halign='center',
                                text='Решено правильно: ' + str(self.correct),
                                font_style='H5'))
        grid.add_widget(MDLabel(halign='center',
                                text='Всего номеров: ' + str(self.match_length),
                                font_style='H5'))
        btn_box = MDBoxLayout(orientation='horizontal',
                              pos_hint={'center_x': 0.5},
                              size_hint_x=0.8,
                              padding=10)
        btn_box.add_widget(MDRectangleFlatButton(text='Начать заново',
                                                 on_press=self.start_again))
        btn_box.add_widget(Widget())
        btn_box.add_widget(MDRaisedButton(text='Выйти',
                                          on_press=self.exit))
        card.add_widget(grid)
        card.add_widget(btn_box)

    def exit(self, instance):
        """A method that changes current screen to the screen with objects."""
        MDApp.get_running_app().change_screen(self.manager, 'data')

    def start_again(self, instance):
        """A method that restarts the training."""
        self.on_pre_enter()


class Card(MatchScreen):
    """Class of template of a guess games task."""
    obj_image = StringProperty()

    def __init__(self, **kwargs):
        super(Card, self).__init__(**kwargs)


class MyLabel(MDLabel, TouchBehavior):
    """Class of label with double press behaviour."""
    obj_id = NumericProperty()
    __events__ = (
        "on_double_press",
    )

    def __init__(self, **kwargs):
        super(MyLabel, self).__init__(**kwargs)
        self.register_event_type("on_double_press")
        self.bind(on_touch_down=self.create_clock)

    def on_double_press(self):
        pass

    def on_double_tap(self, touch, *args):
        self.dispatch('on_double_press')

    def create_clock(self, widget, touch, *args):
        """A method that checks if the label was clicked twice."""
        if touch.is_double_tap:
            if widget.collide_point(touch.x, touch.y):
                self.on_double_tap(touch, *args)
