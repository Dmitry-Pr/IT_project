from math import ceil

from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.image import AsyncImage
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton, MDFloatingActionButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.textfield import MDTextField
from requests.exceptions import ConnectionError as ConnError
from sdamgia import SdamGIA
from sdamege import get_problem_by_id
import webbrowser
from threading import Thread

from buttons import ScrollLabel


class EGEScreen(MDScreen):
    """Class of screen with problems from ege."""
    problems = {14: 1, 15: 1}
    result = []
    item = 0
    url = ''
    correct = 0
    finished = False
    show_text_pressed = False

    def __init__(self, **kwargs):
        super(EGEScreen, self).__init__(**kwargs)

    def on_enter(self):
        """A method that works when user enters the screen."""
        self.clear_widgets()
        EGEScreen.problems = {14: 1, 15: 1}
        self.result = []
        self.item = 0
        self.correct = 0
        self.finished = False
        self.show_text_pressed = False
        self.grid = MDGridLayout(rows=4,
                                 spacing='10dp',
                                 padding=[10, 10, 10, 10])
        self.grid.add_widget(MDLabel(font_style='H5',
                                     halign='center',
                                     text="Выберите количество номеров",
                                     size_hint_y=0.2))
        self.grid.add_widget(self.create_settings_card('14'))
        self.grid.add_widget(self.create_settings_card('15'))
        box = MDBoxLayout(orientation='vertical',
                          adaptive_height=True)
        box.add_widget(MDRaisedButton(text="Готово",
                                      pos_hint={'center_x': .5},
                                      on_release=self.choose_number))
        self.grid.add_widget(box)
        self.add_widget(self.grid)

    def choose_number(self, instance):
        """A method that checks what problems
        and what number of them did the user choose.
        If users chose is correct the method starts
        loading of the problems.
        """
        if self.problems[14] + self.problems[15] == 0:
            self.create_dialog("Вы не выбрали ни один номер")
        else:
            self.clear_widgets()
            self.add_widget(MDSpinner(size_hint=[0.5, 0.5],
                                      pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                      line_width=5))
            thread = Thread(target=self.generate_test)
            thread.start()
            self.show_spinner()
            Clock.schedule_interval(self.gen_finished, 0.1)

    def gen_finished(self, dt):
        """A method that checks if the generation of problems is finished."""
        if self.finished:
            self.finished = False
            self.show_task()
            return False

    def show_spinner(self):
        """A method that shows loading on the screen."""
        self.clear_widgets()
        self.add_widget(MDSpinner(size_hint=[0.5, 0.5],
                                  pos_hint={'center_x': 0.5,
                                            'center_y': 0.5},
                                  line_width=5))

    def generate_test(self):
        """A method that generates test with problems chosen by user."""
        try:
            sdamgia = SdamGIA()
            test = sdamgia.generate_test('hist', EGEScreen.problems)
            tasks = sdamgia.get_test_by_id('hist', test)
            self.result = []
            for task in tasks:
                prob = get_problem_by_id(task)
                self.result.append(prob)
        except ConnError:
            pass
        self.finished = True

    def show_task(self):
        """A method that shows a task from the test."""
        self.clear_widgets()
        if self.result:
            box = MDBoxLayout(orientation='vertical', padding=10)
            card = MDCard(size_hint=[0.95, 0.9],
                          pos_hint={'center_y': 0.5, 'center_x': 0.5},
                          radius=[25, 25, 25, 25],
                          orientation="vertical",
                          padding=10)
            box1 = MDBoxLayout(orientation='vertical',
                               spacing=10)
            txt_box = MDBoxLayout(orientation='vertical',
                                  size_hint=[0.8, 1.5],
                                  pos_hint={'center_x': 0.5, 'center_y': 0.5})
            text = self.result[self.item]['condition']['text'].strip()
            while '\xa0' in text:
                if text.index('\xa0') != len(text) - 1:
                    text = text[:text.index('\xa0')] + '\n' + text[text.index('\xa0') + 1:]
                else:
                    text = text[:-1]
            while '\t' in text:
                if text.index('\t') != len(text) - 1:
                    text = text[:text.index('\t')] + ' ' + text[text.index('\t') + 1:]
                else:
                    text = text[:-1]
            scr_label = ScrollLabel(text=text)
            txt_box.add_widget(scr_label)
            im_scr = ScrollView(size_hint=[0.8, 1.5],
                                pos_hint={'center_x': 0.5, 'center_y': 0.5})
            im_grid = MDGridLayout(cols=ceil(len(self.result[self.item]['condition']['images']) / 2),
                                   size_hint=[1, 1],
                                   pos_hint={'center_x': 0.5, 'center_y': 0.5})
            self.ids['im_grid'] = im_grid
            self.ids['im_scr'] = im_scr
            for im in self.result[self.item]['condition']['images']:
                image = AsyncImage(source=im, allow_stretch=True)
                im_grid.add_widget(image)
            im_scr.add_widget(im_grid)
            size_box = MDBoxLayout(orientation='horizontal',
                                   spacing=40,
                                   adaptive_size=True,
                                   pos_hint={'center_x': 0.5})
            plus = MDFloatingActionButton(icon="plus",
                                          on_release=self.plus)
            size_box.add_widget(plus)

            minus = MDFloatingActionButton(icon="minus",
                                           on_release=self.minus)
            size_box.add_widget(minus)
            ans_scroll = ScrollView(pos_hint={'center_x': 0.5},
                                    effect_cls='ScrollEffect')
            ans_box = MDBoxLayout(orientation='vertical',
                                  adaptive_height=True,
                                  pos_hint={'center_x': 0.5})
            ans_field = MDTextField(size_hint_x=0.8,
                                    pos_hint={'center_x': 0.5},
                                    mode='rectangle',
                                    multiline=True)
            self.ids['ans_field'] = ans_field
            ans_box.add_widget(ans_field)
            ans_scroll.add_widget(ans_box)
            box2 = MDBoxLayout(orientation='horizontal',
                               adaptive_height=True,
                               pos_hint={'center_x': 0.5},
                               size_hint_x=0.8)
            box2.add_widget(MDRectangleFlatButton(text='Пропустить',
                                                  on_release=self.skip_question))
            box2.add_widget(Widget())
            box2.add_widget(MDRaisedButton(text='Готово',
                                           on_release=self.check_answer))
            box1.add_widget(txt_box)
            box1.add_widget(im_scr)
            box1.add_widget(size_box)
            # box1.add_widget(ans_grid)
            box1.add_widget(ans_scroll)
            box1.add_widget(box2)
            card.add_widget(box1)
            box.add_widget(card)
            self.add_widget(box)
        else:
            self.create_dialog('Подключение к сети потерянно')

    def skip_question(self, *args):
        """A method that is called if user has decided to skip a task."""
        self.show_ans(skipped=True)

    def show_ans(self, user_answer='', correct_answer='', skipped=False):
        """A method that shows answer to a task."""
        self.clear_widgets()
        box = MDBoxLayout(orientation='vertical', padding=10)
        card = MDCard(size_hint=[0.95, 0.9],
                      pos_hint={'center_y': 0.5, 'center_x': 0.5},
                      radius=[25, 25, 25, 25],
                      orientation="vertical",
                      padding=10)
        scr = ScrollView(do_scroll_x=False)
        box1 = MDBoxLayout(orientation='vertical',
                           size_hint_y=1,
                           spacing=10,
                           padding=10)
        if skipped:
            label = MDLabel(text='Вопрос пропущен',
                            halign='center',
                            font_style='H4',
                            size_hint_y=0.8)
            box1.add_widget(label)
            self.ids['page_label'] = label
        else:
            txt_box = MDBoxLayout(orientation='vertical',
                                  size_hint=[0.9, 0.8],
                                  spacing=10,)
            label = ScrollLabel(text=correct_answer)
            txt_box.add_widget(label)
            txt_box.add_widget(MDLabel(text='Ваш ответ:',
                                       font_style='H6'))
            self.ids['page_label'] = label
            ans_scroll = ScrollLabel(text=user_answer)
            txt_box.add_widget(ans_scroll)
            box1.add_widget(txt_box)
        box1.add_widget(MDLabel(text='[ref=]Смотреть на Решу ЕГЭ[/ref]',
                                theme_text_color="Custom",
                                text_color=[54 / 255, 63 / 255, 183 / 255, .9],
                                markup=True,
                                on_ref_press=self.open_url,
                                size_hint_y=0.1))
        show_text_btn = MDRectangleFlatButton(text='Смотреть задание',
                                              pos_hint={'center_x': 0.5},
                                              on_release=self.show_text,
                                              size_hint_y=0.1)
        self.ids['answer_scr'] = scr
        self.ids['answer_box'] = box1
        self.ids['show_text_btn'] = show_text_btn
        box1.add_widget(show_text_btn)

        next_button_box = MDBoxLayout(orientation='horizontal', adaptive_height=True)
        next_button_box.add_widget(MDRectangleFlatButton(text='Закончить тест',
                                                         on_release=self.show_results))
        next_button_box.add_widget(Widget())
        next_button_box.add_widget(MDRaisedButton(text='Следующий вопрос',
                                                  on_release=self.next_task))
        scr.add_widget(box1)
        card.add_widget(scr)
        card.add_widget(next_button_box)
        box.add_widget(card)
        self.add_widget(box)

    def show_text(self, *args):
        """A method that is called if user wants to see a task
        while answer to the task is being shown.
        """
        if self.show_text_pressed:
            self.show_text_pressed = False
            self.ids.show_text_btn.text = 'Смотреть задание'
            self.ids.answer_box.remove_widget(self.ids.task_text)
            self.ids.answer_box.size_hint_y = 1
            self.ids.answer_scr.scroll_to(self.ids.page_label)
        else:
            self.show_text_pressed = True
            self.ids.answer_box.size_hint_y = 1.5
            box1 = MDBoxLayout(orientation='vertical',
                               spacing=10,
                               size_hint_y=1)
            txt_box = MDBoxLayout(orientation='vertical',
                                  size_hint=[0.8, 1.5],
                                  pos_hint={'center_x': 0.5, 'center_y': 0.5})
            text = self.result[self.item]['condition']['text'].strip()
            while '\xa0' in text:
                if text.index('\xa0') != len(text) - 1:
                    text = text[:text.index('\xa0')] + '\n' + text[text.index('\xa0') + 1:]
                else:
                    text = text[:-1]
            while '\t' in text:
                if text.index('\t') != len(text) - 1:
                    text = text[:text.index('\t')] + ' ' + text[text.index('\t') + 1:]
                else:
                    text = text[:-1]
            scr_label = MDLabel(text=text)
            txt_box.add_widget(scr_label)
            im_scr = ScrollView(size_hint=[0.8, 1.5],
                                pos_hint={'center_x': 0.5, 'center_y': 0.5})
            im_grid = MDGridLayout(cols=ceil(len(self.result[self.item]['condition']['images']) / 2),
                                   size_hint=[1, 1],
                                   pos_hint={'center_x': 0.5, 'center_y': 0.5})
            for im in self.result[self.item]['condition']['images']:
                im_grid.add_widget(AsyncImage(source=im, allow_stretch=True))
            im_scr.add_widget(im_grid)
            box1.add_widget(txt_box)
            box1.add_widget(im_scr)
            self.ids['task_text'] = box1
            self.ids.answer_scr.scroll_to(im_scr)
            self.ids.answer_box.add_widget(box1)
            self.ids.show_text_btn.text = 'Скрыть задание'

    def open_url(self, *args):
        """A method that shows user current task on the sdamgia.ru website."""
        webbrowser.open(self.result[self.item]['url'])

    def minus(self, instance):
        """A method that makes a tasks picture smaller."""
        if self.ids.im_grid.size_hint[0] > 1:
            self.ids.im_grid.size_hint[0] -= 0.3
            self.ids.im_grid.size_hint[1] -= 0.3
            self.ids.im_scr.update_from_scroll()
            self.ids.im_scr.scroll_x = 0.5
            self.ids.im_scr.scroll_y = 0.5

    def plus(self, instance):
        """A method that makes a tasks picture bigger."""
        if self.ids.im_grid.size_hint[0] < 10:
            self.ids.im_grid.size_hint[0] += 0.3
            self.ids.im_grid.size_hint[1] += 0.3
            self.ids.im_scr.update_from_scroll()
            self.ids.im_scr.scroll_x = 0.5
            self.ids.im_scr.scroll_y = 0.5

    def check_answer(self, instance):
        """A method that is  called when user gives his answer to a task."""
        ans = self.result[self.item]['solution']['text']
        user_ans = self.ids.ans_field.text
        if len(user_ans.strip()):
            self.correct += 1
        self.show_ans(user_ans, ans)

    def next_task(self, instance):
        """A method that switches the screen to another task or to results of the test."""
        if self.item + 1 < len(self.result):
            self.item += 1
            self.show_task()
        else:
            self.show_results()

    def show_results(self, *args):
        """A method that shows results of the test."""
        self.clear_widgets()
        box = MDBoxLayout(orientation='vertical', padding=10)
        card = MDCard(size_hint=[0.95, 0.9],
                      pos_hint={'center_y': 0.5, 'center_x': 0.5},
                      radius=[25, 25, 25, 25],
                      orientation="vertical",
                      padding=10)
        box1 = MDBoxLayout(orientation='vertical',
                           spacing=10)
        box1.add_widget(MDLabel(text='Тест завершен',
                                halign='center',
                                font_style='H4'))
        box1.add_widget(MDLabel(text='Дано ответов: ' + str(self.correct),
                                halign='center',
                                font_style='H5'))
        box1.add_widget(MDLabel(text='Всего заданий: ' + str(len(self.result)),
                                halign='center',
                                font_style='H5'))
        btn_box = MDBoxLayout(orientation='horizontal',
                              pos_hint={'center_x': 0.5},
                              size_hint_x=0.8)
        btn_box.add_widget(MDRectangleFlatButton(text='Начать заново',
                                                 on_release=self.start_again))
        btn_box.add_widget(Widget())
        btn_box.add_widget(MDRaisedButton(text='Выйти',
                                          on_release=self.exit))
        box1.add_widget(btn_box)
        card.add_widget(box1)
        box.add_widget(card)
        self.add_widget(box)

    def exit(self, *args):
        """A method that changes current screen to the screen with objects."""
        MDApp.get_running_app().change_screen(self.manager, 'data')

    def start_again(self, *args):
        """A method restarts the training."""
        self.on_enter()

    def close_dialog(self, obj):
        self.dialog.dismiss()

    def set_attr(self, group, text):
        EGEScreen.problems[int(group)] = int(text)

    def on_checkbox_active(self, group, text, checkbox, value):
        """A method that checks what number of problems did user choose."""
        if group in ['14', '15']:
            if value:
                EGEScreen.set_attr(self, group, text)

    def add_number(self, grid, text, group, val):
        """A method that adds a checkbox to a group."""
        grid.add_widget(MDLabel(text=text,
                                halign='right'))
        check = MyCheckbox(group=group,
                           active=val,
                           text=text)
        grid.add_widget(check)
        return check

    def create_settings_card(self, number):
        """A method that creates a card with settings of the test."""
        card = MDCard()
        card.add_widget(MDLabel(font_style='H6',
                                halign='center',
                                text=(number + " номер")))
        scr = ScrollView(do_scroll_x=False,
                         do_scroll_y=True,
                         size_hint_x=1)
        grid = MDGridLayout(size_hint_y=1.4,
                            cols=2)
        self.add_number(grid, '0', number, False)
        self.add_number(grid, '1', number, True)
        self.add_number(grid, '2', number, False)
        self.add_number(grid, '3', number, False)
        self.add_number(grid, '4', number, False)
        scr.add_widget(grid)
        card.add_widget(scr)
        return card

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


class MyCheckbox(EGEScreen):
    """Class of checkbox for choosing settings of a test for ege screen."""
    text = StringProperty()
    group = StringProperty()
    active = BooleanProperty()

    def __init__(self, **kwargs):
        super(MyCheckbox, self).__init__(**kwargs)
