from lcu_driver import Connector
import json
connector = Connector()


@connector.ready
async def connect(connection):
    print("LCU API is ready to be used.")

    # check if the user is already logged into his account
    summoner = await connection.request("get", "/lol-summoner/v1/current-summoner")
    if summoner.status != 200:
        print(
            "Please login into your account to change your icon and restart the script..."
        )
    else:

        data = await summoner.json()
        summonerId = data['summonerId']
        #request = f"/lol-perks/v1/perks"
        request = "/lol-perks/v1/pages"
        #request = f"/lol-perks/v1/currentpage"
        request_type = "get"
        summoner_spells = await connection.request(request_type, request)
        save = await summoner_spells.json()
        with open("temp.json", "w+") as f:
            json.dump(save, f, indent=4)
connector.start()
