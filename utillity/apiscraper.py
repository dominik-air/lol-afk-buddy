import requests
import json


summoners_data = requests.get("http://ddragon.leagueoflegends.com/cdn/11.16.1/data/en_US/summoner.json").json()["data"]
champions_data = requests.get("http://ddragon.leagueoflegends.com/cdn/11.16.1/data/en_US/champion.json").json()["data"]

# get the summoner spells' names available on Summoner's Rift
summoner_spells = [spell for spell in summoners_data.keys() if "CLASSIC" in summoners_data[spell]["modes"]]
# save it in json
# FIXME: the file path needs a rework
with open("../data/summoners.json", "w+") as output:
    json.dump(summoner_spells, output, indent=4)
# get the summoners_data spells' icons
for summoner_spell in summoner_spells:
    icon = requests.get(f"http://ddragon.leagueoflegends.com/cdn/11.16.1/img/spell/{summoner_spell}.png")
    if icon.status_code == 200:
        # FIXME: the file path needs a rework
        with open(f"../img/summoner_spells_icons/{summoner_spell}.png", "wb+") as output_icon:
            output_icon.write(icon.content)
    else:
        print(f"An unexpected error occurred when downloading the {summoner_spell} icon!")

# get the champions' names
champions = [champion for champion in champions_data.keys()]
# save it in json
# FIXME: the file path needs a rework
with open("../data/champions.json", "w+") as output:
    json.dump(champions, output, indent=4)
# get the champions' icons
for champion in champions:
    icon = requests.get(f"http://ddragon.leagueoflegends.com/cdn/11.16.1/img/champion/{champion}.png")
    if icon.status_code == 200:
        # FIXME: the file path needs a rework
        with open(f"../img/champion_images/{champion}.png", "wb+") as output_icon:
            # FIXME: maybe rescale the images from 120x120 to 80x80
            output_icon.write(icon.content)
    else:
        print(f"An unexpected error occurred when downloading the {champion} icon!")
