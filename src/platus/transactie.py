import datetime as dt

class Transactie:
    
    def __init__(self,
                 index          : int,
                 bedrag         : int,
                 beginsaldo     : int,
                 eindsaldo      : int,
                 betaalmethode  : str,
                 datumtijd      : dt.datetime,
                 dagindex       : int,
                 categorie      : str,
                 subcategorie   : str,
                 derde          : str,
                 uuid           : str,
                 rekeningnummer : str,
                 details        : dict,
                 ):
        
        self.index              =   index
        self.bedrag             =   bedrag
        self.beginsaldo         =   beginsaldo
        self.eindsaldo          =   eindsaldo
        self.betaalmethode      =   betaalmethode
        self.datumtijd          =   datumtijd
        self.dagindex           =   dagindex
        self.categorie          =   categorie
        self.subcategorie       =   subcategorie
        self.derde              =   derde
        self.uuid               =   uuid
        self.rekeningnummer     =   rekeningnummer
        self.details            =   details
    
    @classmethod
    def van_json(cls, transactie_dict: dict, uuid: str):
        
        if len(transactie_dict["datumtijd"]) == 10:
            datumtijd   =   dt.datetime.strptime(transactie_dict["datumtijd"], "%Y-%m-%d")
        else:
            datumtijd   =   dt.datetime.strptime(transactie_dict["datumtijd"], "%Y-%m-%dT%H:%M")
        
        return cls(index            =   transactie_dict["index"],
                   bedrag           =   transactie_dict["bedrag"],
                   beginsaldo       =   transactie_dict["beginsaldo"],
                   eindsaldo        =   transactie_dict["eindsaldo"],
                   betaalmethode    =   transactie_dict["betaalmethode"],
                   datumtijd        =   datumtijd,
                   dagindex         =   transactie_dict["dagindex"],
                   categorie        =   transactie_dict["categorie"],
                   subcategorie     =   transactie_dict["subcategorie"],
                   derde            =   transactie_dict["derde_naam"],
                   uuid             =   uuid,
                   rekeningnummer   =   transactie_dict["rekeningnummer"],
                   details          =   transactie_dict["details"],
                   )
    
    def naar_json(self):
        
        if self.datumtijd.minute == 0 and self.datumtijd.hour == 0:
            datumtijd   =   dt.datetime.strftime(self.datumtijd, "%Y-%m-%d")
        else:
            datumtijd   =   dt.datetime.strftime(self.datumtijd, "%Y-%m-%dT%H:%M")
        
        return {"index":            self.index,
                "bedrag":           self.bedrag,
                "beginsaldo":       self.beginsaldo,
                "eindsaldo":        self.eindsaldo,
                "betaalmethode":    self.betaalmethode,
                "datumtijd":        datumtijd,
                "dagindex":         self.dagindex,
                "categorie":        self.categorie,
                "subcategorie":     self.subcategorie,
                "derde":            self.derde,
                "uuid":             self.uuid,
                "rekeningnummer":   self.rekeningnummer,
                "details":          self.details,
                }
    
    def naar_tabel(self, tabel_type: str = "samenvatting"):
        
        if tabel_type   ==  "samenvatting":
        
            return {"index":            self.index,
                    "bedrag":           self.bedrag,
                    "beginsaldo":       self.beginsaldo,
                    "eindsaldo":        self.eindsaldo,
                    "betaalmethode":    self.betaalmethode,
                    "datumtijd":        self.datumtijd,
                    "dagindex":         self.dagindex,
                    "categorie":        self.categorie,
                    "subcategorie":     self.subcategorie,
                    "derde":            self.derde,
                    "uuid":             self.uuid,
                    "rekeningnummer":   self.rekeningnummer,
                    }