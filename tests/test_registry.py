import unittest
import time
from orchestrator.registry import ServiceRegistry


class TestServiceRegistry(unittest.TestCase):

    def setUp(self):
        self.registry = ServiceRegistry()

    def test_registration_and_round_robin_resolution(self):
        self.registry.register("auth-service", "node-1", "10.0.1.10", 8080)
        self.registry.register("auth-service", "node-2", "10.0.1.11", 8080)

        node_a = self.registry.resolve_next("auth-service")
        node_b = self.registry.resolve_next("auth-service")
        node_c = self.registry.resolve_next("auth-service")

        self.assertNotEqual(node_a.instance_id, node_b.instance_id)
        self.assertEqual(node_a.instance_id, node_c.instance_id)

    def test_ttl_eviction_of_unhealthy_nodes(self):
        t0 = time.time()
        self.registry.register("order-service", "node-1", "10.0.2.1", 9000, ttl=2.0, now=t0)

        # Node should be resolvable immediately at t0
        active = self.registry.resolve_next("order-service", current_time=t0)
        self.assertIsNotNone(active)

        # Forward time past TTL (t0 + 5.0 seconds) -> must be pruned
        resolved = self.registry.resolve_next("order-service", current_time=t0 + 5.0)
        self.assertIsNone(resolved)


if __name__ == "__main__":
    unittest.main()
