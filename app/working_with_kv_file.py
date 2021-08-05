from functools import wraps
import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty
import numpy as np
import itertools as it

def normalize(value, _given_from=0, _given_to=255):
    offset = _given_from/_given_to
    delta = abs(_given_to - _given_from)
    return value/delta + offset

def agen(_from, _to):
    x = _from
    reverse = False
    while True:
        if x > _to:
            reverse = True

        if reverse:
            x -= 1
            yield x
        else:
            x += 1
            yield x

class MyGridLayout(Widget):
    name = ObjectProperty(None)
    surname = ObjectProperty(None)
    age = ObjectProperty(None)
    control_mode = NumericProperty(0)
    myiter = agen(0, 120)
    # color = ObjectProperty(None)
    
    def foo(self):
        name = self.name.text
        surname = self.surname.text
        age = self.age.text 

        print(f'name: {name}, surname: {surname}, age: {age}')

        self.name.text = ""
        self.surname.text = ""
        self.age.text = ""
    
    def reset_color_to_default(self):
        self.tb.background_color = 1, 0, 0, 1
        self.sl.value = 0

    def update_color(self, arg):
        # offset = self.sl.value
        # offset = next(self.myiter)
        offset = self.sl.value if self.control_mode else next(self.myiter)

        color = np.arange(0, 360, 120, dtype=np.float16)
        color = np.abs(np.sin((color+offset)/180 * np.pi))
        color = np.append(color, [1])

        self.tb.background_color = color
        print(color)
    
    def switch_color_control(self):
        self.control_mode = 0 if self.control_mode else 1


class MyApp(App):
    def build(self):
        build = MyGridLayout()
        Clock.schedule_interval(build.update_color, 1.0/30.0)
        return build

if __name__ == "__main__":
    MyApp().run()