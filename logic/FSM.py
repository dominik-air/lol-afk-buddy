from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum, auto


class Context:
    """
    The Context defines the interface of interest to clients. It also maintains
    a reference to an instance of a State subclass, which represents the current
    state of the Context.
    """

    _state = None
    """
    A reference to the current state of the Context.
    """

    def __init__(self, state: State) -> None:
        self.transition_to(state)

    def transition_to(self, state: State) -> None:
        """
        The Context allows changing the State object at runtime.
        """

        print(f"Context: Transition to {type(state).__name__}")
        self._state = state
        self._state.context = self
        self.send_state_request()

    """
    The Context delegates part of its behavior to the current State object.
    """

    def previous_state(self) -> None:
        self._state.previous()

    def next_state(self) -> None:
        self._state.next()

    def send_state_request(self) -> None:
        self._state.request()


class StateTrigger(Enum):
    QueueStarted = auto()
    QueueAborted = auto()
    GameFound = auto()
    GameDeclinedPremade = auto()
    GameDeclinedNonPremade = auto()
    GameAccepted = auto()
    PremadeDodge = auto()
    NonPremadeDodge = auto()
    ChampionDeclared = auto()
    ChampionBanned = auto()
    ChampionPicked = auto()


class State(ABC):
    """
    The base State class declares methods that all Concrete State should
    implement and also provides a backreference to the Context object,
    associated with the State. This backreference can be used by States to
    transition the Context to another State.
    """

    _context = None
    _previous_state_triggers = None
    _next_state_triggers = None

    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context

    @abstractmethod
    def previous(self, *args) -> None:
        pass

    @abstractmethod
    def next(self, *args) -> None:
        pass

    @abstractmethod
    def request(self) -> None:
        pass


"""
Concrete States implement various behaviors, associated with a state of the
Context.
"""


class LobbyState(State):

    _next_state_triggers = [StateTrigger.QueueStarted]

    def previous(self, *args):
        print("Can't go further back than LobbyState")

    def next(self, *args):
        print("Starting queue")
        self.context.transition_to(QueueState())

    def request(self):
        print("get", "is queue")


class QueueState(State):

    _previous_state_triggers = [StateTrigger.QueueAborted]
    _next_state_triggers = [StateTrigger.GameFound]

    def previous(self, *args):
        print("Aborting Queue")
        self.context.transition_to(LobbyState())

    def next(self, *args):
        print("Game Found!")
        self.context.transition_to(ReadyCheckState())

    def request(self):
        print("get", "queue info")


class ReadyCheckState(State):

    _previous_state_triggers = [
        StateTrigger.GameDeclinedPremade,
        StateTrigger.GameDeclinedNonPremade,
    ]
    _next_state_triggers = [StateTrigger.GameAccepted]

    def previous(
        self, decline_reason: StateTrigger = StateTrigger.GameDeclinedNonPremade, *args
    ):
        if decline_reason is StateTrigger.GameDeclinedNonPremade:
            print("Someone declined!")
            self.context.transition_to(QueueState())
        elif decline_reason is StateTrigger.GameDeclinedPremade:
            print("Game aborted!")
            self.context.transition_to(LobbyState())
        else:
            print("Unknown trigger")

    def next(self, *args):
        print("Game Accepted!")
        self.context.transition_to(ChampionSelectDeclareState())

    def request(self):
        print("put", "accept ready check")


class ChampionSelectDeclareState(State):

    _previous_state_triggers = [StateTrigger.NonPremadeDodge, StateTrigger.PremadeDodge]
    _next_state_triggers = [StateTrigger.ChampionDeclared]

    def previous(
        self, dodge_reason: StateTrigger = StateTrigger.NonPremadeDodge, *args
    ):
        if dodge_reason is StateTrigger.PremadeDodge:
            print("Premade Dodge")
            self.context.transition_to(LobbyState())
        elif dodge_reason is StateTrigger.NonPremadeDodge:
            print("Non premade dodge")
            self.context.transition_to(QueueState())
        else:
            print("Unknown trigger")

    def next(self, *args):
        print("Champion declared! Going to banning phase")
        self.context.transition_to(ChampionSelectBanState())

    def request(self):
        print("put", "declare champion specified by user")


class ChampionSelectBanState(State):

    _previous_state_triggers = [StateTrigger.NonPremadeDodge, StateTrigger.PremadeDodge]
    _next_state_triggers = [StateTrigger.ChampionBanned]

    def previous(
        self, dodge_reason: StateTrigger = StateTrigger.NonPremadeDodge, *args
    ):
        if dodge_reason is StateTrigger.PremadeDodge:
            print("Premade Dodge")
            self.context.transition_to(LobbyState())
        elif dodge_reason is StateTrigger.NonPremadeDodge:
            print("Non premade dodge")
            self.context.transition_to(QueueState())
        else:
            print("Unknown trigger")

    def next(self, *args):
        print("Champion banned! Going to picking phase")
        self.context.transition_to(ChampionSelectPickState())

    def request(self):
        print("get", "champion select available bans")
        print("put", "ban champion specified by user")


class ChampionSelectPickState(State):

    _previous_state_triggers = [StateTrigger.NonPremadeDodge, StateTrigger.PremadeDodge]
    _next_state_triggers = [StateTrigger.ChampionPicked]

    def previous(
        self, dodge_reason: StateTrigger = StateTrigger.NonPremadeDodge, *args
    ):
        if dodge_reason is StateTrigger.PremadeDodge:
            print("Premade Dodge")
            self.context.transition_to(LobbyState())
        elif dodge_reason is StateTrigger.NonPremadeDodge:
            print("Non premade dodge")
            self.context.transition_to(QueueState())
        else:
            print("Unknown trigger")

    def next(self, *args):
        print("Champion picked! The game is about to start!")
        self.context.transition_to(InGameState())

    def request(self):
        print("get", "champion select available picks")
        print("put", "pick champion specified by user")


class InGameState(State):
    def previous(self, *args):
        print("Game has already started! You can only go afk now")

    def next(self, *args):
        print("Game finished! Going back to lobby!")
        self.context.transition_to(LobbyState())

    def request(self):
        print("no need for requests")


if __name__ == "__main__":
    # The client code.
    # just for testing purposes as for now
    new_game = Context(LobbyState())
    print()
    while True:
        api_response = input(
            "'n' - next state,\n"
            "'p' - previous state,\n"
            "'r' - send request,\n"
            "input: "
        )
        if api_response == "n":
            new_game.next_state()
        elif api_response == "p":
            new_game.previous_state()
        elif api_response == "r":
            new_game.send_state_request()
        else:
            print("wrong api response")
            break
