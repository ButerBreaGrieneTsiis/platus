import re
from typing import Dict, List, Any

from grienetsiis import Kleur, open_json


class PlatusType:
    
    @classmethod
    def van_json(
        cls,
        **dict: Dict[str, Any]
        ):
        
        patroon_kleur = re.compile(r"^#[0-9a-f]{6}$")
        
        for sleutel, waarde in dict.items():
            if isinstance(waarde, str) and bool(patroon_kleur.match(waarde)):
                dict[sleutel] = Kleur.van_hex(waarde)
        
        return cls(**dict)
    
    def naar_json(self) -> dict:
        
        dict    =   {}
        
        for veld, waarde in self.__dict__.items():
            
            if veld == "type":
                continue
            elif isinstance(waarde, list) and len(waarde) == 0:
                continue
            elif isinstance(waarde, bool) and not waarde:
                continue
            elif isinstance(waarde, Kleur):
                dict[veld] = waarde.hex
            elif waarde is None:
                continue
            else:
                dict[veld] = waarde
        
        return dict

class HoofdCategorie(PlatusType):
    
    def __init__(
        self,
        naam    :   str,
        kleur   :   Kleur,
        ) -> "HoofdCategorie":
        
        self.naam   =   naam
        self.kleur  =   kleur
    
    def __repr__(self):
        return f"hoofdcategorie {self.naam}"

class Categorie(PlatusType):
    
    def __init__(
        self,
        naam            :   str,
        hoofdcat_uuid   :   str,
        kleur           :   Kleur,
        trefwoorden     :   list  =   None,
        ):
        
        self.naam           =   naam
        self.hoofdcat_uuid  =   hoofdcat_uuid
        self.kleur          =   kleur
        self.trefwoorden    =   list() if trefwoorden is None else trefwoorden
    
    def __repr__(self):
        hoofdcategorieen = open_json("gegevens\\configuratie", "hoofdcategorie", "json", class_mapper = (HoofdCategorie, frozenset(("naam", "type")), "van_json"),)
        return f"categorie {self.naam} ({hoofdcategorieen[self.hoofdcat_uuid]})"

class Land(PlatusType):
    
    def __init__(self,
        naam                :   str,
        iso_3166_1_alpha_3  :   str,
        synoniemen          :   List[str] = None,
        ) -> "Land":
        
        self.naam               =   naam
        self.iso_3166_1_alpha_3 =   iso_3166_1_alpha_3
        self.synoniemen         =   list() if synoniemen is None else synoniemen
    
    def __repr__(self):
        return f"land {self.naam}"

class Locatie(PlatusType):
    
    def __init__(
        self,
        naam            :   str,
        land_uuid       :   str,
        breedtegraad    :   float,
        lengtegraad     :   float,
        synoniemen      :   List[str] = None
        ) -> "Locatie":
        
        self.naam           =   naam
        self.land_uuid      =   land_uuid
        self.breedtegraad   =   breedtegraad
        self.lengtegraad    =   lengtegraad
        self.synoniemen     =   list() if synoniemen is None else synoniemen
    
    def __repr__(self):
        landen = open_json("gegevens\\configuratie", "land", "json", class_mapper = (Land, frozenset(("naam", "iso_3166_1_alpha_3", "synoniemen")), "van_json"),)
        return f"locatie {self.naam} ({landen[self.land_uuid]})"
        
class Derde(PlatusType):
    
    def __init__(
        self, 
        naam            :   str,
        type            :   str,
        iban            :   List[str],
        rekeningnummer  :   List[str],
        ) -> "Derde":
        
        self.naam           =   naam
        self.type           =   type
        self.iban           =   list() if iban is None else iban
        self.rekeningnummer =   list() if rekeningnummer is None else rekeningnummer
    
    def __repr__(self):
        return f"{self.type} {self.naam}"
    
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
        naam            :   str,
        groep           :   str         =   "ongegroepeerd",
        rekeningnummer  :   List[str]   =   None,
        iban            :   List[str]   =   None,
        giro            :   List[str]   =   None,
        ) -> "Persoon":
        
        super().__init__(
            naam           =   naam,
            type           =   "persoon",
            iban           =   iban,
            rekeningnummer =   rekeningnummer,
            )
        
        self.groep  =   groep
        self.giro   =   list() if giro is None else giro

class Bedrijf(Derde):

    def __init__(
        self,
        naam            :   str,
        synoniemen      :   list        =   None,
        uitsluiten      :   bool        =   False,
        rekeningnummer  :   List[str]   =   None,
        iban            :   List[str]   =   None,
        giro            :   List[str]   =   None,
        cat_uuid        :   str         =   None,
        ) -> "Bedrijf":
        
        super().__init__(
            naam           =   naam,
            type           =   "bedrijf",
            iban           =   iban,
            rekeningnummer =   rekeningnummer,
            )
        
        self.synoniemen =   list() if synoniemen is None else synoniemen
        self.giro       =   list() if giro is None else giro
        self.uitsluiten =   uitsluiten
        self.cat_uuid   =   cat_uuid

class Cpsp(Derde):

    def __init__(
        self,
        naam            :   str,
        synoniemen      :   List[str]   =   None,
        uitsluiten      :   bool        =   False,
        rekeningnummer  :   List[str]   =   None,
        iban            :   List[str]   =   None,
        ) -> "Cpsp":
        
        super().__init__(
            naam           =   naam,
            type           =   "cpsp",
            iban           =   iban,
            rekeningnummer =   rekeningnummer,
            )
        
        self.synoniemen =   list() if synoniemen is None else synoniemen
        self.uitsluiten =   uitsluiten

class Bank(Derde):

    def __init__(
        self,
        naam            :   str,
        synoniemen      :   List[str]   =   None,
        rekeningnummer  :   List[str]   =   None,
        iban            :   List[str]   =   None,
        bic             :   List[str]   =   None,
        ) -> "Bank":
        
        super().__init__(
            naam           =   naam,
            type           =   "bank",
            iban           =   iban,
            rekeningnummer =   rekeningnummer,
            )
        
        self.synoniemen =   list() if synoniemen is None else synoniemen
        self.bic        =   list() if bic is None else bic