from enum import Enum

from src.database.async_database import connect_db
from src.language.translation_data import data

class SupportedLanguages(Enum):
    PT_BR = 1
    US_EN = 2
    ES    = 3

def int_to_sl(sl_id):
    if sl_id == 1:
        return SupportedLanguages.PT_BR
    elif sl_id == 2:
        return SupportedLanguages.US_EN
    elif sl_id == 3:
        return SupportedLanguages.ES

def sl_to_int(sl):
    if sl == SupportedLanguages.PT_BR:
        return 1
    if sl == SupportedLanguages.US_EN:
        return 2
    if sl == SupportedLanguages.ES:
        return 3
    
def _s(string_id, language : SupportedLanguages):
    if language == SupportedLanguages.PT_BR:
        return data['pt_br'][string_id] if data.get('pt_br') and data['pt_br'].get(string_id) else "Erro de tradução. Contate o dev pls :c"
    elif language == SupportedLanguages.US_EN:
        return data['us_en'][string_id] if data.get('us_en') and data['us_en'].get(string_id) else "Translation error. Contact the dev pls :c"
    elif language == SupportedLanguages.ES:
        return data['es'][string_id] if data.get('es') and data['es'].get(string_id) else "Error de traducción. Contacta el dev pls :c"
    else:
        return "Língua ainda não suportada :c"

class Translator:
    def __init__(self, servers_settings):
        self.servers_settings = servers_settings

    def translate(self, string_id, guild_id):
        lang = SupportedLanguages.PT_BR
        if self.servers_settings.get(guild_id) and self.servers_settings[guild_id].get('language'):
            lang = self.servers_settings[guild_id]['language']
        return _s(string_id, lang)
