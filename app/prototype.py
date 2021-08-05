from functools import wraps
import kivy
from kivy.app import App
from kivy.properties import ObjectProperty, NumericProperty
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.core.window import Window


class MyGridLayout(Widget):
    appLogger = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MyGridLayout, self).__init__(**kwargs)

        # Set gray color of the background
        Window.clearcolor = [i/255 for i in [40]*3 + [1]]
        self.appLogger.text = "App launched. Actual logs are printed in" +\
        "this filed.\nYou can find full log list in " +\
        "C:\\Users\\Martino\\ChujCiWDupe\\logs\\"


    def button_one_action(self):
        theText = "button one is being clicked."
        print(theText)
        self.appLogger.text = self.appLogger.text + '\n' + theText

    def button_two_action(self):
        theText = "button two is being clicked."
        print(theText)
        self.appLogger.text = self.appLogger.text + '\n' + theText

    def button_three_action(self):
        theText = "button three is being clicked."
        print(theText)
        self.appLogger.text = self.appLogger.text + '\n' + theText


class PrototypeApp(App):
    def build(self):
        app = MyGridLayout()
        # Clock.schedule_interval(build.update_color, 1.0/30.0)
        return app


if __name__ == "__main__":
    PrototypeApp().run()