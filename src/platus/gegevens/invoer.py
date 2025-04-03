def invoer_kiezen(beschrijving: str,
                  keuzes: list | dict,
                  ):
    
    print(f"\nkies een {beschrijving}\n")
    
    if isinstance(keuzes, list):
        [print(f" [{ikeuze}] {keuze}") for ikeuze, keuze in enumerate(keuzes)]
        print()
        ikeuze  =   invoer_validatie("keuze", int, waardes = range(len(keuzes)))
        return keuzes[ikeuze]
    elif isinstance(keuzes, dict):
        [print(f" [{ikeuze}] {keuze}") for ikeuze, keuze in enumerate(keuzes.keys())]
        print()
        ikeuze  =   invoer_validatie("keuze", int, waardes = range(len(keuzes)))
        return list(keuzes.values())[ikeuze]
    else:
        raise TypeError

def invoer_validatie(beschrijving: int,
                     type: type,
                     valideren: bool = False,
                     **kwargs,
                     ):
    
    while True:
        
        invoer  =   input(f"{beschrijving}: ")
        
        if valideren:
            if not input("bevestig: ") == "ja":
                continue
        
        if type == int:
            try:
                invoer  =   int(invoer)
            except ValueError:
                print(f"invoer \"{invoer}\" incorrect, enkel type \"{type}\" toegestaan")
                continue
            else:
                if not invoer in kwargs.get("waardes", [invoer]):
                    print(f"invoer \"{invoer}\" incorrect, niet binnen ")
                    continue
                if not kwargs.get("bereik", [invoer, invoer])[0] <= invoer <= kwargs.get("bereik", [invoer, invoer])[1]:
                    print(f"invoer \"{invoer}\" incorrect, moet tussen {kwargs.get("bereik", [invoer, invoer])[0]} en {kwargs.get("bereik", [invoer, invoer])[1]} liggen")
                    continue
                return invoer
        elif type == str:
            return invoer
        else:
            raise NotImplementedError
    