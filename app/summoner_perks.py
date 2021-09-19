import os
from typing import List, Tuple
from kivy.properties import StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from packages.utils import path_problem_solver

import champion_select_utils

icons_path = path_problem_solver("img", "summoner_spells_icons")


def import_rune_pages() -> List[str]:
    # FIXME placeholder function
    return [f"rune page {i}" for i in range(5)]


def import_summoner_spell_icons() -> List[str]:
    # FIXME it should check for summoner spell availability
    return [
        f for f in os.listdir(icons_path) if os.path.isfile(os.path.join(icons_path, f))
    ]


rune_pages = import_rune_pages()
icons = import_summoner_spell_icons()


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
        for icon in icons:
            btn = Button(
                text=icon[:-4],  # removes '.png'
                font_size=0,
                background_normal=os.path.join(icons_path, icon),
                background_down=os.path.join(icons_path, icon),
                size_hint_y=None,
                height=60,
            )

            btn.bind(on_release=lambda btn: self.select(btn))

            self.add_widget(btn)

        # the select button in the dropdown
        self.main_button = Button(
            background_normal=os.path.join(icons_path, default_summoner_spell),
            background_down=os.path.join(icons_path, default_summoner_spell),
            size_hint=(None, None),
        )

        self.main_button.bind(on_release=self.open)
        self._current_summoner_spell = default_summoner_spell[:-4]  # removes '.png'
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

        self._rune_pages = import_rune_pages()

        # creates an option in the dropdown for every available rune page
        for rune_page in self._rune_pages:
            btn = Button(text=rune_page, size_hint_y=None, height=44)

            btn.bind(on_release=lambda btn: self.select(btn.text))

            self.add_widget(btn)

        self.main_button = Button(
            text="Rune pages",
            size_hint=(2, None),
        )

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


class SummonerPerksSlotUI(BoxLayout):
    """The interface class for selecting summoner spells and rune pages. Supposed to be called from the .kv file."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.d_key_summoner_spell = SummonerSpellDropDown(
            default_summoner_spell=icons[0],
            reassign_function=self.reassign_summoner_spells_icons,
        )
        self.f_key_summoner_spell = SummonerSpellDropDown(
            default_summoner_spell=icons[1],
            reassign_function=self.reassign_summoner_spells_icons,
        )

        self.runes = RunesDropDown()

        self.add_widget(self.d_key_summoner_spell.main_button)
        self.add_widget(self.f_key_summoner_spell.main_button)
        self.add_widget(self.runes.main_button)

    def reassign_summoner_spells_icons(
        self, key: SummonerSpellDropDown, selected_button: Button
    ):
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

    def get_selected_summoner_spells(self) -> Tuple[str, str]:
        """Returns the selected summoner spells in the D-key, F-key order."""
        return (
            self.d_key_summoner_spell.current_summoner_spell,
            self.f_key_summoner_spell.current_summoner_spell,
        )

    def get_selected_rune_page(self) -> str:
        """Returns the selected rune page."""
        return self.runes.get_selected_rune_page()
