import json
import os

class Theme():
    THEMES = ['light', 'dark']

    def __init__(self, _type='dark'):
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
        with open('app/theme.json', 'r') as f:
            read_themes = json.load(f)

        self.info_color = read_themes['information_color']
        self.deep_bckg_color = read_themes['deep_background_color']
        self.bckg_color = read_themes['background_color']
        self._btn_normal_color = read_themes['button_normal_color']
        self._btn_down_color = read_themes['button_down_color']
        self.info_font_color = read_themes['information_font_color']

    def _replace_values(self, kv_prop, color_val):
        '''Keep in mind that for loop bases on references.
        using the "=" operator involves creation (copying constructor)
        of new object which impiles creation of new object'''
        for i in range(len(color_val)):
            kv_prop[i] = color_val[i]

    def change_theme(self, _type):
        '''Switches between light/dark theme'''
        self.theme_type =\
            _type if _type in self.THEMES else self.theme_type

    def get_info_color(self):
        '''Get information unit color'''
        return self.info_color[self.theme_type]

    def get_info_font_color(self):
        return self.info_font_color[self.theme_type]
    
    def get_deep_bckg_color(self):
        '''Get deep background color'''
        return self.deep_bckg_color[self.theme_type]

    def get_bckg_color(self):
        '''Get background color'''
        return self.bckg_color[self.theme_type]
    
    def get_btn_color(self, state):
        if state == 'normal':
            return self._btn_normal_color[self.theme_type]

        elif state == 'down':
            return self._btn_down_color[self.theme_type]
    
    def update_theme(self, app):
        pass
    #     '''Replaces values of the main app instance properties wihich are
    #     used in kv file witch those defined in Theme class'''

    #     # self._replace_values(app.info_col, self.get_info_color())
    #     # self._replace_values(app.deep_bckg_col, self.get_deep_bckg_color())
    #     self._replace_values(app.color_normal, self.get_btn_color('normal'))
    #     self._replace_values(app.color_down, self.get_btn_color('down'))