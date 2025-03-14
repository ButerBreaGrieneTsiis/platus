import pandas as pd

from platus.lezerschrijver import open_json, opslaan_json
from platus.transactie import Transactie

class Bankrekening:
    
    def __init__(self,
                 naam               :   str,
                 rekeningnummer     :   str,
                 transacties        :   list,
                 ):
        
        self.naam               =   naam
        self.rekeningnummer     =   rekeningnummer
        self.transacties        =   transacties
    
    @classmethod
    def open_parquet(cls,
                     rekeningnummer     :   str,
                     ):
        
        eigen_bankrekeningen    =   open_json("config", "eigen_bankrekeningen", "json")
        naam                    =   next(eigen_bankrekening["naam"] for eigen_bankrekening in eigen_bankrekeningen if eigen_bankrekening["rekeningnummer"] == rekeningnummer)
        transacties             =   pd.read_parquet(f"data\\{rekeningnummer}.parquet")
        
        return cls(naam, rekeningnummer, transacties)
    
    # @classmethod
    # def open_xlsx(cls,
    #               rekeningnummer    :   str,
    #               ):
        
    #     eigen_bankrekeningen    =   open_json("config", "eigen_bankrekeningen", "json")
    #     naam                    =   next(eigen_bankrekening["naam"] for eigen_bankrekening in eigen_bankrekeningen if eigen_bankrekening["rekeningnummer"] == rekeningnummer)
    #     transacties             =   pd.read_excel(f"data\\{rekeningnummer}.xlsx")
        
    #     return cls(naam, rekeningnummer, transacties)
    
    @classmethod
    def open_json(cls,
                  rekeningnummer    :   str,
                  ):
        
        eigen_bankrekeningen    =   open_json("config", "eigen_bankrekeningen", "json")
        naam                    =   next(eigen_bankrekening["naam"] for eigen_bankrekening in eigen_bankrekeningen if eigen_bankrekening["rekeningnummer"] == rekeningnummer)
        transacties             =   open_json("data", rekeningnummer, "json", class_mapper = lambda uuid, dict: Transactie.van_json(dict, uuid) if "bedrag" in dict.items() else dict)
        
        return cls(naam, rekeningnummer, transacties)
    
    # def opslaan_parquet(self):
        
    #     self.transacties.to_parquet(f"data\\{self.rekeningnummer}.parquet", index = False)
    
    # def opslaan_excel(self):
        
    #     self.transacties.to_excel(f"data\\{self.rekeningnummer}.xlsx", index = False)
    
    def opslaan_json(self):
        opslaan_json(self.transacties, "data", self.rekeningnummer, "json")
        
    @property
    def tabel(self):
        return pd.DataFrame([transactie.naar_tabel() for transactie in self.transacties])
    
    def toevoegen_transactie(self,
                             transactie : Transactie,
                             ):
        
        if not (self.transacties["eindsaldo"] == transactie.eindsaldo & self.transacties["bedrag"] == transactie.bedrag & self.transacties["datumtijd"] == transactie.datumtijd).any():
            
            assert self.transacties[-1].eindsaldo == transactie.beginsaldo
            
            self.transacties.append(transactie)
        
        ...