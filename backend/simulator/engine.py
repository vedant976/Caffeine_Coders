import random
import uuid
import time
from datetime import datetime
from typing import Dict, List
from backend.app.models.transaction import Transaction, PaymentStatus, PaymentMethod, Issuer

class SimulationState:
    def __init__(self):
        self.issuers: Dict[str, float] = {
            "hdfc_bank": 1.0,
            "icici_bank": 1.0, 
            "kotak_mahindra_bank": 1.0,
            "sbi": 1.0
        }
        self.latency_base_ms = 200
    
    def set_issuer_health(self, issuer_id: str, health: float):
        """Health is 0.0 (dead) to 1.0 (perfect)"""
        if issuer_id in self.issuers:
            self.issuers[issuer_id] = health

    def get_issuer_health(self, issuer_id: str) -> float:
        return self.issuers.get(issuer_id, 1.0)

    def scale_infrastructure(self, issuer_id: str) -> bool:
        """Simulates adding cloud resources to improve health/latency."""
        if issuer_id in self.issuers:
            current = self.issuers[issuer_id]
            if current < 1.0:
                # Boost health by 0.3, max 1.0
                new_health = min(1.0, current + 0.3)
                self.issuers[issuer_id] = new_health
                return True
        return False

# Global Simulation State
sim_state = SimulationState()

def generate_transaction_request():
    """Generates a random transaction request."""
    amounts = [10.0, 25.0, 50.0, 99.99, 150.0, 500.0]
    methods = [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD, PaymentMethod.WALLET]
    issuers = list(sim_state.issuers.keys())
    
    return {
        "id": str(uuid.uuid4()),
        "amount": random.choice(amounts),
        "payment_method": random.choice(methods),
        "issuer_id": random.choice(issuers),
        "timestamp": datetime.utcnow()
    }

def process_transaction(tx_request: dict) -> Transaction:
    """Simulates processing logic with failure probability."""
    issuer_health = sim_state.get_issuer_health(tx_request["issuer_id"])
    
    # Calculate Latency
    latency = int(random.gauss(sim_state.latency_base_ms, 50))
    if issuer_health < 0.8:
        latency += random.randint(500, 2000) # Latency spikes when unhealthy
    if latency < 20: latency = 20
    
    # Determine Outcome
    # Base failure rate 1%
    fail_prob = 0.01 + (1.0 - issuer_health)
    
    status = PaymentStatus.SUCCESS
    error_code = None
    
    if random.random() < fail_prob:
        status = PaymentStatus.FAILURE
        error_code = "ISSUER_TIMEOUT" if latency > 1000 else "DECLINED"
    
    return Transaction(
        id=tx_request["id"],
        amount=tx_request["amount"],
        payment_method=tx_request["payment_method"],
        issuer_id=tx_request["issuer_id"],
        status=status,
        error_code=error_code,
        latency_ms=latency,
        timestamp=tx_request["timestamp"]
    )
