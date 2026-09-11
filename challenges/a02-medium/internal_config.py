# ==========================================================
# RedTeam Hacker Academy - Microservice Gateway Configuration
# CONFIDENTIAL: Internal Ingress Settings
# ==========================================================

ENVIRONMENT = "production"
CLUSTER_REGION = "eu-west-1"

# Internal Ingress Verification:
# When requests arrive from the internal management network,
# the reverse proxy forwards this cluster authorization header:
INTERNAL_AUTH_HEADER = "X-Internal-Gateway-Key"
INTERNAL_AUTH_SECRET = "RTA_SEC_INTERNAL_GATEWAY_BYPASS_9918"

# Internal Compliance & Audit Vault API:
VAULT_AUDIT_ENDPOINT = "/api/v1/internal/compliance/audit-vault"
