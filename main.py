from requests_cache import CachedSession
from datamodels.searchItem import *
from datamodels.character import Character
from routes import *
from typing import Union, List
from utils import generate_t, base36encode
from constants import *
from errors import *


class SRSClient:
    '''
    StarRailStation Website Client

    : initializes the client



    '''
    def __init__(self) -> None:
        
        self.__session = CachedSession(cache_name='srs.cache', backend='sqlite', expire_after=3600)

        self.__session.headers.update(
            {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.68',
             'referer': 'https://starrailstation.com/'}
        )

    def generate_hash_route(self, language: Languages, route: Routes, goto: bool = False, item_id : str=''):
        '''
        
        :generates hashed route for fetching data

        --
        params
        --

        language: Languages Enum
            - Languages.ENG, Languages.RU etc
        route: a Routes object
        goto: if you want to search in a specific route [True] 
            - defaults to False
        
        item_id : id of the item you want to search in a route
        
        '''

        if not isinstance(language, Languages):
            raise InvalidLanguage
        
        url = route.generate_main_lang_path(language)
        if goto:
            url = f"{route.generate_goto_lang_path(language)}{item_id}.json"
        hashed_path = base36encode(generate_t(url))

        return  f"{MAIN_ROUTE}{hashed_path}"




        
    
    def fetch(self, language: Languages , route: Routes, goto: bool = False, item_id : str = '') -> List[dict] | dict | None:
        '''
        
        :fetches data from the api route
        --
        params
        --

        language: Languages Enum
            - Languages.ENG, Languages.RU etc
        route: a Routes object
        goto: if you want to search in a specific route [True] 
            - defaults to False
        
        item_id : id of the item you want to search in a route
        
        '''

        if not isinstance(language, Languages):
            raise InvalidLanguage

        response = self.__session.get(self.generate_hash_route(language, route, goto, item_id))
    

        if response.status_code  < 300:
            data = response.json()
            if 'entries' in data:
                return data['entries']
            else:
                return data
            

    def get_all_items(self,  type: Types = None, language: Languages = Languages.ENG) -> list[SearchItem]:
        '''
        
        :fetches all items from api route
        --
        params
        --

        language: Languages Enum
            - Languages.ENG, Languages.RU etc
        type : a type object 
            - Types.MATERIALS, Types.PLAYERCARDS, Types.CHARACTERS etc
        
        
        '''

        if not isinstance(language, Languages):
            raise InvalidLanguage

        response = self.fetch(language, SEARCH, False)

        if response is not None:
            all_items = [SearchItem(**{ **d, **{'id': d['url'].split("/")[1]}}) for d in response]
            if type is not None:
                return list(filter(lambda x: x.type == type, all_items))
           
      
            return all_items
        
    def get_all_character_details(self,item: Union[SearchItem , int], language: Languages = Languages.ENG) -> Character:
        '''
        
        :fetches character details from api route provided a search item or character id
        --
        params
        --

        item: [SearchItem of Character Type] or [Character ID]
        language: Languages Enum
            - Languages.ENG, Languages.RU etc
        
        
        '''
        if isinstance(item, SearchItem):
            if item.type == Types.CHARACTERS:

                response = self.fetch(language, CHARACTERS, True, item.id)
                if response is not None:
                    return Character(**response)
            
            else:

                raise InvalidItemType
        
        else:

            response = self.fetch(language, CHARACTERS, True, item)
            if response is not None:
                    return Character(**response)
