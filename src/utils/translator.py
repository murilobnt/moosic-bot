from enum import Enum

from src.language.translation_data import data

class SupportedLanguages(Enum):
    PT_BR = 1
    US_EN = 2
    ES    = 3

class Translator:
    @staticmethod
    def translate(string_id, language : SupportedLanguages = SupportedLanguages.PT_BR): 
        if language == SupportedLanguages.PT_BR:
            return data['pt_br'][string_id] if data.get('pt_br') and data['pt_br'].get(string_id) else "Erro de tradução :c"
        elif language == SupportedLanguages.US_EN:
            return data['us_en'][string_id] if data.get('us_en') and data['us_en'].get(string_id) else "Translation error :c"
        elif language == SupportedLanguages.ES:
            return data['es'][string_id] if data.get('es') and data['es'].get(string_id) else "Error de traducción :c"
        else:
            return
            # raise error
