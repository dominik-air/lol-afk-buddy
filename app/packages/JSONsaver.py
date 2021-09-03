import json
import os
from datetime import datetime as dtime


class JSONSaver:
    counter = 0

    def __init__(self) -> None:
        self.path = os.path.join(os.path.dirname(__file__),
                                 '..', '..', 'JSONfiles')
    
    def save(self, what,
             filename: str = None,
             type: str = None) -> str:
        '''This method create appropirate directory and files
        then stores indicated json files to them.'''

        # Generate a name for the file if provided filename is empty
        if not filename:
            date = dtime.now().strftime(r'%m.%d_%H-%M')
            filename = f'{type if type else ""}File-{JSONSaver.counter}_{date}'
        filename += '.json' # Add extension

        file_path = os.path.join(self.path, filename)

        # Create directories if needed
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        # Save json to the file
        try:
            with open(file_path, 'w') as file:
                json.dump(what, file, indent=4)
            
            print('[OK]', 'File saved', sep=' ')

        except FileNotFoundError:
            print('[ERR]', 'Fiel not found', sep=' ')

        except Exception as e:
            print('[ERR]', 'An exception occured', sep=' ')
            print(e)
            print(e.with_traceback)
        
        # increase counter - used by auto-generated names
        JSONSaver.counter += 1

        # return full and eventual name of the file
        return filename
