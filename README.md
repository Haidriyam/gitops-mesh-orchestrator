![Mesh Orchestrator CI](https://github.com/Haidriyam/gitops-mesh-orchestrator/actions/workflows/devsecops-ci.yml/badge.svg)

# GitOps Multi-Cluster Ingress & Service Mesh Orchestrator

A high-performance service mesh ingress orchestrator designed for zero-trust microservice environments. Features dynamic TTL service discovery, round-robin load distribution, token-bucket burst traffic shaping, and zero-trust CIDR header inspection.

```text
[ Client Traffic Ingress ] ──► [ Ingress Policy Engine ] ──► (Token Bucket Limiter)
                                      │                                │
                           (CIDR / Header Auditing)             (Burst Shaper)
                                      │                                │
                                      ▼                                ▼
                         [ Dynamic Service Registry ] ◄── (TTL Heartbeat Leases)
                                      │
                         [ Round-Robin Forwarding ]
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                 [ Node-A :8080 ]          [ Node-B :8080 ]