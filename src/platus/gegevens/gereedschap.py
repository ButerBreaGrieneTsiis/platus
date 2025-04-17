import re
from typing import Iterator


def iban_zoeker(tekst: str) -> str:
    
    patronen_iban   =   [r".*(NL\d{2}[A-Z]{4}\d{10}).*",                # Nederland
                         r".*(BE\d{14}).*",                             # België
                         r".*(AT\d{18}).*",                             # Oostenrijk
                         r".*(CZ\d{22}).*",                             # Tsjechië
                         r".*(FR\d{12}[0-9A-Z]{11}\d{2}).*",            # Frankrijk
                         r".*(DE\d{20}).*",                             # Duitsland
                         r".*(IT\d{2}[A-Z]\d{10}[0-9A-Z]{12}).*",       # Italië
                         r".*(LU\d{5}[0-9A-Z]{13}).*",                  # Luxemburg
                         r".*(ES\d{22}).*",                             # Spanje
                         r".*(GB\d{2}[A-Z]{4}\d{14}).*",                # Groot-Brittanië
                         r".*(CH\d{7}[0-9A-Z]{12}).*",                  # Zwitserland
                         ]
        
    for patroon_iban in patronen_iban:
        patroon     =   re.compile(patroon_iban)
        resultaat_iban  =   patroon.match(tekst.upper().replace(" ", ""))
        if bool(resultaat_iban):
            return resultaat_iban.group(1)
    
    else:
        raise NotImplementedError(f"tekst: \"{tekst}\"")

def jaar_maand_iterator(
    jaar_start: int,
    maand_start: int,
    jaar_eind: int,
    maand_eind: int,
) -> Iterator[int]:
    
    jaar_maand_start    =   12*jaar_start + maand_start-1
    jaar_maand_eind     =   12*jaar_eind + maand_eind-1
    
    for jaar_maand in range(jaar_maand_start, jaar_maand_eind):
        jaar, maand = divmod(jaar_maand, 12)
        yield jaar, maand+1