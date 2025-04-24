import datetime as dt
import locale
import re
from typing import Dict, Tuple, List, Any
from uuid import uuid4

import numpy as np
import pandas as pd
import xarray as xr

from grienetsiis import open_json, opslaan_json, invoer_validatie, invoer_kiezen
from .categorie import Categorie, HoofdCategorie
from .derden import Persoon, Bedrijf, Derde, Bank, Cpsp
from .gereedschap import iban_zoeker
from .locatie import Land, Locatie


locale.setlocale(locale.LC_ALL, "nl_NL.UTF-8")

class Transactie:
    
    def __init__(
        self,
        bedrag             : int,
        beginsaldo         : int,
        eindsaldo          : int,
        transactiemethode  : str,
        datumtijd          : dt.datetime,
        cat_uuid           : str,
        derde_uuid         : str,
        index              : int    =   0,
        dagindex           : int    =   0,
        details            : dict   =   None,
        tijdelijk          : dict   =   None,
        ):
        
        assert eindsaldo == beginsaldo + bedrag
        
        self.index              =   index
        self.bedrag             =   bedrag
        self.beginsaldo         =   beginsaldo
        self.eindsaldo          =   eindsaldo
        self.transactiemethode  =   transactiemethode
        self.datumtijd          =   datumtijd
        self.dagindex           =   dagindex
        self.cat_uuid           =   cat_uuid
        self.derde_uuid         =   derde_uuid
        self.details            =   dict() if details is None else details
        self.tijdelijk          =   dict() if tijdelijk is None else tijdelijk
    
    def __repr__(self):
        
        richting    =   "uitgave" if self.bedrag < 0 else "inkomst"
        datumtijd   =   self.datumtijd.strftime("%A %d %B %Y") if self.datumtijd.time() == dt.time(0,0) else self.datumtijd.strftime("%A %d %B %Y om %H:%M")
        lijn_transactie     =   f"{richting} van {self.toon_bedrag()} op {datumtijd},"
        
        derde   =   self.derde()
        
        if self.transactiemethode == "pinbetaling" or self.transactiemethode == "geldopname":
            
            locatie =   self.locatie()
            land    =   self.land()
            
            if locatie is not None:
                toon_locatie = locatie.naam
            else:
                toon_locatie = self.tijdelijk["locatie_oud"]
                
            if land is not None:
                toon_land = land.naam
            else:
                toon_land = self.tijdelijk["land_oud"]
            
            lijn_derde  =   f"aan \"{derde.naam}\" per {self.transactiemethode} in {toon_locatie} ({toon_land})"
        elif self.transactiemethode == "bankkosten" or self.transactiemethode == "rente":
            lijn_derde  =   f"voor {self.transactiemethode}"
        else:
            if richting    ==  "uitgave":
                richtingswoord  =   "aan"
            else:
                richtingswoord  =   "van"
            
            if isinstance(derde, Persoon):
                toon_derde  =   f"persoon \"{derde.naam}\"" if derde.groep == "ongegroepeerd" else f"persoon \"{derde.naam}\" ({derde.groep})"
            elif isinstance(derde, Derde): # zowel Bedrijf als Bank
                toon_derde  =   f"bedrijf \"{derde.naam}\""
            else:
                toon_derde  =   f"bankrekening \"{derde["naam"]}\"" 
            
            medium  =   self.medium()
            
            if medium is None:
                toon_medium     =   ""
            else:
                toon_medium     =   f" (via {medium.naam})"
            
            if "betalingsomschrijving" in self.details.keys():
                lijn_derde  =   f"{richtingswoord} {toon_derde} per {self.transactiemethode}{toon_medium} voor \"{self.details["betalingsomschrijving"]}\""   
            else:
                lijn_derde  =   f"{richtingswoord} {toon_derde} per {self.transactiemethode}{toon_medium}"
        
        if self.cat_uuid is not None:
            lijn_categorie  =   f"hoofdcategorie: {self.hoofdcategorie().naam}, categorie: {self.categorie().naam}"
            return f"\t{lijn_transactie}\n\t{lijn_derde}\n\t{lijn_categorie}"
        else:
            return f"\t{lijn_transactie}\n\t{lijn_derde}"
    
    def toon_bedrag(self):
        
        muntsoorten         =   open_json("gegevens\\configuratie", "muntsoort", "json")
        
        def toon_bedrag_iso(bedrag, valuta_iso):
            
            muntsoort     =   muntsoorten[valuta_iso]
            
            if muntsoort["ervoor"]:
                return f"{muntsoort["symbool"]}{" "*muntsoort["spatie"]}{bedrag}"
            else:
                return f"{bedrag}{" "*muntsoort["spatie"]}{muntsoort["symbool"]}"
        
        bedrag_euro         =   abs(self.bedrag / 100)
        
        bedrag_euro_print   =   str(int(bedrag_euro))+",- " if bedrag_euro % 1 == 0 else f"{bedrag_euro:.2f}".replace(".",",")
        regel_euro_print    =   toon_bedrag_iso(bedrag_euro_print, "eur")
        
        if "valuta_iso" in self.details.keys():
            
            bedrag_valuta       =   abs(self.details["valuta_bedrag"] / 100)
            bedrag_valuta_print =   str(int(bedrag_valuta))+",- " if bedrag_valuta % 1 == 0 else f"{bedrag_valuta:.2f}".replace(".",",")
            regel_valuta_print  =   toon_bedrag_iso(bedrag_valuta_print, self.details["valuta_iso"])
            return f"{regel_euro_print} ({regel_valuta_print})"
        else:
            return regel_euro_print
    
    @classmethod
    def van_json(
        cls,
        **transactie_dict: dict,
        ):
        
        if len(transactie_dict["datumtijd"]) == 10:
            datumtijd   =   dt.datetime.strptime(transactie_dict["datumtijd"], "%Y-%m-%d")
        else:
            datumtijd   =   dt.datetime.strptime(transactie_dict["datumtijd"], "%Y-%m-%dT%H:%M")
        
        return cls(
                    index               =   transactie_dict["index"],
                    bedrag              =   transactie_dict["bedrag"],
                    beginsaldo          =   transactie_dict["beginsaldo"],
                    eindsaldo           =   transactie_dict["eindsaldo"],
                    transactiemethode   =   transactie_dict["transactiemethode"],
                    datumtijd           =   datumtijd,
                    dagindex            =   transactie_dict["dagindex"],
                    cat_uuid            =   transactie_dict["cat_uuid"],
                    derde_uuid          =   transactie_dict["derde_uuid"],
                    details             =   transactie_dict["details"] if "details" in transactie_dict.keys() else None,
                    )
    
    def naar_json(self):
        
        if self.datumtijd.minute == 0 and self.datumtijd.hour == 0:
            datumtijd   =   dt.datetime.strftime(self.datumtijd, "%Y-%m-%d")
        else:
            datumtijd   =   dt.datetime.strftime(self.datumtijd, "%Y-%m-%dT%H:%M")
        
        if self.details == {}:
            return {
                    "index":                self.index,
                    "bedrag":               self.bedrag,
                    "beginsaldo":           self.beginsaldo,
                    "eindsaldo":            self.eindsaldo,
                    "transactiemethode":    self.transactiemethode,
                    "datumtijd":            datumtijd,
                    "dagindex":             self.dagindex,
                    "cat_uuid":             self.cat_uuid,
                    "derde_uuid":           self.derde_uuid,
                    }
        else:
            return {
                    "index":                self.index,
                    "bedrag":               self.bedrag,
                    "beginsaldo":           self.beginsaldo,
                    "eindsaldo":            self.eindsaldo,
                    "transactiemethode":    self.transactiemethode,
                    "datumtijd":            datumtijd,
                    "dagindex":             self.dagindex,
                    "cat_uuid":             self.cat_uuid,
                    "derde_uuid":           self.derde_uuid,
                    "details":              self.details,
                    }
    
    def naar_tabel(
        self,
        personen        :   Dict[str, Persoon]          =   None,
        bedrijven       :   Dict[str, Bedrijf]          =   None,
        bankrekeningen  :   Dict[str, Any]              =   None,
        banken          :   Dict[str, Bank]             =   None,
        cpsps           :   Dict[str, Cpsp]             =   None,
        categorieen     :   Dict[str, Categorie]        =   None,
        hoofdcategorieen:   Dict[str, HoofdCategorie]   =   None,
        locaties        :   Dict[str, Locatie]          =   None,
        landen          :   Dict[str, Land]             =   None,
        ) -> Dict[str, Any]:
        
        personen            =   personen            if personen         is not None else open_json("gegevens\\derden",          "persoon",          "json", class_mapper = (Persoon, frozenset(("naam", "iban", "rekeningnummer", "giro", "groep",)), "van_json"),)
        bedrijven           =   bedrijven           if bedrijven        is not None else open_json("gegevens\\derden",          "bedrijf",          "json", class_mapper = (Bedrijf, frozenset(("naam", "iban", "rekeningnummer", "giro", "synoniemen", "uitsluiten", "cat_uuid",)), "van_json"),)
        bankrekeningen      =   bankrekeningen      if bankrekeningen   is not None else open_json("gegevens\\configuratie",    "bankrekening",     "json")
        banken              =   banken              if banken           is not None else open_json("gegevens\\derden",          "bank",             "json", class_mapper = (Bank, frozenset(("naam", "iban", "rekeningnummer", "synoniemen", "bic",)), "van_json"),)
        cpsps               =   cpsps               if cpsps            is not None else open_json("gegevens\\derden",          "cpsp",             "json", class_mapper = (Cpsp, frozenset(("naam", "iban", "rekeningnummer", "giro", "synoniemen", "uitsluiten",)), "van_json"),)
        categorieen         =   categorieen         if categorieen      is not None else open_json("gegevens\\configuratie",    "categorie",        "json", class_mapper = (Categorie, frozenset(("naam", "hoofdcat_uuid", "bedrijven", "trefwoorden",)), "van_json"),)
        hoofdcategorieen    =   hoofdcategorieen    if hoofdcategorieen is not None else open_json("gegevens\\configuratie",    "hoofdcategorie",   "json", class_mapper = (HoofdCategorie, frozenset(("naam", "type")), "van_json"),)
        locaties            =   locaties            if locaties         is not None else open_json("gegevens\\configuratie",    "locatie",          "json", class_mapper = (Locatie, frozenset(("naam", "land_uuid", "breedtegraad", "lengtegraad", "synoniemen")), "van_json"),)
        landen              =   landen              if landen           is not None else open_json("gegevens\\configuratie",    "land",             "json", class_mapper = (Land, frozenset(("naam", "iso_3166_1_alpha_3", "synoniemen")), "van_json"),)
        
        derde = self.derde(
            personen,
            bedrijven,
            bankrekeningen,
            banken,
            cpsps,
            )
        
        locatie = self.locatie(
            locaties,
        )
        
        land = self.land(
            locaties,
            land,
        )
        
        return {
            "index":                self.index,
            "bedrag":               self.bedrag / 100,
            "bedrag_abs":           abs(self.bedrag / 100),
            "beginsaldo":           self.beginsaldo / 100,
            "eindsaldo":            self.eindsaldo / 100,
            "transactiemethode":    self.transactiemethode,
            "datumtijd":            self.datumtijd,
            "hoofdcategorie":       self.hoofdcategorie(categorieen, hoofdcategorieen).naam,
            "categorie":            self.categorie(categorieen).naam,
            "derde":                derde["naam"]  if isinstance(derde, dict) else derde.naam,
            "type":                 "bankrekening" if isinstance(derde, dict) else derde.type,
            "locatie":              locatie.naam if locatie is not None else None,
            "breedtegraad":         locatie.breedtegraad if locatie is not None else None,
            "lengtegraad":          locatie.lengtegraad if locatie is not None else None,
            "land":                 land.naam if land is not None else None,
            }
    
    @classmethod
    def van_bankexport(
        cls, 
        rij: pd.core.series.Series,
        ):
        
        if rij.muntsoort.casefold() != "eur":
            raise NotImplementedError
        
        bedrag          =   int(round(100 * rij.transactiebedrag))
        beginsaldo      =   int(round(100 * rij.beginsaldo))
        eindsaldo       =   int(round(100 * rij.eindsaldo))
        datumtijd       =   dt.datetime.strptime(str(rij.rentedatum), "%Y%m%d")
        
        details         =   {}
        tijdelijk       =   {}
        
        if rij.omschrijving.casefold().startswith("rente"):
            
            transactiemethode   =   "rente"
            cat_uuid            =   "b123402b-7d55-4eb1-9eac-c41df3c784c4"
            derde_uuid          =   "7fe30da2-dfb9-4d07-8d85-6132cf0c8816"
            details["betalingsomschrijving"]    =   rij.omschrijving.strip()
        
        elif rij.omschrijving.casefold().startswith("BEA, Betaalpas".casefold()) or rij.omschrijving.casefold().startswith("GEA, Betaalpas".casefold()):
            
            patroon_pinpas      =   re.compile(r"(?i)^(?:B|G)EA, Betaalpas\s+(?P<derde_naam>.*),PAS(?P<pasnummer>\d{3})\s+NR:(?P<terminal>.*),?\s+(?P<datumtijd>\d{2}.\d{2}.\d{2}\/\d{2}(.?:|.)\d{2})\s+(?P<locatie>.*)$")
            resultaat_pinpas    =   patroon_pinpas.match(rij.omschrijving).groupdict()
            
            datumtijd               =   dt.datetime.strptime(resultaat_pinpas.get("datumtijd"), "%d.%m.%y/%H:%M") if ":" in resultaat_pinpas.get("datumtijd") else dt.datetime.strptime(resultaat_pinpas.get("datumtijd"), "%d.%m.%y/%H.%M")
            
            details["pasnummer"]    =   str(resultaat_pinpas.get("pasnummer").strip())
            details["terminal"]     =   resultaat_pinpas.get("terminal").strip()
            
            if "land:" in resultaat_pinpas.get("locatie"):
                if ", land:" in resultaat_pinpas.get("locatie"):
                    locatie_oud     =   resultaat_pinpas.get("locatie").split(", land:")[0].strip()
                    land_oud        =   resultaat_pinpas.get("locatie").split(", land:")[1].strip()
                else:
                    locatie_oud     =   resultaat_pinpas.get("locatie").split("land:")[0].strip()
                    land_oud        =   resultaat_pinpas.get("locatie").split("land:")[1].strip()
            else:
                locatie_oud         =   locatie = resultaat_pinpas.get("locatie").strip()
                land_oud            =   "Nederland"
            
            details["locatie_uuid"] =   cls.verwerken_locatie(
                locatie_oud = locatie_oud,
                land_oud = land_oud,
                )
            
            tijdelijk["locatie_oud"]    =   locatie_oud
            tijdelijk["land_oud"]       =   land_oud
            
            derde_uuid, cat_uuid    =   cls.verwerken_derde_uuid(naam = resultaat_pinpas.get("derde_naam"))
            
            if rij.omschrijving.casefold().startswith("BEA, Betaalpas".casefold()):
                transactiemethode   =   "pinbetaling" 
            else:
                transactiemethode   =   "pinbetaling" 
                cat_uuid            =   "6507437f-f21a-4458-bbdd-1ed7c2f5cebd"
            
            tijdelijk["naam"]       =   resultaat_pinpas.get("derde_naam")
        
        elif rij.omschrijving.casefold().startswith("SEPA Overboeking".casefold()) or rij.omschrijving.casefold().startswith("/TRTP/SEPA OVERBOEKING/".casefold()):
            
            if rij.omschrijving.startswith("SEPA Overboeking"):
                if "Betalingskenm.:" in rij.omschrijving or "Kenmerk:" in rij.omschrijving:
                    if "Betalingskenm.:" in rij.omschrijving:
                        patroon_overboeking =   re.compile(r"(?i)^SEPA Overboeking\s*IBAN:\s(?P<iban>\S*)\s*BIC:\s(?P<bic>\S*)\s*Naam:\s(?P<naam>.*)\s*Betalingskenm.:\s(?P<betalingskenmerk>.*)$")
                    else:
                        patroon_overboeking =   re.compile(r"(?i)^SEPA Overboeking\s*IBAN:\s(?P<iban>\S*)\s*BIC:\s(?P<bic>\S*)\s*Naam:\s(?P<naam>.*)\s*Omschrijving:\s(?P<betalingsomschrijving>.*)\s*Kenmerk:\s(?P<betalingskenmerk>.*)$")
                elif "Omschrijving:" in rij.omschrijving:
                    patroon_overboeking     =   re.compile(r"(?i)^SEPA Overboeking\s*IBAN:\s(?P<iban>\S*)\s*BIC:\s(?P<bic>\S*)\s*Naam:\s(?P<naam>.*)\s*Omschrijving:\s(?P<betalingsomschrijving>.*)$")
                else:
                    patroon_overboeking     =   re.compile(r"(?i)^SEPA Overboeking\s*IBAN:\s(?P<iban>\S*)\s*BIC:\s(?P<bic>\S*)\s*Naam:\s(?P<naam>.*)$")
            else:
                if "/REMI/" in rij.omschrijving:
                    patroon_overboeking     =   re.compile(r"(?i)^\/TRTP\/SEPA OVERBOEKING\/IBAN\/(?P<iban>.*)\/BIC\/(?P<bic>.*)\/NAME\/(?P<naam>.*)\/REMI\/(?P<betalingsomschrijving>.*)\/EREF\/(?P<betalingskenmerk>.*)$")
                else:
                    patroon_overboeking     =   re.compile(r"(?i)^\/TRTP\/SEPA OVERBOEKING\/IBAN\/(?P<iban>.*)\/BIC\/(?P<bic>.*)\/NAME\/(?P<naam>.*)\/EREF\/(?P<betalingskenmerk>.*)$")
            resultaat_overboeking   =   patroon_overboeking.match(rij.omschrijving).groupdict()
            
            iban                    =   resultaat_overboeking.get("iban").strip()
            bic                     =   resultaat_overboeking.get("bic").strip()
            naam                    =   resultaat_overboeking.get("naam").strip()
            betalingsomschrijving   =   resultaat_overboeking.get("betalingsomschrijving", "").strip()
            betalingskenmerk        =   resultaat_overboeking.get("betalingskenmerk", "").strip()
            
            if betalingskenmerk != "" or betalingskenmerk.casefold() != "NOTPROVIDED".casefold():
                details["betalingskenmerk"]     =   betalingskenmerk
            
            if "Tikkie".casefold() in betalingsomschrijving.casefold():
                
                transactiemethode       =   "betaalverzoek"
                
                bank_uuid               =   "7fe30da2-dfb9-4d07-8d85-6132cf0c8816"
                details["bank_uuid"]    =   bank_uuid
                
                patroon_tikkie          =   re.compile(r"(?i)^Tikkie ID (?:[0-9 ]+), ?(?P<betalingsomschrijving_tikkie>.+), ?Van ?(?P<derde_naam>[\w\s\.]+),? ?(?P<derde_iban>.*)?$")
                resultaat_tikkie        =   patroon_tikkie.match(betalingsomschrijving).groupdict()
                
                derde_naam              =   resultaat_tikkie.get("derde_naam")
                derde_iban              =   iban_zoeker(resultaat_tikkie.get("derde_iban"))
                
                derde_uuid, cat_uuid    =   cls.verwerken_derde_uuid(iban = derde_iban, naam = derde_naam)
                
                details["betalingsomschrijving"]    =   resultaat_tikkie.get("betalingsomschrijving_tikkie")
                
                banken   =   open_json("gegevens\\derden", "bank", "json", class_mapper = (Bank, frozenset(("naam", "iban", "rekeningnummer", "synoniemen", "bic",)), "van_json"),)
                
                if iban not in banken[bank_uuid].iban:
                    banken[bank_uuid].iban.append(iban)
                    opslaan_json(banken, "gegevens\\derden", "bank", "json", {"Bank": "naar_json"})
                
            else:
                transactiemethode       =   "overboeking"
                
                if not betalingsomschrijving == "":
                    details["betalingsomschrijving"]    =   betalingsomschrijving
                
                cpsp_uuid                   =   cls.verwerken_cpsp_uuid(naam, iban)
                
                if cpsp_uuid is None:
                    derde_uuid, cat_uuid    =   cls.verwerken_derde_uuid(iban = iban, naam = naam)
                    tijdelijk["derde_iban"] =   iban
                else:
                    derde_uuid, cat_uuid    =   cls.verwerken_derde_uuid(naam = naam)
                    details["cpsp_uuid"]    =   cpsp_uuid
                    tijdelijk["medium_iban"]=   iban
                
                details     =   cls.verwerken_inkomen(derde_uuid, datumtijd, details, bedrag)
            
            tijdelijk["naam"]   =   naam
            tijdelijk["bic"]    =   bic
        
        elif rij.omschrijving.casefold().startswith("SEPA iDEAL".casefold()) or rij.omschrijving.casefold().startswith("/TRTP/iDEAL/".casefold()):
            
            if rij.omschrijving.casefold().startswith("SEPA iDEAL".casefold()):
                patroon_ideal   =   re.compile(r"(?i)^SEPA iDEAL\s*IBAN:\s(?P<iban>.*)\s*BIC:\s(?P<bic>.*)\s*Naam:\s(?P<naam>.*)\s*Omschrijving:\s(?P<betalingsomschrijving>.*)\s*Kenmerk:\s(?P<datumtijd>\d{2}-\d{2}-\d{4} \d{2}:\d{2})\s(?P<betalingskenmerk>.*)$")
            else:
                patroon_ideal   =   re.compile(r"(?i)^\/TRTP\/iDEAL\/IBAN\/(?P<iban>.*)\/BIC\/(?P<bic>.*)\/NAME\/(?P<naam>.*)\/REMI\/(?P<betalingsomschrijving>.*)\/EREF\/(?P<datumtijd>\d{2}-\d{2}-\d{4} \d{2}:\d{2}) (?P<betalingskenmerk>.*)$")
            
            resultaat_ideal     =   patroon_ideal.match(rij.omschrijving).groupdict()
            
            iban                    =   resultaat_ideal.get("iban").strip()
            bic                     =   resultaat_ideal.get("bic").strip()
            naam                    =   resultaat_ideal.get("naam").strip()
            betalingsomschrijving   =   resultaat_ideal.get("betalingsomschrijving", "").strip()
            datumtijd               =   dt.datetime.strptime(resultaat_ideal.get("datumtijd").strip(), "%d-%m-%Y %H:%M")
            betalingskenmerk        =   resultaat_ideal.get("betalingskenmerk", "").strip()
            
            if "betaalverzoek" in naam.casefold() or "betaalverzoek" in betalingsomschrijving.casefold() or "tikkie" in naam.casefold() or "tikkie" in betalingsomschrijving.casefold() or "bunq b.v." in naam.casefold() or "abn amro" in naam.casefold():
                
                transactiemethode           =   "betaalverzoek"
                
                bank_uuid, derde_iban, derde_naam, betalingsomschrijving    =   cls.verwerken_bank_uuid(naam = naam, betalingsomschrijving = betalingsomschrijving, betalingskenmerk = betalingskenmerk, bank_iban = iban)
                derde_uuid, cat_uuid                                        =   cls.verwerken_derde_uuid(iban = derde_iban, naam = derde_naam)
                
                details["bank_uuid"]                =   bank_uuid
                
                details["betalingskenmerk"]         =   betalingskenmerk
                tijdelijk["derde_iban"]             =   derde_iban
                tijdelijk["derde_naam"]             =   derde_naam
            
            else:
                
                transactiemethode                   =   "ideal"
                
                details["betalingsomschrijving"]    =   betalingsomschrijving
                details["betalingskenmerk"]         =   betalingskenmerk
                
                cpsp_uuid                   =   cls.verwerken_cpsp_uuid(naam, iban)
                
                if cpsp_uuid is None:
                    derde_uuid, cat_uuid    =   cls.verwerken_derde_uuid(iban = iban, naam = naam)
                    tijdelijk["derde_iban"] =   iban
                else:
                    derde_uuid, cat_uuid    =   cls.verwerken_derde_uuid(naam = naam)
                    details["cpsp_uuid"]    =   cpsp_uuid
                    tijdelijk["medium_iban"]=   iban
            
            if not betalingsomschrijving == "":
                    details["betalingsomschrijving"]    =   betalingsomschrijving
            tijdelijk["naam"]   =   naam
            tijdelijk["bic"]    =   bic
        
        elif "SEPA Incasso algemeen doorlopend".casefold() in rij.omschrijving.casefold():
            
            transactiemethode       =   "incasso"
            
            if rij.omschrijving.casefold().startswith("/trtp/".casefold()):
                patroon_incasso     =   re.compile(r"(?i)^\/TRTP\/SEPA Incasso algemeen doorlopend\/CSID\/(?P<incassant>.*)\/NAME\/(?P<naam>.*)\/MARF\/(?P<machtiging>.*)\/REMI\/(?P<betalingsomschrijving>.*)\/IBAN\/(?P<iban>.*)\/BIC\/(?P<bic>.*)\/EREF\/(?P<betalingskenmerk>.*)$")
            else:
                if "Kenmerk:".casefold() in rij.omschrijving.casefold():
                    patroon_incasso     =   re.compile(r"(?i)^SEPA Incasso algemeen doorlopend\s*Incassant:\s(?P<incassant>.*)\s*Naam:\s(?P<naam>.*)\s*Machtiging:\s(?P<machtiging>.*)\s*Omschrijving:\s(?P<betalingsomschrijving>.*)\s*IBAN:\s(?P<iban>.*)\s*Kenmerk:\s(?P<betalingskenmerk>.*)$")
                elif "IBAN:".casefold() in rij.omschrijving.casefold():
                    patroon_incasso     =   re.compile(r"(?i)^SEPA Incasso algemeen doorlopend\s*Incassant:\s(?P<incassant>.*)\s*Naam:\s(?P<naam>.*)\s*Machtiging:\s(?P<machtiging>.*)\s*Omschrijving:\s(?P<betalingsomschrijving>.*)\s*IBAN:\s(?P<iban>.*)$")
                else:
                    patroon_incasso     =   re.compile(r"(?i)^SEPA Incasso algemeen doorlopend\s*Incassant:\s(?P<incassant>.*)\s*Naam:\s(?P<naam>.*)\s*Machtiging:\s(?P<machtiging>.*)\s*Omschrijving:\s(?P<betalingsomschrijving>.*)$")
            resultaat_incasso       =   patroon_incasso.match(rij.omschrijving).groupdict()
            
            incassant               =   resultaat_incasso.get("incassant").strip()
            naam                    =   resultaat_incasso.get("naam").strip()
            machtiging              =   resultaat_incasso.get("machtiging").strip()
            betalingsomschrijving   =   resultaat_incasso.get("betalingsomschrijving").strip()
            iban                    =   resultaat_incasso.get("iban", "").strip()
            bic                     =   resultaat_incasso.get("bic", "").strip()
            betalingskenmerk        =   resultaat_incasso.get("betalingskenmerk", "").strip()
            
            details["incassant"]                =   incassant
            details["machtiging"]               =   machtiging
            details["betalingsomschrijving"]    =   betalingsomschrijving
            details["betalingskenmerk"]         =   betalingskenmerk
            
            cpsp_uuid                   =   cls.verwerken_cpsp_uuid(naam, iban)
            
            if cpsp_uuid is None:
                derde_uuid, cat_uuid    =   cls.verwerken_derde_uuid(iban = iban, naam = naam)
                tijdelijk["derde_iban"] =   iban
            else:
                derde_uuid, cat_uuid    =   cls.verwerken_derde_uuid(naam = naam)
                details["cpsp_uuid"]    =   cpsp_uuid
                tijdelijk["medium_iban"]=   iban
        
            tijdelijk["naam"]   =   naam
            tijdelijk["bic"]    =   bic
        
        elif rij.omschrijving.casefold().startswith("ABN AMRO".casefold()):
            
            transactiemethode   =   "bankkosten"
            
            derde_uuid          =   "7fe30da2-dfb9-4d07-8d85-6132cf0c8816"
            cat_uuid            =   "d188a43a-fb79-4a83-844d-6feb78855924"
            details["betalingsomschrijving"]    =   rij.omschrijving
        
        else:
            print(rij.omschrijving)
            raise NotImplementedError
        
        if cat_uuid is None and "betalingsomschrijving" in details.keys():
            cat_uuid = cls.verwerken_cat_uuid(details.get("betalingsomschrijving"))
        
        return cls(bedrag               =   bedrag,
                   beginsaldo           =   beginsaldo,
                   eindsaldo            =   eindsaldo,
                   transactiemethode    =   transactiemethode,
                   datumtijd            =   datumtijd,
                   cat_uuid             =   cat_uuid,
                   derde_uuid           =   derde_uuid,
                   details              =   details,
                   tijdelijk            =   tijdelijk,
                   )
    
    @staticmethod
    def verwerken_derde_uuid(
        iban: str = "",
        naam: str = "",
        ) -> Tuple[str | None, str | None]:
        
        personen                =   open_json("gegevens\\derden", "persoon",        "json", class_mapper = (Persoon, frozenset(("naam", "iban", "rekeningnummer", "giro", "groep",)), "van_json"),)
        bedrijven               =   open_json("gegevens\\derden", "bedrijf",        "json", class_mapper = (Bedrijf, frozenset(("naam", "iban", "rekeningnummer", "giro", "synoniemen", "uitsluiten", "cat_uuid",)), "van_json"),)
        bankrekeningen          =   open_json("gegevens\\configuratie", "bankrekening",   "json")
        
        if iban != "":
            for uuid_bankrekening, bankrekening in bankrekeningen.items():
                if iban == bankrekening.get("iban", "dummy"):
                    derde_uuid  =   uuid_bankrekening
                    cat_uuid    =   "1e8fd286-4cdd-4836-a1c5-7e815123ea25"
                    return derde_uuid, cat_uuid
            
            for uuid_persoon, persoon in personen.items():
                if iban in getattr(persoon, "iban", "dummy"):
                    derde_uuid  =   uuid_persoon
                    return derde_uuid, None
            
            for uuid_bedrijf, bedrijf in bedrijven.items():
                if iban in getattr(bedrijf, "iban", "dummy"):
                    derde_uuid  =   uuid_bedrijf
                    cat_uuid    =   getattr(bedrijf, "cat_uuid", None)
                    return derde_uuid, cat_uuid
        
        if naam != "":
            for uuid_bedrijf, bedrijf in bedrijven.items():
                if naam.casefold() == getattr(bedrijf, "naam").casefold() or any([naam.casefold() == synoniem for synoniem in getattr(bedrijf, "synoniemen")]):
                    derde_uuid  =   uuid_bedrijf
                    cat_uuid    =   getattr(bedrijf, "cat_uuid", None)
                    return derde_uuid, cat_uuid
        
        else:
            ...
        
        return None, None
    
    @staticmethod
    def verwerken_cpsp_uuid(
        naam: str,
        iban: str,
        ) -> str | None:
        
        cpsps   =   open_json("gegevens\\derden", "cpsp", "json", class_mapper = (Cpsp, frozenset(("naam", "iban", "rekeningnummer", "giro", "synoniemen", "uitsluiten",)), "van_json"),)
        
        for cpsp_uuid, cpsp in cpsps.items():
            if cpsp.naam.casefold() in naam.casefold() or any([cpsp_synoniem.casefold() in naam.casefold() for cpsp_synoniem in cpsp.synoniemen]) or any([cpsp_iban == iban for cpsp_iban in cpsp.iban]):
                if iban not in cpsp.iban:
                    cpsps[cpsp_uuid].iban.append(iban)
                    opslaan_json(cpsps, "gegevens\\derden", "cpsp", "json", {"Cpsp": "naar_json"})
                return cpsp_uuid
        return None
    
    @staticmethod
    def verwerken_bank_uuid(
        naam: str, 
        betalingsomschrijving: str, 
        betalingskenmerk: str, 
        bank_iban: str,
        ) -> Tuple[str, str ,str ,str]:
        
        banken   =   open_json("gegevens\\derden", "bank", "json", class_mapper = (Bank, frozenset(("naam", "iban", "rekeningnummer", "synoniemen", "bic",)), "van_json"),)
        
        if "asn" in naam.casefold():
            
            bank_uuid               =   "3de40e75-c036-41f5-9e6d-112ee6b26c93"
            derde_iban              =   iban_zoeker(betalingsomschrijving)
            derde_naam              =   betalingsomschrijving.split(" ",1)[0]
            betalingsomschrijving   =   betalingsomschrijving.split(f"{derde_iban}")[1].replace(f"{derde_iban}","").strip()
        
        elif "tikkie" in betalingsomschrijving.casefold() or "tikkie" in naam.casefold() or "abn amro" in naam.casefold():
            
            bank_uuid               =   "7fe30da2-dfb9-4d07-8d85-6132cf0c8816"
            derde_iban              =   iban_zoeker(betalingsomschrijving)
            for aantal_spaties in range(betalingsomschrijving.count(" ")): # fix voor indien betalingskenmerk spaties bevat
                if betalingskenmerk in betalingsomschrijving.replace(" ", "", aantal_spaties):
                    derde_naam      =   betalingsomschrijving.replace(" ", "", aantal_spaties).split(betalingskenmerk)[1].split(derde_iban)[0].strip()
            betalingsomschrijving   =   ""
        
        elif "rabo" in naam.casefold():
            
            bank_uuid               =   "18e6fc70-35cd-4bc7-a713-29be66a177f1"
            derde_iban              =   iban_zoeker(betalingsomschrijving)
            derde_naam              =   betalingsomschrijving.split(f"{betalingskenmerk}")[1].strip()
            betalingsomschrijving   =   ""
        
        elif "bunq" in betalingsomschrijving.casefold():
            
            bank_uuid               =   "4d2d88d4-b8d3-46ca-85f4-55fa5b364bb3"
            derde_iban              =   iban_zoeker(betalingsomschrijving)
            derde_naam              =   betalingsomschrijving.split(f"{derde_iban}")[1].split(f"{betalingskenmerk}")[0].strip()
            betalingsomschrijving   =   ""
        
        elif "ingb" in betalingsomschrijving.casefold():
        
            bank_uuid               =   "cf541b4f-1fee-4562-a47b-2792d7ca42e6"
            derde_iban              =   iban_zoeker(betalingsomschrijving)
            derde_naam              =   betalingsomschrijving.split(f"{derde_iban}")[0].strip()
            betalingsomschrijving   =   betalingsomschrijving.split(f"{betalingskenmerk}")[1].split("ING")[0].strip()
        
        if bank_iban not in banken[bank_uuid].iban:
            banken[bank_uuid].iban.append(bank_iban)
            opslaan_json(banken, "gegevens\\derden", "bank", "json", {"Bank": "naar_json"})
        
        return bank_uuid, derde_iban, derde_naam, betalingsomschrijving
    
    @staticmethod
    def verwerken_locatie(
        locatie_oud: str,
        land_oud: str,
        ) -> str:
        
        locaties    =   open_json("gegevens\\configuratie", "locatie", "json", class_mapper = (Locatie, frozenset(("naam", "land_uuid", "breedtegraad", "lengtegraad", "synoniemen")), "van_json"),)
        landen      =   open_json("gegevens\\configuratie", "land",    "json", class_mapper = (Land, frozenset(("naam", "iso_3166_1_alpha_3", "synoniemen")), "van_json"),)
        
        locaties_mogelijk = []
        
        for locatie_uuid, locatie in locaties.items():
            if any(locatie_oud.casefold() == synoniem for synoniem in locatie.synoniemen) or locatie_oud.casefold() == locatie.naam.casefold():
                if any(land_oud.casefold() == synoniem for synoniem in landen[locatie.land_uuid].synoniemen) or land_oud.casefold() == landen[locatie.land_uuid].naam.casefold():
                    locaties_mogelijk.append(locatie_uuid)
        
        if len(locaties_mogelijk) == 1:
            return locaties_mogelijk[0]
        elif len(locaties_mogelijk) > 1:
            [print(locaties[locatie_uuid]) for locatie_uuid in locaties_mogelijk]
            raise NotImplementedError
        else:
            return None
        
    @staticmethod
    def verwerken_cat_uuid(
        betalingsomschrijving: str,
        ) -> str:
        
        categorieen     =   open_json("gegevens\\configuratie", "categorie", "json", class_mapper = (Categorie, frozenset(("naam", "hoofdcat_uuid", "bedrijven", "trefwoorden",)), "van_json"),)
        
        for cat_uuid, categorie in categorieen.items():
            for trefwoord in getattr(categorie, "trefwoorden"):
                if trefwoord in betalingsomschrijving.casefold():
                    return cat_uuid
        return None        
    
    @staticmethod
    def verwerken_inkomen(
        derde_uuid: str,
        datumtijd: dt.datetime.date,
        details: dict,
        bedrag: int,
        ) -> Dict[str, int]:
        
        inkomen_json    =   open_json("gegevens\\configuratie", "inkomen", "json")
        
        if derde_uuid in inkomen_json.keys():
            
            inkomen         =   inkomen_json[derde_uuid]
            salarisstrook   =   open_json(f"{inkomen["pad"]}", dt.datetime.strftime(datumtijd, "%Y-%m"), "json")
            
            if int(round(100 * salarisstrook["netPay"]["value"])) == bedrag:
                
                details["inkomen"]  =   {}
                
                for cat_uuid, trefwoorden in inkomen["inkomen"].items():
                    for salarisstrook_dict in salarisstrook["earningsData"]:
                        if any([trefwoord in salarisstrook_dict["codeName"].casefold() for trefwoord in trefwoorden]):
                            if cat_uuid not in details["inkomen"].keys():
                                details["inkomen"][cat_uuid] = 0
                            details["inkomen"][cat_uuid] += int(round(100 * salarisstrook_dict["value"]))
                
                for cat_uuid, trefwoorden in inkomen["uitgave"].items():
                    for salarisstrook_dict in salarisstrook["deductionsData"]:
                        if any([trefwoord in salarisstrook_dict["codeName"].casefold() for trefwoord in trefwoorden]):
                            if cat_uuid not in details["inkomen"].keys():
                                details["inkomen"][cat_uuid] = 0
                            details["inkomen"][cat_uuid] -= int(round(100 * salarisstrook_dict["value"]))
        
        return details
    
    def opdracht(self):     
        
        while True:
        
            opdracht    =   invoer_validatie("opdracht", str, regex = r"(?i)^(?P<opdracht>|bewerk|velden|weergeef|trefwoord|toon)(\s+(?P<veld>.*))?$")
            
            if opdracht.get("opdracht") == "":
                print()
                break
            
            elif opdracht.get("opdracht") == "toon":
                try:
                    attr =  getattr(self, opdracht.get("veld"))
                    if isinstance(attr, Derde) or isinstance(attr, Categorie) or isinstance(attr, HoofdCategorie):
                        print(getattr(attr, "naam"))
                    else:
                        print(attr)
                except:
                    continue
            
            elif opdracht.get("opdracht") == "velden":
                print(f"\n\t{"INDEX":<6}{"VELD":<35}WAARDE")
                for iveld, (veld, waarde) in enumerate(self.__dict__.items()):
                    if isinstance(waarde, dict):
                        print(f"\t{iveld:<6}{veld:<35}")
                        for subveld, subwaarde in waarde.items():
                            if isinstance(subwaarde, dict):
                                categorieen     =   open_json("gegevens\\configuratie", "categorie", "json", class_mapper = (Categorie, frozenset(("naam", "hoofdcat_uuid", "bedrijven", "trefwoorden",)), "van_json"),)
                                print(f"\t       -> {subveld:<31}")
                                for cat_uuid, bedrag in subwaarde.items():
                                    categorie   =   categorieen[cat_uuid]
                                    print(f"\t           -> {categorie.naam:<27}{bedrag}")
                            else:
                                print(f"\t       -> {subveld:<31}{subwaarde}")
                                if subveld == "cpsp_uuid":
                                    print(f"\t           -> {"medium":<27}{self.medium().naam}")
                                elif subveld == "bank_uuid":
                                    print(f"\t           -> {"bank":<27}{self.bank().naam}")
                                elif subveld == "locatie_uuid":
                                    print(f"\t           -> {"locatie":<27}{self.locatie().naam}")
                                    print(f"\t           -> {"land":<27}{self.land().naam}")
                    else:
                        print(f"\t{iveld:<6}{veld:<35}{waarde}")
                        if veld == "cat_uuid":
                            print(f"\t       -> {"hoofdcategorie":<31}{self.hoofdcategorie().naam}")
                            print(f"\t       -> {"categorie":<31}{self.categorie().naam}")
                        elif veld == "derde_uuid":
                            print(f"\t       -> {"derde":<31}{self.derde().naam}")
                            
                print("")
                continue
            
            elif opdracht.get("opdracht") == "weergeef":
                print()
                print(self)
                print()
                continue
            
            elif opdracht.get("opdracht") == "trefwoord":
                invoer_trefwoord   =   opdracht.get("veld", "")
                
                if invoer_trefwoord != "":
                    categorieen         =   open_json("gegevens\\configuratie", "categorie", "json", class_mapper = (Categorie, frozenset(("naam", "hoofdcat_uuid", "bedrijven", "trefwoorden",)), "van_json"),)
                    
                    if any([invoer_trefwoord.casefold() == trefwoord for categorie in categorieen.values() for trefwoord in getattr(categorie, "trefwoorden")]):
                        categorie   =   next(categorie for cat_uuid, categorie in categorieen.items() for trefwoord in getattr(categorie, "trefwoorden") if invoer_trefwoord.casefold() == trefwoord)
                        print(f"het trefwoord \"{invoer_trefwoord.casefold()}\" komt reeds voor bij categorie \"{categorie.naam}\"")
                        continue
                    else:
                        categorieen[self.cat_uuid].trefwoorden.append(invoer_trefwoord.casefold())
                        opslaan_json(categorieen, "gegevens\\configuratie", "categorie", "json", {"Categorie": "naar_json"})
                        print(f"het trefwoord \"{invoer_trefwoord.casefold()}\" is toegevoegd aan de categorie \"{self.categorie().naam} ({self.hoofdcategorie().naam})\"")
                        continue
                else:
                    print("vul een trefwoord in")
                    continue
                    
            elif opdracht.get("opdracht") == "bewerk":
                
                if opdracht.get("veld").casefold() == "derde":
                    self.bewerken("derde_uuid")
                    continue
                elif opdracht.get("veld").casefold() == "medium":
                    self.bewerken("cpsp_uuid")
                    continue
                elif opdracht.get("veld").casefold().startswith("cat"):
                    self.bewerken("cat_uuid")
                    continue
                elif opdracht.get("veld").casefold().startswith("loc"):
                    self.bewerken("locatie_uuid")
                    continue
                elif opdracht.get("veld").casefold().startswith("opm"):
                    self.bewerken("opmerking")
                    continue
                else:
                    print(f"veld \"{opdracht.get("veld").casefold()}\" niet herkend")
                    continue
    
    def aanvullen(self):
        
        if self.derde_uuid is None:
            self.bewerken("derde_uuid")
        
        if self.cat_uuid is None:
            self.bewerken("cat_uuid")
            
        if self.details.get("locatie_uuid", ...) is None:
            self.bewerken("locatie_uuid")
        
    def bewerken(
        self,
        veld: str,
        ):
        
        if veld == "derde_uuid":
            
            if self.derde_uuid == None:
                if "naam" in self.tijdelijk.keys():
                    print(f"derde \"{self.tijdelijk.get("naam")}\" niet automatisch toegewezen, kies een bestaande of maak een nieuwe")
                else:
                    print("derde niet automatisch toegewezen, kies een bestaande of maak een nieuwe")
            
            derde_type  =   invoer_kiezen("type derde", ["bedrijf", "persoon"])
            
            while True:
                
                print(f"kies een bestaande derde met \"zoek <zoekterm>\" of een nieuwe met \"nieuw\"")
                opdracht    =   invoer_validatie("opdracht", str, regex = r"(?i)^(?P<opdracht>nieuw|zoek)(\s+(?P<zoekterm>.*))?$")
                
                if opdracht.get("opdracht") == "nieuw":
                    
                    uuid    =   str(uuid4())
                    naam    =   invoer_validatie("naam", str, valideren = True)
                    
                    if derde_type == "bedrijf":
                        if "naam" in self.tijdelijk.keys():
                            if "derde_iban" in self.tijdelijk.keys():
                                bedrijf     =   Bedrijf(naam, iban = [self.tijdelijk.get("derde_iban")], synoniemen = [self.tijdelijk["naam"].casefold()])
                            else:
                                bedrijf     =   Bedrijf(naam, synoniemen = [self.tijdelijk["naam"].casefold()])
                        else:
                            if "derde_iban" in self.tijdelijk.keys():
                                bedrijf     =   Bedrijf(naam, iban = [self.tijdelijk.get("derde_iban")])
                            else:
                                bedrijf     =   Bedrijf(naam)
                        
                        bedrijven       =   open_json("gegevens\\derden", "bedrijf", "json", class_mapper = (Bedrijf, frozenset(("naam", "iban", "rekeningnummer", "giro", "synoniemen", "uitsluiten", "cat_uuid",)), "van_json"),)
                        bedrijven[uuid] =   bedrijf
                        self.derde_uuid =   uuid
                        opslaan_json(bedrijven, "gegevens\\derden", "bedrijf", "json", {"Bedrijf": "naar_json"})
                        break
                    else:
                        persoonsgroepen =   open_json("gegevens\\configuratie", "persoonsgroep", "json")
                        persoonsgroep   =   invoer_kiezen("persoonsgroep", persoonsgroepen)
                        
                        if "derde_iban" in self.tijdelijk.keys():
                            persoon     =   Persoon(naam, persoonsgroep, iban = [self.tijdelijk.get("derde_iban")])
                        else:
                            persoon     =   Persoon(naam, persoonsgroep)
                        
                        personen        =   open_json("gegevens\\derden", "persoon", "json", class_mapper = (Persoon, frozenset(("naam", "iban", "rekeningnummer", "giro", "groep",)), "van_json"),)
                        personen[uuid]  =   persoon
                        self.derde_uuid =   uuid
                        opslaan_json(personen, "gegevens\\derden", "persoon", "json", {"Persoon": "naar_json"})
                        break
                
                elif opdracht.get("opdracht") == "zoek":
                    
                    if opdracht.get("zoekterm").strip() == "":
                        continue
                    
                    if derde_type == "bedrijf":
                        bedrijven       =   open_json("gegevens\\derden", "bedrijf", "json", class_mapper = (Bedrijf, frozenset(("naam", "iban", "rekeningnummer", "giro", "synoniemen", "uitsluiten", "cat_uuid",)), "van_json"),)
                        bedrijven_match_uuid    =   []
                        for bedrijf_uuid, bedrijf in bedrijven.items():
                            if opdracht.get("zoekterm").casefold() in bedrijf.naam.casefold():
                                bedrijven_match_uuid.append(bedrijf_uuid)
                        
                        if len(bedrijven_match_uuid) == 0:
                            print(f"geen bedrijven gevonden voor zoekterm \"{opdracht.get("zoekterm")}\"")
                            continue
                        
                        uuid    =   invoer_kiezen("bedrijf", {bedrijven[bedrijf_match_uuid].naam: bedrijf_match_uuid for bedrijf_match_uuid in bedrijven_match_uuid}, stoppen = True)
                        if not bool(uuid):
                            continue
                        self.derde_uuid     =   uuid
                        print(f"derde veranderd naar \"{bedrijven[uuid].naam}\"")
                        if "naam" in self.tijdelijk.keys():
                            bedrijven[uuid].synoniemen.append(self.tijdelijk.get("naam").casefold())
                        if "derde_iban" in self.tijdelijk.keys():
                            bedrijven[uuid].iban.append(self.tijdelijk.get("derde_iban"))
                        if bedrijven[uuid].cat_uuid is not None:
                            self.cat_uuid = bedrijven[uuid].cat_uuid
                            print(f"categorie veranderd naar \"{self.categorie().naam} ({self.hoofdcategorie().naam})\"")
                        opslaan_json(bedrijven, "gegevens\\derden", "bedrijf", "json", {"Bedrijf": "naar_json"})
                        break
                        
                    else:
                        personen    =   open_json("gegevens\\derden", "persoon", "json", class_mapper = (Persoon, frozenset(("naam", "iban", "rekeningnummer", "giro", "groep",)), "van_json"),)
                        personen_match_uuid    =   []
                        for persoon_uuid, persoon in personen.items():
                            if opdracht.get("zoekterm").casefold() in persoon.naam.casefold():
                                personen_match_uuid.append(persoon_uuid)
                        
                        if len(personen_match_uuid) == 0:
                            print(f"geen personen gevonden voor zoekterm \"{opdracht.get("zoekterm")}\"")
                            continue
                        
                        uuid    =   invoer_kiezen("persoon", {personen[persoon_match_uuid].naam: persoon_match_uuid for persoon_match_uuid in personen_match_uuid}, stoppen = True)
                        if not bool(uuid):
                            continue
                        self.derde_uuid     =   uuid
                        print(f"derde veranderd naar \"{personen[uuid].naam}\"")
                        if "derde_iban" in self.tijdelijk.keys():
                            personen[uuid].iban.append(self.tijdelijk.get("derde_iban"))
                        opslaan_json(personen, "gegevens\\derden", "persoon", "json", {"Persoon": "naar_json"})
                        break
                else:
                    raise Exception
        
        elif veld == "cpsp_uuid":
            
            while True:
                
                print(f"kies een bestaand medium met een zoekterm")
                zoekterm    =   invoer_validatie("zoekterm", str)
                
                if zoekterm == "":
                    continue
                
                cpsps       =   open_json("gegevens\\derden", "cpsp", "json", class_mapper = (Cpsp, frozenset(("naam", "iban", "rekeningnummer", "giro", "synoniemen", "uitsluiten",)), "van_json"),)
                cpsps_match_uuid    =   []
                for cpsp_uuid, cpsp in cpsps.items():
                    if zoekterm.casefold() in cpsp.naam.casefold():
                        cpsps_match_uuid.append(cpsp_uuid)
                
                if len(cpsps_match_uuid) == 0:
                    print(f"geen cpsps gevonden voor zoekterm \"{zoekterm}\"")
                    continue
                
                cpsp_uuid   =   invoer_kiezen("cpsp", {cpsps[cpsp_match_uuid].naam: cpsp_match_uuid for cpsp_match_uuid in cpsps_match_uuid}, stoppen = True)
                if not bool(cpsp_uuid):
                    continue
                self.details["cpsp_uuid"]   =   cpsp_uuid
                print(f"cpsp veranderd naar \"{cpsps[cpsp_uuid].naam}\"")
                if "naam" in self.tijdelijk.keys():
                    cpsps[cpsp_uuid].synoniemen.append(self.tijdelijk.get("naam").casefold())
                if "medium_iban" in self.tijdelijk.keys():
                    cpsps[cpsp_uuid].iban.append(self.tijdelijk.get("medium_iban"))
                opslaan_json(cpsps, "gegevens\\derden", "cpsp", "json", {"Cpsp": "naar_json"})
                break
        
        elif veld == "cat_uuid":
            
            categorieen         =   open_json("gegevens\\configuratie", "categorie",      "json", class_mapper = (Categorie, frozenset(("naam", "hoofdcat_uuid", "bedrijven", "trefwoorden",)), "van_json"),)
            hoofdcategorieen    =   open_json("gegevens\\configuratie", "hoofdcategorie", "json", class_mapper = (HoofdCategorie, frozenset(("naam", "type")), "van_json"),)
            
            while True:
                
                hoofdcat_uuid       =   invoer_kiezen("hoofdcategorie", {hoofdcategorie.naam: hoofdcat_uuid for hoofdcat_uuid, hoofdcategorie in hoofdcategorieen.items()})
                cat_uuid            =   invoer_kiezen("hoofdcategorie", {categorie.naam: cat_uuid for cat_uuid, categorie in categorieen.items() if categorie.hoofdcat_uuid == hoofdcat_uuid}, stoppen = True)
                if not bool(cat_uuid):
                    continue
                break
            
            print(f"categorie \"{categorieen[cat_uuid].naam}\" gekozen")
            self.cat_uuid       =   cat_uuid
            
            bedrijven       =   open_json("gegevens\\derden", "bedrijf", "json", class_mapper = (Bedrijf, frozenset(("naam", "iban", "rekeningnummer", "giro", "synoniemen", "uitsluiten", "cat_uuid",)), "van_json"),)
            if self.derde_uuid in bedrijven.keys():
                if not bedrijven[self.derde_uuid].uitsluiten and bedrijven[self.derde_uuid].cat_uuid is None:
                    print(f"toevoegen categorie \"{self.categorie().naam} ({self.hoofdcategorie().naam})\" aan bedrijf \"{bedrijven[self.derde_uuid].naam}\"?")
                    toevoegen   =   invoer_kiezen("toevoegen aan derde", ["ja", "nee", "uitsluiten"])
                    if toevoegen == "ja":
                        bedrijven[self.derde_uuid].cat_uuid     =   cat_uuid
                    elif toevoegen == "uitsluiten":
                        bedrijven[self.derde_uuid].uitsluiten   =   True
                    opslaan_json(bedrijven, "gegevens\\derden", "bedrijf", "json", {"Bedrijf": "naar_json"})
        
        elif veld == "opmerking":
            
            opmerking   =   invoer_validatie("opmerking", str)
            self.details["opmerking"]   =   opmerking
        
        elif veld == "locatie_uuid":
            
            if "locatie_uuid" in self.details.keys():
                
                locaties    =   open_json("gegevens\\configuratie", "locatie", "json", class_mapper = (Locatie, frozenset(("naam", "land_uuid", "breedtegraad", "lengtegraad", "synoniemen")), "van_json"),)
                landen      =   open_json("gegevens\\configuratie", "land",    "json", class_mapper = (Land, frozenset(("naam", "iso_3166_1_alpha_3", "synoniemen")), "van_json"),)
                
                if self.details.get("locatie_uuid") is None:
                        print(f"geen automatische locatie toegekend voor locatie \"{self.tijdelijk["locatie_oud"]}\", land \"{self.tijdelijk["land_oud"]}\"")
                
                while True:
                    
                    print(f"kies een bestaande locatie met \"zoek <zoekterm>\" of een nieuwe met \"nieuw\"")
                    opdracht = invoer_validatie("opdracht", str, regex = r"(?i)^(?P<opdracht>nieuw|zoek)(\s+(?P<zoekterm>.*))?$")
                    
                    if opdracht.get("opdracht") == "nieuw":
                        
                        uuid            =   str(uuid4())
                        naam            =   invoer_validatie("locatie", str, valideren =  True)
                        
                        for land_uuid, land in landen.items():
                            if self.tijdelijk["land_oud"].casefold() == land.naam.casefold() or any(self.tijdelijk["land_oud"].casefold() == synoniem for synoniem in land.synoniemen):
                                break
                        else:
                            print(f"geen automatische land toegekend voor land \"{self.tijdelijk["land_oud"]}\"")
                            while True:
                                print(f"kies een bestaande locatie met \"zoek <zoekterm>\" of een nieuwe met \"nieuw\"")
                                opdracht = invoer_validatie("opdracht", str, regex = r"(?i)^(?P<opdracht>nieuw|zoek)(\s+(?P<zoekterm>.*))?$")
                                
                                if opdracht.get("opdracht") == "nieuw":
                                    raise NotImplementedError
                                
                                else:
                                    if opdracht.get("zoekterm").strip() == "":
                                        continue
                                    
                                    landen_uuid_overeenkomst = []
                                    
                                    for land_uuid, land in landen.items():
                                        if opdracht.get("zoekterm").casefold() in land.naam.casefold() or any(opdracht.get("zoekterm").casefold() in synoniem for synoniem in land.synoniemen):
                                            landen_uuid_overeenkomst.append(land_uuid)
                                    
                                    if len(landen_uuid_overeenkomst) == 0:
                                        print(f"geen landen gevonden voor zoekterm \"{opdracht.get("zoekterm")}\"")
                                        continue
                                    
                                    land_uuid = invoer_kiezen("land", {landen[land_uuid_overeenkomst].naam: land_uuid_overeenkomst for land_uuid_overeenkomst in landen_uuid_overeenkomst}, stoppen = True)
                                    
                                    if not bool(land_uuid):
                                        continue
                                    
                                    print(f"land veranderd naar \"{landen[land_uuid].naam}\"")
                                    
                                    landen[land_uuid].synoniemen.append(self.tijdelijk["land_oud"].casefold())
                                    opslaan_json(landen, "gegevens\\configuratie", "land", "json")
                                    break
                        
                        breedtegraad    =   invoer_validatie("breedtegraad", float, valideren = True)
                        lengtegraad     =   invoer_validatie("lengtegraad", float, valideren = True)
                        
                        print(f"toevoegen synoniemn \"{self.tijdelijk["locatie_oud"]}\" aan locatie \"{naam}\"?")
                        if invoer_kiezen("keuze", {"ja": True, "nee": False}):
                            locatie = Locatie(
                                naam,
                                land_uuid,
                                breedtegraad,
                                lengtegraad,
                                [self.tijdelijk["locatie_oud"].casefold()]
                                )
                        else:
                            locatie = Locatie(
                                naam,
                                land_uuid,
                                breedtegraad,
                                lengtegraad,
                                )
                        
                        locaties[uuid] = locatie
                        opslaan_json(locaties, "gegevens\\configuratie", "locatie", "json")
                    
                    elif opdracht.get("opdracht") == "zoek":
                        
                        if opdracht.get("zoekterm").strip() == "":
                            continue
                        
                        locaties_uuid_overeenkomst = []
                        
                        for locatie_uuid, locatie in locaties.items():
                            if opdracht.get("zoekterm").casefold() in locatie.naam.casefold() or any(opdracht.get("zoekterm").casefold() in synoniem for synoniem in locatie.synoniemen):
                                locaties_uuid_overeenkomst.append(locatie_uuid)
                        
                        if len(locaties_uuid_overeenkomst) == 0:
                            print(f"geen locaties gevonden voor zoekterm \"{opdracht.get("zoekterm")}\"")
                            continue
                        
                        locatie_uuid = invoer_kiezen("locatie", {locaties[locatie_uuid_overeenkomst].naam: locatie_uuid_overeenkomst for locatie_uuid_overeenkomst in locaties_uuid_overeenkomst}, stoppen = True)
                        
                        if not bool(locatie_uuid):
                            continue
                        
                        self.details["locatie_uuid"]    =   locatie_uuid
                        print(f"locatie veranderd naar \"{locaties[locatie_uuid].naam} ({landen[locaties[locatie_uuid].land_uuid].naam})\"")
                        
                        if self.tijdelijk["locatie_oud"].casefold() not in locaties[locatie_uuid].synoniemen:
                            print(f"toevoegen synoniemn \"{self.tijdelijk["locatie_oud"]}\" aan locatie \"{locaties[locatie_uuid].naam}\"?")
                            if invoer_kiezen("keuze", {"ja": True, "nee": False}):
                                locaties[locatie_uuid].synoniemen.append(self.tijdelijk["locatie_oud"].casefold())
                            
                        if self.tijdelijk["land_oud"].casefold() != landen[locaties[locatie_uuid].land_uuid].naam.casefold() and self.tijdelijk["land_oud"].casefold() not in landen[locaties[locatie_uuid].land_uuid].synoniemen:
                            landen[locaties[locatie_uuid].land_uuid].synoniemen.append(self.tijdelijk["land_oud"].casefold())
                        
                        opslaan_json(locaties, "gegevens\\configuratie", "locatie", "json")
                        opslaan_json(landen, "gegevens\\configuratie", "land", "json")
                        break
            
            else:
                print("deze transatie bevat geen locatie")
            
            
            
            
            
        
        # elif veld == "locatie":
            
        #     if "locatie" in self.details.keys():
                
        #         locatie_nieuw   =   invoer_validatie("locatie", str, valideren =  True)
        #         if self.details["locatie"] != locatie_nieuw:
        #             toevoegen       =   invoer_kiezen("optie, toevoegen hernoeminstructie", ["ja", "nee"])
        #             if toevoegen == "ja":
        #                 locatie_oud     =   self.details["locatie"]
        #                 locatiebestand  =   open_json("gegevens\\configuratie", "locatie", "json")
        #                 if any([locatie_nieuw.casefold() == locatie.casefold() for locatie in locatiebestand.keys()]):
        #                     locatiebestand[locatie_nieuw].append(locatie_oud)
        #                 else:
        #                     locatiebestand[locatie_nieuw]   =   [locatie_oud]
                        
        #                 opslaan_json(locatiebestand, "gegevens\\configuratie", "locatie", "json")
                        
        #             self.details["locatie"]     =   locatie_nieuw
                
        #     else:
        #         print("deze transatie bevat geen locatie")
            
        # elif veld == "land":
            
        #     if "land" in self.details.keys():
                
        #         land_nieuw      =   invoer_validatie("land", str, valideren =  True)
        #         if self.details["land"] != land_nieuw:
        #             toevoegen       =   invoer_kiezen("optie, toevoegen hernoeminstructie", ["ja", "nee"])
        #             if toevoegen == "ja":
        #                 land_oud        =   self.details["land"]
        #                 landenbestand   =   open_json("gegevens\\configuratie", "land", "json")
        #                 if any([land_nieuw.casefold() == land.casefold() for land in landenbestand.keys()]):
        #                     landenbestand[land_nieuw].append(land_oud)
        #                 else:
        #                     landenbestand[land_nieuw]   =   [land_oud]
                        
        #                 opslaan_json(landenbestand, "gegevens\\configuratie", "land", "json")
                        
        #             self.details["land"]     =   land_nieuw
                
        #     else:
        #         print("deze transatie bevat geen land")
        
        return self
    
    def categorie(
        self,
        categorieen     :   Dict[str, Categorie]        = None,
        ) -> Categorie:
        
        categorieen         =   categorieen         if categorieen      is not None else open_json("gegevens\\configuratie", "categorie", "json", class_mapper = (Categorie, frozenset(("naam", "hoofdcat_uuid", "bedrijven", "trefwoorden",)), "van_json"),)
        return categorieen.get(self.cat_uuid)
    
    def hoofdcategorie(
        self,
        categorieen     :   Dict[str, Categorie]        = None,
        hoofdcategorieen:   Dict[str, HoofdCategorie]   = None,
        ) -> HoofdCategorie:
        
        categorieen         =   categorieen         if categorieen      is not None else open_json("gegevens\\configuratie", "categorie", "json", class_mapper = (Categorie, frozenset(("naam", "hoofdcat_uuid", "bedrijven", "trefwoorden",)), "van_json"),)
        hoofdcategorieen    =   hoofdcategorieen    if hoofdcategorieen is not None else open_json("gegevens\\configuratie", "hoofdcategorie", "json", class_mapper = (HoofdCategorie, frozenset(("naam", "type")), "van_json"),)
        return hoofdcategorieen.get(self.categorie(categorieen).hoofdcat_uuid)
    
    def locatie(
        self,
        locaties:   Dict[str, Locatie]  = None,
        ) -> Locatie:
        
        locaties    =   locaties if locaties is not None else open_json("gegevens\\configuratie", "locatie", "json", class_mapper = (Locatie, frozenset(("naam", "land_uuid", "breedtegraad", "lengtegraad", "synoniemen")), "van_json"),)
        
        return locaties.get(self.details["locatie_uuid"]) if self.details.get("locatie_uuid", None) is not None else None
    
    def land(
        self,
        locaties:   Dict[str, Locatie]  = None,
        landen  :   Dict[str, Land]     = None,
        ) -> Land:
        
        locaties    =   locaties if locaties is not None else open_json("gegevens\\configuratie", "locatie", "json", class_mapper = (Locatie, frozenset(("naam", "land_uuid", "breedtegraad", "lengtegraad", "synoniemen")), "van_json"),)
        landen      =   landen   if landen   is not None else open_json("gegevens\\configuratie", "land",    "json", class_mapper = (Land, frozenset(("naam", "iso_3166_1_alpha_3", "synoniemen")), "van_json"),)
        
        return landen[locaties.get(self.details["locatie_uuid"]).land_uuid] if self.details.get("locatie_uuid", None) is not None else None
    
    def derde(
        self,
        personen        :   Dict[str, Persoon]          =   None,
        bedrijven       :   Dict[str, Bedrijf]          =   None,
        bankrekeningen  :   Dict[str, Any]              =   None,
        banken          :   Dict[str, Bank]             =   None,
        cpsps           :   Dict[str, Cpsp]             =   None,
        ) -> Persoon | Bedrijf | Dict | Bank | Cpsp:
        
        personen            =   personen            if personen         is not None else open_json("gegevens\\derden",          "persoon",      "json", class_mapper = (Persoon, frozenset(("naam", "iban", "rekeningnummer", "giro", "groep",)), "van_json"),)
        bedrijven           =   bedrijven           if bedrijven        is not None else open_json("gegevens\\derden",          "bedrijf",      "json", class_mapper = (Bedrijf, frozenset(("naam", "iban", "rekeningnummer", "giro", "synoniemen", "uitsluiten", "cat_uuid",)), "van_json"),)
        bankrekeningen      =   bankrekeningen      if bankrekeningen   is not None else open_json("gegevens\\configuratie",    "bankrekening", "json")
        banken              =   banken              if banken           is not None else open_json("gegevens\\derden",          "bank",         "json", class_mapper = (Bank, frozenset(("naam", "iban", "rekeningnummer", "synoniemen", "bic",)), "van_json"),)
        cpsps               =   cpsps               if cpsps            is not None else open_json("gegevens\\derden",          "cpsp",         "json", class_mapper = (Cpsp, frozenset(("naam", "iban", "rekeningnummer", "giro", "synoniemen", "uitsluiten",)), "van_json"),)
        
        if self.derde_uuid is None:
            return bedrijven["f2892946-cc42-4d6f-8360-9b0d28249cd0"]
        else:
            if self.derde_uuid in personen.keys():
                return personen.get(self.derde_uuid)
            elif self.derde_uuid in bedrijven.keys():
                return bedrijven.get(self.derde_uuid)
            elif self.derde_uuid in bankrekeningen.keys():
                return bankrekeningen.get(self.derde_uuid)
            elif self.derde_uuid in banken.keys():
                return banken.get(self.derde_uuid)
            elif self.derde_uuid in cpsps.keys():
                return cpsps.get(self.derde_uuid)
    
    def medium(self) -> Cpsp:
        
        if "cpsp_uuid" in self.details.keys():
            cpsps = open_json("gegevens\\derden", "cpsp", "json", class_mapper = (Cpsp, frozenset(("naam", "iban", "rekeningnummer", "giro", "synoniemen", "uitsluiten",)), "van_json"),)
            return cpsps[self.details.get("cpsp_uuid")]
        return None
    
    def bank(self) -> Bank:
        
        if "bank_uuid" in self.details.keys():
            banken = open_json("gegevens\\derden", "bank", "json", class_mapper = (Bank, frozenset(("naam", "iban", "rekeningnummer", "synoniemen", "bic",)), "van_json"),)
            return banken[self.details.get("bank_uuid")]
        return None

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