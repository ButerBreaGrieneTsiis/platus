import datetime as dt

from grienetsiis import open_json, invoer_kiezen, invoer_validatie
from .bank import Bankrekening


def verwerken():
    
    eigen_bankrekeningen    =   open_json("gegevens\\config", "bankrekening", "json")
    bankrekening_uuid       =   invoer_kiezen("bankrekening", {eigen_bankrekening["naam"]: bankrekening_uuid  for bankrekening_uuid, eigen_bankrekening in eigen_bankrekeningen.items()})
    
    bankrekening    =   Bankrekening.openen(bankrekening_uuid)
    
    jaar    =   invoer_validatie("jaar", int, bereik = (1998, dt.datetime.now().year))
    maand   =   invoer_validatie("maand", int, bereik = (1, dt.datetime.now().month-1) if jaar == dt.datetime.now().year else (1, 12))
    
    bankrekening.verwerken(jaar, maand)
    bankrekening.opslaan()