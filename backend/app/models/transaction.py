from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel

class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"
    BLOCKED = "blocked"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    UPI = "upi"
    WALLET = "wallet"

class Issuer(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    name: str
    health_score: float = 1.0  # 0.0 to 1.0

class RoutingRule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    issuer_id: str
    payment_method: PaymentMethod
    priority: int = 1
    is_active: bool = True
    
class Transaction(SQLModel, table=True):
    id: str = Field(primary_key=True)
    amount: float
    currency: str = "USD"
    payment_method: PaymentMethod
    issuer_id: str
    status: PaymentStatus
    error_code: Optional[str] = None
    latency_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_retry: bool = False
