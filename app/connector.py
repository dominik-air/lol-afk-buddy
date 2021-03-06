from session_manager import SessionManager, Action
from lcu_driver import Connector
from termcolor import colored
from command import Command
from packages.champNameIdMapper import ChampNameIdMapper
from pprint import pprint

connector = Connector()
session_manager = SessionManager()
Command.session_manager = session_manager

# FLAGS
IS_CONNECTED = False
async def wait_for_connection():
    while True:
        if IS_CONNECTED:
            return True
    

@connector.ready
async def connect(connection):
    print(Command.OK_S,
        'LCU API is ready to be used.')
    
    # get summoner name
    res = await connection.request('get', '/lol-summoner/v1/current-summoner')
    if res.status == 200:
        IS_CONNECTED = True
        data = await res.json()
        SUMMONER_NAME: str = data['internalName']
        SUMMONER_ID: int = data['summonerId']
        SUMMONER_PUUID: str = data['puuid']

        session_manager.set_summoner_id(SUMMONER_ID)

        print(Command.OK_S,
        'Logged in successfully\n',
        '\t-Currently logged as summoner:',
        colored(f'{SUMMONER_NAME}\n', attrs=('bold',)),
        '\t-summoner id:',
        colored(f'{SUMMONER_ID}\n', attrs=('bold',)),
        sep=' ')
        # connection.locals.update({'lobby': None})
        connection.locals.update({'my_summoner_id': SUMMONER_ID})
        connection.locals.update({'my_cell_id': 'Unknown'})

        status = await ChampNameIdMapper.get_data()
        print(Command.OK_S,
            'champion id and name mapped successfully',
            f' .status: {status}')

    # else:
    #     MenuApp._error_whit_connection(res)

@connector.close
async def disconnect(_):
    print('The client have been closed!')
    await connector.stop()

@connector.ws.register('/lol-lobby/v2/lobby', event_types=('UPDATE',
                                                           'DELETE'))
async def lobby(connection, event):
    # print(type(event))

    # helping variables
    content: str = str()
    header: str = colored('The game lobby started.', 'red')

    # If event does not exist then function will never called
    # If event lobby is deleted then event exist but it's data is empty
    if event.data:
        data: dict = {
            'Game mode': event.data['gameConfig']['gameMode'],
        }

        # fulfill content variable
        for key, value in data.items():
            content += colored(f"\t-{key}: ", 'red')
            content += colored(f"{value}", 'red', attrs=('bold',))
            content += '\n'

        # print out data
        print(header)
        print(content)

    else:
        data: dict = {'Game mode': None}
        # event.data = None
        
    # ADD EVENT OBJECT TO CONNECTION'S LOCALS IN OREDER TO GAIN OUTER ACCESS
    connection.locals.update({'lobby': event})
    # pprint(connector.ws.registered_uris)

@connector.ws.register('/lol-champ-select/v1/session', event_types=('UPDATE',
                                                                    'DELETE',
                                                                    'CREATE'))
async def session(connection, event):
        if event.type in ('Update', 'Create'):
            if d := event.data:
                # FIRST MUST BE SYNCED myTeam THAT'S IMPORTANT!!!
                session_manager.my_team.sync_with_websocket(d['myTeam'])
                session_manager.actions.sync_with_websocket(d['actions'])
        
        my_action: Action = session_manager.get_my_action()

        if my_action:
            champs: dict = ChampNameIdMapper.get_champion_dict(order='reversed')

            try:
                hovered_champ: str = champs[str(my_action.champion_id)]

            except KeyError:
                # If not hovering any champion set None
                hovered_champ: str = None

            pprint(my_action.__dict__)
            print(f"hovered champion name: {hovered_champ}")


        # ADD EVENT OBJECT TO CONNECTION'S LOCALS IN OREDER TO GAIN OUTER ACCESS
        connection.locals.update({'session': event})

        # connection.locals.update({'session': event,
        #                         'active_id': active_action_id,
        #                         'active_action': active_action,
        #                         'actor_cell_id': actor_cell_id})
        # pprint(connector.ws.registered_uris)

@connector.ws.register('/lol-game-queues/v1/queues', event_types=('UPDATE',))
async def queue(connection, event):
    # print(type(event))

    # helping variables
    content: str = str()
    header: str = colored('The queue has been updated.', 'red')
    data: dict = {
        'type of the queue': event.data['type'],
        'name of the queue': event.data['name'],
    }

    # fulfill content variable
    for key, value in data.items():
        content += colored(f"\t-{key}: ", 'red')
        content += colored(f"{value}", 'red', attrs=('bold',))
        content += '\n'

    # print out data
    print(header)
    print(content)

    # ADD EVENT OBJECT TO CONNECTION'S LOCALS IN OREDER TO GAIN OUTER ACCESS
    connection.locals.update({'queue': event})
    # pprint(connector.ws.registered_uris)

@connector.ws.register('/lol-matchmaking/v1/search', event_types=('UPDATE',
                                                                  'DELETE'))
async def search(connection, event):
    # print(type(event))

    # helping variables
    content: str = str()
    header: str = colored('The search has been updated.', 'red')

    if event.data:
        data: dict = {
            'est queue time': event.data['estimatedQueueTime'],
            'is currently in queue': event.data['isCurrentlyInQueue'],
            'lobby id': event.data['lobbyId'],
            'search state': event.data['searchState'],
            'time in queue': event.data['timeInQueue'],
        }

        # fulfill content variable
        for key, value in data.items():
            content += colored(f"\t-{key}: ", 'red')
            content += colored(f"{value}", 'red', attrs=('bold',))
            content += '\n'

        # print out data
        print(header)
        print(content)
    
    else:
        event.data = None

    # ADD EVENT OBJECT TO CONNECTION'S LOCALS IN OREDER TO GAIN OUTER ACCESS
    connection.locals.update({'search': event})
    # pprint(connector.ws.registered_uris)