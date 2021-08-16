import json
from typing import List
from lcu_driver import Connector


class ClientScraper:
    # TODO: the class functionality can be extended to other api calls.

    def __init__(self):

        self.connector = Connector()

        @self.connector.ready
        async def connector(connection):
            # gets the user's champions
            summoner = await connection.request('get', '/lol-champions/v1/owned-champions-minimal')
            champions = [champ_data["alias"] for champ_data in await summoner.json()]
            if "MonkeyKing" in champions:
                # exceptions I've noticed
                # FIXME: after the api scraper will be fully implemented this if statement will be unnecessary
                champions.remove("MonkeyKing")
                champions.append("Wukong")
                champions.sort()
            with open("available_champions.json", "w+") as output_file:
                json.dump(champions, output_file, indent=4)

    def request_data(self) -> None:
        self.connector.start()

    def get_available_champions(self) -> List[str]:
        with open("available_champions.json", "r+") as input_file:
            return json.load(input_file)


# only this should be imported
client_scraper = ClientScraper()
