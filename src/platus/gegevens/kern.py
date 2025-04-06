from .invoer import invoer_kiezen, invoer_validatie
from .bank import Transactie, Bankrekening
from .lezerschrijver import open_json
from pandas import read_excel
import datetime as dt

def verwerken():
    
    eigen_bankrekeningen    =   open_json("gegevens\\config",    "bankrekeningen", "json")
    bankrekening_uuid       =   invoer_kiezen("bankrekening", {eigen_bankrekening["naam"]: bankrekening_uuid  for bankrekening_uuid, eigen_bankrekening in eigen_bankrekeningen.items()})
    
    bankrekening    =   Bankrekening.openen(bankrekening_uuid)
    
    jaar    =   invoer_validatie("jaar", int, bereik = (1998, dt.datetime.now().year))
    maand   =   invoer_validatie("maand", int, bereik = (1, dt.datetime.now().month) if jaar == dt.datetime.now().year else (1, 12))
    
    bankrekening.verwerken(jaar, maand)
    # bankrekening.opslaan()
    
def verwerken_excel(
                    rekeningnummer  : str,
                    jaar            : int,
                    maand           : int,
                    ) -> None:
    
    bankrekening        =   Bankrekening.open(rekeningnummer)
    
    bankexport          =   read_excel(f"{bankrekening.pad}\\digitaal\\{jaar}-{maand:02}.xlsx")
    bankexport.columns  =   [col.lower() for col in bankexport.columns]
    
    for irij, rij in bankexport.iterrows():
        transactie  =   Transactie.van_bankexport(rij)
        bankrekening.toevoegen_transactie(transactie)
    
    bankrekening.opslaan()