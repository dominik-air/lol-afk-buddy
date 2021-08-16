from riotwatcher import LolWatcher, ApiError
import pandas as pd
from pprint import pprint
import json
import time
import itertools as it

api_key = 'RGAPI-bd2b02e9-306d-476c-9613-f418fd98d2ef'
watcher = LolWatcher(api_key)
my_region = 'EUN1'

me = watcher.summoner.by_name(my_region, 'llwafelll')
print('\nAbout me:')
pprint(me)
print(type(me))

my_puuid = me['puuid']

# print('\nMy ranked status: ')
# my_ranked_status = watcher.league.by_summoner(my_region, me['id'])
# pprint(my_ranked_status)

pprint(watcher.match_v5.matchlist_by_puuid('europe', my_puuid))
last = 'EUN1_2899817634'

c = it.count()
while True:

    localtime = time.localtime()
    _time: str = time.strftime("%Mm-%Ss %p", localtime)

    try:
        sp = watcher.spectator.by_summoner(my_region, me['id'])

    except ApiError as e:
        print(f'err response: {e.response}')
        print(f'err request: {e.request}')
        print(f'err args: {e.args}')
        print('The game not started yet')
        sp = None
        
    
    except Exception as e2:
        print(f'antoghe exception occured: {e2}')

    else:
        with open(f'./spectators/sp-{next(c)}_{_time}.json', 'w') as f:
            if sp:
                json.dump(sp, f, indent=4, sort_keys=True)

    time.sleep(5) 
    print()

# while True:
#     inp = input('check?[y/n/e]') 
#     if inp == 'y':
#         try:
#             sp = watcher.spectator.by_summoner(my_region, me['id'])
#             with open('spectator.json', 'w') as f:
#                 json.dump(sp, f, indent=4, sort_keys=True)
#         except ApiError as e:
#             print(f'err response: {e.response}')
#             print(f'err request: {e.request}')
#             print(f'err filename: {e.filename}')
#             print(f'err winerror: {e.winerror}')
#             print(f'err args: {e.args}')
#             print(f'err strerror: {e.strerror}')


#     elif inp == 'n':
#         print('Just skipping')

#     elif inp == 'e':
#         break

#     else:
#         continue
