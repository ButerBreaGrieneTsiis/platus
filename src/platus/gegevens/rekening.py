import datetime as dt
import locale
from typing import Dict,  List
from uuid import uuid4

import pandas as pd

from grienetsiis import open_json, opslaan_json
from .transactie import Transactie
from .types import Categorie, HoofdCategorie, Land, Locatie, Persoon, Bedrijf, Bank, Cpsp


locale.setlocale(locale.LC_ALL, "nl_NL.UTF-8")

class Rekening:
    
    def __init__(
        self,
        naam                :   str,
        uuid                :   str,
        actief_van          :   dt.datetime, 
        transacties         :   dict                =   None,
        actief              :   bool                =   True,
        actief_tot          :   dt.datetime         =   None,
        ) -> "Rekening":
        
        self.naam               =   naam
        self.uuid               =   uuid
        self.transacties        =   dict() if transacties is None else transacties
        self.actief             =   actief
        self.actief_van         =   actief_van
        self.actief_tot         =   actief_tot
    
    def opslaan(self):
        opslaan_json(self.transacties, "gegevens\\rekeningen", self.uuid, "json", {"Transactie": "naar_json"})
    
    def backup(self):
        opslaan_json(self.transacties, "gegevens\\rekeningen", f"{dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d")} - {self.uuid}", "json", {"Transactie": "naar_json"})
    
    @property
    def transactie_lijst(self) -> List[Transactie]:
        return list(sorted(self.transacties.values(), key = lambda transactie: transactie.index))
    
    def tabel(
        self,
        ) -> pd.DataFrame:
        
        personen        = 	open_json("gegevens\\derden",           "persoon",        "json", class_mapper = (Persoon, frozenset(("naam", "iban", "rekeningnummer", "giro", "groep",)), "van_json"),)
        bedrijven       = 	open_json("gegevens\\derden",           "bedrijf",        "json", class_mapper = (Bedrijf, frozenset(("naam", "iban", "rekeningnummer", "giro", "synoniemen", "uitsluiten", "cat_uuid",)), "van_json"),)
        bankrekeningen  = 	open_json("gegevens\\configuratie",     "bankrekening",   "json")
        banken          = 	open_json("gegevens\\derden",           "bank",           "json", class_mapper = (Bank, frozenset(("naam", "iban", "rekeningnummer", "synoniemen", "bic",)), "van_json"),)
        cpsps           = 	open_json("gegevens\\derden",           "cpsp",           "json", class_mapper = (Cpsp, frozenset(("naam", "iban", "rekeningnummer", "giro", "synoniemen", "uitsluiten",)), "van_json"),)
        categorieen     =   open_json("gegevens\\configuratie",     "categorie",      "json", class_mapper = (Categorie, frozenset(("naam", "hoofdcat_uuid", "bedrijven", "trefwoorden",)), "van_json"),)
        hoofdcategorieen=   open_json("gegevens\\configuratie",     "hoofdcategorie", "json", class_mapper = (HoofdCategorie, frozenset(("naam", "type")), "van_json"),)
        locaties        =   open_json("gegevens\\configuratie",     "locatie",        "json", class_mapper = (Locatie, frozenset(("naam", "land_uuid", "breedtegraad", "lengtegraad", "synoniemen")), "van_json"),)
        landen          =   open_json("gegevens\\configuratie",     "land",           "json", class_mapper = (Land, frozenset(("naam", "iso_3166_1_alpha_3", "synoniemen")), "van_json"),)
        
        return pd.DataFrame([transactie_rij for transactie_rij in [transactie.naar_tabel(
            personen,
            bedrijven,
            bankrekeningen,
            banken,
            cpsps,
            categorieen,
            hoofdcategorieen,
            locaties,
            landen,
        ) for transactie in self.transactie_lijst] if transactie_rij is not None])
        
class Bankrekening(Rekening): 
    
    def __init__(
        self,
        naam               :   str,
        bank_uuid          :   str,
        pad                :   str,
        rekeningnummer     :   str,
        uuid               :   str,
        actief_van         :   dt.datetime, 
        iban               :   str         =   None,
        transacties        :   dict        =   None,
        actief             :   bool        =   True,
        actief_tot         :   dt.datetime =   None,
        ):
        
        super().__init__(
            naam            =   naam,
            uuid            =   uuid,
            actief_van      =   actief_van,
            transacties     =   transacties,
            actief          =   actief,
            actief_tot      =   actief_tot,
            )
        
        self.bank_uuid          =   bank_uuid
        self.pad                =   pad
        self.rekeningnummer     =   rekeningnummer
        self.iban               =   iban
    
    @classmethod
    def openen(
        cls,
        bankrekening_uuid  :   str,
        ):
        
        eigen_bankrekeningen        =   open_json("gegevens\\configuratie", "bankrekening", "json")
        
        bankrekening_dict           =   {}
        
        bankrekening_dict["naam"]                   =   eigen_bankrekeningen[bankrekening_uuid]["naam"]
        bankrekening_dict["bank_uuid"]              =   eigen_bankrekeningen[bankrekening_uuid]["bank_uuid"]
        bankrekening_dict["pad"]                    =   eigen_bankrekeningen[bankrekening_uuid]["pad"]
        bankrekening_dict["uuid"]                   =   bankrekening_uuid
        bankrekening_dict["actief_van"]             =   dt.datetime.strptime(eigen_bankrekeningen[bankrekening_uuid]["actief_van"], "%Y-%m-%d").date()
        if "rekeningnummer" in eigen_bankrekeningen[bankrekening_uuid].keys():
            bankrekening_dict["rekeningnummer"]     =   eigen_bankrekeningen[bankrekening_uuid]["rekeningnummer"]
        if "iban" in eigen_bankrekeningen[bankrekening_uuid].keys():
            bankrekening_dict["iban"]               =   eigen_bankrekeningen[bankrekening_uuid]["iban"]
        if "actief_tot" in eigen_bankrekeningen[bankrekening_uuid].keys():
            bankrekening_dict["actief_tot"]         =   dt.datetime.strptime(eigen_bankrekeningen[bankrekening_uuid]["actief_tot"], "%Y-%m-%d").date()
            bankrekening_dict["actief"]             =   False
        
        bankrekening_dict["transacties"]            =   open_json("gegevens\\rekeningen", bankrekening_uuid, "json", class_mapper = (Transactie, frozenset(("index", "bedrag", "beginsaldo", "eindsaldo", "transactiemethode", "datumtijd", "dagindex", "cat_uuid", "uuid", "details", "derde_uuid",)), "van_json"),)
        
        return cls(**bankrekening_dict)
    
    def verwerken_maand(
        self,
        jaar : int,
        maand : int,
        ):
        
        bankexport          =   pd.read_excel(f"{self.pad}\\digitaal\\{jaar}-{maand:02}.xlsx")
        bankexport.columns  =   [col.casefold() for col in bankexport.columns]
        
        for _, rij in bankexport.iterrows():
            transactie  =   Transactie.van_bankexport(rij)
            print(transactie)
            print("")
            transactie.aanvullen()
            transactie.opdracht()
            self.toevoegen_transactie(transactie)
    
    @property
    def bank(self) -> str:
        banken  =   open_json("gegevens\\derden", "bank", "json", class_mapper = (Bank, frozenset(("naam", "iban", "rekeningnummer", "synoniemen", "bic",)), "van_json"),)
        return banken[self.bank_uuid]
    
    def toevoegen_transactie(
        self,
        transactie : Transactie,
        ):
        
        if not transactie.beginsaldo == self.transactie_lijst[-1].eindsaldo:
            raise ValueError(f"beginsaldo {transactie.beginsaldo} moet gelijk zijn aan eindsaldo laatste transactie {self.transactie_lijst[-1].eindsaldo}")
        
        if not transactie.eindsaldo == transactie.beginsaldo + transactie.bedrag:
            raise ValueError(f"eindsaldo {transactie.eindsaldo} is ongelijk aan de som van beginsaldo {transactie.beginsaldo} en bedrag {transactie.bedrag}")
        
        uuid    =   str(uuid4())
        
        if transactie.cat_uuid    ==   "1e8fd286-4cdd-4836-a1c5-7e815123ea25":
            bankrekening_ander  =   Bankrekening.openen(transactie.derde_uuid)
            for ander_transactie_uuid, ander_transactie in bankrekening_ander.transacties.items():
                if ander_transactie.cat_uuid == "1e8fd286-4cdd-4836-a1c5-7e815123ea25" and transactie.datumtijd == ander_transactie.datumtijd and transactie.bedrag == -ander_transactie.bedrag and ander_transactie_uuid not in self.transacties.keys():
                    uuid    =   ander_transactie_uuid
        
        transactie.index    =   len(self.transactie_lijst)
        transactie.dagindex =   len([_transactie for _transactie in self.transactie_lijst if _transactie.datumtijd.date() == transactie.datumtijd.date()])
        
        self.transacties[uuid]  =   transactie
        return self

class Lening(Rekening):
    
    def __init__(
        self,
        naam                :   str,
        schuldeiser_uuid    :   str,
        uuid                :   str,
        actief_van          :   dt.datetime, 
        transacties         :   dict                =   None,
        actief              :   bool                =   True,
        actief_tot          :   dt.datetime         =   None,
        rente               :   Dict[str, float]    =   None,
        ):
            
            super().__init__(
                naam            =   naam,
                uuid            =   uuid,
                actief_van      =   actief_van,
                transacties     =   transacties,
                actief          =   actief,
                actief_tot      =   actief_tot,
                )
            
            self.schuldeiser_uuid   =   schuldeiser_uuid
            self.rente              =   rente
    
    @classmethod
    def openen(cls,
        lening_uuid      :   str,
        ):
        
        leningen    =   open_json("gegevens\\configuratie", "lening", "json")
        
        lening_dict =   {}
        
        lening_dict["naam"]             =   leningen[lening_uuid]["naam"]
        lening_dict["schuldeiser_uuid"] =   leningen[lening_uuid]["schuldeiser_uuid"]
        lening_dict["uuid"]             =   lening_uuid
        lening_dict["actief_van"]       =   dt.datetime.strptime(leningen[lening_uuid]["actief_van"], "%Y-%m-%d").date()
        if "actief_tot" in leningen[lening_uuid].keys():
            lening_dict["actief_tot"]   =   dt.datetime.strptime(leningen[lening_uuid]["actief_tot"], "%Y-%m-%d").date()
            lening_dict["actief"]       =   False
        
        lening_dict["transacties"]      =   open_json("gegevens\\rekeningen", lening_uuid, "json", class_mapper = (Transactie, frozenset(("index", "bedrag", "beginsaldo", "eindsaldo", "transactiemethode", "datumtijd", "dagindex", "cat_uuid", "uuid", "details", "derde_uuid",)), "van_json"),)
        
        return cls(**lening_dict)