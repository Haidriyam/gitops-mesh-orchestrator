import unittest
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
        # Register with short TTL
        self.registry.register("order-service", "node-1", "10.0.2.1", 9000, ttl=2.0)

        # Simulate time jump beyond TTL
        self.registry.prune_unhealthy_nodes(current_time=100.0)

        # Querying now should return None
        resolved = self.registry.resolve_next("order-service")
        self.assertIsNone(resolved)


if __name__ == "__main__":
    unittest.main()