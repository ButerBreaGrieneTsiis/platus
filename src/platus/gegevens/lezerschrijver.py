import json
import platus

def decoder(dictionary, **kwargs):
    
    mapping     =   {
                        "transactie": (frozenset(("index", "bedrag", "beginsaldo", "eindsaldo", "transactiemethode", "datumtijd", "dagindex", "cat_uuid", "rekeningnummer", "uuid", "details", "derde_uuid")), platus.Transactie.van_json),
                        "categorie" : (frozenset(("naam", "hoofdcat_uuid", "bedrijven", "trefwoorden")), platus.Categorie.van_json),
                        "hoofdcategorie" : (frozenset(("naam",)), platus.HoofdCategorie.van_json),
                        "persoon": (frozenset(("naam", "iban", "rekeningnummer", "giro", "groep")), platus.Persoon.van_json),
                        "bedrijf": (frozenset(("naam", "iban", "rekeningnummer", "giro", "synoniemen", "uitsluiten", "cat_uuid")), platus.Bedrijf.van_json),
                        "cpsp": (frozenset(("naam", "iban", "rekeningnummer", "giro", "synoniemen", "uitsluiten")), platus.CPSP.van_json),
                        }
    
    if "class" in kwargs.keys():
        if mapping[kwargs["class"]][0].issuperset(dictionary.keys()):
            return mapping[kwargs["class"]][1](**dictionary)
        else:
            return dictionary
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
            
def open_json(map : str, bestandsnaam : str, extensie : str = None, class_mapper = None, encoding : str= "utf-8", kwargs : dict = {}) -> dict:
    
    bestandsnaam    =   bestandsnaam if extensie is None else f"{bestandsnaam}.{extensie}"
    with open(f"{map}\\{bestandsnaam}", "r", encoding = encoding) as bestand:
        if class_mapper is None:
            return json.load(bestand, object_hook = lambda x: decoder(x, **kwargs))
        else:
            return json.load(bestand, object_hook = class_mapper)
    
def opslaan_json(dictionary : dict, map : str, bestandsnaam : str, extensie : str = None, encoder = Encoder, encoding : str = "utf-8"):
    
    bestandsnaam    =   bestandsnaam if extensie is None else f"{bestandsnaam}.{extensie}"
    
    with open(f"{map}\\{bestandsnaam}", "w", encoding = encoding) as bestand:
        bestand.write(json.dumps(dictionary, indent = 4, ensure_ascii = False, sort_keys = False, cls = encoder))