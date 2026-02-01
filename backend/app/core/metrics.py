from typing import List, Dict
from datetime import datetime, timedelta
from backend.app.models.transaction import Transaction, PaymentStatus
import threading

class MetricsStore:
    def __init__(self, window_seconds=60):
        self.transactions: List[Transaction] = []
        self.window_seconds = window_seconds
        self.lock = threading.Lock()
        
    def add(self, tx: Transaction):
        with self.lock:
            self.transactions.append(tx)
            self._cleanup()
            
    def _cleanup(self):
        cutoff = datetime.utcnow() - timedelta(seconds=self.window_seconds)
        self.transactions = [t for t in self.transactions if t.timestamp > cutoff]
        
    def get_stats(self):
        with self.lock:
            total = len(self.transactions)
            if total == 0:
                return {"total": 0, "success_rate": 1.0, "avg_latency": 0}
            
            success = sum(1 for t in self.transactions if t.status == PaymentStatus.SUCCESS)
            avg_lat = sum(t.latency_ms for t in self.transactions) / total
            
            # Group by Issuer
            issuers = {}
            for t in self.transactions:
                if t.issuer_id not in issuers:
                    issuers[t.issuer_id] = {"total": 0, "success": 0, "latency": []}
                issuers[t.issuer_id]["total"] += 1
                issuers[t.issuer_id]["latency"].append(t.latency_ms)
                if t.status == PaymentStatus.SUCCESS:
                    issuers[t.issuer_id]["success"] += 1
            
            issuer_stats = {}
            for iid, data in issuers.items():
                issuer_stats[iid] = {
                    "success_rate": data["success"] / data["total"],
                    "avg_latency": sum(data["latency"]) / len(data["latency"]),
                    "volume": data["total"]
                }
                
            return {
                "total": total,
                "success_rate": success / total,
                "avg_latency": avg_lat,
                "by_issuer": issuer_stats
            }

global_metrics = MetricsStore()
