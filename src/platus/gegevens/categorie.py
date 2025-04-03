from uuid import uuid4

class HoofdCategorie:
     
    def __init__(self,
                 naam       :   str,
                 ):
        
        self.naam              =   naam
    
    @classmethod
    def van_json(cls, **hoofdcategorie_dict: dict):
        return cls(**hoofdcategorie_dict)

class Categorie:
    
    def __init__(self,
                 naam           :   str,
                 hoofdcategorie :   str,
                 trefwoorden    :   list  =   None,
                ):
        
        self.naam           =   naam
        self.hoofdcategorie =   hoofdcategorie
        self.trefwoorden    =   list() if trefwoorden is None else trefwoorden
    
    @classmethod
    def van_json(cls, **categorie_dict: dict):
        return cls(**categorie_dict)