from command import *
import threading
import re
from enum import Enum, auto

# TODO: move CMDCode to another file and import it here
class CMDCode(Enum):
    EXT = auto()
    FIND_MATCH = auto()
    CANCEL = auto()
    ACCEPT = auto()
    DECLINE = auto()
    SAVE = auto()
    AL_BANS = auto()
    EN_BANS = auto()
    HOVER = auto()
    GET_HOVER = auto()
    AL_PICKS = auto()
    EN_PICKS = auto()
    MY_POS = auto()
    COMPLETE = auto()
    INIT_STATE = auto()
    DEINIT_STATE = auto()
    SEND_MESSAGES = auto()


class LauncherCommand:
    '''Defines what function match witch command.'''
    CMD = {
        CMDCode.EXT: ['exit'],
        CMDCode.FIND_MATCH: ['findmatch', 'fm'],
        CMDCode.CANCEL: ['cancel', 'c', 'd'],
        CMDCode.ACCEPT: ['accept', 'acc', 'ok'],
        CMDCode.DECLINE: ['decline', 'c', 'd'],
        CMDCode.SAVE: ['save', 's'],
        CMDCode.AL_BANS: ['getAllyBans', 'alb'],
        CMDCode.EN_BANS: ['getEnemyBans', 'enb'],
        CMDCode.HOVER: ['hover', 'h'],
        CMDCode.GET_HOVER: ['getHover', 'H'],
        CMDCode.AL_PICKS: ['getAllyPicks', 'gap'],
        CMDCode.EN_PICKS: ['getEnemyPicks', 'gep'],
        CMDCode.MY_POS: ['getMyPosition', 'gmp'],
        CMDCode.COMPLETE: ['complete', 'ok'],
        CMDCode.INIT_STATE: ['start', 'st', 'init'],
        CMDCode.DEINIT_STATE: ['stop', 'terminate', 'term', 'deinit'],
        CMDCode.SEND_MESSAGES: ['send', 'M', 'message']
    }
    user_accounts: Dict[str, str] = {}

    def __init__(self):
        self.command: Command = None

    @classmethod
    def set_command(cls, command: Command):
        if isinstance(command, Command):
            cls.command = command

    @classmethod
    def update_user_accounts(cls, new_account: Dict[str, str]):
        cls.user_accounts.update(new_account)

    @classmethod
    def execute_command(cls):
        try:
            cls.command.execute()
        
        except Exception as e:
            print(Command.ERR_S, e, sep=' ')

    @classmethod
    def find_match(cls):
        cls.set_command(MatchFinder())
        cls.execute_command()
    
    @classmethod
    def cancel(cls):
        cls.set_command(Canceller())
        cls.execute_command()

    @classmethod
    def accept(cls):
        cls.set_command(Acceptor())
        cls.execute_command()

    @classmethod
    def decline(cls):
        cls.set_command(Decliner())
        cls.execute_command()

    @classmethod
    def save_to_file(cls, what, filename):
        cls.set_command(
            WS_JSONSaver(
                spinner=what,
                textinput=filename
                )
            )

        cls.execute_command()

    @classmethod
    def get_ally_bans(cls):
        cls.set_command(AllyBansGetter())
        cls.execute_command()

    @classmethod
    def get_enemy_bans(cls):
        cls.set_command(EnemyBansGetter())
        cls.execute_command()

    @classmethod
    def hover(cls, arg):
        cls.set_command(Hover(champion=arg))
        cls.execute_command()

    @classmethod
    def get_hover(cls):
        cls.set_command(HoverGetter())
        cls.execute_command()

    @classmethod
    def get_my_team_champs(cls):
        cls.set_command(MyTeamChampsGetter())
        cls.execute_command()

    @classmethod
    def get_enemy_team_champs(cls):
        cls.set_command(EnemyTeamChampsGetter())
        cls.execute_command()

    @classmethod
    def get_my_position(cls):
        cls.set_command(MyPositionGetter())
        cls.execute_command()

    @classmethod
    def complete(cls):
        cls.set_command(Complete())
        cls.execute_command()

    @classmethod
    def init(cls):
        cls.set_command(InitState())
        cls.execute_command()
    
    @classmethod
    def deinit(cls):
        cls.set_command(DeinitState())
        cls.execute_command()

    @classmethod
    def default_action(cls):
        print(Command.INFO_S,
              'For this button an action has not been set yet.',
               sep=' ')

    @classmethod
    def send_messages(cls, event_type: str):
        # just for testing purposes
        cls.set_command(MessagesSender(user_accounts=cls.user_accounts, event_type=event_type))
        cls.execute_command()

    def start(self):
        regex = r'\w+'
        while True:
            _input = input('$>')
            matches = re.findall(regex, _input)
            _cmd = matches[0] # command string

            if _cmd in self.CMD[CMDCode.EXT]:
                break
            
            elif _cmd in self.CMD[CMDCode.FIND_MATCH]:
                LauncherCommand.find_match()
            
            elif _cmd in self.CMD[CMDCode.CANCEL]:
                LauncherCommand.cancel()

            elif _cmd in self.CMD[CMDCode.SAVE]:
                try:
                    LauncherCommand.save_to_file(what=matches[1],
                                                filename=matches[2])
                except IndexError:
                    print(Command.ERR_S, 'provide an argument')

            elif _cmd in self.CMD[CMDCode.AL_BANS]:
                LauncherCommand.get_ally_bans()

            elif _cmd in self.CMD[CMDCode.EN_BANS]:
                LauncherCommand.get_enemy_bans()

            elif _cmd in self.CMD[CMDCode.HOVER]:
                try:
                    LauncherCommand.hover(matches[1])
                except IndexError:
                    print(Command.ERR_S, 'provide an argument')

            elif _cmd in self.CMD[CMDCode.GET_HOVER]:
                LauncherCommand.get_hover()

            elif _cmd in self.CMD[CMDCode.AL_PICKS]:
                LauncherCommand.get_my_team_champs()

            elif _cmd in self.CMD[CMDCode.EN_PICKS]:
                LauncherCommand.get_enemy_team_champs()

            elif _cmd in self.CMD[CMDCode.MY_POS]:
                LauncherCommand.get_my_position()

            elif _cmd in self.CMD[CMDCode.COMPLETE]:
                LauncherCommand.complete()
            
            elif _cmd in self.CMD[CMDCode.INIT_STATE]:
                LauncherCommand.init()

            elif _cmd in self.CMD[CMDCode.DEINIT_STATE]:
                LauncherCommand.deinit()
            elif _cmd in self.CMD[CMDCode.SEND_MESSAGES]:
                try:
                    LauncherCommand.send_messages(matches[1])
                except IndexError:
                    print(Command.ERR_S, 'provide an argument')

            else:
                LauncherCommand.default_action()


# class ConsoleController:
#     '''This class is to provide method which starts ifinite loop
#     which reads input from the user and runs relevant method of
#     LaucherCommand class instance.'''

#     def __init__(self):
#         self.command: LauncherCommand = LauncherCommand()

#     def start(self):
#         while True:
#             _input = input('$>')

#             if _input == 'exit':
#                 break
            
#             if _input == 'findmatch':
#                 self.command.find_match()


# # old code, not relevant
# if __name__ == '__main__':

#     import time
#     cc = ConsoleController()
#     t = threading.Thread(target=cc.start)
#     t.daemon = True
#     t.start()

#     for i in range(10):
#         time.sleep(.4)
#         print(f'counter: {i}')
