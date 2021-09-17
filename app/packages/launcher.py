from __future__ import annotations
from abc import ABC, abstractmethod
from sys import argv
from typing import Match
from time import sleep
from command import *


class Launcher:
    _state = None

    def __init__(self, arg_state: State) -> None:
        self.change_state(arg_state)
    
    def change_state(self, arg_state: State) -> None:
        self._state = arg_state
        self._state.set_context(self)

    def next(self) -> None:
        self._state.next()

    def cancel(self) -> None:
        self._state.cancel()
    
    async def _scan_for_state_change(self) -> None:
        while True:
            await asyncio.sleep(.2)
            await self._state._scan()
            # if conn.locals['seesion'].data['specyfic_value'] == 'mid':
            #     pass


class State(ABC):
    def __init__(self) -> None:
        self._command: Command = None
        self._context: Launcher = None
        self._run_loop: bool = True
        self.allowed_to_change_state: bool = False

    def get_context(self) -> Launcher:
        return self._context
    
    def set_context(self, arg_context: Launcher) -> None:
        self._context = arg_context
    
    def _set_command(self, arg_command: Command) -> None:
        self._command = arg_command
    
    def _execute_command(self):
        self._command.execute()
    
    def _get_json(self):
        pass

    @abstractmethod
    def next(self) -> None:
        '''Depending on state it can be: findmatch/accept/ban/pick/
        perform hover command'''
        pass

    @abstractmethod
    def cancel(self) -> None:
        '''Depending on state it can be: cancel match search/decline/quit
        command'''
        pass
    
    @abstractmethod
    async def _scan(self) -> None:
        '''This method is responsible for scanning for specyfic data in
        json file provided by websockets. Depending on state it will
        search for relevant data.
        
        Conside the idea of creating a flag in State class which states if 
        the state can be switched or not. The flag will be assigned by this
        method and next and cancel method will be use one in order to
        determine whether they are allowed to perform itself action.'''
        pass


class LobbyState(State):
    initialized : bool = False

    def __init__(self) -> None:
        super().__init__()
        self.lobby_getter_cmd : Command = None
        Command.actual_state = LobbyState
        
    def next(self) -> None:
        self._set_command(MatchFinder())

        try:
            self._execute_command()
        
        except Exception as e:
            print(Command.ERR_S,
                  'exception during executing "next" command in LobbyState')
            print(e)
        
        else:
            self._context.change_state(ReadyCheckState())

    def cancel(self) -> None:
        print(Command.ERR_S,
              'For this state "cancel" does not make sense.',
               sep=' ')
    
    async def _scan(self) -> None:
        if not self.lobby_getter_cmd:
            self.lobby_getter_cmd = LobbyGetter()

        self.lobby_getter_cmd.execute()

        lobby = self.lobby_getter_cmd.get_data()
        _type = self.lobby_getter_cmd.get_type()
        can_start = True if _type != None \
                    and _type != 'Delete' else False

        print(LobbyState.initialized)
        if LobbyState.initialized and lobby and can_start:
            self.next()
        

class ReadyCheckState(State):
    def __init__(self) -> None:
        super().__init__()
        self.search_getter_cmd : Command = None

    def next(self) -> None:
        self._set_command(Acceptor())

        try:
            self._execute_command()
        
        except Exception as e:
            print('exception during executing "next" command in ReadyCheckState')
            print(e)
        
        else:
            # tutaj jakies zabezpieczenie jesli gra zostanie zdeclie'owana przez kogos
            self._context.change_state(DeclarePositionState())

    
    def cancel(self) -> None:
        self._set_command(Canceller())

        try:
            self._execute_command()

        except Exception as e:
            print('exception during executing "cancel" command in ReadyCheckState')
            print(e)
        
        else:
            self._context.change_state(LobbyState())
    
    async def _scan(self) -> None:

        if not self.search_getter_cmd:
            self.search_getter_cmd = SearchGetter()

        # if not self.lobby_getter_cmd:
        #     self.lobby_getter_cmd = LobbyGetter()

        # run coroutine threadsafe here????????
        await self.search_getter_cmd._execute()
        search = self.search_getter_cmd.get_data()


        print('searching state is active now')

        if search:
            print(Command.INFO_S, 'searching...')

            # in_queue = data['isCurrentlyInQueue']
            # is_found = search['searchState'] == 'Found'
            is_in_progress = search['readyCheck']['state'] == 'InProgress'
            self_declined = search['readyCheck']['playerResponse'] == 'Declined'
            # decliner_ids = search['readyCheck']['declinerIds']

            # TODO: add delay (using counter for safety)
            if is_in_progress and not self_declined:
                self.next()
            
            elif self_declined:
                LobbyState.initialized = False
            
        else:
            self._context.change_state(LobbyState())


class DeclarePositionState(State):
    def __init__(self) -> None:
        super().__init__()
        self.lobby_getter_command: Command = None
        self.session_getter_command: Command = None

    def next(self) -> None:
        print('executing next command for DeclarePositionState class.')
    
    def cancel(self) -> None:
        pass
    
    async def _scan(self) -> None:
        # TODO: you should just check if session exist here.
        # if existes go next (so execute command and switch to next)
        # you should chack if lobby has been hanged as well
        # canStartActivity is useful to terermine if everyone accepted
        print(Command.OK_S, 'HURRAAAAA!', sep=' ')

        if not self.lobby_getter_command:
            self.lobby_getter_command = LobbyGetter()
        
        self.lobby_getter_command.execute()

        if not self.session_getter_command:
            self.session_getter_command = SessionGetter()
        
        self.session_getter_command.execute()

        # Check if after your acceptance someone else declined
        if lobby := self.lobby_getter_command.get_result():
            if not lobby['canStartActivity']:

                # fix this (if someone dodge, then session will still exit)
                if self.session_getter_command.get_return():
                    self.next()
            else:
                self._context.change_state(ReadyCheckState())


class BanningState(State):
    def next(self) -> None:
        pass
    
    def cancel(self) -> None:
        pass


class PickingState(State):
    def next(self) -> None:
        pass
    
    def cancel(self) -> None:
        pass


class PreGameState(State):
    def next(self) -> None:
        pass
    
    def cancel(self) -> None:
        pass
