"""
Distributed Service Registry with Active TTL Lease Tracking.
Evicts degraded nodes and dynamically balances traffic across healthy upstream targets.
"""
from dataclasses import dataclass
import time
from typing import Dict, List, Optional


@dataclass
class ServiceInstance:
    instance_id: str
    service_name: str
    host: str
    port: int
    ttl_seconds: float
    last_heartbeat: float


class ServiceRegistry:
    def __init__(self):
        self._services: Dict[str, Dict[str, ServiceInstance]] = {}
        self._round_robin_index: Dict[str, int] = {}

    def register(self, service_name: str, instance_id: str, host: str, port: int, ttl: float = 5.0):
        """Register or renew a service node with a time-to-live (TTL) lease."""
        if service_name not in self._services:
            self._services[service_name] = {}
            self._round_robin_index[service_name] = 0

        now = time.time()
        self._services[service_name][instance_id] = ServiceInstance(
            instance_id=instance_id,
            service_name=service_name,
            host=host,
            port=port,
            ttl_seconds=ttl,
            last_heartbeat=now
        )

    def prune_unhealthy_nodes(self, current_time: Optional[float] = None):
        """Evict stale instances whose TTL lease has expired."""
        now = current_time if current_time is not None else time.time()
        for s_name in list(self._services.keys()):
            for inst_id in list(self._services[s_name].keys()):
                node = self._services[s_name][inst_id]
                if now - node.last_heartbeat > node.ttl_seconds:
                    del self._services[s_name][inst_id]

    def resolve_next(self, service_name: str) -> Optional[ServiceInstance]:
        """Round-robin load balancer returning the next healthy service node."""
        self.prune_unhealthy_nodes()
        nodes: List[ServiceInstance] = list(self._services.get(service_name, {}).values())

        if not nodes:
            return None

        idx = self._round_robin_index.get(service_name, 0) % len(nodes)
        self._round_robin_index[service_name] = idx + 1
        return nodes[idx]