from uuid import uuid4

class Derde:
    
    def __init__(self, 
                 naam           :   str,
                 type           :   str,
                 iban           :   list,
                 rekeningnummer :   list,
                 giro           :   list,
                 ):
        
        self.naam               =   naam
        self.type               =   type
        self.iban               =   list() if iban is None else iban
        self.rekeningnummer     =   list() if rekeningnummer is None else rekeningnummer
        self.giro               =   list() if giro is None else giro
    
    @classmethod
    def van_json(cls, **subcategorie_dict: dict):
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
    
    def toevoegen_iban(self,
                       iban_nieuw:  str,
                       ):
        
        if not iban_nieuw in self.iban:
            self.iban.append(iban_nieuw)
        
        return self

    def toevoegen_rekeningnummer(self,
                                rekeningnummer_nieuw:  str,
                                ):
        
        if not rekeningnummer_nieuw in self.rekeningnummer:
            self.rekeningnummer.append(rekeningnummer_nieuw)
        
        return self
    
    def toevoegen_giro(self,
                       giro_nieuw:  str,
                       ):
        
        if not giro_nieuw in self.giro:
            self.giro.append(giro_nieuw)
        
        return self
    
class Persoon(Derde):
    
    def __init__(self,
                 naam           :   str,
                 groep          :   str     =   "ongegroepeerd",
                 rekeningnummer :   list    =   None,
                 iban           :   list    =   None,
                 giro           :   list    =   None,
                ):
                 
        super().__init__(naam           =   naam,
                         type           =   "persoon",
                         iban           =   iban,
                         rekeningnummer =   rekeningnummer,
                         giro           =   giro,
                         )
        
        self.groep              =   groep

class Bedrijf(Derde):

    def __init__(self,
                 naam           :   str,
                 synoniemen     :   list    =   None,
                 uitsluiten     :   bool    =   False,
                 rekeningnummer :   list    =   None,
                 iban           :   list    =   None,
                 giro           :   list    =   None,
                 cat_uuid       :   str     =   None,
                 ):
        
        super().__init__(naam           =   naam,
                         type           =   "bedrijf",
                         iban           =   iban,
                         rekeningnummer =   rekeningnummer,
                         giro           =   giro,
                         )
        
        self.synoniemen     =   list() if synoniemen is None else synoniemen
        self.uitsluiten     =   uitsluiten
        self.cat_uuid       =   cat_uuid

class CPSP(Derde):

    def __init__(self,
                 naam           :   str,
                 synoniemen     :   list    =   None,
                 uitsluiten     :   bool    =   False,
                 rekeningnummer :   list    =   None,
                 iban           :   list    =   None,
                 giro           :   list    =   None,
                 ):
        
        super().__init__(naam           =   naam,
                         type           =   "cpsp",
                         iban           =   iban,
                         rekeningnummer =   rekeningnummer,
                         giro           =   giro,
                         )
        
        self.synoniemen     =   list() if synoniemen is None else synoniemen
        self.uitsluiten     =   uitsluiten