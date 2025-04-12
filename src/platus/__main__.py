from grienetsiis import invoer_kiezen
from .gegevens.gegevens import verwerken_maand

def uitvoeren():
    
    while True:
    
        opdracht   =   invoer_kiezen("opdracht", ["stop", "gegevens", "weergave", "rapport"])
        
        if opdracht == "stop":
            break
        elif opdracht == "gegevens":
            verwerken_maand()
        else:
            raise NotImplementedError

if __name__ == "__main__":
    uitvoeren()