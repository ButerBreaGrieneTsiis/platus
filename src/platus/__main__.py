from .invoer import invoer_kiezen, verwerken

def uitvoeren():
    
    while True:
    
        opdracht   =   invoer_kiezen("opdracht", ["stop", "gegevens", "weergave", "rapport"])
        
        if opdracht == "stop":
            break
        elif opdracht == "gegevens":
            verwerken()

if __name__ == "__main__":
    uitvoeren()