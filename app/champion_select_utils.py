# -*- coding: utf-8 -*-
"""This module contains useful functions that allow to easily download champions, summoner spell and rune page
data from the LCU.
"""

import json
from typing import List, Tuple
from packages.utils import path_problem_solver
from command import EndpointSaver

saved_to_json = None


def get_summoner_id(output_filename="users_summoner_id") -> str:
    """Function returns the user's summoner id."""

    command = EndpointSaver(
        reqs="/lol-summoner/v1/current-summoner", filename=output_filename
    )
    command.execute()

    with open(
        path_problem_solver("JSONfiles") + "\\" + output_filename + ".json", "r"
    ) as file:
        summoner_data = json.load(file)

    return summoner_data["summonerId"]


def get_available_champions(output_filename="users_champions") -> List[str]:
    """Function gets the user's available champions' names through the LCU and returns them as a list of strings."""

    command = EndpointSaver(
        reqs="/lol-champions/v1/owned-champions-minimal", filename=output_filename
    )
    command.execute()

    with open(
        path_problem_solver("JSONfiles") + "\\" + output_filename + ".json", "r"
    ) as file:
        summoner_champions = json.load(file)

    return [champ_data["alias"].lower() for champ_data in summoner_champions]


def get_available_summoner_spells(output_filename="users_summoner_spells") -> List[str]:
    """Function returns summoner spells owned by the user in case his account is under level 9 at which all summoner
    spells are available. It might be more more optimal to check the account's level beforehand.

    """

    summoner_id = get_summoner_id()
    command = EndpointSaver(
        reqs=f"/lol-collections/v1/inventories/{summoner_id}/spells",
        filename=output_filename,
    )
    command.execute()

    with open(
        path_problem_solver("JSONfiles") + "\\" + output_filename + ".json", "r"
    ) as file:
        summoner_spells_data = json.load(file)

    spell_ids = summoner_spells_data["spells"]

    with open(
        path_problem_solver("data") + "\\" + "summoner_spells.json", "r+"
    ) as spells_file:
        spells = json.load(spells_file)

    return [spell for spell, id in spells if id in spell_ids]


def get_user_rune_pages(output_filename="users_rune_pages") -> List[Tuple[str, int]]:
    """Functions fetches user's rune pages and saves them in a format of a list of tuples, where each tuple
    consists of the rune page's name and the rune page's id.
    """

    command = EndpointSaver(
        reqs="/lol-perks/v1/pages", filename=output_filename
    )
    command.execute()

    with open(
        path_problem_solver("JSONfiles") + "\\" + output_filename + ".json", "r"
    ) as file:
        rune_pages = json.load(file)

    return [(rune_page["name"], rune_page["id"]) for rune_page in rune_pages]


def save_settings(filepath: str, settings: dict) -> saved_to_json:
    """Saves provided settings to a JSON file, which filepath is also given in the arguments."""

    with open(filepath, "w") as save_file:
        json.dump(settings, save_file, indent=4)
