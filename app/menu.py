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
from kivy.uix.spinner import SpinnerOption, Spinner
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

from lcu_driver import Connector, connector
import aioconsole
from termcolor import colored
from pprint import pprint

import command as cd
from packages.champNameIdMapper import ChampNameIdMapper

import threading
import asyncio

class AppLayout(TabbedPanel):
    '''Main container in the kivy file. Methods and properties
    which are defined here shouldn't be shared across another
    dynamic classes (should be in used only in the socope of this cls)'''

    # QUESTION: this property should be here or in menu class?
    number_of_bans = NumericProperty(5)

    def __init__(self, **kwargs):
        super(AppLayout, self).__init__(**kwargs)

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

class LauncherButton(MyButton):
    # foo = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.command: cd.Command = None
        self._app = kivy.app.App.get_running_app()
        
    
    def set_command(self, command):
        # if isinstance(command, cd.Command):
        self.command = command
        
        # else:
        #     print(cd.Command.ERR_S, 'Failiture while assigning a command')
    
    def execute_command(self) -> None:
        try:
            self.command.execute()
        except Exception as e:
            print(e)
    
    def find_match(self):
        self.set_command(cd.MatchFinder(receiver=self._app.connector,
                         loop=MenuApp.loop))

    def cancell(self):
        self.set_command(cd.Canceller())
    
    def nothing(self):
        print('abc')

    def on_press(self):
        self.foo()
        self.execute_command()



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

    # LOL client properties
    lol_client = LOLClientStatusInformer()
    is_lol_client_running = NumericProperty(0)

    # Font settings
    _font_size = NumericProperty(16)

    # Appearance settings
    info_wp_offset = NumericProperty(300)  # information wrapper left padding

    # LCU driver connector object (static)
    connector = Connector()
    # loop = None
    _is_running = None

    # DEFINITIONS OF METHODS
    def __init__(self, **kwargs):
        super(MenuApp, self).__init__(**kwargs)

        # LCU driver connector initialization
        threads = []
        # ten watek nigdy nie zakończy swojego działania!!!! Nawet jak wyjdziesz z petli
        t = threading.Thread(target=self.connector.start)
        # t.daemon = True
        t.start()
        threads.append(t)

        # to ma byc wylaczone!!!
        # self.connector.start()

    
    @classmethod
    def get_is_running(cls) -> bool:
        if cls._is_running != None:
            return cls._is_running

        else:
            raise Exception('is_running property is None type.')

    @classmethod
    def set_is_running(cls, value: bool) -> None:
        if isinstance(value, bool):
            cls._is_running = value
        
        else:
            raise Exception('is_running can be assigned only to bool type.')
    
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


    # LCU driver related
    @staticmethod
    @connector.ready
    async def connect(connection):
        print(cd.Command.OK_S,
            'LCU API is ready to be used.')
        
        # print('runnign LOOP: ' + asyncio.get_event_loop())
        # print('all tasks: ' + asyncio.all_tasks())
        MenuApp.loop = asyncio.get_running_loop()
        print(cd.Command.INFO_S,
              'Connector running on loop:',
              MenuApp.loop, sep=' ')


        # get summoner name
        res = await connection.request('get', '/lol-summoner/v1/current-summoner')
        if res.status == 200:
            data = await res.json()
            SUMMONER_NAME: str = data['internalName']
            SUMMONER_ID: int = data['summonerId']
            SUMMONER_PUUID: str = data['puuid']

            print(cd.Command.OK_S,
            'Logged in successfully\n',
            '\t-Currently logged as summoner:',
            colored(f'{SUMMONER_NAME}\n', attrs=('bold',)),
            '\t-summoner id:',
            colored(f'{SUMMONER_ID}\n', attrs=('bold',)),
            sep=' ')

            status = await ChampNameIdMapper.get_data()
            print(cd.Command.OK_S,
                'champion id and name mapped successfully',
                f' .status: {status}')

        else:
            MenuApp._error_whit_connection(res)

        while MenuApp._is_running:
        # while True:
            try:
                u_command = await aioconsole.ainput('command:\n')

            except KeyboardInterrupt:
                break

            except Exception:
                break
        

            # command = LauncherrCommands()
            # command.set_command(u_command)
            # command.execute_command()


            # Lobby and searching for game related
            if u_command == 'findmatch':
                '''While in lobby start fingin a match.'''
                res = await connection.request('post', '/lol-lobby/v2/lobby/matchmaking/search')
                if res.status == 200:
                    print(colored('[OK]', 'green'),
                            'Game searching has been started.')

                else:
                    MenuApp._error_whit_connection(res)

            elif u_command == 'cancel':
                res = await connection.request('delete', '/lol-lobby/v2/lobby/matchmaking/search')
                if res.status == 200:
                    print(colored('[OK]', 'green'),
                            'Search has been cancelled.')

                else:
                    MenuApp._error_whit_connection(res)


        print('about to die')
        raise KeyboardInterrupt


    @staticmethod
    @connector.close
    async def disconnect(_):
        print('The client have been closed!')
        await MenuApp.connector.stop()

    @staticmethod
    def _error_whit_connection(res):
        print(colored('[error]', 'red'),
                f'An error occured while request. Err no.: {res.status}',
                end='')


    @staticmethod
    @connector.ws.register('/lol-lobby/v2/lobby', event_types=('UPDATE',))
    async def lobby(connection, event):
        # print(type(event))

        # helping variables
        content: str = str()
        header: str = colored('The game lobby started.', 'red')
        data: dict = {
            'Game mode': event.data['gameConfig']['gameMode'],
        }

        # fulfill content variable
        for key, value in data.items():
            content += colored(f"\t-{key}: ", 'red')
            content += colored(f"{value}", 'red', attrs=('bold',))
            content += '\n'

        # print out data
        print(header)
        print(content)

        # ADD EVENT OBJECT TO CONNECTION'S LOCALS IN OREDER TO GAIN OUTER ACCESS
        connection.locals.update({'lobby': event})
        # pprint(connector.ws.registered_uris)

    @staticmethod
    @connector.ws.register('/lol-champ-select/v1/session', event_types=('UPDATE',))
    async def session(connection, event):
    
        # print(type(event))

        # helping variables
        champs = ChampNameIdMapper.get_champion_dict(order='reversed')
        for e in event.data['actions']:
            for d in e:
                if d['isInProgress']:
                    active_action_id = d['id']
                    active_action = d
                else:
                    active_action_id = None
                    active_action = None

        try:
            hovered_champ = champs[str(active_action['championId'])]

        except KeyError:
            hovered_champ = None
        
        except TypeError:
            hovered_champ = None


                # print(f'Champion {colored(champ, "red")} is hovered.')
        content: str = str()
        header: str = colored('Session has been updated:', 'red')
        data: dict = {
            'bans': event.data['bans']['myTeamBans'],
            # 'benchChampionIds': event.data['benchChampionIds'],
            # 'gameId': event.data['gameId'],
            # 'actions': event.data['actions'],
            'activeAction': active_action_id,
            'hoveredChampion': hovered_champ,
        }

        # fulfill content variable
        for key, value in data.items():
            content += colored(f"\t-{key}: ", 'red')
            content += colored(f"{value}", 'red', attrs=('bold',))
            content += '\n'

        # print out data
        print(header)
        print(content)

        # ADD EVENT OBJECT TO CONNECTION'S LOCALS IN OREDER TO GAIN OUTER ACCESS
        connection.locals.update({'session': event,
                                'active_id': active_action_id,
                                'active_action': active_action,})
        # pprint(connector.ws.registered_uris)

    def on_start(self):
        self.set_is_running(True)

    def on_stop(self):
        self.set_is_running(False)

    def build(self):
        app = AppLayout()
        Clock.schedule_interval(self.update_lol_client_status_property, 2)
        return app


if __name__ == "__main__":
    MenuApp().run()
