import random

from kivy.properties import StringProperty
from kivy.uix.image import AsyncImage
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, IconLeftWidget, OneLineIconListItem
from kivymd.uix.screen import MDScreen
from pymysql import OperationalError, InterfaceError

from buttons import ImageBtn


class GuessScreen(MDScreen):
    """Class of screen with a guessing game."""
    data = []
    item = 0
    obj_name = ''
    obj_id = 0
    obj_type = ''
    guess_level = 4
    correct = 0
    guess_length = 4

    def __init__(self, **kwargs):
        super(GuessScreen, self).__init__(**kwargs)

    def on_pre_enter(self):
        """A method that works when user enters the screen.
        It shows settings of the game.
        """
        self.item = 0
        self.data = []
        self.clear_widgets()
        self.obj_type = ''
        self.correct = 0
        self.guess_level = MDApp.get_running_app().user.settings['guess_level']
        self.guess_length = MDApp.get_running_app().user.settings['guess_length']
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
            self.show_task('architecture')
        elif text == 'Картины':
            self.obj_type = 'drawing'
            self.show_task('drawing')
        elif text == 'Личности':
            self.obj_type = 'person'
            self.show_task('person')
        elif text == 'Марки':
            self.obj_type = 'stamp'
            self.show_task('stamp')

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
                                       LIMIT {self.guess_level}''')
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

    def show_task(self, instance):
        """A method that shows a task of the game."""
        self.item += 1
        if self.item > self.guess_length:
            self.show_result()
            return
        self.clear_widgets()
        self.data = self.get_objects(self.obj_type)
        if not self.data:
            return
        obj = random.choice(self.data)
        self.obj_id = obj['id']
        self.obj_name = obj['name']
        mycard = MyCard(obj_name=self.obj_name)
        self.add_widget(mycard)
        self.ids['mycard'] = mycard
        card = self.ids.mycard.ids.card
        grid = MDGridLayout(cols=2, spacing=10, padding=10)
        for j in range(self.guess_level):
            im = ImageBtn(source=self.data[j]['image'],
                          obj_id=self.data[j]['id'])
            im.bind(on_release=self.show_answer)
            im_card = MDCard(radius=[25, 25, 25, 25],
                             orientation="vertical",
                             padding=10)
            im_card.add_widget(im)
            grid.add_widget(im_card)
        card.add_widget(grid)
        card.add_widget(Widget(size_hint_y=0.11))

    def show_answer(self, instance):
        """A method that shows if the answer is correct or not."""
        card = self.ids.mycard.ids.card
        card.clear_widgets()
        obj_names = {elem['id']: elem['name'] for elem in self.data}
        if instance.obj_id == self.obj_id:
            self.correct += 1
            res = 'Правильно'
            color = [40 / 255, 200 / 255, 40 / 255, 1]
        else:
            res = 'Неправильно'
            color = [200 / 255, 40 / 255, 40 / 255, 1]
        card.add_widget(MDLabel(text=res, halign='center',
                                font_style='H4', size_hint_y=0.2,
                                theme_text_color="Custom",
                                text_color=color))
        grid = MDGridLayout(cols=2, spacing=10, padding=10)
        for j in range(self.guess_level):
            im_card = MDCard(radius=[25, 25, 25, 25],
                             orientation="vertical",
                             padding=10)
            im = AsyncImage(source=self.data[j]['image'])
            if self.obj_id == self.data[j]['id']:
                color = [40 / 255, 200 / 255, 40 / 255, 1]
            elif self.data[j]['id'] == instance.obj_id and res == 'Неправильно':
                color = [200 / 255, 40 / 255, 40 / 255, 1]
            else:
                if MDApp.get_running_app().user.settings['theme'] == 'dark':
                    color = [1, 1, 1, 1]
                else:
                    color = None
            label = MDLabel(text=obj_names[self.data[j]['id']],
                            adaptive_height=True,
                            halign='center',
                            theme_text_color="Custom",
                            text_color=color)
            im_card.add_widget(im)
            im_card.add_widget(label)
            grid.add_widget(im_card)

        btn = MDRaisedButton(text='Следующий вопрос',
                             on_release=self.show_task,
                             pos_hint={'center_x': 0.5})
        card.add_widget(grid)
        card.add_widget(btn)
        card.add_widget(Widget(size_hint_y=0.01))

    def show_result(self):
        """A method that shows results of the game."""
        card = self.ids.mycard.ids.card
        card.clear_widgets()
        card.add_widget(MDLabel(text='Угадайка закончена',
                                font_style='H4',
                                halign='center'))
        grid = MDGridLayout(rows=2, padding=10, spacing=10)
        grid.add_widget(MDLabel(halign='center',
                                text='Решено правильно: ' + str(self.correct),
                                font_style='H5'))
        grid.add_widget(MDLabel(halign='center',
                                text='Всего номеров: ' + str(self.guess_length),
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


class MyCard(GuessScreen):
    """Class of a template of a guess game's task."""
    obj_name = StringProperty()

    def __init__(self, **kwargs):
        super(MyCard, self).__init__(**kwargs)
