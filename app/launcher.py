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

        # try:
        self._execute_command()
        
        # except Exception as e:
        #     print(Command.ERR_S,
        #           'exception during executing "next" command in LobbyState')
        #     print(e)
        
        # else:
        self._context.change_state(ReadyCheckState())

    def cancel(self) -> None:
        print(Command.ERR_S,
              'For this state "cancel" does not make sense.',
               sep=' ')
    
    async def _scan(self) -> None:
        if not self.lobby_getter_cmd:
            self.lobby_getter_cmd = LobbyGetter()

        # self.lobby_getter_cmd.execute()
        await self.lobby_getter_cmd._execute()

        lobby = self.lobby_getter_cmd.get_data()
        _type = self.lobby_getter_cmd.get_type()
        can_start = True if _type != None \
                    and _type != 'Delete' else False

        print(LobbyState.initialized)
        if LobbyState.initialized and lobby and can_start:
            self.next()
        

class ReadyCheckState(State):
    verbose : bool = True

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
        deleted = self.search_getter_cmd.get_type() == 'Delete'

        if search and not deleted:
            print(Command.INFO_S, 'searching...') if self.verbose else None

            # is_in_progress = search['readyCheck']['state'] == 'InProgress'
            is_found = search['searchState'] == 'Found'

            if is_found:
                print(Command.INFO_S, 'game is found') if self.verbose else None
                await asyncio.sleep(3)

                self_declined = search['readyCheck']['playerResponse'] == 'Declined'
                decliner_ids = search['readyCheck']['declinerIds']
                print('     >decliner ids: ', decliner_ids)
                
                if not self_declined:
                    print(Command.INFO_S, 'transition to next state') if self.verbose else None
                    self.next()
                
                else:
                    print(Command.INFO_S, 'self declination detected') if self.verbose else None
                    LobbyState.initialized = False
            
        else:
            self._context.change_state(LobbyState())


class DeclarePositionState(State):
    verbose : bool = True

    def __init__(self) -> None:
        super().__init__()
        self.lobby_getter_cmd: Command = None
        self.session_getter_cmd: Command = None
        self.search_getter_cmd: Command = None

    async def next(self) -> None:
        print('executing next command for DeclarePositionState class.')\
            if self.verbose else None
        
        hover_command = Hover('Singed')
        print(f"hover command: {hover_command}")
        print("before sleep")
        await asyncio.sleep(10)
        print("after sleep")
        # self._set_command(Hover('Zed'))

        try:
            # self._execute_command()
            print("before _execute")
            await hover_command._execute()
            print("after _execute")
        
        except Exception as e:
            print(Command.ERR_S, 'Error occured while calling next funcion',
                  'in DeclarePositionState class object')
            print(e)
        
        else:
            print("before state change")
            self._context.change_state(BanningState())

    
    def cancel(self) -> None:
        pass
    
    async def _scan(self) -> None:
        print(Command.INFO_S,
              'scanning in DeclarePositionState') if self.verbose else None

        # SEARCH GETTER INITIALIZATION
        # if not self.search_getter_cmd:
        #     self.search_getter_cmd = SearchGetter()
        
        # await self.search_getter_cmd._execute()

        # is_search_deleted = self.search_getter_cmd.get_type() == 'Delete'

        # SESSION GETTER INITIALIZATION
        if not self.session_getter_cmd:
            self.session_getter_cmd = SessionGetter()
        
        # self.session_getter_command.execute()
        await self.session_getter_cmd._execute()

        session_data = self.session_getter_cmd.get_data()
        session_type = self.session_getter_cmd.get_type()
        print(Command.INFO_S, f"session type: {session_type}") if self.verbose else None

        if session_data:
            print(Command.INFO_S, 'session exists') if self.verbose else None
            await self.next()


            # if self.session_getter_cmd.get_data():
            #     print(Command.INFO_S, 'Changing to a next state') if self.verbose else None
            
            # else:
            #     print(Command.INFO_S, 'Returning to Lobby State') if self.verbose else None
            #     self._context.change_state(LobbyState())
                # LOBBY GETTER INITIALIZATION
                # if not self.lobby_getter_cmd:
                #     self.lobby_getter_cmd = LobbyGetter()
                
                # await self.lobby_getter_cmd._execute()


class BanningState(State):
    verbose: bool = True

    def next(self) -> None:
        pass
    
    def cancel(self) -> None:
        pass

    def _scan(self) -> None:
        print(Command.INFO_S,
              'Scanning in banning state...') if self.verbose else None



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
