# from LCU_driver_test.get_lobby_status import session
from abc import ABC, abstractmethod, abstractclassmethod
import asyncio
from typing import Optional, final

from lcu_driver import connector
from packages.JSONsaver import JSONSaver
from packages.champNameIdMapper import ChampNameIdMapper

from termcolor import colored
# from packages.launcher import LobbyState
# from menu import MenuApp

class Command(ABC):
    OK_S = f"[{colored(' OK  ', 'green')}]"
    ERR_S = f"[{colored('ERROR', 'red')}]"
    INFO_S = f"[{colored('INFO ', 'blue')}]"

    receiver = None
    actual_state = None
    lock = asyncio.Lock()

    def __init__(self):
        if Command.receiver:
            # self.receiver = receiver
            Command.connection = Command.receiver.connection
            Command._loop = Command.receiver.loop
            Command.locals = Command.connection.locals

        else:
            print(self.INFO_S, 'receiver is None type', sep=' ')

    def execute(self):
        return asyncio.run_coroutine_threadsafe(self._execute(), Command._loop)
        
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

        if self.text == 'session' or self.text == 'all':
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


        if self.text == 'lobby' or self.text == 'all':
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
                  

        if self.text == 'queue' or self.text == 'all':
            try:
                to_save = Command.locals['queue'].data

            except KeyError:
                print(Command.ERR_S, 'queue is empty')

            else:
                name = self.saver.save(what=to_save, 
                                       filename=self.filename,
                                       type=self.text)

                print(Command.OK_S,
                    f'the saving the "{self.text}".',
                    f'Name of file: "{name}".',
                    sep=' ')

        if self.text == 'search' or self.text == 'all':
            try:
                to_save = Command.locals['search'].data

            except KeyError:
                print(Command.ERR_S, 'search is empty')

            else:
                name = self.saver.save(what=to_save, 
                                       filename=self.filename,
                                       type=self.text)

                print(Command.OK_S,
                    f'the saving the "{self.text}".',
                    f'Name of file: "{name}".',
                    sep=' ')

class AllyBansGetter(Command):
    async def _execute(self):
        champs = ChampNameIdMapper.get_champion_dict(order='reversed')
        my_team_bans = self.locals['session'].data['bans']['myTeamBans']
        bans = (champs[str(ban)] for ban in my_team_bans)
        
        try:
            print('Our team bans: |', *[colored(f'{b}', 'cyan') + ' |' for b in bans])

        except KeyError as e:
            print(f'key error:\n{e}')
        
        # except Exception as e:
        #     print(e)
        #     print(e.with_traceback)

class EnemyBansGetter(Command):
    async def _execute(self):
        champs = ChampNameIdMapper.get_champion_dict(order='reversed')
        enemy_team_bans = self.locals['session'].data['bans']['theirTeamBans']
        bans = (champs[str(ban)] for ban in enemy_team_bans)
        
        try:
            print('enemy team bans: |', *[colored(f'{b}', 'cyan') + ' |' for b in bans])

        except KeyError as e:
            print(f'key error:\n{e}')
        
        # except Exception as e:
        #     print(e)
        #     print(e.with_traceback)

class Hover(Command):
    def __init__(self, champion: str = None):
        super().__init__()
        try:
            self.champion = int(champion)

        except ValueError:
            champs = ChampNameIdMapper.get_champion_dict(order='normal')

            try:
                self.champion = champs[champion]

            except KeyError:
                print(Command.ERR_S,
                      'Invalid name of the champion.',
                      'Note, that this field is case-sensitive', sep=' ')

    async def _execute(self):
        champ_id = self.champion
        active_action = Command.locals['active_action']

        # START (printing variables)
        print(f"active action from locals: {active_action}")
        d = await self.connection.request('get', '/lol-champ-select/v1/session')
        json = await d.json()
        for e in json:
            for i in e:
                if i['isInProgress']:
                    active_action2 = i

        print(f"active action from request: {active_action2}")
        # STOP (printing variables)


        reqs = f'/lol-champ-select/v1/session/actions/{active_action["id"]}'

        res = await self.connection.request('patch', reqs,
                                            data={'championId': champ_id})

        if res.status in list(range(200, 209)):
            print(Command.OK_S,
                  'successfully changed hovered champ to:',
                    colored(self.champion, 'red'), sep=' ')

        else:
            print(Command.ERR_S,
                  'something went wrong while hovering the champion',
                    colored(self.champion, 'red'), sep=' ')

class HoverGetter(Command):
    async def _execute(self):
        action = self.locals['active_action']
        champs = ChampNameIdMapper.get_champion_dict(order='reversed')

        if action['championId']:
            champ = champs[str(action['championId'])]
            print(f'Champion {colored(champ, "red")} is hovered.')
        
        else:
            print('A champion has not been selected yet.')

class MyTeamChampsGetter(Command):
    async def _execute(self):
        champs = ChampNameIdMapper.get_champion_dict(order='reversed')
        my_team_picks = self.locals['session'].data['myTeam']
        bans = (champs.get(str(ban['championId'])) for ban in my_team_picks)
        
        try:
            print('Our team picks: |', *[colored(f'{b}', 'cyan') + ' |' for b in bans])

        except KeyError as e:
            print(f'key error:\n{e}')

class EnemyTeamChampsGetter(Command):
    async def _execute(self):
        champs = ChampNameIdMapper.get_champion_dict(order='reversed')
        my_team_picks = self.locals['session'].data['theirTeam']
        bans = (champs.get(str(ban['championId'])) for ban in my_team_picks)
        
        try:
            print('enemy team picks: |', *[colored(f'{b}', 'cyan') + ' |' for b in bans])

        except KeyError as e:
            print(f'key error:\n{e}')

class MyPositionGetter(Command):
    async def _execute(self):

        # TODO: this shoudl be available globally
        reqs = '/lol-summoner/v1/current-summoner'
        res = await self.connection.request('get', reqs)

        data = await res.json()
        SUMMONER_ID = data['summonerId']

        for player in self.locals['session'].data['myTeam']:
            if player['summonerId'] == SUMMONER_ID:
                if player['assignedPosition']:
                    print(f"Your position: {player['assignedPosition']}")

                else:
                    print('In this mode positioning is disabled')

class Complete(Command):

    async def _execute(self):
        active_action = self.locals['active_action']
        champs = ChampNameIdMapper.get_champion_dict(order='reversed')
        action_type = active_action['type']
        champ_id = active_action['championId']

        # reqs = f'/lol-champ-select/v1/session/actions/{active_action["id"]}'
        # res = await connection.request('patch', reqs,
        #                                data={'isInProgress': False})

        reqs = f'/lol-champ-select/v1/session/actions/{active_action["id"]}/complete'
        res = await self.connection.request('post', reqs)

        if res.status in list(range(200, 209)):
            act = lambda: action_type + 'n' if action_type == 'ban'\
                                            else action_type
            print(Command.OK_S,
                    f'Champion has been {act()}ed.',
                    colored(champs[str(champ_id)], 'red'), sep=' ')

class EndpointSaver(Command):
    def __init__(self, reqs: str, filename: str):
        super().__init__()

        self.reqs: str = reqs
        self.filename: str = filename
        self.saver = JSONSaver()

    async def _execute(self):
        res = await self.connection.request('get', self.reqs)

        if res.status in list(range(200, 209)):
            print(Command.OK_S,
                    f'endpoint requested successfully', sep=' ')

            data = await res.json()
            name = self.saver.save(what=data,
                                   filename=self.filename,
                                   type='customEndpoint')
        
        else:
            print(Command.ERR_S,
                  f'error no.: {res.status}', sep=' ')


# Made for Launcher class:
class InitState(Command):
    async def _execute(self):
        Command.actual_state.initialized = True


class DeinitState(Command):
    async def _execute(self):
        Command.actual_state.initialized = False
        Canceller().execute()


class LobbyGetter(Command):
    def __init__(self):
        super().__init__()

        self._return = None # for internal usage only!
        self.data = None
        self.type = None

    async def _execute(self):
        '''Do not modify locals['lobby'] in this method!'''

        try:
            # If it does exit that means it was created by websocket
            # and containt data as well as type fields
            self._return = Command.locals['lobby']

        except KeyError:
            print(Command.ERR_S,
                  'lobby object not found in locals!')
            print(Command.INFO_S,
                  'requesting for the data.')

            await self.request_data()

        else:
            if self._return: 
                if self._return.data:
                    self.data = self._return.data

                self.type = self._return.type

            # If data is empty that means that lobby has been removed
            # else:
            #     print(Command.INFO_S,
            #         'data is NoneType\n')
                
            #     self._reutrn
            #     self.type = self._return.type
        
    async def request_data(self):
        '''Use this method force data acqusition '''

        reqs = '/lol-lobby/v2/lobby'
        res = await self.connection.request('get', reqs)
        if res.status in list(range(200, 210)):
            print(Command.INFO_S, 'Getting lobby data')
            self.data = await res.json()
            self.type = 'Manual'
        
        else:
            print(Command.ERR_S, 'Requested data cannot be get')
            self.data = None
            self.type = None


    def _get_return(self):
        '''Return direct return from Command.locals['lobby']'''
        return self._return
    
    def get_data(self):
        '''json file describing lobby (acquired from locals or requested)'''
        return self.data
    
    def get_type(self):
        '''type can be Update or Delete or Manual.
        take value only if data is acquired from websocket.'''
        return self.type


class SearchGetter(Command):
    def __init__(self):
        super().__init__()
        self._return = None

        self.data = None
        self.type = None
        # self.arg = arg_ready_check

    async def _execute(self):
        '''Do not modify locals['search'] in this method!'''

        try:
            # If it does exit that means it was created by websocket
            # and containt data as well as type fields
            self._return = Command.locals['search']

        except KeyError:
            print(Command.ERR_S,
                  'search object not found in locals.')

        else:
            if self._return:
                if self._return.data:
                    self.data = self._return.data

                self.type = self._return.type

    def _get_return(self):
        '''Return direct return from Command.locals['search']'''
        return self._return
    
    def get_data(self):
        '''json file describing lobby (acquired from locals or requested)'''
        return self.data
    
    def get_type(self):
        '''type can be Update or Delete or Manual.
        take value only if data is acquired from websocket'''
        return self.type


class SessionGetter(Command):
    def __init__(self):
        super().__init__()

        self._return = None
        self.data = None
        self.type = None

    async def _execute(self):
        '''Do not modify locals['session'] in this method'''

        try:
            self._return = Command.locals['session']

        except KeyError:
            print(Command.ERR_S,
                  'session object not found in session\n')

        else:
            if self._return:
                if self._return.data:
                    self.data = self._return.data
                
                self.type = self._return.type

    def _get_return(self):
        return self._return
    
    def get_data(self):
        return self.data
    
    def get_type(self):
        return self.type


class QueueGetter(Command):
    def __init__(self):
        super().__init__()

        self._return = None
        self.data = None
        self.type = None

    async def _execute(self):
        try:
            data = Command.locals['queue']

        except KeyError:
            print(Command.ERR_S,
                  'queue object not found in queue\n')

        else:
            if self._return:
                if self._return.data:
                    self.data = self._return.data

                self.type = self._return.type

    def _get_return(self):
        return self._return
    
    def get_data(self):
        return self.data
    
    def get_type(self):
        return self.type


class EndpointSender(Command):
    """Class for sending POST, PUT and DELETE requests to the LCU through the LCU driver.

    Attributes:
        request: link of the endpoint.
        request_data: dictionary with necessary request body.
        request_type: type of the request it can be POST, PUT and DELETE(GET request doesn't make sense here).

    """

    def __init__(self, request: str, request_type: str, request_data: dict = None):
        super().__init__()
        self.request = request
        self.request_type = request_type

        self.request_data = request_data
        if self.request_data is None:
            self.request_data = {}

    async def _execute(self):
        result = await self.connection.request(self.request_type, self.request, data=self.request_data)
        # check if the request was successful
        return result.status in list(range(200, 209))
