from command import *
import threading

class LauncherCommand:
    def __init__(self):
        self.command: Command = None
        self.u_input: str = None
    
    def set_command(self, command: Command):
        if isinstance(command, Command):
            self.command = command

    def execute_command(self):
        if self.command:
            self.command.execute()
        
        else:
            print(Command.ERR_S,
                  'Command is not set.', sep=' ')


class ConsoleController:
    def __init__(self, receiver):
        self._input: str = None
        self.run: bool = True
        self.console: LauncherCommand = LauncherCommand()
        self.receiver = receiver
        self._loop = self.receiver.loop

    def start(self):
        while self.run:
            self._input = input('$>')

            if self._input == 'exit':
                self.run = False
            
            if self._input == 'findmatch':
                self.console.set_command(MatchFinder(receiver=self.receiver))
                self.console.execute_command()

    
    def stop(self):
        self.run = False
    
    def get_input(self):
        return self._input


import time
if __name__ == '__main__':

    cc = ConsoleController()
    t = threading.Thread(target=cc.start)
    t.daemon = True
    t.start()

    for i in range(10):
        time.sleep(.4)
        print(f'counter: {i}')

    # keyboard.send('enter')
    # cc.stop()
    # keyboard.send('enter')
    # t.join()


    # console = LauncherCommand()
    # console.set_command(Greet())
    # console.execute_command()
