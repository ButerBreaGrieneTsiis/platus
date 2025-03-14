from platus.lezerschrijver import open_json, opslaan_json, class_mapper
from platus.bank import Bankrekening
from platus.transactie import Transactie
from platus.derden import Persoon, Bedrijf, PersoonGroep
from platus.categorie import Categorie, Subcategorie

def kern():
    
    derden                  =   open_json("data",   "derden",               "json", class_mapper = class_mapper())
    categorieen             =   open_json("data",   "categorieen",          "json", class_mapper = class_mapper())
    
    betaal_rekening         =   Bankrekening.open_json("432125906")
    spaar_rekening          =   Bankrekening.open_json("486717429")
    
    while True:
        # alle handelingen
        pass
    
    opslaan_json(derden, "data", "derden", "json")
    opslaan_json(categorieen, "data", "categorieen", "json")
    
    betaal_rekening.opslaan_json()
    spaar_rekening.opslaan_json()
    
    
    
    
    