import kivy
from kivy import event
from kivy.app import App
from kivy.lang.builder import Instruction
from kivy.logger import ColoredFormatter
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.stencilview import StencilView
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty,\
                            ListProperty, StringProperty
from kivy.graphics import Color, Rectangle
from app.theme import Theme


# or TabbedPanel
class MyView(TabbedPanel):
    def __init__(self, **kwargs):
        super(MyView, self).__init__(**kwargs)


class TestApp(App):

    def build(self):
        _app = MyView()
        print(_app.ids.aI.container.size)
        print(_app.ids.aI.content_size)
        return _app


if __name__ == "__main__":
    TestApp().run()