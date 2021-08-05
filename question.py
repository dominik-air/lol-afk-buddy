import kivy
from kivy import event
from kivy.app import App
from kivy.lang.builder import Instruction
from kivy.logger import ColoredFormatter
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty,\
                            ListProperty, StringProperty
from kivy.graphics import Color, Rectangle
from app.theme import Theme


class MyView(Widget):
    def __init__(self, **kwargs):
        super(MyView, self).__init__(**kwargs)

class CustomButton(ButtonBehavior, Label):
    own_text = StringProperty(None)

    def color_picker(self, object, value):
        print(f'{object} changed state on {value}.')
        # return [.9, .9, .9, 1] if self.state == 'normal' else [.3, .3, .3, 1]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.canvas.before.add(Color(rgba=(1, 1, .9, 1)))

        # add own text
        self.own_text = 'this is my own text'
        self.text = self.own_text

        # add colour from python code instead of kv file
        with self.canvas.before:
            # by doing so we can store the object and access it later
            self.c = Color(1, 0, 0, .5, mode='rgba')
            # Rectangle(pos=self.pos, size=self.size)

            # Can we pass a function?
            # self.c = Color(self.color_picker, mode='rgba')

        # accessing the object manually
        self.col_obj = self.canvas.before.children[0]
        if type(Color()) == type(self.col_obj):
            print(self.col_obj.rgba)
        
        # check if self.c is the same object as col_obj
        res = self.c is self.col_obj
        print(f'Is self.c the same object as col_obj?: {res}')

        self.bind(state=self.color_picker)
        
    
    def on_press(self):
        self.col_obj.rgba = [1, 0, 1, 1]
        print(self.col_obj.rgba)

class QuestionApp(App):
    theme =  Theme()
    color_normal = ListProperty(theme.get_btn_color('normal'))
    color_down = ListProperty(theme.get_btn_color('down'))
    

    btn_colour = ListProperty(theme.get_btn_color('normal'))

    def build(self):
        _app = MyView()
        return _app

    # def do_sth(self, btn):
    #     print('lsfk')
    
    def activate_dark_theme(self):
        print(self)
        self.theme.change_theme('dark')
        self.theme.update_theme(self)
    
    def activate_light_theme(self):
        self.theme.change_theme('light')
        self.theme.update_theme(self)

if __name__ == "__main__":
    QuestionApp().run()