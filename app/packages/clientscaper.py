import json
from typing import List
from lcu_driver import Connector


async def get_summoner_id(connection) -> None:
    # get the user's id
    summoner = await connection.request("get", "/lol-summoner/v1/current-summoner")
    data = await summoner.json()
    return data['summonerId']


async def get_available_champions(connection) -> None:
    # gets the user's champions_data
    summoner_champions = await connection.request(
        "get", "/lol-champions/v1/owned-champions-minimal"
    )
    champions = [champ_data["alias"] for champ_data in await summoner_champions.json()]
    with open("available_champions.json", "w+") as output_file:
        json.dump(champions, output_file, indent=4)


async def get_available_summoner_spells(connection, summoner_id) -> None:
    # gets the user's summoner spell data
    summoner_spells = await connection.request(
        "get",  f"/lol-collections/v1/inventories/{summoner_id}/spells"
    )

    summoner_spells = await summoner_spells.json()

    spell_ids = summoner_spells["spells"]

    with open("../data/summoner_spells.json", "r+") as spells_file:
        spells = json.load(spells_file)

    available_spells = list(filter(lambda s: int(s[1]) in spell_ids, spells))

    with open("available_summoner_spells.json", "w+") as output_file:
        json.dump(available_spells, output_file, indent=4)


class ClientScraper:
    # TODO: the class functionality can be extended to other api calls.

    def __init__(self):

        self.connector = Connector()

        @self.connector.ready
        async def connector(connection):
            summoner_id = await get_summoner_id(connection)
            await get_available_champions(connection)
            await get_available_summoner_spells(connection, summoner_id)

    def request_data(self) -> None:
        self.connector.start()

    def get_available_champions(self) -> List[str]:
        self.request_data()
        with open("available_champions.json", "r") as input_file:
            return json.load(input_file)


# only this should be imported
client_scraper = ClientScraper()
