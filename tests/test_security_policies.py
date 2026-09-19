import unittest
from orchestrator.rate_limiter import TokenBucketLimiter
from orchestrator.policy_engine import IngressPolicyEngine


class TestSecurityPolicies(unittest.TestCase):

    def setUp(self):
        self.limiter = TokenBucketLimiter(capacity=3, refill_rate=1.0)
        self.policy = IngressPolicyEngine(
            allowed_subnets=["10.0.0.0/16", "172.16.0.0/12"],
            required_headers=["X-Service-Mesh-Token", "X-Request-ID"]
        )

    def test_token_bucket_burst_exhaustion(self):
        ip = "192.168.1.50"
        t0 = 1000.0

        # Initial burst of 3 should pass
        self.assertTrue(self.limiter.allow_request(ip, now=t0))
        self.assertTrue(self.limiter.allow_request(ip, now=t0))
        self.assertTrue(self.limiter.allow_request(ip, now=t0))

        # 4th immediate request must be blocked
        self.assertFalse(self.limiter.allow_request(ip, now=t0))

        # After 1 second, 1 token is refilled
        self.assertTrue(self.limiter.allow_request(ip, now=t0 + 1.0))

    def test_cidr_network_policy_enforcement(self):
        valid_headers = {
            "X-Service-Mesh-Token": "secret-mesh-token",
            "X-Request-ID": "req-99124"
        }

        # Authorized subnet (10.0.5.2)
        res_allowed = self.policy.validate_ingress("10.0.5.2", valid_headers)
        self.assertTrue(res_allowed["allowed"])

        # Unauthorized public IP
        res_blocked = self.policy.validate_ingress("203.0.113.195", valid_headers)
        self.assertFalse(res_blocked["allowed"])
        self.assertEqual(res_blocked["reason"], "UNAUTHORIZED_SOURCE_NETWORK")

    def test_malicious_script_injection_interception(self):
        toxic_headers = {
            "X-Service-Mesh-Token": "mesh-tok",
            "X-Request-ID": "123",
            "User-Agent": "<script>alert('xss')</script>"
        }
        res = self.policy.validate_ingress("10.0.1.5", toxic_headers)
        self.assertFalse(res["allowed"])
        self.assertEqual(res["reason"], "MALICIOUS_PAYLOAD_DETECTED")


if __name__ == "__main__":
    unittest.main()