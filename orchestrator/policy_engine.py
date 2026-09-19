"""
Zero-Trust Ingress Policy Interceptor.
Inspects headers, enforces CIDR network restrictions, and prevents injection attacks.
"""
from typing import Dict, Any, List
import ipaddress


class IngressPolicyEngine:
    def __init__(self, allowed_subnets: List[str], required_headers: List[str]):
        self.allowed_networks = [ipaddress.ip_network(subnet) for subnet in allowed_subnets]
        self.required_headers = required_headers

    def validate_ingress(self, source_ip: str, headers: Dict[str, str]) -> Dict[str, Any]:
        client_addr = ipaddress.ip_address(source_ip)

        # Check CIDR IP allowlist
        ip_permitted = any(client_addr in network for network in self.allowed_networks)
        if not ip_permitted:
            return {"allowed": False, "reason": "UNAUTHORIZED_SOURCE_NETWORK"}

        # Validate mandatory zero-trust mesh headers
        for required in self.required_headers:
            if required not in headers:
                return {"allowed": False, "reason": f"MISSING_MANDATORY_HEADER_{required.upper()}"}

        # Injection heuristic check
        for header, value in headers.items():
            if any(char in value for char in ["<script>", "../", "||", ";"]):
                return {"allowed": False, "reason": "MALICIOUS_PAYLOAD_DETECTED"}

        return {"allowed": True, "reason": "AUTHORIZED"}