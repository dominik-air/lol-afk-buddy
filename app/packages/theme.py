import json
from ntpath import join
from typing import List
from kivy.uix.widget import Widget
import os
from kivy.properties import (
    ObjectProperty,
    NumericProperty,
    ListProperty,
    StringProperty,
)


class Theme:
    THEMES = ["light", "dark"]

    def __init__(self, _type="dark"):
        self.theme_type = _type

        print(os.listdir())
        print(os.getcwd())

        self._load_theme_from_file()

        # Old code:
        # self.info_color = {'light': [1, 1, 1, .5],
        #                   'dark': [.1, .1, .1, .5]}
        # self.deep_bckg_color = {'light': [.9, .9, .9, 1],
        #                         'dark': [.1, .1, .1, 1]}
        # self.bckg_color = {'light': [.8, .8, .8, 1],
        #                    'dark': [.4, .4, .4, 1]}
        # self._btn_normal_color = {'light': [.8, .8, .8, 1],
        #                         'dark': [.3, .3, .3, 1]}
        # self._btn_down_color = {'light': [.7, .7, .7, 1],
        #                         'dark': [.2, .2, .2, 1]}

    def _load_theme_from_file(self):
        theme_dir = os.path.join(os.path.abspath('..'), 'config')
        # theme_dir = "../config"  # works for me

        with open(os.path.join(theme_dir, 'theme.json'), "r") as f:
            read_themes = json.load(f)

        self.info_color = read_themes["information_color"]
        self.deep_bckg_color = read_themes["deep_background_color"]
        self.bckg_color = read_themes["background_color"]
        self._btn_normal_color = read_themes["button_normal_color"]
        self._btn_down_color = read_themes["button_down_color"]
        self.info_font_color = read_themes["information_font_color"]

    def _replace_values(self, kv_prop, color_val):
        """Keep in mind that for loop bases on references.
        using the "=" operator involves creation (copying constructor)
        of new object which impiles creation of new object"""
        for i in range(len(color_val)):
            kv_prop[i] = color_val[i]

    def change_theme(self, _type):
        """Switches between light/dark theme"""
        self.theme_type = _type if _type in self.THEMES else self.theme_type

    def update_theme(self, app):
        '''Abstract method, should be overrided after inheriting this class'''
        pass

    # Getters
    def get_info_color(self):
        """Get information unit color"""
        return self.info_color[self.theme_type]

    def get_info_font_color(self):
        return self.info_font_color[self.theme_type]

    def get_deep_bckg_color(self):
        """Get deep background color"""
        return self.deep_bckg_color[self.theme_type]

    def get_bckg_color(self):
        """Get background color"""
        return self.bckg_color[self.theme_type]

    def get_btn_color(self, state):
        if state == "normal":
            return self._btn_normal_color[self.theme_type]

        elif state == "down":
            return self._btn_down_color[self.theme_type]


    #     '''Replaces values of the main app instance properties wihich are
    #     used in kv file witch those defined in Theme class'''

    #     # self._replace_values(app.info_col, self.get_info_color())
    #     # self._replace_values(app.deep_bckg_col, self.get_deep_bckg_color())
    #     self._replace_values(app.color_normal, self.get_btn_color('normal'))
    #     self._replace_values(app.color_down, self.get_btn_color('down'))

class KivyTheme(Widget, Theme):
    info_col = ListProperty(None)
    deep_bckg_col = ListProperty(None)
    bckg_col = ListProperty(None)
    info_font_col = ListProperty(None)

    _btn_color = ListProperty(None)
    btn_normal_color = ListProperty(None)
    btn_down_color = ListProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Static elements
        self.info_col = self.get_info_color()
        self.deep_bckg_col = self.get_deep_bckg_color()
        self.bckg_col = self.get_bckg_color()
        self.info_font_col = self.get_info_font_color()

        self._btn_color = self.get_btn_color("normal")
        self.btn_normal_color = self.get_btn_color("normal")
        self.btn_down_color = self.get_btn_color("down")

    def update_theme(self, app):
        """This is overrided method of custom Theme class. Describes how
        how the theme should be updated, based on application's specific
        variables and methods. Try to stick to single responsibility
        principle while editing this method, it should edit only the
        app instance's fields."""

        # Change properties for info and deep background color
        self._replace_values(app.info_col, self.get_info_color())
        self._replace_values(app.deep_bckg_col, self.get_deep_bckg_color())
        self._replace_values(app.bckg_col, self.get_bckg_color())

        # Change properties for button (pressed and released) color
        self._replace_values(app.btn_normal_color, self.get_btn_color("normal"))
        self._replace_values(app.btn_down_color, self.get_btn_color("down"))

        # Change font color
        self._replace_values(app.info_font_col, self.get_info_font_color())

        app._btn_color = app.btn_normal_color

        # future edits:
        pass

    # Test method
    def click_effect(self, obj, value):
        '''Involves change in color on darker while the mouse button is clicked
        and restores the previous color when the mouse button is released.'''

        if value == "normal":
            obj.canvas.before.children[0].rgba = self.get_btn_color(value)

        if value == "down":
            obj.canvas.before.children[0].rgba = self.get_btn_color(value)