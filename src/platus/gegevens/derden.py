from typing import List, Dict, Any
from uuid import uuid4


class Derde:
    
    def __init__(
        self, 
        naam            :   str,
        type            :   str,
        iban            :   List[str],
        rekeningnummer  :   List[str],
    ) -> "Derde":
        
        self.naam               =   naam
        self.type               =   type
        self.iban               =   list() if iban is None else iban
        self.rekeningnummer     =   list() if rekeningnummer is None else rekeningnummer
    
    @classmethod
    def van_json(
        cls,
        **subcategorie_dict: Dict[str, Any]
    ) -> "Derde":
        
        return cls(**subcategorie_dict)
    
    def naar_json(self) -> dict:
        
        derde_dict     =   {}
        
        for veld, waarde in self.__dict__.items():
            
            if veld == "type":
                continue
            if isinstance(waarde, list):
                if len(waarde) == 0:
                    continue
            if isinstance(waarde, bool):
                if not waarde:
                    continue
            if waarde is None:
                continue
            derde_dict[veld]    =   waarde
        
        return derde_dict
    
    def toevoegen_iban(
        self,
        iban_nieuw:  str,
    ) -> "Derde":
        
        if not iban_nieuw in self.iban:
            self.iban.append(iban_nieuw)
        
        return self

    def toevoegen_rekeningnummer(
        self,
        rekeningnummer_nieuw:  str,
    ) -> "Derde":
        
        if not rekeningnummer_nieuw in self.rekeningnummer:
            self.rekeningnummer.append(rekeningnummer_nieuw)
        
        return self
    
    def toevoegen_giro(
        self,
        giro_nieuw:  str,
    ) -> "Derde":
        
        if not giro_nieuw in self.giro:
            self.giro.append(giro_nieuw)
        
        return self
    
class Persoon(Derde):
    
    def __init__(
        self,
        naam           :   str,
        groep          :   str         =   "ongegroepeerd",
        rekeningnummer :   List[str]   =   None,
        iban           :   List[str]   =   None,
        giro           :   List[str]   =   None,
    ) -> "Persoon":
                 
        super().__init__(
            naam           =   naam,
            type           =   "persoon",
            iban           =   iban,
            rekeningnummer =   rekeningnummer,
        )
        
        self.groep              =   groep
        self.giro               =   list() if giro is None else giro

class Bedrijf(Derde):

    def __init__(
        self,
        naam           :   str,
        synoniemen     :   list        =   None,
        uitsluiten     :   bool        =   False,
        rekeningnummer :   List[str]   =   None,
        iban           :   List[str]   =   None,
        giro           :   List[str]   =   None,
        cat_uuid       :   str         =   None,
    ) -> "Bedrijf":
        
        super().__init__(
            naam           =   naam,
            type           =   "bedrijf",
            iban           =   iban,
            rekeningnummer =   rekeningnummer,
        )
        
        self.synoniemen     =   list() if synoniemen is None else synoniemen
        self.giro           =   list() if giro is None else giro
        self.uitsluiten     =   uitsluiten
        self.cat_uuid       =   cat_uuid

class Cpsp(Derde):

    def __init__(
        self,
        naam           :   str,
        synoniemen     :   List[str]   =   None,
        uitsluiten     :   bool        =   False,
        rekeningnummer :   List[str]   =   None,
        iban           :   List[str]   =   None,
    ) -> "Cpsp":
        
        super().__init__(
            naam           =   naam,
            type           =   "cpsp",
            iban           =   iban,
            rekeningnummer =   rekeningnummer,
        )
        
        self.synoniemen     =   list() if synoniemen is None else synoniemen
        self.uitsluiten     =   uitsluiten

class Bank(Derde):

    def __init__(
        self,
        naam           :   str,
        synoniemen     :   List[str]   =   None,
        rekeningnummer :   List[str]   =   None,
        iban           :   List[str]   =   None,
        bic            :   List[str]   =   None,
    ) -> "Bank":
        
        super().__init__(
            naam           =   naam,
            type           =   "bank",
            iban           =   iban,
            rekeningnummer =   rekeningnummer,
        )
        
        self.synoniemen     =   list() if synoniemen is None else synoniemen
        self.bic            =   list() if bic is None else bic