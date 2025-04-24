import re
from typing import Iterator


def iban_zoeker(tekst: str) -> str:
    
    patronen_iban   =   [
        r".*(NL\d{2}[A-Z]{4}\d{10}).*",                # Nederland
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