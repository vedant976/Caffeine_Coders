from typing import Dict, Optional

class RoutingTable:
    def __init__(self):
        # Default: All enabled (True)
        self.routes: Dict[str, bool] = {
            "hdfc_bank": True,
            "icici_bank": True,
            "kotak_mahindra_bank": True,
            "sbi": True
        }
    
    def is_enabled(self, issuer_id: str) -> bool:
        return self.routes.get(issuer_id, True)
    
    def set_route(self, issuer_id: str, enabled: bool):
        self.routes[issuer_id] = enabled

global_routing = RoutingTable()
