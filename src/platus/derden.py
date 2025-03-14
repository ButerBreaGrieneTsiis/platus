class Derde:
    
    def __init__(self, 
                 naam           :   str,
                 uuid           :   str,
                 type           :   str,
                 transacties    :   list,
                 ):
        
        self.naam           =   naam
        self.uuid           =   uuid
        self.type           =   type
        self.transacties    =   transacties
    
    def toevoegen_transacatie(self, transactie):
        
        self.transacties.append(transactie.uuid)

class Persoon(Derde):
    
    def __init__(self,
                 naam           :   str,
                 uuid           :   str,
                 transacties    :   list,
                 groep          :   str,
                 rekeningnummer :   list,
                 iban           :   list,
                ):
                 
        Derde.super().__init__(naam         =   naam,
                               uuid         =   uuid,
                               type         =   "persoon",
                               transacties  =   transacties,
                               )
        
        self.groep              =   groep
        self.rekeningnummer     =   rekeningnummer
        self.iban               =   iban
    
    # @classmethod
    # def nieuw(cls, naam, groep)
    
class Bedrijf(Derde):

    def __init__(self,
                 naam           :   str,
                 uuid           :   str,
                 transacties    :   list,
                 synoniemen     :   list,
                 uitsluiten     :   bool,
                 subcategorie   :   str,
                 
                 ):
        # sommige bedrijven bevatten geen rekeningnummer, zoals Albert Heijn, maar bij online bestellingen wel... Deze gewoon in transactie.details laten
        Derde.super().__init__(naam         =   naam,
                               uuid         =   uuid,
                               type         =   "bedrijf",
                               transacties  =   transacties,
                               )
        
        self.synoniemen     =   synoniemen
        self.uitsluiten     =   uitsluiten
        self.subcategorie   =   subcategorie

class PersoonGroep:
        
    def __init__(self,
                    naam       :   str,
                    uuid       :   str,
                    personen   :   list,
                    ):
            
            self.naam      =   naam
            self.personen  =   personen
            self.uuid      =   uuid

