from enum import Enum, auto
from kivy.app import App
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Line, Color
from os import listdir
from os.path import isfile, join
from abc import ABC, abstractmethod
from typing import List, Union

# defines type hints and constants
RGBA = List[float]
BAN_COLOR = [1, 0, 0, 1]
PICK_COLOR = [0.2, 0.6, 1, 1]
SELECT_COLOR = [1, 0.875, 0, 1]
DEFAULT_COLOR = [0.5, 0.5, 0.5, 1]

# loads the images' names into a list
images_path = "../img/champion_images/"
images = [f for f in listdir(images_path) if isfile(join(images_path, f))]


# POSSIBLE REWORK: the implementation part of the bridge design pattern im using may be moved into another module
class ChampionAction(ABC):
    """Abstraction base class for various actions that can be performed with champions in champion select.
    It's supposed to be the implementation part of the bridge design pattern.
    """

    @abstractmethod
    def action(self, champion_name: str, is_active: bool):
        pass


class BanChampion(ChampionAction):
    """This class should provide the champion banning functionality. It's a dummy class for now."""

    def action(self, champion_name: str, is_active: bool):
        if is_active:
            print(f"{champion_name} banned!")
        else:
            print(f"{champion_name} unbanned!")


class PickChampion(ChampionAction):
    """This class should provide the champion selection functionality. It's a dummy class for now."""

    def action(self, champion_name: str, is_active: bool):
        if is_active:
            print(f"{champion_name} picked!")
        else:
            print(f"{champion_name} unpicked!")


class ChampionStates(Enum):
    INERT = auto()
    BAN = auto()
    PICK = auto()


class ChampionButton(Button):
    """Creates champions as buttons with an additional outline border."""

    border_color = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.border_color: RGBA = DEFAULT_COLOR
        self.champion_state = ChampionStates.INERT

    def recolor(self):
        color_mapping = {
            ChampionStates.INERT: DEFAULT_COLOR,
            ChampionStates.BAN: BAN_COLOR,
            ChampionStates.PICK: PICK_COLOR,
        }
        self.border_color = color_mapping[self.champion_state]


class SearchBar(TextInput):
    """Search bar for the ChampionSelect class."""

    def clear(self):
        self.text = ""


class ChampionArray(BoxLayout):
    """A BoxLayout child class used as a container for champions selected by the user."""

    champions = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.champions: List[ChampionButton] = []
        self._create_blank_array()

    def _create_blank_array(self, cols: int = 5):
        """Creates a row of champion placeholders.

        Args:
            cols: number of columns in the row array.

        """
        for dummy_label in ["Dummy"] * cols:
            self.add_widget(Label(text=dummy_label))

    def _create_array_buttons(self):
        for champion in self.champions:
            self.add_widget(Image(source=images_path + champion.text + ".png"))

    def add_champion(self, new_champion: ChampionButton):
        """Adds a champion into the array by replacing the first from left champion placeholder.

        Args:
            new_champion: input champion that is going to be added to the array.

        """
        self.clear_widgets()
        self.champions.append(new_champion)
        self._create_array_buttons()
        self._create_blank_array(cols=5 - len(self.champions))

    def remove_champion(self, champion: ChampionButton):
        """Removes the input champion from the array by replacing it with a champion placeholder and shifts the
        remaining champions in the array to the left if necessary.

         Args:
                champion: input champion that is going to be removed from the array.
        """
        self.clear_widgets()
        self.champions.remove(champion)
        self._create_array_buttons()
        self._create_blank_array(cols=5 - len(self.champions))

    def clear(self):
        """Clears the array from all champions."""
        self.clear_widgets()
        for champion in self.champions:
            champion.champion_state = ChampionStates.INERT
            champion.recolor()
        self.champions = []
        self._create_blank_array()

    def contains(self, champion: ChampionButton) -> bool:
        """Checks if the array contains a given champion.

        Args:
            champion: the champion that its occurrence in the array is checked.

        Returns:
            True if the champion is in the array and False otherwise.

        """
        return champion in self.champions


class ChampionArrayHandler:
    """This class handles ChampionButtons' actions for a ChampionArray object.

    Attributes:
        champion_action: action that is performed on champions contained in the ChampionArray.
        champion_array: visual row array with a container for champions.
        state_type: the state ChampionButtons' states will be changed to if an action is performed.

    """

    def __init__(self, champion_action: ChampionAction, champion_array: ChampionArray):
        self.champion_action = champion_action
        self.champion_array = champion_array
        # FIXME: there's probably a more elegant way to determine the state_type
        self.state_type = ChampionStates.BAN if isinstance(champion_action, BanChampion) else ChampionStates.PICK

    def action(self, champion: ChampionButton) -> None:
        """Services the logic behind ChampionActions and ChampionArrays. If the provided champion has been
        serviced before then it reverts its state from active to inactive and removes it from an ChampionArray,
        otherwise it adds it into a ChampionArray and activates it.

        Args:
            champion: provided ChampionButton which will be serviced.

        """
        if champion.champion_state == self.state_type:
            champion.champion_state = ChampionStates.INERT
            champion.recolor()
            self.champion_array.remove_champion(champion)
            self.champion_action.action(champion.text, is_active=False)
        else:
            champion.champion_state = self.state_type
            champion.recolor()
            self.champion_array.add_champion(champion)
            self.champion_action.action(champion.text, is_active=True)


class ChampionSelect(StackLayout):
    """ChampionSelect interface with two fields indicating the current selected champion."""

    champion = ObjectProperty()
    champion_name = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.champion: ChampionButton = ChampionButton(text="Dummy")
        self.champion_name: str = "Dummy"

        self.available_champions: List[ChampionButton] = []

        # loop initializes ChampionButtons that will be worked on in this class and other parts of the app
        for image_name in images:
            champ = ChampionButton(
                text=image_name[:-4],  # removes the '.png' from the image_name
                font_size=0,
                size_hint=(None, None),
                size=(dp(42), dp(42)),  # can't make it bigger without stretching
                background_normal=images_path + image_name,
                background_down=images_path + image_name,
            )

            champ.bind(on_press=self._set_champion)
            self.available_champions.append(champ)
            self.add_widget(champ)

    def _set_champion(self, new_champion: ChampionButton) -> None:
        """Sets new values into the class fields champion and champion_name. For internal use only.

        Args:
            new_champion: ChampionButton that will replace old values.

        """
        self.champion.recolor()
        new_champion.border_color = SELECT_COLOR
        self.champion = new_champion
        self.champion_name = new_champion.text

    def update_list(self, text: str):
        """Updates the champion list based on the input text of the ChampionSelect SearchBar.

        Args:
            text: text inputted by the user into the search bar.

        """

        self.clear_widgets()
        if not text or text.lower() == "Search Bar".lower():
            # shows all champions if the searchbar is unused
            for champion in self.available_champions:
                self.add_widget(champion)
        # FIXME: might change it later
        # evil python level hacking
        elif found_champion := list(filter(lambda champ: champ.text.lower() == text.lower(), self.available_champions)):
            self._set_champion(*found_champion)
            self.add_widget(*found_champion)
        else:
            for champion in self.available_champions:
                if text in champion.text.lower():
                    self.add_widget(champion)


class ChampionSelectUI(BoxLayout):
    """ChampionSelect user interface that connects the banUI ChampionArrayHandler with pickUI ChampionArrayHandler."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        ban_array_label = Label(
            text="Ban Priority Queue",
            font_size=20,
            size_hint=(1, 0.25),
            color=BAN_COLOR,
        )
        pick_array_label = Label(
            text="Pick Priority Queue",
            font_size=20,
            size_hint=(1, 0.25),
            color=PICK_COLOR,
        )
        ban_array = ChampionArray()
        pick_array = ChampionArray()

        self.add_widget(ban_array_label)
        self.add_widget(ban_array)
        self.add_widget(pick_array_label)
        self.add_widget(pick_array)

        self.banUI = ChampionArrayHandler(
            champion_action=BanChampion(), champion_array=ban_array
        )
        self.pickUI = ChampionArrayHandler(
            champion_action=PickChampion(), champion_array=pick_array
        )

    def ban_champion(self, champion):
        if self.pickUI.champion_array.contains(champion):
            # if the champion is already picked but we want to ban it we need to unpick it
            self.pickUI.action(champion)
        self.banUI.action(champion)

    def pick_champion(self, champion):
        if self.banUI.champion_array.contains(champion):
            # if the champion is already banned but we want to pick it we need to unban it
            self.banUI.action(champion)
        self.pickUI.action(champion)

    def clear_bans(self):
        self.banUI.champion_array.clear()
        print("bans array cleared")

    def clear_picks(self):
        self.pickUI.champion_array.clear()
        print("picks array cleared")


class ChampionSelectInterface(BoxLayout):
    """The main interface used by the .kv file."""

    pass


class ChampionApp(App):
    def build(self):
        root_widget = ChampionSelectInterface()
        return root_widget


if __name__ == "__main__":
    ChampionApp().run()
