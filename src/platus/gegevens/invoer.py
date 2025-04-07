import re

def invoer_kiezen(beschrijving: str,
                  keuzes: list | dict,
                  **kwargs,
                  ):
    
    print(f"\nkies een {beschrijving}\n")
    
    if isinstance(keuzes, list):
        if kwargs.get("stoppen", False):
            print(f" [ 0] TERUG")
        [print(f" [{ikeuze}] {keuze}") for ikeuze, keuze in enumerate(keuzes, 1)]
        print()
        if kwargs.get("stoppen", False):
            ikeuze  =   invoer_validatie("keuze", int, waardes = range(len(keuzes)+1))
        else:
            ikeuze  =   invoer_validatie("keuze", int, waardes = range(1, len(keuzes)+1))
        return keuzes[ikeuze-1] if bool(ikeuze) else ikeuze
    elif isinstance(keuzes, dict):
        if kwargs.get("stoppen", False):
            print(f" [0] TERUG")
        [print(f" [{ikeuze}] {keuze}") for ikeuze, keuze in enumerate(keuzes.keys(), 1)]
        print()
        if kwargs.get("stoppen", False):
            ikeuze  =   invoer_validatie("keuze", int, waardes = range(len(keuzes)+1))
        else:
            ikeuze  =   invoer_validatie("keuze", int, waardes = range(1, len(keuzes)+1))
        return list(keuzes.values())[ikeuze-1] if bool(ikeuze) else ikeuze
    else:
        raise TypeError

def invoer_validatie(beschrijving: int,
                     type: type,
                     **kwargs,
                     ):
    
    while True:
        
        invoer  =   input(f"{beschrijving}: ")
        
        if kwargs.get("valideren", False):
            if not input("bevestig: ") == "ja":
                continue
        
        if type == int:
            try:
                invoer  =   int(invoer)
            except ValueError:
                print(f"invoer \"{invoer}\" incorrect, enkel type \"{type.__name__}\" toegestaan")
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
            if not invoer in kwargs.get("waardes", [invoer]):
                    print(f"invoer \"{invoer}\" incorrect, niet binnen ")
                    continue
            if "regex" in kwargs.keys():
                patroon     =   re.compile(kwargs.get("regex"))
                match       =   patroon.match(invoer)
                if match:
                    return match.groupdict("")
                else:
                    print(f"invoer \"{invoer}\" ongeldig")
                    continue
            return invoer
        else:
            raise NotImplementedError 
    