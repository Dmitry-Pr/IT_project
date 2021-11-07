from kivy.event import EventDispatcher
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.screenmanager import RiseInTransition, CardTransition
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRectangleFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget
from kivymd.uix.screen import MDScreen
from pymysql import OperationalError, InterfaceError


class LearningScreen(MDScreen):
    objects = []
    item = 0

    def __init__(self, **kwargs):
        super(LearningScreen, self).__init__(**kwargs)

    def on_pre_enter(self):
        """A method that works when user enters the screen.
        It shows settings of a training.
        """
        self.clear_widgets()
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

        marked_item = OneLineIconListItem(text='Помеченные', on_press=self.choose_item)
        marked_icon = IconLeftWidget(icon='star', on_press=self.choose_item)
        marked_item.add_widget(marked_icon)

        lst.add_widget(arc_item)
        lst.add_widget(stamp_item)
        lst.add_widget(person_item)
        lst.add_widget(picture_item)
        lst.add_widget(marked_item)
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
        """A method that checks what settings of the training did user choose."""
        if isinstance(instance, IconLeftWidget):
            if instance.icon == 'castle':
                text = 'Архитектура'
            elif instance.icon == 'drawing':
                text = 'Картины'
            elif instance.icon == 'horse-human':
                text = 'Личности'
            elif instance.icon == 'postage-stamp':
                text = 'Марки'
            elif instance.icon == 'star':
                text = 'Помеченные'
        else:
            text = instance.text
        if text == 'Архитектура':
            self.start_training('architecture')
        elif text == 'Картины':
            self.start_training('drawing')
        elif text == 'Личности':
            self.start_training('person')
        elif text == 'Марки':
            self.start_training('stamp')
        elif text == 'Помеченные':
            self.start_training('marked')

    def get_objects(self, obj_type):
        """A method that gets objects for the training from the database."""
        if MDApp.get_running_app().connected:
            try:
                MDApp.get_running_app().con.ping(True)
                with MDApp.get_running_app().con.cursor() as cursor:
                    level = MDApp.get_running_app().user.settings['learning_level']
                    if obj_type == 'marked':
                        cursor.execute(f'''SELECT * FROM marked_objects
                                           WHERE user_id="{MDApp.get_running_app().user.user_id}"''')
                        tmp = cursor.fetchall()
                        if tmp:
                            ids = ', '.join([str(tmp[i]['obj_id']) for i in range(len(tmp))])
                            cursor.execute(f'''SELECT * FROM objects
                                               WHERE id IN ({ids})
                                               ORDER BY RAND()
                                               LIMIT {level}''')
                    else:
                        cursor.execute(f'''SELECT * FROM objects
                                           WHERE type="{obj_type}" 
                                           AND (user_id = "0" 
                                           OR user_id="{MDApp.get_running_app().user.user_id}")
                                           ORDER BY RAND() LIMIT {level}''')
                    self.objects = cursor.fetchall()
                    self.item = 0
            except OperationalError:
                self.create_dialog("Подключение к сети потерянно")
            except InterfaceError:
                pass

    def start_training(self, obj_type):
        """A method that shows first object of the training."""
        self.clear_widgets()
        box = MDBoxLayout(orientation='vertical', padding=10)
        self.get_objects(obj_type)
        if self.objects:
            self.swiper = MySwiper(on_swipe_left=self.swipe_left,
                                   on_swipe_right=self.swipe_right,
                                   transition=RiseInTransition(duration=0.2))
            if obj_type == 'stamp':
                obj_name = ''
            else:
                obj_name = self.objects[self.item]['name']
            obj_pict = self.objects[self.item]['image']
            obj_info = self.objects[self.item]['information']
            self.swiper.ids.scr1.add_widget(InfoCard(obj_name=obj_name,
                                                     obj_pict=obj_pict,
                                                     obj_info=obj_info))
            box.add_widget(self.swiper)
            self.add_widget(box)

    def swipe_right(self, instance):
        """A method that works when user wants
        to go to the next object without saving it.
        """
        self.swiper.ids.screen_manager.transition = CardTransition(duration=0.3, mode='push')
        if self.item + 1 < len(self.objects):
            self.item += 1
            self.update_screen()
        else:
            self.show_final_screen()

    def swipe_left(self, instance):
        """A method that works when user wants
        to save the object in marked objects.
        """
        self.swiper.ids.screen_manager.transition = CardTransition(duration=0.3, mode='pop', direction='right')
        if MDApp.get_running_app().connected:
            try:
                MDApp.get_running_app().con.ping(True)
                with MDApp.get_running_app().con.cursor() as cursor:
                    cursor.execute(f'''SELECT * FROM marked_objects
                                       WHERE user_id="{MDApp.get_running_app().user.user_id}"
                                       AND obj_id="{self.objects[self.item]['id']}"''')
                    added = cursor.fetchall()
                    if not added:
                        cursor.execute(f'''INSERT INTO marked_objects (user_id, obj_id)
                                           VALUES ("{MDApp.get_running_app().user.user_id}",
                                           "{self.objects[self.item]['id']}")''')
                        MDApp.get_running_app().con.commit()
            except OperationalError:
                self.create_dialog('Подключение к сети потерянно')
            except InterfaceError:
                pass
        if self.item + 1 < len(self.objects):
            self.item += 1
            self.update_screen()
        else:
            self.show_final_screen()

    def update_screen(self):
        """A method that shows the next object on the screen."""
        if self.objects[self.item]['type'] == 'stamp':
            obj_name = ''
        else:
            obj_name = self.objects[self.item]['name']
        obj_pict = self.objects[self.item]['image']
        obj_info = self.objects[self.item]['information']
        if self.swiper.ids.screen_manager.current == 'scr1':
            self.swiper.ids.scr2.clear_widgets()
            self.swiper.ids.scr2.add_widget(InfoCard(obj_name=obj_name,
                                                     obj_pict=obj_pict,
                                                     obj_info=obj_info))
            self.swiper.ids.screen_manager.current = 'scr2'
        else:
            self.swiper.ids.scr1.clear_widgets()
            self.swiper.ids.scr1.add_widget(InfoCard(obj_name=obj_name,
                                                     obj_pict=obj_pict,
                                                     obj_info=obj_info))
            self.swiper.ids.screen_manager.current = 'scr1'

    def show_final_screen(self):
        """A method that shows the final screen of the training."""
        self.clear_widgets()
        box = MDBoxLayout(orientation='vertical', padding=10)
        card = MDCard(size_hint=[0.95, 0.9],
                      pos_hint={'center_y': 0.5, 'center_x': 0.5},
                      radius=[25, 25, 25, 25],
                      orientation="vertical",
                      padding=10)
        box1 = MDBoxLayout(orientation='vertical',
                           spacing=10)
        box1.add_widget(MDLabel(text='Тренировка закончена',
                                font_style='H4',
                                halign='center'))
        btn_box = MDBoxLayout(orientation='horizontal',
                              pos_hint={'center_x': 0.5},
                              size_hint_x=0.8)
        btn_box.add_widget(MDRectangleFlatButton(text='Начать заново',
                                                 on_press=self.start_again))
        btn_box.add_widget(Widget())
        btn_box.add_widget(MDRaisedButton(text='Выйти',
                                          on_press=self.exit))
        box1.add_widget(btn_box)
        card.add_widget(box1)
        box.add_widget(card)
        self.add_widget(box)

    def start_again(self, instance):
        """A method that restarts the training."""
        self.on_pre_enter()

    def exit(self, instance):
        """A method that changes current screen to screen with objects."""
        MDApp.get_running_app().change_screen(self.manager, 'data')

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


class InfoCard(LearningScreen):
    """Class of template of card with objects information."""
    obj_pict = StringProperty()
    obj_name = StringProperty()
    obj_info = StringProperty()

    def __init__(self, **kwargs):
        super(InfoCard, self).__init__(**kwargs)


class MySwiper(LearningScreen, EventDispatcher):
    """Class that makes swiping objects possible."""
    transition = ObjectProperty()

    __events__ = (
        "on_swipe_left",
        "on_swipe_right",
    )

    def __init__(self, **kwargs):
        super(MySwiper, self).__init__(**kwargs)
        self.x0 = None
        self.x1 = 0
        self.y0 = 0
        self.y1 = 0
        self.register_event_type("on_swipe_left")
        self.register_event_type("on_swipe_right")

    def on_swipe_left(self):
        pass

    def on_swipe_right(self):
        pass

    def on_touch_down(self, touch):
        if not self.collide_point(touch.pos[0], touch.pos[1]):
            return
        self.x0 = touch.pos[0]
        self.y0 = touch.pos[1]

    def on_touch_up(self, touch):
        if not self.x0:
            return
        self.x1 = touch.pos[0]
        self.y1 = touch.pos[1]
        if abs(self.x1 - self.x0) < 70:
            return
        if self.x0 < self.x1:
            self.dispatch('on_swipe_left')
        else:
            self.dispatch('on_swipe_right')
        self.x0 = None
        return
