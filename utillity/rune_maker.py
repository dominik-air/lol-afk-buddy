#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
from typing import Optional


def prepare_name(rune_name: str, prefix: Optional[str], suffix: Optional[str]) -> str:
    """Normalizes the input rune's name into a format recognizable by other parts in the app.py

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


def get_rune_id(rune_name: str, mapping) -> int:
    for rune in mapping:
        if rune[0] == rune_name:
            return rune[1]


lower_case_champion_name = 'rakan'
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
keystone_perk_active = prepare_name(keystone_perk_active, prefix_to_remove, suffix_to_remove)

# get and prepare other perks
other_active_perks = soup.find_all("div", class_="perk perk-active")
perks = [div.find("img")["alt"] for div in other_active_perks][:5]  # there are 5 perks besides the keystone perk
prefix_to_remove = "The Rune "
suffix_to_remove = None
perks = [prepare_name(perk, prefix_to_remove, suffix_to_remove) for perk in perks]

# get and prepare shards
active_shards = soup.find_all("div", "shard shard-active")
shards = [div.find("img")["alt"] for div in active_shards][:3]  # there are 3 shards
prefix_to_remove = "The "
suffix_to_remove = " Shard"
shards = [prepare_name(shard, prefix_to_remove, suffix_to_remove) for shard in shards]

runes = {"keystone": keystone_perk_active,
         "main_tree_perks": perks[:3],
         "secondary_tree_perks": perks[3:],
         "shards": shards}


with open("rune_data.json", "r") as rune_id_data:
    rune_data = json.load(rune_id_data)

all_runes = [keystone_perk_active, *perks, *shards]
rune_ids = [get_rune_id(rune_name, rune_data) for rune_name in all_runes]

with open("../data/runes.json", "w+") as save_file:
    json.dump(runes, save_file, indent=4)

with open("send_this_runes.json", "w+") as rune_ids_to_send:
    json.dump(rune_ids, rune_ids_to_send, indent=4)
