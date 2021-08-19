from lcu_driver import Connector

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
        request = f"/lol-collections/v1/inventories/{summonerId}/spells"
        request_type = "get"
        summoner_spells = await connection.request(request_type, request)
        print(await summoner_spells.json())

        #
        # for ID in range(0, 10):
        #     request = f"/lol-champ-select/v1/session/actions/{ID}"
        #     response = await connection.request(
        #         "patch",
        #         request,
        #         data={
        #             "championId": 76+ID,
        #             "id": ID,
        #             "isAllyAction": True,
        #             "type": "ban",
        #         },
        #     )
        #     check = response.status
        #     if check not in (*list(range(200, 209)), 226):
        #         print(f'brejkuje przy ID={ID}')
        #         continue
        #
        #     print(await response.json())
        #
        #     complete_request = f"/lol-champ-select/v1/session/actions/{ID}/complete"
        #     await connection.request(
        #         "post",
        #         complete_request)

connector.start()
