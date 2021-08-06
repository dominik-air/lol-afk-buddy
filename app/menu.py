from functools import wraps
from typing import overload
import kivy
from kivy.app import App
from kivy.logger import ColoredFormatter
from kivy.properties import (
    ObjectProperty,
    NumericProperty,
    ListProperty,
    StringProperty,
)
from kivy.clock import Clock
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.factory import Factory
from kivy.graphics import Color
from kivy.graphics import Canvas
from kivy.utils import rgba
from packages.theme import Theme, KivyTheme
from packages.utils import LOLClientStatusInformer
import weakref
from collections import defaultdict

from champion_select import ChampionSelectUI, ChampionSelect, ChampionSelectInterface

# class InformationUnit(BoxLayout):
#     pro = ObjectProperty(None)

# class InformationUnit(BoxLayout):
#     # pro = ObjectProperty(None)

#     def __init__(self, **kwargs):
#             super(InformationUnit, self).__init__(**kwargs)
#             print("constructing InformationUnit")
#             print(self.ids.pro_o.text)
#             # self.pro.text = "hello"


class AppLayout(TabbedPanel):
    # appLogger = ObjectProperty(None)
    prop = ObjectProperty(None)
    # alist = ListProperty([])

    def __init__(self, **kwargs):
        super(AppLayout, self).__init__(**kwargs)


# sproboj to zrobic tak jak tu:
# https://stackoverflow.com/questions/53015154/kivy-custom-button-on-press-change-canvas-colour
# class CustomButton(ButtonBehavior, Label):
#     def __init__(self, **kwargs):
#         super(CustomButton, self).__init__(**kwargs)

#         self.text = "text"
#         with self.canvas.before:
#             self.shape_colour = Color(rgba=(.5, .5, .5, .5))

#         def on_press(self, *args):
#             self.background_color = 1, 0, 0, 1

#         def on_release(self, *args):
#             self.background_color = .5, .5, .5, .5

# class InformationUnitWrapper(BoxLayout):
#     _s = 10
#     _spacing = NumericProperty(None)
#     _height = NumericProperty(None)
#     _counter = 0
#     def __init__(self, **kwargs):
#         super(InformationUnitWrapper, self).__init__(**kwargs)
#         self._spacing = self._s
#         # Clock.schedule_once(self.init_height)
#         self._height = (InformationUnit._h + self._s)
#         # print(f'counter: {InformationUnitWrapper._counter}')
#         # self._height = InformationUnitWrapper._counter * (InformationUnit._height + self._spacing)
#         # InformationUnitWrapper._spacing = self._spacing

#         # Clock.schedule_once(lambda dt: print(f'{InformationUnit._height}, {dt}'), 1)

#     # def init_height(self, dt):
#     #     self._height = 3 * (InformationUnit._height + self._spacing)

#     @classmethod
#     def increase_counter(cls):
#         cls._counter += 1


# class InformationUnit(BoxLayout):
#     _h = 50
#     _height = NumericProperty(None)
#     # _weakref = None
#     def __init__(self, **kwargs):
#         super(InformationUnit, self).__init__(**kwargs)
#         self._height = self._h
#         InformationUnitWrapper.increase_counter()
#         # self._weakref = weakref.ref(self)
#         # InformationUnit._height = self._height

#         # nalezy wypisac z opoznieniem bo
#         Clock.schedule_once(lambda a: print(f'{self.height}, {a}'))


class InfoGridLayout(GridLayout):
    _spacing = NumericProperty(4)
    _width_ratio = NumericProperty(0.7)

    def __init__(self, **kwargs):
        super(InfoGridLayout, self).__init__(**kwargs)


class MyButton(ButtonBehavior, Label):
    # Old code:
    # __refs__ = defaultdict(list)
    # _inst_name = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bind(state=self.click_effect)

        # Old code:
        # self.__refs__[self.__class__].append(weakref.ref(self))
        self._app = kivy.app.App.get_running_app()
        MyButton._inst_name = self.__class__

    # @classmethod
    # def get_intances_weakrefs(cls):
    #     '''return list of weakref to all instances which type is
    #     the same as given object'''
    #     return cls.__refs__[cls]

    # @classmethod
    # def get_intance_weakref(cls):
    #     '''return weakref to first instance which type is
    #     the same as given object'''
    #     return cls.__refs__[cls][0]

    def click_effect(self, obj, value):
        if value == "normal":
            self.canvas.before.children[0].rgba = self._app.btn_normal_color

        if value == "down":
            self.canvas.before.children[0].rgba = self._app.btn_down_color


class MenuApp(App, KivyTheme, Theme):
    # theme = Theme()
    lol_client = LOLClientStatusInformer()
    is_lol_client_running = NumericProperty(0)

    # Static elements
    # info_col = ListProperty(theme.get_info_color())
    # deep_bckg_col = ListProperty(theme.get_deep_bckg_color())
    # bckg_col = ListProperty(theme.get_bckg_color())
    # info_font_col = ListProperty(theme.get_info_font_color())

    # Buttons
    # _btn_color = ListProperty(theme.get_btn_color("normal"))
    # btn_normal_color = ListProperty(theme.get_btn_color("normal"))
    # btn_down_color = ListProperty(theme.get_btn_color("down"))

    # Fonts
    _font_size = NumericProperty(16)

    # Other
    info_wp_offset = NumericProperty(300)  # information wrapper left padding

    # DEFINITIONS OF METHODS
    def __init__(self, **kwargs):
        super(MenuApp, self).__init__(**kwargs)


    def update_lol_client_status_property(self, dt):
        self.lol_client.is_running()
        self.is_lol_client_running = self.lol_client._is_running

    # Button's on_press methods definitions:
    def switch_dark(self, b):
        self.change_theme("dark")
        self.update_theme(self)

    def switch_light(self, b):
        self.change_theme("light")
        self.update_theme(self)

    def show_values(self, **kwargs):
        # accessing MyButton instances
        for i in MyButton.get_intances_weakrefs():
            print(i().text)

    def load_new_theme_config(self):
        self._load_theme_from_file()
        self.update_theme(self)

    def add(self):
        self._font_size += 2

    def sub(self):
        self._font_size -= 2

    def changing_something(self):
        pass

    def build(self):
        app = AppLayout()
        Clock.schedule_interval(self.update_lol_client_status_property, 1)
        return app


if __name__ == "__main__":
    MenuApp().run()
