from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

Window.clearcolor = (0, 0, .6, 1)


class Container(BoxLayout):
    def press(self, instance):
        instance.background_color = (1, 1, 1, 1)
        print('The button <%s> is being pressed' % instance.text)

    def release(self, instance):
        instance.background_color = (0, 0, 0, 0.1)
        print('The button <%s> is being pressed' % instance.text)


class MainApp(App):
    def build(self):
        self.data = ['1', '2']
        return Container()


if __name__ == '__main__':
    app = MainApp()
    app.run()
