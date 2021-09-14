from __future__ import annotations
from abc import ABC, abstractmethod
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
    initialized: bool = False
    def __init__(self) -> None:
        super().__init__()
        # self.get_game_mode_cmd : Command = None

    def next(self) -> None:
        self._set_command(MatchFinder())

        # if self.allowed_to_change_state:
        try:
            self._execute_command()
        
        except Exception as e:
            print('exception during executing "next" command in LobbyState')
            print(e)
        
        else:
            self._context.change_state(ReadyCheckState())

        # else:
        #     print(Command.INFO_S,
        #           'Not allowed to change state', sep=' ')

    
    def cancel(self) -> None:
        print(Command.ERR_S,
              'For this state "cancel" does not make sense.',
               sep=' ')
        # self._set_command(Canceller())

        # try:
        #     self._execute_command()
        
        # except Exception as e:
        #     print('exception during executing "cancel" command in LobbyState')
    
    async def _scan(self) -> None:
        get_game_mode_cmd = GameModeGetter()
        get_game_mode_cmd.execute()

        # if self.initialized:
        #     self.next()

        if LobbyState.initialized or get_game_mode_cmd.get_result():
            self.next()

        # res = get_game_mode_cmd.get_result()
        # if res:
        #     self.allowed_to_change_state = True


class ReadyCheckState(State):
    def __init__(self) -> None:
        super().__init__()
        self.get_ready_check_cmd : Command = None
        self.get_lobby_cmd : Command = None

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
        pass
    
    async def _scan(self) -> None:
        print('###scanning from ReadyCheckState')
        # should involve next state but this next state under some conditions
        # can back to this one
        if not self.get_ready_check_cmd:
            print(Command.INFO_S, 'creating new instance of ReadyCheck')
            self.get_ready_check_cmd = ReadyCheckGetter()

        # if not self.get_lobby_cmd:
        #     self.get_lobby_cmd = IsActiveable()

        # if not self.get_lobby_cmd._return:
        #     print(Command.INFO_S, 'getting data...')
        #     self.get_lobby_cmd.execute()

        else:
            print(Command.INFO_S, 'data is not empty: ')
            print(self.get_ready_check_cmd._return)

        self.get_ready_check_cmd.execute()
        data = self.get_ready_check_cmd.get_return()
        # is_activeable = self.get_lobby_cmd.get_return()
        # second approach - get_return is async and await it

        if data:
            print('$$$data is retreved:')
            print(data)
            # in_queue = data['isCurrentlyInQueue']
            is_found = data['searchState'] == 'Found'
            is_in_progress = data['readyCheck']['state'] == 'InProgress'
            self_declined = data['readyCheck']['playerResponse'] == 'Declined'
            decliner_ids = data['readyCheck']['declinerIds']

            print(f'is found: {is_found}')
            print(f'is in progress: {is_in_progress}')
            print(f'self declined: {self_declined}')
            print(f'decliner ids: {decliner_ids}')

            if (is_in_progress and is_found
                and not self_declined and not decliner_ids):
                print('pass to the next state')
                self.next()
            
            # elif is_activeable['canStartActivity']:
            #     LobbyState.initialized = False
            #     self._context.change_state(LobbyState())


class DeclarePositionState(State):
    def next(self) -> None:
        pass
    
    def cancel(self) -> None:
        pass
    
    async def _scan(self) -> None:
        print(Command.OK_S, 'HURRAAAAA!', sep=' ')
        get_ready_check_cmd = ReadyCheckGetter()
        get_ready_check_cmd.execute()

        # Check if after your acceptance someone else declined
        if data := get_ready_check_cmd.get_return():
            self_declined = True \
                            if data['readyCheck']['playerRespone'] == 'Declined' \
                            else False
            decliner_ids = data['readyCheck']['declinerIds']
            is_in_progress = True \
                             if data['readyCheck']['state'] == 'InProgress' \
                             else False

            if (decliner_ids or not is_in_progress):
                print(Command.INFO_S,
                      'Returning to ReadyCheckState', sep=' ')
                self._context.change_state(ReadyCheckState())

            if (self_declined or not is_in_progress):
                print(Command.INFO_S,
                      'Returning to LobbyState', sep=' ')
                self._context.change_state(LobbyState())

        
        # TODO: chekc if session exists then execute next (hover and change state)



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
