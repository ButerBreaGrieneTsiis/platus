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
                 hoofdcat_uuid  :   str,
                 trefwoorden    :   list  =   None,
                ):
        
        self.naam           =   naam
        self.hoofdcat_uuid  =   hoofdcat_uuid
        self.trefwoorden    =   list() if trefwoorden is None else trefwoorden
    
    @classmethod
    def van_json(cls, **categorie_dict: dict):
        return cls(**categorie_dict)
    
    def naar_json(self) -> dict:
        
        if len(self.trefwoorden) == 0:
            return {
                    "naam":             self.naam,
                    "hoofdcat_uuid":    self.hoofdcat_uuid,
                    }
        else:
            return {
                    "naam":             self.naam,
                    "hoofdcat_uuid":    self.hoofdcat_uuid,
                    "trefwoorden":      self.trefwoorden,
                    } 