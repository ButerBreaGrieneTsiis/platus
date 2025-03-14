import json
from platus.derden import Persoon, Bedrijf, PersoonGroep
from platus.categorie import Categorie, Subcategorie

def class_mapper(dictionary):
    
    class_mapper    =   {frozenset(("naam", "uuid", "type", "transacties", "groep", "rekeningnummer", "iban")): Persoon,
                         frozenset(("naam", "uuid", "type", "transacties", "synoniemen", "uitsluiten", "trefwoorden")): Bedrijf,
                         frozenset(): PersoonGroep.van_json,
                         }
    
    for sleutels, cls in class_mapper.items():
        if sleutels.issuperset(dictionary.keys()):
            return cls(**dictionary)
    else:
        return dictionary

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "naar_json"):
            return obj.naar_json()
        try:
            obj.__dict__
        except:
            return json.JSONEncoder.default(self, obj)
        else:
            return obj.__dict__
            

def open_json(map : str, bestandsnaam : str, extensie : str = None, class_mapper : dict = None, encoding : str= "utf-8") -> dict:
    
    bestandsnaam    =   bestandsnaam if extensie is None else f"{bestandsnaam}.{extensie}"
    
    with open(f"{map}\\{bestandsnaam}", "r", encoding = encoding) as bestand:
        if class_mapper is None:
            return json.load(bestand)
        else:
            return json.load(bestand, object_hook = class_mapper)
    
def opslaan_json(dictionary : dict, map : str, bestandsnaam : str, extensie : str = None, encoder : object = None, encoding : str = "utf-8"):
    
    bestandsnaam    =   bestandsnaam if extensie is None else f"{bestandsnaam}.{extensie}"
    
    with open(f"{map}\\{bestandsnaam}.{extensie}", "w", encoding = encoding) as bestand:
        if encoder == None:
            bestand.write(json.dumps(dictionary, indent = 4, ensure_ascii = False, sort_keys = False))
        else:
            bestand.write(json.dumps(dictionary, indent = 4, ensure_ascii = False, sort_keys = False, cls = encoder))