from __future__ import annotations
from abc import ABC, abstractmethod
from sys import argv
from typing import Match
from time import sleep
from command import *
import json
import os
from packages.champNameIdMapper import ChampNameIdMapper
from rune_maker import send_most_optimal_runes_for
from summoner_perks import send_user_defined_summoner_spells

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

        # print(LobbyState.initialized)
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
                    self._context.change_state(LobbyState())
            
        else:
            self._context.change_state(LobbyState())


class DeclarePositionState(State):
    verbose : bool = True

    def __init__(self) -> None:
        super().__init__()
        self.session_getter_cmd: Command = None
        self.search_getter_cmd: Command = None

    def next(self) -> None:
        print(Command.INFO_S, 'Switching to the next state: BanningState.')
        self._context.change_state(BanningState())
    
    def cancel(self) -> None:
        pass
    
    async def _scan(self) -> None:
        print(Command.INFO_S, 'Scanning in DeclarePositionState...')

        if not self.search_getter_cmd:
            self.search_getter_cmd = SearchGetter()

        if not self.session_getter_cmd:
            self.session_getter_cmd = SessionGetter()

        await self.search_getter_cmd._execute()
        search = self.search_getter_cmd.get_data()
        print(f"    >search: {search}")

        if search:
            print("search contains a data, backing to ReadyCheckState.")
            self._context.change_state(ReadyCheckState())
        
        await self.session_getter_cmd._execute()
        session = self.session_getter_cmd.get_data()
        # print(f"    >session: {session}")

        if session:
            if session["timer"]["phase"] == "BAN_PICK":
                self.next()
            

class BanningState(State):
    verbose: bool = True

    BASE: str = os.path.join(os.path.dirname(__file__), '..', 'data')
    FILENAME: str = os.path.join(os.path.normpath(os.path.join(BASE)),
                                     'champion_select_picks_and_bans.json')

    def next(self) -> None:
        champ_to_ban = self._choose_first_available_ban()
        self._set_command(Hover(champ_to_ban))
        self._execute_command()

        self._set_command(Complete())
        try:
            self._execute_command()
            print('right after executing command - Complete()')
        except Exception as e:
            print('execption while executing Complete in BanningState.')
            print(e)


        # await Hover('Zed')._execute()
        # await Complete()._execute()

        print(Command.INFO_S, 'transition to PickingState.')
        self._context.change_state(PickingState())
    
    def cancel(self) -> None:
        pass

    async def _scan(self) -> None:
        print(Command.INFO_S,
              'Scanning in banning state...') if self.verbose else None

        my_action: Action = Command.session_manager.get_my_action()

        if my_action.type == 'ban':
            print(Command.INFO_S, 'banning phase detected executing next.')\
                if self.verbose else None

            self.next()
        
        else:
            print(Command.INFO_S, 'banning phase not detected.')\
                if self.verbose else None
    
    def _choose_first_available_ban(self) -> int:
        with open(self.FILENAME, "r") as pick_priority_data:
            ban_queue = json.load(pick_priority_data)["bans"]

            champs = ChampNameIdMapper.get_champion_dict(order='normal')
            ban_queue: list[int] = [int(champs[ban]) for ban in ban_queue]
            
            return ban_queue[0]

class PickingState(State):
    verbose: bool = True
    
    BASE: str = os.path.join(os.path.dirname(__file__), '..', 'data')
    FILENAME: str = os.path.join(os.path.normpath(os.path.join(BASE)),
                                     'champion_select_picks_and_bans.json')
    
    def next(self) -> None:
        champ_to_pick = self._choose_first_available_pick()
        self._set_command(Hover(champ_to_pick))
        self._execute_command()
        sleep(1)
        self._set_command(Complete())
        self._execute_command()
        # await Hover('TwistedFate')._execute()
        # await Complete()._execute()

        self._context.change_state(PreGameState())
    
    def cancel(self) -> None:
        pass

    async def _scan(self) -> None:
        # print(Command.INFO_S, 'Scanning in picking state...')
        print(Command.INFO_S, 'Scanning in PickingState...')

        # 1. try to comment everything
        # 2. breakpoint on my_aciton = Command.session_manager...

        my_action: Action = Command.session_manager.get_my_action()


        # print(Command.INFO_S, 'my action:', my_action.__dict__)

        if my_action:
            if my_action.type == 'pick':
                print(Command.INFO_S, 'picking phase detected executing next.')

                self.next()
            
            else:
                print(Command.INFO_S, 'picking phase not detected.')
    
    def _choose_first_available_pick(self) -> str:

        with open(self.FILENAME, "r") as pick_priority_data:
            pick_queue = json.load(pick_priority_data)["picks"]

            champs = ChampNameIdMapper.get_champion_dict(order='normal')
            pick_queue_id: list[int] = []
            # [int(champs[pick]) for pick in pick_queue]

            for pick in pick_queue:
                # TODO: Allow a programmer read this line of code without
                # need of buying second screen
                formatted_key = list(filter(lambda name: name.lower() == pick.lower(), champs.keys()))[0]
                pick_queue_id.append(int(champs[formatted_key]))

        actions: list[Action] = \
        Command.session_manager.get_actions_with_unavailable_champions()

        unavailable_champions: list[int] = [c.champion_id for c in actions]

        for pick in pick_queue_id:
            if pick not in unavailable_champions:
                return pick
        # with open(self.FILENAME, "r") as pick_priority_data:
        #     pick_queue = json.load(pick_priority_data)["picks"]

        #     champs = ChampNameIdMapper.get_champion_dict(order='normal')
        #     pick_queue: list[int] = [int(champs[pick]) for pick in pick_queue]
            
        
        # actions: list[Action] = \
        # Command.session_manager.get_actions_with_unavailable_champions()

        # unavailable_champions: list[int] = [c.champion_id for c in actions]

        # for pick in pick_queue:
        #     if pick not in unavailable_champions:
        #         return pick


class PreGameState(State):
    def next(self) -> None:
        champion_id: int = 0

        # bug is here

        # If this won't work try to get picked champion from action
        champion_id: int = Command.session_manager.get_me_as_teammember().champion_id
        champs: dict = ChampNameIdMapper.get_champion_dict(order='reversed')
        champion: str = champs[str(champion_id)]
        # bug is here

        print('before sending runes')
        send_most_optimal_runes_for(champion)
        print('after sending runes')
        send_user_defined_summoner_spells()

        self._context.change_state(LobbyState())
        
    def cancel(self) -> None:
        pass

    async def _scan(self) -> None:
        print(" >>>>>>>>>>>>UR IN PRE GAME STATE<<<<<<<<<<<<<< ")
        await asyncio.sleep(3)
        self.next()
