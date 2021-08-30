from abc import ABC, abstractmethod, abstractclassmethod
import asyncio
from packages.JSONsaver import JSONSaver

from termcolor import colored
# from menu import MenuApp

class Command(ABC):
    OK_S = f"[{colored(' OK  ', 'green')}]"
    ERR_S = f"[{colored('ERROR', 'red')}]"
    INFO_S = f"[{colored('INFO ', 'blue')}]"

    receiver = None

    def __init__(self):
        if Command.receiver:
            # self.receiver = receiver
            Command.connection = Command.receiver.connection
            Command._loop = Command.receiver.loop
            Command.locals = Command.connection.locals

        else:
            print(self.INFO_S, 'receiver is None type', sep=' ')

    def execute(self):
        asyncio.run_coroutine_threadsafe(self._execute(), Command._loop)
        
    @abstractmethod
    async def _execute(self):
        pass


class MatchFinder(Command):

    async def _execute(self):

        res = await self.connection.request('post', '/lol-lobby/v2/lobby/matchmaking/search')
        if res.status == 204:
            print(self.OK_S,
                    'Game searching has been started.')

        else:
            print(self.ERR_S, f'error: {res.status}')
            # _error_whit_connection(res)

class Canceller(Command):
    async def _execute(self):

        res = await self.connection.request('delete', '/lol-lobby/v2/lobby/matchmaking/search')
        if res.status == 204:
            print(self.OK_S,
                    'Gamer searching has been cancelled.')

        else:
            print(self.ERR_S, f'error: {res.status}')
            # _error_whit_connection(res)
    
class Acceptor(Command):
    async def _execute(self):

        reqs = '/lol-matchmaking/v1/ready-check/accept'
        res = await self.connection.request('post', reqs)

        if res.status == 200:
            print(self.OK_S,
                    'Game has been accepted.', sep=' ')

        else:
            print(self.ERR_S, f'error: {res.status}')
            # _error_whit_connection(res)

class Decliner(Command):
    async def _execute(self):

        reqs = '/lol-matchmaking/v1/ready-check/decline'
        res = await self.connection.request('post', reqs)

        if res.status == 200:
            print(self.OK_S,
                    'Game has been declined.', sep=' ')

        else:
            print(self.ERR_S, f'error: {res.status}')
            # _error_whit_connection(res)

class WS_JSONSaver(Command):
    def __init__(self, spinner, textinput):
        super().__init__()
        self.text, self.values = spinner.text, spinner.values
        self.filename = textinput.text
        self.saver = JSONSaver()


    async def _execute(self):

        if self.text == 'session':
            try:
                to_save = Command.locals['session'].data

            except KeyError:
                print(Command.ERR_S, 'session is empty')

            else:
                print(Command.OK_S,
                    f'the saving the {self.text}.',
                    f'Name of file: {self.filename}.',
                    sep=' ')
                    
                self.saver.save(what=to_save,
                                filename=self.filename,
                                type=self.text)


        elif self.text == 'lobby':
            try:
                to_save = Command.locals['lobby'].data

            except KeyError:
                print(Command.ERR_S, 'lobby is empty')

            else:
                name = self.saver.save(what=to_save, 
                                       filename=self.filename,
                                       type=self.text)

                print(Command.OK_S,
                    f'the saving the "{self.text}".',
                    f'Name of file: "{name}".',
                    sep=' ')
                  

        elif self.text == 'nothing':
            print('opierdalansko hue hue.')