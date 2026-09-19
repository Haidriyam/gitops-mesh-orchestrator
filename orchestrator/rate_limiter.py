"""
High-Frequency Token-Bucket Rate Limiter.
Prevents DDoS and API starvation by governing burst rates per client IP.
"""
import time
from typing import Dict


class TokenBucketLimiter:
    def __init__(self, capacity: int = 10, refill_rate: float = 2.0):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.buckets: Dict[str, float] = {}
        self.last_update: Dict[str, float] = {}

    def allow_request(self, client_ip: str, now: float = None) -> bool:
        current_time = now if now is not None else time.time()

        if client_ip not in self.buckets:
            self.buckets[client_ip] = float(self.capacity)
            self.last_update[client_ip] = current_time

        elapsed = current_time - self.last_update[client_ip]
        self.last_update[client_ip] = current_time

        # Refill tokens up to maximum capacity
        self.buckets[client_ip] = min(
            float(self.capacity),
            self.buckets[client_ip] + (elapsed * self.refill_rate)
        )

        if self.buckets[client_ip] >= 1.0:
            self.buckets[client_ip] -= 1.0
            return True
        return False