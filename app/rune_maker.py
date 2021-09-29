#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
from typing import Optional, List
from packages.utils import path_problem_solver
from command import EndpointSender, EndpointSaver

with open(path_problem_solver("data") + "\\" + "op_gg_rune_name_mapping.json", "r") as f:
    PROBLEMATIC_NAMES = json.load(f)


def _prepare_name(rune_name: str, prefix: Optional[str], suffix: Optional[str]) -> str:
    """Normalizes the input rune's name into a format recognizable by other parts in the app.

    Args:
        rune_name: the unprocessed name of a rune.
        prefix: prefix to be removed from the rune's name.
        suffix: suffix to be removed from the rune's name.

    Returns:
        Processed name of a rune.

    """

    # this part handles exceptional naming conventions of u.gg
    if "Adaptive" in rune_name:
        suffix = " Force" + suffix
    # most common fix
    if prefix is not None:
        rune_name = rune_name[len(prefix):]
    if suffix is not None:
        rune_name = rune_name[:-(len(suffix))]
    if problematic_rune_name := PROBLEMATIC_NAMES.get(rune_name):
        return problematic_rune_name
    return rune_name


def _get_rune_id(rune_name: str, mapping: list) -> int:
    """Returns the id for a given rune's name. Based on a mapping from the LCU driver."""
    for rune in mapping:
        if rune[0] == rune_name:
            return rune[1]


def import_runes_for(champion_name: str, output_filename: str = "send_this_runes.json") -> List[int]:
    """Saves a list of rune ids to a JSON file under the provided output filename for a given champion.
    The runes are webscraped from op.gg. It isn't our intellectual property.
    
    Args:
        champion_name: name of the champion the runes are supposed to be created.
        output_filename: name of the rune's save file. By default it lands in the data folder.
    
    """

    lower_case_champion_name = champion_name.lower()

    if lower_case_champion_name == "monkeyking":
        # RIOT calls Wukong 'Monkey King' so we need to change that here
        lower_case_champion_name = "wukong"

    webpage = f"https://u.gg/lol/champions/{lower_case_champion_name}/runes"  # source website
    result = requests.get(webpage)

    if result.status_code == 200:
        soup = BeautifulSoup(result.content, "html.parser")
    else:
        raise ValueError("The website didn't respond as expected.")

    # get and prepare the keystone perk
    keystone_perk_active = soup.find("div", class_="perk keystone perk-active").find("img")["alt"]
    prefix_to_remove = "The Keystone "
    suffix_to_remove = None
    keystone_perk_active = _prepare_name(keystone_perk_active, prefix_to_remove, suffix_to_remove)

    # get and prepare other perks
    other_active_perks = soup.find_all("div", class_="perk perk-active")
    perks = [div.find("img")["alt"] for div in other_active_perks][:5]  # there are 5 perks besides the keystone perk
    prefix_to_remove = "The Rune "
    suffix_to_remove = None
    perks = [_prepare_name(perk, prefix_to_remove, suffix_to_remove) for perk in perks]

    # get and prepare shards
    active_shards = soup.find_all("div", "shard shard-active")
    shards = [div.find("img")["alt"] for div in active_shards][:3]  # there are 3 shards
    prefix_to_remove = "The "
    suffix_to_remove = " Shard"
    shards = [_prepare_name(shard, prefix_to_remove, suffix_to_remove) for shard in shards]

    # open file with [rune_name, rune_id] mapping
    with open(path_problem_solver("data") + "//" + "rune_data.json", "r") as rune_id_data:
        rune_data = json.load(rune_id_data)

    all_runes = [keystone_perk_active, *perks, *shards]
    rune_ids = [_get_rune_id(rune_name, rune_data) for rune_name in all_runes]

    with open(output_filename, "w+") as rune_ids_to_send:
        json.dump(rune_ids, rune_ids_to_send, indent=4)

    return rune_ids


def send_most_optimal_runes_for(champion: str) -> None:
    """Function scrapes the best runes from u.gg for a provided champion and posts it to the LCU. In case of no
    place for another rune page the first fetched rune page will be deleted and in its place the new one is added.
    """

    runes = import_runes_for(champion_name=champion)

    # empirically tested formulas for style ids
    primary_style_id = (runes[0] // 100) * 100
    sub_style_id = (runes[4] // 100) * 100

    add_new_rune_page_command = EndpointSender(request=f"/lol-perks/v1/pages",
                                               request_type="post",
                                               request_data={
                                                   'autoModifiedSelections': [],
                                                   "current": True,
                                                   "isActive": False,
                                                   "isDeletable": True,
                                                   "isEditable": True,
                                                   "isValid": True,
                                                   "name": f"Best Win Rate {champion}",
                                                   'primaryStyleId': primary_style_id,
                                                   "selectedPerkIds": runes,
                                                   "subStyleId": sub_style_id
                                               })
    was_the_page_added = add_new_rune_page_command.execute().result()

    # in case that we cannot add another rune page(most likely there is no space for another one)
    if not was_the_page_added:
        rune_pages_info_command = EndpointSaver(reqs="/lol-perks/v1/pages",
                                                filename="users_rune_pages")
        rune_pages_info_command.execute()

        with open(path_problem_solver('JSONFiles') + "\\" + "users_rune_pages.json", "r") as rune_info_file:
            rune_pages_data = json.load(rune_info_file)
        # take the first rune page and delete it
        delete_rune_page_id = rune_pages_data[0]["id"]
        delete_page_command = EndpointSender(request=f"/lol-perks/v1/pages/{delete_rune_page_id}",
                                             request_type="delete")
        delete_page_command.execute()
        # now we can try again and add the rune page for the requested champion
        add_new_rune_page_command.execute()

