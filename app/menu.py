# kivy packages:
from os import sep
from sys import argv
import kivy
from kivy.animation import CompoundAnimation
from kivy.app import App
from kivy.properties import (
    NumericProperty, ObjectProperty, StringProperty
)
from kivy.clock import Clock
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import SpinnerOption, Spinner
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

# non-kivy packages:

# my packages:
from packages.theme import KivyTheme
from packages.utils import LOLClientStatusInformer

from champion_select import ChampionSelectUI, ChampionSelect, ChampionSelectInterface
from summoner_perks import SummonerPerksSlotUI

from lcu_driver import Connector
from termcolor import colored
from pprint import pprint
import asyncio

from command import *

import threading
from packages.LauncherCommand import LauncherCommand
from packages.launcher import Launcher, LobbyState

# import connector instance and websockets
from connector import connector


class AppLayout(TabbedPanel):
    '''Main container in the kivy file. Methods and properties
    which are defined here shouldn't be shared across another
    dynamic classes (should be in used only in the socope of this cls)'''

    # QUESTION: this property should be here or in menu class?
    number_of_bans = NumericProperty(5)

    def __init__(self, **kwargs):
        super(AppLayout, self).__init__(**kwargs)
        # print(self.btn, self.spnr, sep='\n')
        print()


    def spinner_clicked(self, value):
        opt = self.ids.spinner_id.text
        print(f'The option "{opt}" have been selected.')

    # QUESTION: those methods should be here or in menu class?
    def fooA(self):
        self.number_of_bans += 1
        print(f'fooA has been called. Method awaits to be implemented.')

    def fooB(self):
        print(f'fooB has been called. Method awaits to be implemented.')
        self.number_of_bans -= 1


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

class SettingsSpinner(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._app = kivy.app.App.get_running_app()
        self.bind(state=self._app.click_effect)

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

# currently working on
class LauncherButton(MyButton):
    '''This class is dedicated for all buttons related with
    league of legends launcher.'''
    # foo = ObjectProperty(None)
    # setting_spinner = ObjectProperty(None)
    save_selection = ObjectProperty(None)
    name_of_json_file = ObjectProperty(None)
    champion = ObjectProperty(None)

    endpoint_url_text_btn = StringProperty(None)
    endpoint_json_filename_btn = StringProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.command: Command = None
        self._app = kivy.app.App.get_running_app()
    

    def set_command(self, command):
        # if isinstance(command, Command):
        self.command = command
    
    def execute_command(self) -> None:
        try:
            self.command.execute()

        except Exception as e:
            print(Command.ERR_S, e, sep=' ')

    def on_press(self):

        # this method is replaced inside kivy file by one of the
        # following definitions of methods (find_match, cancell, ...)
        # we call it to set a command...
        self.buttons_method()

        # ...then we call execute() for setted command
        # by calling execute_command (kinda wrapper)
        self.execute_command()
    

    # user defined methods which set a appropirate command:

    def find_match(self):
        self.set_command(MatchFinder())

    def cancell(self):
        self.set_command(Canceller())
    
    def accept(self):
        self.set_command(Acceptor())
    
    def decline(self):
        self.set_command(Decliner())
    
    def save_to_file(self):
        self.set_command(
                         WS_JSONSaver(
                             spinner=self.save_selection,
                             textinput=self.name_of_json_file)
                         )
    
    def get_ally_bans(self):
        self.set_command(AllyBansGetter())

    def get_enemy_bans(self):
        self.set_command(EnemyBansGetter())

    def hover(self):
        self.set_command(Hover(self.champion.text))

    def get_hover(self):
        self.set_command(HoverGetter())

    def get_my_team_champs(self):
        self.set_command(MyTeamChampsGetter())

    def get_enemy_team_champs(self):
        self.set_command(EnemyTeamChampsGetter())

    def get_my_position(self):
        self.set_command(MyPositionGetter())

    def complete(self):
        self.set_command(Complete())
    
    def save_endpoint(self):
        self.set_command(
                EndpointSaver(
                    reqs=self.endpoint_url_text_btn,
                    filename=self.endpoint_json_filename_btn
                )
            )

    def default_action(self):
        print(Command.INFO_S,
              'For this button an action has not been set yet.',
               sep=' ')

class PlusMinusButton(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    '''Those methods doesn't need necessarily to be defined here. but doing
    so we are adding a wrapper for any function that will be called from
    any instance of a button. We can add some common activities that will
    be involved during clicking ANY button (of this cls).'''
    def minusButton(self):
        self.methodSub()
    
    def plusButton(self):
        self.methodAdd()
    
    def go(self):
        '''Temporary method for testing purposes.'''
        print('go is running')
    
class DropDown(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_select=lambda inst, x: self.setatter(inst, 'text', x))
        self.bind(on_release=self.open)

class MenuApp(App, KivyTheme):
    '''App class. Methods and properties which are defined here are
    probably shared across another dynamic classes in the project, 
    so they are here in order to provide easy communication between
    those classes.'''

    # Font settings
    _font_size = NumericProperty(16)

    # Appearance settings
    info_wp_offset = NumericProperty(300)  # information wrapper left padding

    # DEFINITIONS OF METHO
    def __init__(self, connector, **kwargs):
        super(MenuApp, self).__init__(**kwargs)

        # LOL client properties
        self.lol_client = LOLClientStatusInformer()
        self.is_lol_client_running = None


        Command.receiver = connector
        # Command.set_receiver(self.connector)
        # self._is_running = False

        # LCU driver connector initialization
        self.connector_thread = threading.Thread(target=connector.start)
        self.connector_thread.daemon = True
        self.connector_thread.start()

        # CololeController is class to handle and manage commands provied
        # by user through console. console.start() starts a infinite loop
        # which reads input
        self.console = LauncherCommand()
        self.console_thread = threading.Thread(target=self.console.start)
        self.console_thread.daemon = True
        self.console_thread.start()

        # Try to make this function async!!
        asyncio.run_coroutine_threadsafe(self._init_launcher(), connector.loop)
        # self.state = Launcher(LobbyState())
        # Command.state = self.state
        # self.state_thread = threading.Thread(target=self.state._scan_for_state_change)
        # self.state_thread.daemon = True
        # self.state_thread.start()

    async def _init_launcher(self):
        self.state = Launcher(LobbyState())
        Command.state = self.state
        await self.state._scan_for_state_change()
        # self.state_thread = threading.Thread(target=self.state._scan_for_state_change)
        # self.state_thread.daemon = True
        # self.state_thread.start()

    def update_lol_client_status_property(self, dt):
        self.lol_client.is_running()
        self.is_lol_client_running = self.lol_client._is_running

    # Buttons on_press method definitions:
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
    MenuApp(connector).run()
