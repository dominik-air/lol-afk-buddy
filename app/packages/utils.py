from wmi import WMI

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class LOLClientStatusInformer(metaclass=SingletonMeta):
    PROCESS_NAME = "LeagueClient.exe"

    def __init__(self):
        self._is_running, self._pid = None, None

    def _update_processes(self):
        WMI_obj = WMI()
        self._processes = WMI_obj.Win32_Process(name=self.PROCESS_NAME)
    
    def _update_is_running(self):
        self._is_running = len(self._processes)
    
    def _update_pid(self):
        self._pid = self._processes[0].ProcessId
    
    # Client's methods
    def is_running(self):
        self._update_processes()
        self._update_is_running()
        print(f'updating [{self._is_running}]')
        return self._is_running
    
    def get_pid(self):
        if self.is_running():
            self._update_pid()
        else:
            self._pid = None

        return self._pid