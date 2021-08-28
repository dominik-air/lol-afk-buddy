from lcu_driver import Connector
import json
connector = Connector()


with open("send_this_runes.json", "r") as f:
    runes = json.load(f)

primary_style_id = (runes[0] // 100) * 100
sub_style_id = (runes[4] // 100) * 100


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
        request = f"/lol-perks/v1/pages"
        request_type = "post"
        data = {
          'autoModifiedSelections': [],
          "current": True,
          "id": 94698869,
          "isActive": False,
          "isDeletable": True,
          "isEditable": True,
          "isValid": True,
          'lastModified': 1629808281841,
          "name": "nice runes",
          "order": 1,
          'primaryStyleId': primary_style_id,
          "selectedPerkIds": runes,
          "subStyleId": sub_style_id
        }
        co_tam = await connection.request(request_type, request, data=data)
        print(co_tam)
connector.start()
