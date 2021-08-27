from command import *
import threading

class LauncherCommand:
    '''Defines what function match witch command.'''

    def __init__(self):
        self.command: Command = None
    
    def set_command(self, command: Command):
        if isinstance(command, Command):
            self.command = command

    def execute_command(self):
        try:
            self.command.execute()
        
        except Exception as e:
            print(Command.ERR_S, e, sep=' ')
    

    def find_match(self):
        self.set_command(MatchFinder())
        self.execute_command()



class ConsoleController:
    '''This class is to provide method which starts ifinite loop
    which reads input from the user and runs relevant method of
    LaucherCommand class instance.'''

    def __init__(self):
        self.command: LauncherCommand = LauncherCommand()

    def start(self):
        while True:
            _input = input('$>')

            if _input == 'exit':
                break
            
            if _input == 'findmatch':
                self.command.find_match()


# old code, not relevant
if __name__ == '__main__':

    import time
    cc = ConsoleController()
    t = threading.Thread(target=cc.start)
    t.daemon = True
    t.start()

    for i in range(10):
        time.sleep(.4)
        print(f'counter: {i}')
