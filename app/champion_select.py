import os
import json
from enum import Enum, auto
from typing import List, Union

from kivy.metrics import dp
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

import champion_select_utils
from packages.utils import path_problem_solver


# defines type hints and constants
RGBA = List[float]
BAN_COLOR = [1, 0, 0, 1]
PICK_COLOR = [0.2, 0.6, 1, 1]
SELECT_COLOR = [1, 0.875, 0, 1]
DEFAULT_COLOR = [0.5, 0.5, 0.5, 1]


IMAGES_PATH = path_problem_solver("img", "champion_images")
# loads the images' names into a list
images = [
    f for f in os.listdir(IMAGES_PATH) if os.path.isfile(os.path.join(IMAGES_PATH, f))
]

CHAMPION_SELECT_SETTINGS_PATH = path_problem_solver("data") + "\\" + "champion_select_picks_and_bans.json"
# loads saved data about in app champion select
with open(CHAMPION_SELECT_SETTINGS_PATH, "r") as settings_file:
    try:
        settings = json.load(settings_file)
    except json.JSONDecodeError:
        settings = {"picks": None, "bans": None}
    finally:
        LOADED_PICKS, LOADED_BANS = settings.values()


class ChampionStates(Enum):
    """Class determines the states a ChampionButton can be in."""

    INERT = auto()
    BAN = auto()
    PICK = auto()


class ChampionButton(Button):
    """Creates champions_data as buttons with an additional outline border."""

    border_color = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.border_color: RGBA = DEFAULT_COLOR
        self.champion_state: ChampionStates = ChampionStates.INERT
        self.is_selected: bool = False

    def recolor(self) -> None:
        """Changes the border color of the button according to the mapping provided below."""
        color_mapping = {
            ChampionStates.INERT: DEFAULT_COLOR,
            ChampionStates.BAN: BAN_COLOR,
            ChampionStates.PICK: PICK_COLOR,
        }
        self.border_color = color_mapping[self.champion_state]

        if self.is_selected:
            self.border_color = SELECT_COLOR

    def reset(self) -> None:
        """Resets the button to the default state."""
        self.champion_state = ChampionStates.INERT
        self.recolor()

    def select(self) -> None:
        """Sets the button as selected."""
        self.is_selected = True

    def deselect(self) -> None:
        """Sets the button as not selected."""
        self.is_selected = False


class SearchBar(TextInput):
    """Search bar for the ChampionSelect class."""

    def clear(self) -> None:
        self.text = ""


class ChampionArrayButton(ButtonBehavior, Image):
    """Class for the buttons in a ChampionArray."""

    def __init__(self, champion_name: str, **kwargs):
        super().__init__(**kwargs)
        self.champion_name = champion_name


class ChampionPlaceholder(Image):
    """Placeholder for ChampionButtons and ChampionArrayButtons."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = path_problem_solver("img", "buttons_images", "placeholder.png")
        self.name = "Dummy"


class ChampionSelect(StackLayout):
    """ChampionSelect interface with a field indicating the current selected champion."""

    champion = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.champion: Union[
            ChampionButton, ChampionPlaceholder
        ] = ChampionPlaceholder()

        self.available_champions: List[ChampionButton] = []

        # loop initializes ChampionButtons that will be worked on in this class and other parts of the app
        for image_name in images:
            champ = ChampionButton(
                text=image_name[:-4],  # removes the '.png' from the image_name
                font_size=0,
                size_hint=(None, None),
                size=(dp(80), dp(80)),
                background_normal=os.path.join(IMAGES_PATH, image_name),
                background_down=os.path.join(IMAGES_PATH, image_name),
            )

            champ.bind(on_press=self._set_champion)
            self.available_champions.append(champ)
            self.add_widget(champ)

    def _set_champion(
        self, new_champion: Union[ChampionButton, ChampionPlaceholder]
    ) -> None:
        """Sets new values into the class fields champion and champion_name. For internal use only.

        Args:
            new_champion: ChampionButton that will replace old values.

        """
        if not isinstance(self.champion, ChampionPlaceholder):
            self.champion.deselect()
            self.champion.recolor()
        if not isinstance(new_champion, ChampionPlaceholder):
            new_champion.select()
            new_champion.recolor()
        self.champion = new_champion

    def update_list(self, text: str) -> None:
        """Updates the champion list based on the input text of the ChampionSelect SearchBar.

        Args:
            text: text inputted by the user into the search bar.

        """

        self.clear_widgets()
        if not text or text.lower() == "Search Bar".lower():
            # shows all champions_data if the searchbar is unused or blank
            for champion in self.available_champions:
                self.add_widget(champion)
        # evil python level hacking
        elif found_champion := list(
            filter(
                lambda champ: champ.text.lower() == text.lower(),
                self.available_champions,
            )
        ):
            self._set_champion(*found_champion)
            self.add_widget(*found_champion)
        else:
            # show every available champion with name partly matching with the user input
            for champion in self.available_champions:
                if text.lower() in champion.text.lower():
                    self.add_widget(champion)


class ChampionArray(BoxLayout):
    """A BoxLayout child class used as a container for champions_data selected by the user.

    Attributes:
        champion_number_limit: integer defining the size on the row array.

    """

    champions = ListProperty()

    def __init__(self, champion_number_limit: int = 5, **kwargs):
        super().__init__(**kwargs)

        self.champion_number_limit = champion_number_limit
        self.champions: List[ChampionButton] = []
        self._create_blank_array()

    def _create_blank_array(self, cols: int = None) -> None:
        """Creates a row of champion placeholders.

        Args:
            cols: number of columns in the row array.

        """

        if cols is None:
            cols = self.champion_number_limit
        for i in range(cols):
            self.add_widget(ChampionPlaceholder())

    def _create_array_buttons(self) -> None:
        """Creates ChampionArrayButtons from the ChampionButtons in the champions_data class field."""

        for champion in self.champions:
            array_button = ChampionArrayButton(
                champion_name=champion.text,
                source=IMAGES_PATH + "\\" + champion.text + ".png",
            )
            array_button.bind(on_press=self.remove_champion)
            self.add_widget(array_button)

    def add_champion(self, new_champion: ChampionButton) -> None:
        """
        Adds a champion into the array by replacing the first from left placeholder. If the number of champions_data
        exceeds the champion number limit then the least priority champion is substituted with the new champion.

        Args:
            new_champion: input champion that is going to be added to the array.

        """

        if self.champion_number_limit > len(self.champions):
            self.champions.append(new_champion)
        else:
            # if the array is full replace the last champion with the new one
            self.champions[-1].reset()
            self.champions[-1] = new_champion

        self.clear_widgets()
        self._create_array_buttons()
        # fills the unused spaces with placeholders
        self._create_blank_array(cols=self.champion_number_limit - len(self.champions))

    def remove_champion(
        self, champion: Union[ChampionButton, ChampionArrayButton]
    ) -> None:
        """
        Removes the input champion from the array by replacing it with a champion placeholder and shifts the
        remaining champions_data in the array to the left if necessary.

         Args:
                champion: input champion that is going to be removed from the array.
        """

        if isinstance(champion, ChampionArrayButton):
            counterpart: ChampionButton = self._find_champion_button_counterpart(
                champion
            )
            counterpart.reset()
            champion = counterpart

        self.clear_widgets()
        self.champions.remove(champion)
        self._create_array_buttons()
        # fills the unused spaces with placeholders
        self._create_blank_array(cols=self.champion_number_limit - len(self.champions))

    def clear(self) -> None:
        """Clears the array from all champions_data."""

        self.clear_widgets()
        for champion in self.champions:
            champion.reset()
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

    def _find_champion_button_counterpart(
        self, array_button: ChampionArrayButton
    ) -> ChampionButton:
        """Searches for the ChampionButton counterpart of a ChampionArrayButton.

        Args:
            array_button: the ChampionArrayButton we want to find a ChampionButton counterpart for.

        Returns:
            ChampionButton. The method assumes that there is no need to check for the existence of such counterpart.
        """
        # fmt: off
        return list(filter(lambda champ: champ.text.lower() == array_button.champion_name.lower(), self.champions))[0]
        # fmt: on

    def export_champions(self) -> List[str]:
        """Exports the current champions_data in the array.

        Returns:
            List of champion names as strings.
        """
        return [champion.text for champion in self.champions]


class ChampionArrayHandler:
    """This class handles ChampionButtons' actions for a ChampionArray object.

    Attributes:
        champion_action: action that is performed on champions_data contained in the ChampionArray.
        champion_array: visual row array with a container for champions_data.

    """

    def __init__(self, champion_action: ChampionStates, champion_array: ChampionArray):
        self.champion_action = champion_action
        self.champion_array = champion_array

    def action(self, champion: ChampionButton) -> None:
        """
        Services the logic behind ChampionActions and ChampionArrays. If the provided champion has been
        serviced before then it reverts its state from active to inactive and removes it from an ChampionArray,
        otherwise it adds it into a ChampionArray and activates it.

        Args:
            champion: provided ChampionButton which will be serviced.

        """

        if champion.champion_state == self.champion_action:
            champion.reset()
            self.champion_array.remove_champion(champion)
        else:
            champion.champion_state = self.champion_action
            champion.recolor()
            self.champion_array.add_champion(champion)

    def export_array_champions(self) -> List[str]:
        return self.champion_array.export_champions()


class ChampionSelectUI(BoxLayout):
    """ChampionSelect user interface that connects the ban_handler with pick_handler."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings_already_loaded = False  # we don't need to load the settings more than once

        self.champion_select = ObjectProperty()

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

        self.ban_handler = ChampionArrayHandler(
            champion_action=ChampionStates.BAN, champion_array=ban_array
        )
        self.pick_handler = ChampionArrayHandler(
            champion_action=ChampionStates.PICK, champion_array=pick_array
        )

        self.champion_pool: List[str] = []

    def ban_champion(
        self, champion: Union[ChampionButton, ChampionPlaceholder]
    ) -> None:
        """
        Redirects the BanChampion action of the ban_handler. It also checks if a champion needs to be removed from the
        pickUI ChampionArray in case it contains this specific champion(a champion can't be a ban and a pick
        simultaneously).
        """

        if not isinstance(champion, ChampionButton):
            # if it's not a ChampionButton we should not touch it
            return

        if self.pick_handler.champion_array.contains(champion):
            # if the champion is already picked but we want to ban it we need to unpick it
            self.pick_handler.action(champion)
        self.ban_handler.action(champion)

    def pick_champion(
        self, champion: Union[ChampionButton, ChampionPlaceholder]
    ) -> None:
        """
        Redirects the PickChampion action of the pick_handler. It also checks if a champion needs to be removed from
        the ban_handler ChampionArray in case it contains this specific champion(a champion can't be a ban and a pick
        simultaneously).
        """

        if not isinstance(champion, ChampionButton):
            # if it's not a ChampionButton we should not touch it
            return

        if self.champion_pool is not None and champion.text not in self.champion_pool:
            popup = Popup(
                title="Champion selection error",
                content=Label(text=f"You don't have {champion.text}"),
                auto_dismiss=True,
                size_hint=(None, None),
                size=(300, 300),
            )
            popup.open()
            return

        if self.ban_handler.champion_array.contains(champion):
            # if the champion is already banned but we want to pick it we need to unban it
            self.ban_handler.action(champion)
        self.pick_handler.action(champion)

    def clear_bans(self) -> None:
        """Clears the ban_handler ChampionArray."""
        self.ban_handler.champion_array.clear()
        print("bans array cleared")

    def clear_picks(self) -> None:
        """Clears the pick_handler ChampionArray."""
        self.pick_handler.champion_array.clear()
        print("picks array cleared")

    def load_bans(self, bans: List[str]) -> None:
        """Loads bans from a list of champion names.

        Args:
            bans: list of champion names.

        """
        self.clear_bans()
        champion_bans = [champion for champion in self.champion_select.available_champions if champion.text in bans]
        for champion_ban in reversed(champion_bans):
            # banning champions in the reversed order to preserve their priority
            self.ban_champion(champion_ban)

    def load_picks(self, picks: List[str]) -> None:
        """Loads picks from a list of champion names.

        Args:
            picks: list of champion names.

        """
        self.clear_picks()
        champion_picks = [champion for champion in self.champion_select.available_champions if champion.text in picks]
        for champion_pick in reversed(champion_picks):
            # picking champions in the reversed order to preserve their priority
            self.pick_champion(champion_pick)

    def export_bans(self) -> List[str]:
        """Exports bans from the champion array.

        Returns:
            List of champion names as strings.

        """

        return self.ban_handler.export_array_champions()

    def export_picks(self) -> List[str]:
        """Exports pick from the champion array.

        Returns:
            List of champion names as strings.

        """

        return self.pick_handler.export_array_champions()

    def _restrict_champion_pool(self) -> None:
        """Restricts the ChampionSelect champion pool to champions owned by the user."""
        champion_pool = champion_select_utils.get_available_champions()

        if champion_pool is None:
            # in case of no connection with LCU
            return

        unowned_champions = [
            champion
            for champion in self.champion_select.available_champions
            if champion.text not in champion_pool
            and self.pick_handler.champion_array.contains(champion)
        ]
        for unowned_champion in unowned_champions:
            # calling this method on an selected champion clears the pick
            self.pick_champion(unowned_champion)
            unowned_champion.recolor()

        self.champion_pool = champion_pool

    def _load_default_settings(self) -> None:
        """Macro for calling all the methods responsible for loading saved champion select settings. It also restricts
         the champion pool. Meant to be called in the main .kv file.
        """

        if not self.settings_already_loaded:
            self._restrict_champion_pool()
            self.load_bans(LOADED_BANS)
            self.load_picks(LOADED_PICKS)

            self.settings_already_loaded = True

    def _save_current_settings(self) -> None:
        """Macro for saving current champion select settings. Meant to be called in the main .kv file."""

        current_settings = {"picks": self.export_picks(),
                            "bans": self.export_bans()}
        champion_select_utils.save_settings(filepath=CHAMPION_SELECT_SETTINGS_PATH, settings=current_settings)


class ChampionSelectInterface(BoxLayout):
    """The main interface used by the .kv file."""

    pass
