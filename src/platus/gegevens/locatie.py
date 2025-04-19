from typing import List

from .types import PlatusType


class Land(PlatusType):
    
    def __init__(self,
        naam: str,
        iso_3166_1_alpha_3: str,
        synoniemen: List[str] = None,
        ) -> "Land":
        
        self.naam               =   naam
        self.iso_3166_1_alpha_3 =   iso_3166_1_alpha_3
        self.synoniemen         =   list() if synoniemen is None else synoniemen

class Locatie(PlatusType):
    
    def __init__(
        self,
        naam:           str,
        land_uuid:      str,
        breedtegraad:   float,
        lengtegraad:    float,
        synoniemen:     List[str] = None
    ) -> "Locatie":
        
        self.naam           =   naam
        self.land_uuid      =   land_uuid
        self.breedtegraad   =   breedtegraad
        self.lengtegraad    =   lengtegraad
        self.synoniemen     =   list() if synoniemen is None else synoniemen

