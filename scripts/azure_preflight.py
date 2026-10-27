"""Read-only Azure inventory through the user's already authenticated local CLI.
No login, role change, resource registration, provisioning or token output.
"""

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def az(*args):
    return json.loads(
        subprocess.check_output(
            [
                shutil.which("az") or "az",
                *args,
                "--output",
                "json",
                "--only-show-errors",
            ],
            text=True,
        )
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--resource-group", default="rg-trajectan-hackathon")
    p.add_argument("--location", default="spaincentral")
    p.add_argument("--output", default="azure-preflight.local.json")
    a = p.parse_args()
    if not shutil.which("az"):
        raise SystemExit(
            "Azure CLI is unavailable here. Run this script with your authenticated local Azure CLI."
        )
    account = az("account", "show", "--query", "{name:name,id:id,state:state}")
    scope = "/subscriptions/" + account["id"]
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "account": account,
        "requested_location": a.location,
        "checks": {},
    }
    checks = {
        "resource_group": [
            "group",
            "show",
            "--name",
            a.resource_group,
            "--query",
            "{name:name,location:location,state:properties.provisioningState}",
        ],
        "resources": [
            "resource",
            "list",
            "--query",
            "[].{name:name,type:type,region:location,resourceGroup:resourceGroup}",
        ],
        "subscription_policy": [
            "policy",
            "assignment",
            "list",
            "--scope",
            scope,
            "--disable-scope-strict-match",
            "true",
        ],
        "resource_group_policy": [
            "policy",
            "assignment",
            "list",
            "--scope",
            scope + "/resourceGroups/" + a.resource_group,
            "--disable-scope-strict-match",
            "true",
        ],
        "container_quota": ["containerapp", "list-usages", "--location", a.location],
        "postgres_skus": [
            "postgres",
            "flexible-server",
            "list-skus",
            "--location",
            a.location,
        ],
    }
    for provider in (
        "Microsoft.App",
        "Microsoft.DBforPostgreSQL",
        "Microsoft.ServiceBus",
        "Microsoft.Network",
        "Microsoft.ManagedIdentity",
        "Microsoft.OperationalInsights",
    ):
        checks[provider] = [
            "provider",
            "show",
            "--namespace",
            provider,
            "--query",
            "{state:registrationState,resources:resourceTypes[].{type:resourceType,locations:locations}}",
        ]
    failures = []
    for name, command in checks.items():
        try:
            report["checks"][name] = az(*command)
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            report["checks"][name] = {"status": "unverified"}
            failures.append(name)
    report["unverified"] = failures
    report["eligibility_confirmed"] = False
    report["next_gate"] = (
        "Review actual policy parameters, quotas, B1ms availability and regional prices; ARM validate/what-if must pass. Resource-group location alone proves no service eligibility."
    )
    Path(a.output).write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {"output": a.output, "unverified": failures, "eligibility_confirmed": False}
        )
    )
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
