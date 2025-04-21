from typing import Dict, Any


class PlatusType:
    
    @classmethod
    def van_json(
        cls,
        **dict: Dict[str, Any]
    ):
        
        return cls(**dict)
    
    def naar_json(self) -> dict:
        
        dict    =   {}
        
        for veld, waarde in self.__dict__.items():
            
            if veld == "type":
                continue
            if isinstance(waarde, list):
                if len(waarde) == 0:
                    continue
            if isinstance(waarde, bool):
                if not waarde:
                    continue
            if waarde is None:
                continue
            dict[veld]    =   waarde
        
        return dict
