import locale
import re
import datetime as dt
from uuid import uuid4

import pandas

from .utils import iban_zoeker
from .lezerschrijver import open_json, opslaan_json
from .invoer import invoer_validatie

locale.setlocale(locale.LC_ALL, "nl_NL.UTF-8")

muntsoorten         =   open_json("gegevens\\config",   "muntsoorten",      "json")
categorieen         =   open_json("gegevens\\config",   "categorieen",      "json", kwargs = {"class": "categorie"})
hoofdcategorieen    =   open_json("gegevens\\config",   "hoofdcategorieen", "json", kwargs = {"class": "hoofdcategorie"})

class Transactie:
    
    def __init__(self,
                 bedrag             : int,
                 beginsaldo         : int,
                 eindsaldo          : int,
                 transactiemethode  : str,
                 datumtijd          : dt.datetime,
                 cat_uuid           : str,
                 derde_uuid         : str,
                 rekeningnummer     : str,
                 index              : int   =   0,
                 dagindex           : int   =   0,
                 details            : dict  =   None,
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
        self.rekeningnummer     =   rekeningnummer
        self.details            =   dict() if details is None else details
    
    def __repr__(self):
        
        richting    =   "uitgave" if self.bedrag < 0 else "inkomst"
        datumtijd   =   self.datumtijd.strftime("%A %d %B %Y") if self.datumtijd.time() == dt.time(0,0) else ("%A %d %B %Y om %H:%M")
        lijn_transactie     =   f"{richting} van {self.toon_bedrag()} op {datumtijd},"
        
        if self.derde_uuid == "":
            toon_derde  =   "\"onbekend\""
        else:
            personen                =   open_json("gegevens\\derden",   "personen",             "json", kwargs = {"class": "persoon"})
            bedrijven               =   open_json("gegevens\\derden",   "bedrijven",            "json", kwargs = {"class": "bedrijf"})
            bankrekeningen          =   open_json("gegevens\\config",   "bankrekeningen",       "json")
            cpsps                   =   open_json("gegevens\\derden",   "cpsp",                 "json")
            
            if self.derde_uuid in personen.keys():
                persoon     =   personen.get(self.derde_uuid)
                toon_derde  =   f"persoon \"{persoon.naam}\"" if persoon.groep == "ongegroepeerd" else f"persoon \"{persoon.naam}\" ({persoon.groep})"
            elif self.derde_uuid in bedrijven.keys():
                bedrijf     =   bedrijven.get(self.derde_uuid)
                toon_derde  =   f"bedrijf \"{bedrijf.naam}\""
            elif self.derde_uuid in bankrekeningen.keys():
                bankrekening=   bankrekeningen.get(self.derde_uuid)
                toon_derde  =   f"bankrekening {bankrekening.naam}"
            
        if self.transactiemethode == "pinbetaling" or self.methode == "geldopname":
            lijn_derde  =   f"aan {toon_derde} per {self.methode} in {self.details["locatie"]} ({self.details["land"]})"
        elif self.transactiemethode == "bankkosten" or self.transactiemethode == "spaarrente":
            lijn_derde  =   f"voor {self.transactiemethode}"
        else:
            if richting    ==  "uitgave":
                richtingswoord  =   "aan"
            else:
                richtingswoord  =   "van"
            
            if "cpsp_uuid" in self.details.keys():
                toon_medium     =   f"(via \"{cpsps.get(self.details["cpsp_uuid"])["naam"]})\""
            else:
                toon_medium     =   ""    
            
            if self.betalingsomschrijving == "":
                lijn_derde  =   f"{richtingswoord} {toon_derde} per {self.methode} {toon_medium}"
            else:
                lijn_derde  =   f"{richtingswoord} {toon_derde} per {self.methode} {toon_medium} voor \"{self.betalingsomschrijving}\""   
        
        if self.categorie != "":
            lijn_categorie  =   f"categorie: {hoofdcategorieen.get(categorieen.get(self.cat_uuid))["hoofdcategorie"]}, subcategorie: {categorieen.get(self.cat_uuid)}"
            return f"\t{lijn_transactie}\n\t{lijn_derde}\n\t{lijn_categorie}"
        else:
            return f"\t{lijn_transactie}\n\t{lijn_derde}"
    
    def toon_bedrag(self):
        
        def toon_bedrag_iso(bedrag, valuta_iso):
            
            valuta_dict     =   next(muntsoort for muntsoort in muntsoorten if muntsoort["ISO 4217"] == valuta_iso)
            
            if valuta_dict["ervoor"]:
                return f"{valuta_dict['symbool']}{' '*valuta_dict['spatie']}{bedrag}"
            else:
                return f"{bedrag}{' '*valuta_dict['spatie']}{valuta_dict['symbool']}"
            # return f"{regel_euro_print} ({regel_valuta_print})"
        
        bedrag_euro         =   self.bedrag / 100
        
        bedrag_euro_print   =   str(int(bedrag_euro))+",- " if bedrag_euro % 1 == 0 else f"{bedrag_euro:.2f}".replace('.',',')
        regel_euro_print    =   toon_bedrag_iso(bedrag_euro_print, "EUR")
        
        if "valuta_iso" in self.details.keys():
            
            bedrag_valuta       =   self.details["valuta_bedrag"] / 100
            bedrag_valuta_print =   str(int(bedrag_valuta))+",- " if bedrag_valuta % 1 == 0 else f"{bedrag_valuta:.2f}".replace('.',',')
            regel_valuta_print  =   toon_bedrag_iso(bedrag_valuta_print, self.details["valuta_iso"])
            return f"{regel_euro_print} ({regel_valuta_print})"
        else:
            return regel_euro_print
        
    @classmethod
    def van_json(cls, **transactie_dict: dict):
        
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
                    rekeningnummer      =   transactie_dict["rekeningnummer"],
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
                    "rekeningnummer":       self.rekeningnummer,
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
                    "rekeningnummer":       self.rekeningnummer,
                    "details":              self.details,
                    }
    
    def naar_tabel(self, 
                   personen                 : dict  =   None,
                   bedrijven                : dict  =   None,
                   bankrekeningen           : dict  =   None,
                   categorieen              : dict  =   None,
                   hoofdcategorieen         : dict  =   None,
                   ) -> dict:
        
        personen                =   open_json("gegevens\\derden",    "personen",             "json", kwargs = {"class": "persoon"})         if personen is None else personen
        bedrijven               =   open_json("gegevens\\derden",    "bedrijven",            "json", kwargs = {"class": "bedrijf"})         if bedrijven is None else bedrijven
        bankrekeningen          =   open_json("gegevens\\config",    "bankrekeningen", "json")                                              if bankrekeningen is None else bankrekeningen
        categorieen             =   open_json("gegevens\\config",    "categorieen",          "json", kwargs = {"class": "categorie"})       if categorieen is None else categorieen
        hoofdcategorieen        =   open_json("gegevens\\config",    "hoofdcategorieen",     "json", kwargs = {"class": "hoofdcategorie"})  if hoofdcategorieen is None else hoofdcategorieen
        
        derde                   =   personen[self.derde_uuid] if self.derde_uuid in personen.keys() else (bedrijven[self.derde_uuid] if self.derde_uuid in bedrijven.keys() else bankrekeningen[self.derde_uuid])
        
        return {
                "index":                self.index,
                "bedrag":               self.bedrag,
                "beginsaldo":           self.beginsaldo,
                "eindsaldo":            self.eindsaldo,
                "transactiemethode":    self.transactiemethode,
                "datumtijd":            self.datumtijd,
                "dagindex":             self.dagindex,
                "hoofdcategorie":       hoofdcategorieen[categorieen[self.cat_uuid].hoofdcategorie].naam,
                "categorie":            categorieen[self.cat_uuid].naam,
                "derde":                derde["naam"] if isinstance(derde, dict) else derde.naam,
                "type":                 "bankrekening" if isinstance(derde, dict) else derde.type,
                }
    
    @classmethod
    def van_bankexport(cls, rij):
        
        cpsps                   =   open_json("gegevens\\derden",   "cpsp",                 "json")
        
        rekeningnummer  =   str(rij.rekeningnummer)
        
        if rij.muntsoort.casefold() != "eur":
            raise NotImplementedError
        
        bedrag          =   int(round(100 * rij.transactiebedrag))
        beginsaldo      =   int(round(100 * rij.beginsaldo))
        eindsaldo       =   int(round(100 * rij.eindsaldo))
        datumtijd       =   dt.datetime.strptime(str(rij.rentedatum), "%Y%m%d")
        
        details         =   {}
        
        if rij.omschrijving.casefold().startswith("rente"):
            
            transactiemethode   =   "rente"
            cat_uuid            =   "b123402b-7d55-4eb1-9eac-c41df3c784c4"
            derde_uuid          =   "7fe30da2-dfb9-4d07-8d85-6132cf0c8816"
            details["betalingsomschrijving"]    =   rij.omschrijving.strip()
        
        elif rij.omschrijving.casefold().startswith("BEA, Betaalpas".casefold()) or rij.omschrijving.casefold().startswith("GEA, Betaalpas".casefold()):
            
            if rij.omschrijving.casefold().startswith("BEA, Betaalpas".casefold()):
                transactiemethode   =   "pinbetaling" 
                cat_uuid            =   ""
            else:
                transactiemethode   =   "pinbetaling" 
                cat_uuid            =   "6507437f-f21a-4458-bbdd-1ed7c2f5cebd"
            
            patroon_pinpas      =   re.compile(r"(?i)^(?:B|G)EA, Betaalpas\s+(?P<derde_naam>.*),PAS(?P<pasnummer>\d{3})\s+NR:(?P<terminal>.*),?\s+(?P<datumtijd>\d{2}.\d{2}.\d{2}\/\d{2}(.?:|.)\d{2})\s+(?P<locatie>.*)$")
            resultaat_pinpas    =   patroon_pinpas.match(rij.omschrijving).groupdict()
            
            datumtijd               =   dt.datetime.strptime(resultaat_pinpas.get("datumtijd"), "%d.%m.%y/%H:%M") if ":" in resultaat_pinpas.get("datumtijd") else dt.datetime.strptime(resultaat_pinpas.get("datumtijd"), "%d.%m.%y/%H.%M")
            
            details["pasnummer"]    =   resultaat_pinpas.get("pasnummer").strip()
            details["terminal"]     =   resultaat_pinpas.get("terminal").strip()
            
            if "land:" in resultaat_pinpas.get("locatie"):
                if ", land:" in resultaat_pinpas.get("locatie"):
                    details["land"]     =   cls.verwerken_land(resultaat_pinpas.get("locatie").split(", land:")[1].strip())
                    details["locatie"]  =   cls.verwerken_locatie(resultaat_pinpas.get("locatie").split(", land:")[0].strip())
                else:
                    details["land"]     =   cls.verwerken_land(resultaat_pinpas.get("locatie").split("land:")[1].strip())
                    details["locatie"]  =   cls.verwerken_locatie(resultaat_pinpas.get("locatie").split("land:")[0].strip())
            else:
                details["land"]         =   "Nederland"
                details["locatie"]      =   cls.verwerken_locatie(resultaat_pinpas.get("locatie").strip())
            
            derde_uuid, cat_uuid    =   cls.verwerken_derde_uuid(derde_naam = resultaat_pinpas.get("derde_naam"))
        
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
                
                details["bank_uuid"]=   "7fe30da2-dfb9-4d07-8d85-6132cf0c8816"
                
                patroon_tikkie          =   re.compile(r"(?i)^Tikkie ID (?:[0-9 ]+), ?(?P<betalingsomschrijving_tikkie>.+), ?Van ?(?P<derde_naam>[\w\s\.]+),? ?(?P<derde_iban>.*)?$")
                resultaat_tikkie        =   patroon_tikkie.match(betalingsomschrijving).groupdict()
                
                derde_naam              =   resultaat_tikkie.get("derde_naam")
                derde_iban              =   iban_zoeker(resultaat_tikkie.get("derde_iban"))
                
                derde_uuid, cat_uuid    =   cls.verwerken_derde_uuid(derde_iban = derde_iban, derde_naam = derde_naam)
                
                details["betalingsomschrijving"]    =   resultaat_tikkie.get("betalingsomschrijving_tikkie")
                
            else:
                transactiemethode       =   "overboeking"
                
                if not betalingsomschrijving == "":
                    details["betalingsomschrijving"]    =   betalingsomschrijving
                
                for cpsp_uuid, cpsp in cpsps.items():
                    if cpsp["naam"].casefold() in naam.casefold() or any([cpsp_synoniem.casefold() in naam.casefold() for cpsp_synoniem in cpsp.get("synoniemen", [])]) or any([cpsp_iban == iban for cpsp_iban in cpsp.get("iban", [])]):
                        details["cpsp_uuid"]    =   cpsp_uuid
                        derde_uuid, cat_uuid    =   cls.verwerken_derde_uuid(derde_naam = naam)
                        break
                else:
                    derde_uuid, cat_uuid    =   cls.verwerken_derde_uuid(derde_iban = iban, derde_naam = naam)
        
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
                
                elif "rabo" in betalingsomschrijving.casefold():
                    
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
                
                derde_uuid, cat_uuid    =   cls.verwerken_derde_uuid(derde_iban = derde_iban, derde_naam = derde_naam)
                
                details["bank_uuid"]                =   bank_uuid
                details["betalingsomschrijving"]    =   betalingsomschrijving
                details["betalingskenmerk"]         =   betalingskenmerk
                
            else:
                
                transactiemethode                   =   "ideal"
                
                details["betalingsomschrijving"]    =   betalingsomschrijving
                details["betalingskenmerk"]         =   betalingskenmerk
                
                for cpsp_uuid, cpsp in cpsps.items():
                    if cpsp["naam"].casefold() in naam.casefold() or any([cpsp_synoniem.casefold() in naam.casefold() for cpsp_synoniem in cpsp.get("synoniemen", [])]) or any([cpsp_iban == iban for cpsp_iban in cpsp.get("iban", [])]):
                        details["cpsp_uuid"]    =   cpsp_uuid
                        derde_uuid, cat_uuid    =   cls.verwerken_derde_uuid(derde_naam = naam)
                        break
                else:
                    derde_uuid, cat_uuid    =   cls.verwerken_derde_uuid(derde_iban = iban, derde_naam = naam)
        
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
            iban                    =   resultaat_incasso.get("iban","").strip()
            bic                     =   resultaat_incasso.get("bic", "").strip()
            betalingskenmerk        =   resultaat_incasso.get("betalingskenmerk", "").strip()
            
            details["incassant"]                =   incassant
            details["machtiging"]               =   machtiging
            details["betalingsomschrijving"]    =   betalingsomschrijving
            details["betalingskenmerk"]         =   betalingskenmerk
            
            for cpsp_uuid, cpsp in cpsps.items():
                if cpsp["naam"].casefold() in naam.casefold() or any([cpsp_synoniem.casefold() in naam.casefold() for cpsp_synoniem in cpsp.get("synoniemen", [])]) or any([cpsp_iban == iban for cpsp_iban in cpsp.get("iban", [])]):
                    details["cpsp_uuid"]    =   cpsp_uuid
                    derde_uuid, cat_uuid    =   cls.verwerken_derde_uuid(derde_naam = naam)
                    break
            else:
                derde_uuid, cat_uuid    =   cls.verwerken_derde_uuid(derde_iban = iban, derde_naam = naam)
        
        elif rij.omschrijving.casefold().startswith("ABN AMRO".casefold()):
            
            transactiemethode   =   "bankkosten"
            
            derde_uuid          =   "7fe30da2-dfb9-4d07-8d85-6132cf0c8816"
            cat_uuid            =   "d188a43a-fb79-4a83-844d-6feb78855924"
            details["betalingsomschrijving"]    =   rij.omschrijving
            
        else:
            print(rij.omschrijving)
            raise NotImplementedError
        
        return cls(bedrag               =   bedrag,
                   beginsaldo           =   beginsaldo,
                   eindsaldo            =   eindsaldo,
                   transactiemethode    =   transactiemethode,
                   datumtijd            =   datumtijd,
                   cat_uuid             =   cat_uuid,
                   derde_uuid           =   derde_uuid,
                   rekeningnummer       =   rekeningnummer,
                   details              =   details,
                   )
    
    @staticmethod
    def verwerken_derde_uuid(**kwargs):
        
        personen                =   open_json("gegevens\\derden",   "personen",             "json", kwargs = {"class": "persoon"})
        bedrijven               =   open_json("gegevens\\derden",   "bedrijven",            "json", kwargs = {"class": "bedrijf"})
        bankrekeningen          =   open_json("gegevens\\config",   "bankrekeningen",       "json")
        
        if "derde_iban" in kwargs.keys():
            
            for uuid_bankrekening, bankrekening in bankrekeningen.items():
                if kwargs.get("derde_iban") == getattr(bankrekening, "iban", ""):
                    derde_uuid  =   uuid_bankrekening
                    cat_uuid    =   "1e8fd286-4cdd-4836-a1c5-7e815123ea25"
                    return derde_uuid, cat_uuid
            
            for uuid_persoon, persoon in personen.items():
                if kwargs.get("derde_iban") in getattr(persoon, "iban", ""):
                    derde_uuid  =   uuid_persoon
                    return derde_uuid, ""
            
            for uuid_bedrijf, bedrijf in bedrijven.items():
                if kwargs.get("derde_iban") in getattr(bedrijf, "iban", ""):
                    derde_uuid  =   uuid_bedrijf
                    return derde_uuid, ""
        
        elif "derde_naam" in kwargs.keys():
            
            for uuid_bedrijf, bedrijf in bedrijven.items():
                if kwargs.get("derde_naam").casefold() == getattr(bedrijf, "naam").casefold() or any([kwargs.get("derde_naam").casefold() == synoniem for synoniem in getattr(bedrijf, "synoniemen")]):
                    derde_uuid  =   uuid_bedrijf
                    cat_uuid    =   getattr(bedrijf, "categorie", "")
                    return derde_uuid, cat_uuid
        
        else:
            ...
        
        return "", ""
    
    @staticmethod
    def verwerken_locatie(locatie_oud):
        
        locatiebestand  =   open_json("gegevens\\config", "locaties", "json")
        return next((locatie["naam"] for locatie in locatiebestand for synoniem in locatie["synoniemen"] if synoniem == locatie_oud.casefold()), locatie_oud.capitalize())
    
    @staticmethod
    def verwerken_land(land_oud):
        
        if land_oud != "Nederland" and land_oud is not None:
            
            landenbestand   =   open_json("gegevens\\config", "landen", "json")
            
            if any([afkorting == land_oud for land in landenbestand for afkorting in land["afkortingen"]]):
                return next(land["land"] for land in landenbestand for afkorting in land["afkortingen"] if afkorting == land_oud.casefold())
            else:
                print(f"\nHet land met de afkorting \"{land_oud}\" komt niet voor in het landenbestand.")
                print("Geef de volledige naam op van het land om toe te voegen.")
                
                invoer_land    =   invoer_validatie("land", str, valideren = True)
                
                # onderstaande wordt uitgevoerd als de afkorting niet voorkomt, maar de volledige naam wel
                if any([invoer_land == land["land"] for land in landenbestand]):
                    iland   =   next(iland for iland, land in enumerate(landenbestand) if invoer_land == land["land"])
                    landenbestand[iland]["afkortingen"].append(land_oud.casefold())
                    print(f"De afkorting \"{land_oud.casefold()}\" is toegevoegd aan het land \"{invoer_land}\"")
                
                # onderstaande wordt uitgevoerd als zowel afkorting als volledige naam niet voorkomen in het landenbestand
                else:
                    
                    landenbestand.append(dict(land = invoer_land, afkortingen = [land_oud.casefold()]))
                    print(f"Het land {invoer_land} is toegevoegd, alsmede de afkorting \"{land_oud.casefold()}\"\n")
                
                opslaan_json(landenbestand, "gegevens\\config", "landen", "json")
                
                return invoer_land
        
        return land_oud
    
class Bankrekening:
    
    def __init__(self,
                 naam               :   str,
                 bank               :   str,
                 pad                :   str,
                 rekeningnummer     :   str,
                 uuid               :   str,
                 actief_van         :   dt.datetime, 
                 iban               :   str         =   None,
                 transacties        :   dict        =   None,
                 actief             :   bool        =   True,
                 actief_tot         :   dt.datetime =   None,
                 ):
        
        self.naam               =   naam
        self.bank               =   bank
        self.pad                =   pad
        self.rekeningnummer     =   rekeningnummer
        self.uuid               =   uuid
        self.iban               =   iban
        self.transacties        =   dict() if transacties is None else transacties
        self.actief             =   actief
        self.actief_van         =   actief_van
        self.actief_tot         =   actief_tot
    
    @classmethod
    def openen(cls,
               bankrekening_uuid  :   str,
               ):
        
        eigen_bankrekeningen        =   open_json("gegevens\\config", "bankrekeningen", "json")
        
        bankrekening_dict           =   {}
        
        bankrekening_dict["naam"]                   =   eigen_bankrekeningen[bankrekening_uuid]["naam"]
        bankrekening_dict["bank"]                   =   eigen_bankrekeningen[bankrekening_uuid]["bank"]
        bankrekening_dict["pad"]                    =   eigen_bankrekeningen[bankrekening_uuid]["pad"]
        bankrekening_dict["uuid"]                   =   bankrekening_uuid
        bankrekening_dict["actief_van"]             =   dt.datetime.strptime(eigen_bankrekeningen[bankrekening_uuid]["actief van"], "%Y-%m-%d")
        if "rekeningnummer" in eigen_bankrekeningen[bankrekening_uuid].keys():
            bankrekening_dict["rekeningnummer"]     =   eigen_bankrekeningen[bankrekening_uuid]["rekeningnummer"]
        if "iban" in eigen_bankrekeningen[bankrekening_uuid].keys():
            bankrekening_dict["iban"]               =   eigen_bankrekeningen[bankrekening_uuid]["iban"]
        if "actief tot" in eigen_bankrekeningen[bankrekening_uuid].keys():
            bankrekening_dict["actief_tot"]         =   dt.datetime.strptime(eigen_bankrekeningen[bankrekening_uuid]["actief tot"], "%Y-%m-%d")
            bankrekening_dict["actief"]             =   False
        
        bankrekening_dict["transacties"]            =   open_json("gegevens\\bankrekeningen", bankrekening_uuid, "json", kwargs = {"class": "transactie"})
        
        return cls(**bankrekening_dict)
    
    def opslaan(self):
        opslaan_json(self.transacties, "gegevens\\bankrekeningen", self.uuid, "json")
    
    def verwerken(self,
                  jaar : int,
                  maand : int,
                  ):
        
        bankexport          =   pandas.read_excel(f"{self.pad}\\digitaal\\{jaar}-{maand:02}.xlsx")
        bankexport.columns  =   [col.casefold() for col in bankexport.columns]
        
        for _, rij in bankexport.iterrows():
            transactie  =   Transactie.van_bankexport(rij)
            print(transactie)
            self.toevoegen_transactie(transactie)
    
    @property
    def transactie_lijst(self):
        return list(sorted(self.transacties.values(), key = lambda transactie: transactie.index))
    
    @property
    def saldo(self):
        return self.transactie_lijst[-1].eindsaldo
    
    @property
    def tabel(self):
        
        personen                    =   open_json("gegevens\\derden",    "personen", "json", kwargs = {"class": "persoon"})
        bedrijven                   =   open_json("gegevens\\derden",    "bedrijven", "json", kwargs = {"class": "bedrijf"})
        eigen_bankrekeningen        =   open_json("gegevens\\config",    "bankrekeningen", "json")
        
        return pandas.DataFrame([transactie.naar_tabel(personen             =   personen,
                                                bedrijven            =   bedrijven,
                                                eigen_bankrekeningen =   eigen_bankrekeningen,
                                                categorieen          =   categorieen,
                                                hoofdcategorieen     =   hoofdcategorieen) 
                                                for transactie in self.transacties.values()])
    
    def toevoegen_transactie(self,
                             transactie : Transactie,
                             ):
        
        if not transactie.rekeningnummer == self.rekeningnummer:
            raise ValueError(f"rekeningnummer transactie {transactie.rekeningnummer} niet gelijk aan rekeningnummer bankrekening {self.rekeningnummer}")
        
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