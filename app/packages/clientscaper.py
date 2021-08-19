import json
from typing import List
from lcu_driver import Connector


async def get_available_champions(connection) -> None:
    # gets the user's champions_data
    summoner_champions = await connection.request(
        "get", "/lol-champions/v1/owned-champions-minimal"
    )
    champions = [champ_data["alias"] for champ_data in await summoner_champions.json()]
    with open("available_champions.json", "w+") as output_file:
        json.dump(champions, output_file, indent=4)


async def get_available_summoner_spells(connection) -> None:
    # gets the user's champions_data
    summoner_spells = await connection.request(
        "get", "/lol-champions_data/v1/owned-champions_data-minimal"
    )
    spells = [spell_data["alias"] for spell_data in await summoner_spells.json()]
    with open("available_summoner_spells.json", "w+") as output_file:
        json.dump(spells, output_file, indent=4)


class ClientScraper:
    # TODO: the class functionality can be extended to other api calls.

    def __init__(self):

        self.connector = Connector()

        @self.connector.ready
        async def connector(connection):
            await get_available_champions(connection)
            #await get_available_summoner_spells(connection)

    def request_data(self) -> None:
        self.connector.start()

    def get_available_champions(self) -> List[str]:
        self.request_data()
        with open("available_champions.json", "r+") as input_file:
            return json.load(input_file)


# only this should be imported
client_scraper = ClientScraper()
