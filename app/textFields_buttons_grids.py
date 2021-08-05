from functools import wraps
import kivy
from kivy.app import App
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


class MyGridLayout(GridLayout):
    def __init__(self, **kwargs):
        super(MyGridLayout, self).__init__(**kwargs)

        self.cols = 3 

        # Label
        self.add_widget(Label(text="Name: "))

        # Text field
        self.name = TextInput(multiline=True)
        self.add_widget(self.name)

        # Button
        self.button1 = Button(text="a butt")
        self.button1.bind(on_press=self.foo)
        self.add_widget(self.button1)
    
    def foo(self, e):
        self.name.text = "" # wipe provided text
        _text = f"I got pressed: {e}"
        print(_text)
        self.add_widget(Label(text=_text, text_size=(200, 200)))


class SomeApp(App):
    def build(self):
        return MyGridLayout()


if __name__ == "__main__":
    SomeApp().run()