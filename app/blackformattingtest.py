class Dupa:
    def __init__(self) -> None:
        def foo():
            if True:
                if not self_declined:
                    print(
                        Command.INFO_S, "transition to next state"
                    ) if self.verbose else None
                    self.next()

                else:
                    print(
                        Command.INFO_S, "self declination detected"
                    ) if self.verbose else None
                    LobbyState.initialized = False
