class Categorie:
     
    def __init__(self,
                 naam,
                 uuid,
                 subcategorieen,
                 ):
        
        self.naam              =   naam
        self.uuid              =   uuid
        self.subcategorieen    =   subcategorieen

class Subcategorie:
    
    def __init__(self,
                naam          :   str,
                index         :   int,
                uuid          :   str,
                transacties   :   list,
                bedrijven     :   list,
                trefwoorden   :   list,
                ):
        
        self.naam         =   naam
        self.index        =   index
        self.uuid         =   uuid
        self.transacties  =   transacties
        self.bedrijven    =   bedrijven
        self.trefwoorden  =   trefwoorden