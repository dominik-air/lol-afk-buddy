# -*- coding: utf-8 -*-
"""This module is responsible for managing user input regarding summoner spells and rune pages.
It also allows to send it directly to the LCU.

Attributes:
    ICONS_PATH (str): absolute path to summoner spell icons(images).
    CHAMPION_PERKS_SETTINGS_PATH (str): absolute path to summoner spells and rune pages config file.
    LOADED_SUMMONER_SPELLS (Optional[List[str]]): names of summoner spells chosen by the user.
    LOADED_RUNES (Optional[List[str]]): name of the rune page chosen by the user.
    ICON_NAMES (List[str]): icon names derived from filenames by removing the last 4 chars('.png').

"""

import os
import json
from typing import List, Tuple
from kivy.properties import StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from packages.utils import path_problem_solver
from command import EndpointSender


import champion_select_utils

ICONS_PATH = path_problem_solver("img", "summoner_spells_icons")

CHAMPION_PERKS_SETTINGS_PATH = path_problem_solver("data") + "\\" + "champion_select_perks.json"
# loads saved data about in app champion select
with open(CHAMPION_PERKS_SETTINGS_PATH, "r") as settings_file:
    try:
        settings = json.load(settings_file)
    except json.JSONDecodeError:
        settings = {"summoner_spells": None, "runes": None}
    finally:
        LOADED_SUMMONER_SPELLS, LOADED_RUNES = settings.values()


def import_rune_pages() -> List[str]:
    rune_pages = champion_select_utils.get_user_rune_pages()
    return [rune_pages[0] for rune_pages in rune_pages]


def import_summoner_spell_icons() -> List[str]:
    # FIXME it should check for summoner spell availability
    return [
        f[:-4] for f in os.listdir(ICONS_PATH) if os.path.isfile(os.path.join(ICONS_PATH, f))
    ]


ICON_NAMES = import_summoner_spell_icons()


class SummonerSpellDropDown(DropDown):
    """Summoner spell dropdown class.

    Attributes:
        default_summoner_spell: the summoner spell the dropdown is initialized with.
        reassign_function: summoner spell change function.

    """

    # /lol-collections/v1/inventories/{summonerId}/spells - might be helpful to check for summoner spell availability

    _current_summoner_spell = StringProperty()

    def __init__(
            self, default_summoner_spell: str, reassign_function: callable, **kwargs
    ):
        super().__init__(**kwargs)

        # creates an option in the dropdown for every available summoner spell
        for icon_name in ICON_NAMES:
            btn = Button(
                text=icon_name,
                font_size=0,
                background_normal=os.path.join(ICONS_PATH, icon_name + ".png"),
                background_down=os.path.join(ICONS_PATH, icon_name + ".png"),
                size_hint_y=None,
                height=60,
            )

            btn.bind(on_release=lambda btn: self.select(btn))

            self.add_widget(btn)

        # the select button in the dropdown
        self.main_button = Button(
            background_normal=os.path.join(ICONS_PATH, default_summoner_spell + ".png"),
            background_down=os.path.join(ICONS_PATH, default_summoner_spell + ".png"),
            size_hint=(None, None),
        )

        self.main_button.bind(on_release=self.open)
        self._current_summoner_spell = default_summoner_spell
        self.bind(on_select=reassign_function)

    @property
    def current_summoner_spell(self) -> str:
        return self._current_summoner_spell

    @current_summoner_spell.setter
    def current_summoner_spell(self, summoner_spell: str):
        self._current_summoner_spell = summoner_spell


class RunesDropDown(DropDown):
    """Runes list dropdown class."""

    _rune_pages = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._rune_pages = ["afk", "zed", "kekw"]
        self.runes_already_loaded = False

        # creates an option in the dropdown for every available rune page
        self._display_rune_pages()

        self.main_button = Button(
            text="Best Win Rate Runes",
            size_hint=(2, None),
        )

        self.main_button.bind(on_press=self._main_button_func)
        self.main_button.bind(on_release=self.open)
        self.bind(on_select=lambda instance, x: setattr(self.main_button, "text", x))

    @property
    def rune_pages(self) -> List[str]:
        return self._rune_page

    @rune_pages.setter
    def rune_pages(self, rune_pages: List[str]):
        self._rune_pages = rune_pages

    def get_selected_rune_page(self) -> str:
        """Returns the selected rune page's name."""
        return self.main_button.text

    def set_selected_rune_page(self, rune_page_name: str) -> None:
        self.main_button.text = rune_page_name

    def _display_rune_pages(self) -> None:
        self.clear_widgets()
        for rune_page in self._rune_pages:
            btn = Button(text=rune_page, size_hint_y=None, height=44)

            btn.bind(on_release=lambda btn: self.select(btn.text))

            self.add_widget(btn)

    def _main_button_func(self, instance, x) -> None:
        if not self.runes_already_loaded:
            rune_pages = champion_select_utils.get_user_rune_pages()
            self._rune_pages = [rune_page[0] for rune_page in rune_pages]
            self._display_rune_pages()
            self.runes_already_loaded = True


class SummonerPerksSlotUI(BoxLayout):
    """The interface class for selecting summoner spells and rune pages. Supposed to be called from the .kv file."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        d_key_summoner, f_key_summoner = LOADED_SUMMONER_SPELLS

        self.d_key_summoner_spell = SummonerSpellDropDown(
            default_summoner_spell=d_key_summoner,
            reassign_function=self.reassign_summoner_spells_icons,
        )
        self.f_key_summoner_spell = SummonerSpellDropDown(
            default_summoner_spell=f_key_summoner,
            reassign_function=self.reassign_summoner_spells_icons,
        )

        self.runes = RunesDropDown()

        self.add_widget(self.d_key_summoner_spell.main_button)
        self.add_widget(self.f_key_summoner_spell.main_button)
        self.add_widget(self.runes.main_button)

    def reassign_summoner_spells_icons(
            self, key: SummonerSpellDropDown, selected_button: Button
    ) -> None:
        """
        Changes the current summoner spell for the selected one. In case when the selected summoner spell is
        already the other key's current summoner spell it swaps them.

        Args:
            key: the dropdown in which the selected_button is located.
            selected_button: button(that represents a summoner spell) selected by the user.

        """

        other_key = (
            self.d_key_summoner_spell
            if key is self.f_key_summoner_spell
            else self.f_key_summoner_spell
        )

        if selected_button.text == other_key.current_summoner_spell:
            # swaps the summoner spells
            setattr(
                other_key.main_button,
                "background_normal",
                key.main_button.background_normal,
            )
            setattr(
                other_key.main_button,
                "background_down",
                key.main_button.background_down,
            )
            other_key.current_summoner_spell = key.current_summoner_spell

        setattr(key.main_button, "background_normal", selected_button.background_normal)
        setattr(key.main_button, "background_down", selected_button.background_down)
        key.current_summoner_spell = selected_button.text

        # saves the changes to the settings file after a change in summoner spells
        self._save_current_settings()

    def get_selected_summoner_spells(self) -> Tuple[str, str]:
        """Returns the selected summoner spells in the D-key, F-key order."""
        return (
            self.d_key_summoner_spell.current_summoner_spell,
            self.f_key_summoner_spell.current_summoner_spell,
        )

    def get_selected_rune_page(self) -> str:
        """Returns the selected rune page."""
        return self.runes.get_selected_rune_page()

    def _save_current_settings(self) -> None:
        """Macro for saving the current settings regarding summoner spells and runes to a JSON file."""
        current_settings = {"summoner_spells": self.get_selected_summoner_spells(),
                            "selected_runes": self.get_selected_rune_page()}
        champion_select_utils.save_settings(filepath=CHAMPION_PERKS_SETTINGS_PATH, settings=current_settings)


def send_user_defined_summoner_spells() -> None:
    """Sends summoner spells selected by the user to the LCU."""

    with open(path_problem_solver("data") + "\\" + "champion_select_perks.json") as perks_file:
        summoner_spell_data = json.load(perks_file)["summoner_spells"]

    with open(path_problem_solver("data") + "\\" + "summoner_spells.json") as id_mapping_file:
        id_name_data = json.load(id_mapping_file)
        id_name_mapper = {name: id_ for (name, id_) in id_name_data}

    d_spell_name, f_spell_name = summoner_spell_data
    d_spell_id = id_name_mapper[d_spell_name]
    f_spell_id = id_name_mapper[f_spell_name]

    request_data = {
        "spell1Id": int(d_spell_id),
        "spell2Id": int(f_spell_id)
    }

    update_summoner_spells_command = EndpointSender(request="/lol-champ-select/v1/session/my-selection",
                                                    request_type="patch",
                                                    request_data=request_data)
    update_summoner_spells_command.execute()
