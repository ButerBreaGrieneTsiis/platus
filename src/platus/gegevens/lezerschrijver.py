import json

def decoder(dictionary, **kwargs):
    
    from .categorie import Categorie, HoofdCategorie
    from .derden import Bedrijf, Persoon, CPSP, Bank
    from .bank import Transactie
    
    mapping     =   {
                        "transactie":       (Transactie.van_json,       frozenset(("index", "bedrag", "beginsaldo", "eindsaldo", "transactiemethode", "datumtijd", "dagindex", "cat_uuid", "rekeningnummer", "uuid", "details", "derde_uuid",))),
                        "categorie" :       (Categorie.van_json,        frozenset(("naam", "hoofdcat_uuid", "bedrijven", "trefwoorden",))),
                        "hoofdcategorie" :  (HoofdCategorie.van_json,   frozenset(("naam",))),
                        "persoon":          (Persoon.van_json,          frozenset(("naam", "iban", "rekeningnummer", "giro", "groep",))),
                        "bedrijf":          (Bedrijf.van_json,          frozenset(("naam", "iban", "rekeningnummer", "giro", "synoniemen", "uitsluiten", "cat_uuid",))),
                        "cpsp":             (CPSP.van_json,             frozenset(("naam", "iban", "rekeningnummer", "giro", "synoniemen", "uitsluiten",))),
                        "bank":             (Bank.van_json,             frozenset(("naam", "iban", "rekeningnummer", "synoniemen", "bic",))),
                        }
    
    if "clss" in kwargs.keys():
        if mapping[kwargs["clss"]][1].issuperset(dictionary.keys()):
            return mapping[kwargs["clss"]][0](**dictionary)
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
            
def open_json(map : str, bestandsnaam : str, extensie : str = None, class_mapper = None, encoding : str= "utf-8", **kwargs) -> dict:
    
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