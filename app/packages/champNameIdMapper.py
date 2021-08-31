import asyncio
import collections
import aiohttp
import json
from termcolor import colored
from pprint import pprint

class ChampNameIdMapper():
    champions_data: dict = None
    champ_ids: dict = None
    reqs: str = \
        "http://ddragon.leagueoflegends.com/cdn/11.16.1/data/en_US/champion.json"

    @classmethod
    async def get_data(cls):

        # Clear champ ids, because this funcion will be called when we want
        # update data (we unlocking _updata_champion_dict function)
        cls.champ_ids = None

        async with aiohttp.ClientSession() as session:
            async with session.get(cls.reqs) as resp:
                cls.champions_data = await resp.json()
        
            return resp.status

    @classmethod
    def _update_champion_dict(cls):
        if not cls.champ_ids:
            x = cls.champions_data['data']
            cls.champ_ids = {_name: _id for _name, _dict
                        in x.items() for k, _id
                        in _dict.items() if k == 'key'}
    
    @classmethod
    def get_champion_dict(cls, order='normal'):
        cls._update_champion_dict()

        if order == 'normal':
            return cls.champ_ids

        elif order == 'reversed':
            return {v: k for k, v in cls.champ_ids.items()}
        
        else:
            raise Exception


    @classmethod
    def save_to_json(cls):
        cls._update_champion_dict()

        if not cls.champions_data:
            print(colored('[error]', 'red'), 'There is no data.',
                sep=' ')

            return

        with open('ChampNameIdMap.json', 'w') as file:
            try:
                json.dump(cls.champ_ids, file, indent=4)

            except Exception as e:
                print(colored('[error]', 'red'), 'Error while saving to file\n',
                      e, sep=' ')
                      
            else:
                print(colored('[OK]', 'green'), 'successfully saved to file',
                      sep=' ')


async def main():
    status = await ChampNameIdMapper.get_data()
    print(f'status: {status}')

    champs_dict = ChampNameIdMapper.get_champion_dict('reversed')
    # with open('champs_sorted.json', 'w') as file:
        # json.dump(dict(sorted(champs_dict.items(), key=lambda x: (x[1], x[0])), file, indent=4))
        # champs_dict = {k: int(v) for k, v in champs_dict.items()}
        # json.dump(dict(sorted(champs_dict.items(), key=lambda x: int(x[1]))), file, indent=4)

    pprint(champs_dict)

    ChampNameIdMapper.save_to_json()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
