"""Reproducible, approval-gated deployment using an authenticated local Azure CLI.
Plan performs no provisioning. Apply requires the owner's approved configuration
and estimate; this software cannot enforce the subscription's actual spending.
"""

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def az(*args, capture=False):
    command = [shutil.which("az") or "az", *map(str, args), "--only-show-errors"]
    if capture:
        return json.loads(
            subprocess.check_output(command + ["--output", "json"], text=True)
        )
    subprocess.run(command, check=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=["plan", "apply"])
    p.add_argument("--subscription", required=True)
    p.add_argument(
        "--parameters",
        type=Path,
        required=True,
        help="Private local ARM parameters JSON; never commit it",
    )
    p.add_argument("--resource-group", default="rg-trajectan-hackathon")
    p.add_argument("--approved-estimate-usd", type=float)
    p.add_argument("--approved-hours", type=int)
    a = p.parse_args()
    if not shutil.which("az"):
        raise SystemExit(
            "Azure CLI is unavailable; run with the authenticated local Azure CLI."
        )
    account = az("account", "show", capture=True)
    if account["id"] != a.subscription or account["state"] != "Enabled":
        raise SystemExit(
            "Select the approved enabled subscription in Azure CLI first; no account was changed."
        )
    parameters = json.loads(a.parameters.read_text())["parameters"]
    values = {k: v["value"] for k, v in parameters.items()}
    required = [
        "prefix",
        "containerImage",
        "postgresPassword",
        "appDatabasePassword",
        "foundryProjectEndpoint",
        "foundryResourceGroup",
        "foundryResourceName",
    ]
    if any(not values.get(k) for k in required):
        raise SystemExit("Missing required deployment parameters.")
    if values.get("deployApi") or values.get("deployStaticWebApp"):
        raise SystemExit(
            "Initial parameters must leave deployApi/deployStaticWebApp false; the script stages API creation after bootstrap."
        )
    if not values["containerImage"].count("@sha256:") == 1:
        raise SystemExit(
            "Use a public, tested container image pinned by @sha256 digest."
        )
    if a.mode == "apply" and not (
        a.approved_estimate_usd is not None
        and 0 < a.approved_estimate_usd <= 15
        and a.approved_hours is not None
        and 0 < a.approved_hours <= 72
    ):
        raise SystemExit(
            "Apply requires the owner-approved estimate (<= $15) and deployment period (<=72 hours). Review docs/AZURE_COSTS.md first."
        )
    common = [
        "--subscription",
        a.subscription,
        "--resource-group",
        a.resource_group,
        "--template-file",
        ROOT / "infra/main.bicep",
        "--parameters",
        "@" + str(a.parameters.resolve()),
    ]
    az("deployment", "group", "validate", *common, "--output", "none")
    az("deployment", "group", "what-if", *common)
    # Also review the second phase, which exposes the API and its identity.
    az("deployment", "group", "what-if", *common, "--parameters", "deployApi=true")
    if a.mode == "plan":
        print(
            "Plan only: review policy/quota, costs, both what-if phases, image access and Foundry role scope before approving apply."
        )
        return
    az(
        "deployment",
        "group",
        "create",
        *common,
        "--name",
        "trajectan-infrastructure",
        "--output",
        "none",
    )
    prefix = values["prefix"]
    execution = az(
        "containerapp",
        "job",
        "start",
        "--name",
        prefix + "-bootstrap",
        "--resource-group",
        a.resource_group,
        "--subscription",
        a.subscription,
        capture=True,
    )
    execution_name = execution["name"]
    for _ in range(30):
        state = az(
            "containerapp",
            "job",
            "execution",
            "show",
            "--name",
            prefix + "-bootstrap",
            "--job-execution-name",
            execution_name,
            "--resource-group",
            a.resource_group,
            "--subscription",
            a.subscription,
            capture=True,
        )
        status = state["properties"]["status"]
        if status == "Succeeded":
            break
        if status in ("Failed", "Stopped", "Degraded"):
            raise SystemExit(
                "Database bootstrap failed; inspect job logs privately. API was not deployed."
            )
        time.sleep(5)
    else:
        raise SystemExit(
            "Bootstrap not confirmed within 150 seconds; inspect execution before proceeding. API was not deployed."
        )
    outputs = az(
        "deployment",
        "group",
        "show",
        "--name",
        "trajectan-infrastructure",
        "--resource-group",
        a.resource_group,
        "--subscription",
        a.subscription,
        "--query",
        "properties.outputs",
        capture=True,
    )
    # Foundry User on the existing project (not Owner on the subscription).
    project_scope = (
        outputs["foundryScope"]["value"]
        + "/projects/"
        + values["foundryProjectEndpoint"].rstrip("/").split("/")[-1]
    )
    az(
        "role",
        "assignment",
        "create",
        "--assignee-object-id",
        outputs["principalId"]["value"],
        "--assignee-principal-type",
        "ServicePrincipal",
        "--role",
        "53ca6127-db72-4b80-b1b0-d745d6d5456d",
        "--scope",
        project_scope,
        "--subscription",
        a.subscription,
        "--output",
        "none",
    )
    az(
        "deployment",
        "group",
        "create",
        *common,
        "--parameters",
        "deployApi=true",
        "--name",
        "trajectan-application",
        "--output",
        "none",
    )
    url = az(
        "deployment",
        "group",
        "show",
        "--name",
        "trajectan-application",
        "--resource-group",
        a.resource_group,
        "--subscription",
        a.subscription,
        "--query",
        "properties.outputs.apiUrl.value",
        capture=True,
    )
    print("Deployed origin: " + url)
    print(
        "Run scripts/smoke.py and browser tests against this origin. Verify managed-identity Foundry inference, Service Bus and persistence before claiming cloud success."
    )
    print(
        "Review actual Azure Cost Management usage before the approved period ends; no automatic financial cap was created."
    )


if __name__ == "__main__":
    main()
