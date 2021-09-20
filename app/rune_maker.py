#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
from typing import Optional, List
from packages.utils import path_problem_solver
from command import EndpointSender


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
    # FIXME: more research is needed
    if "Adaptive" in rune_name:
        suffix = " Force" + suffix
    # most common fix
    if prefix is not None:
        rune_name = rune_name[len(prefix):]
    if suffix is not None:
        rune_name = rune_name[:-(len(suffix))]
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

    runes = {"keystone": keystone_perk_active,
             "main_tree_perks": perks[:3],
             "secondary_tree_perks": perks[3:],
             "shards": shards}

    # open file with [rune_name, rune_id] mapping
    with open(path_problem_solver("data") + "//" + "rune_data.json", "r") as rune_id_data:
        rune_data = json.load(rune_id_data)

    all_runes = [keystone_perk_active, *perks, *shards]

    # FIXME: it's for testing purposes only, after every rune name is checked there will be no need to keep this
    with open(path_problem_solver("data") + "//" + "runes.json", "w+") as save_file:
        json.dump(runes, save_file, indent=4)

    rune_ids = [_get_rune_id(rune_name, rune_data) for rune_name in all_runes]

    with open(output_filename, "w+") as rune_ids_to_send:
        json.dump(rune_ids, rune_ids_to_send, indent=4)

    return rune_ids


def send_most_optimal_runes_for(champion: str) -> None:
    """Function fetches the best runes from u.gg for a provided champion and outputs it in a JSON file.
    Returns list of ids for every perk(rune), which then can be send to the LCU to update a rune page.
    """
    runes = import_runes_for(champion_name=champion)

    primary_style_id = (runes[0] // 100) * 100
    sub_style_id = (runes[4] // 100) * 100

    command = EndpointSender(request=f"/lol-perks/v1/pages",
                             request_type="post",
                             request_data={
                                 'autoModifiedSelections': [],
                                 "current": True,
                                 "id": 94698869,
                                 "isActive": False,
                                 "isDeletable": True,
                                 "isEditable": True,
                                 "isValid": True,
                                 'lastModified': 1629808281841,
                                 "name": f"Most Optimal {champion}",
                                 "order": 1,
                                 'primaryStyleId': primary_style_id,
                                 "selectedPerkIds": runes,
                                 "subStyleId": sub_style_id
                             })
    print('was the request successful?', command.execute())
