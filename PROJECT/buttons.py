from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivymd.uix.screen import MDScreen


class ImageBtn(ButtonBehavior, AsyncImage):
    """Class of an image with button behaviour."""
    obj_id = NumericProperty()
    """ID of an object from the database."""

    def __init__(self, **kwargs):
        super(ImageBtn, self).__init__(**kwargs)

    def on_release(self):
        pass


class DataScroll(MDScreen):
    """Class of refreshable layout for data in DataScreen."""
    refresh_callback = ObjectProperty()
    """A method that should be called after refreshing the layout."""

    def __init__(self, **kwargs):
        super(DataScroll, self).__init__(**kwargs)


class ScrollLabel(ScrollView):
    """Class of scrollable label."""
    text = StringProperty()
    """Text to show on the label."""

    def __init__(self, **kwargs):
        super(ScrollLabel, self).__init__(**kwargs)
