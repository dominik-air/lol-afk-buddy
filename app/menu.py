# kivy packages:
import kivy
from kivy.app import App
from kivy.logger import ColoredFormatter
from kivy.properties import (
    ObjectProperty,
    NumericProperty,
    ListProperty,
    StringProperty,
)
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.spinner import SpinnerOption
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color
from kivy.graphics import Canvas
from kivy.utils import rgba

# non-kivy packages:
from collections import defaultdict
from functools import wraps
from typing import overload

# my packages:
from packages.theme import Theme, KivyTheme
from packages.utils import LOLClientStatusInformer
from champion_select import (
    ChampionSelectUI, ChampionSelect, ChampionSelectInterface)


class AppLayout(TabbedPanel):
    '''Main container in the kivy file.'''

    def __init__(self, **kwargs):
        super(AppLayout, self).__init__(**kwargs)

    def spinner_clicked(self, value):
        opt = self.ids.spinner_id.text
        print(f'The option "{opt}" have been selected.')


class InfoGridLayout(GridLayout):
    '''This grid layout contains information bar objects in the
    'pre-game' and 'in-game' sections.'''

    _spacing = NumericProperty(4)
    _width_ratio = NumericProperty(0.7)

    def __init__(self, **kwargs):
        super(InfoGridLayout, self).__init__(**kwargs)

class SubInfoGridLayout(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    

# TODO: Try different approach here and in the MyButton class:
# move click_effect to the MenuApp class (receive obj and value args)
# move self.bind to click_effect methdos after that as obj.bind
# if it won't work you can always try to keep 72 line (self._app = ki...)
# and access the method in this way
class SettingsSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._app = kivy.app.App.get_running_app()
        self.bind(state=self._app.click_effect)

    # def click_effect(self, obj, value):
    #     '''Involves change in color on darker while the mouse button is clicked
    #     and restores the previous color when the mouse button is released.'''

    #     if value == "normal":
    #         self.canvas.before.children[0].rgba = self._app.btn_normal_color

    #     if value == "down":
    #         self.canvas.before.children[0].rgba = self._app.btn_down_color


class MyButton(ButtonBehavior, Label):
    '''Class created to represent my own button appearance and behaviour.'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._app = kivy.app.App.get_running_app()
        self.bind(state=self._app.click_effect)


class DropDown(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_select=lambda inst, x: self.setatter(inst, 'text', x))
        self.bind(on_release=self.open)

class MenuApp(App, KivyTheme):
    '''App class.'''

    # LOL client properties
    lol_client = LOLClientStatusInformer()
    is_lol_client_running = NumericProperty(0)

    # Font settings
    _font_size = NumericProperty(16)

    # Appearance settings
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

    def load_new_theme_config(self):
        '''After modyfing the 'theme.json' this method is required to run
        in order to apply changes in the program at run-time.'''
        self._load_theme_from_file()
        self.update_theme(self)

    # add and sub methods increase/decrease the font size.
    # TODO: Change their name in the future
    def add(self):
        self._font_size += 2

    def sub(self):
        self._font_size -= 2

    def changing_something(self):
        '''This methods does nothing. Use it carefully.'''
        pass

    def build(self):
        app = AppLayout()
        Clock.schedule_interval(self.update_lol_client_status_property, 2)
        return app


if __name__ == "__main__":
    MenuApp().run()
