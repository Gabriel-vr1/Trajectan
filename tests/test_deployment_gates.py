"""Deployment must stop before publication when approval/bootstrap gates fail.
These are CLI test doubles, not evidence of Azure service eligibility or deployment.
"""

import importlib.util
import json
from pathlib import Path
import sys
import pytest


def module():
    spec = importlib.util.spec_from_file_location(
        "deploy_azure", Path(__file__).parents[1] / "scripts/deploy_azure.py"
    )
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def parameters(tmp_path):
    values = dict(
        prefix="testapp",
        containerImage="example/trajectan@sha256:" + "a" * 64,
        postgresPassword="ci-test-placeholder",
        appDatabasePassword="ci-app-placeholder",
        foundryProjectEndpoint="https://example.services.ai.azure.com/api/projects/test",
        foundryResourceGroup="existing-group",
        foundryResourceName="example",
    )
    path = tmp_path / "params.json"
    path.write_text(
        json.dumps({"parameters": {k: {"value": v} for k, v in values.items()}})
    )
    return path


def test_apply_requires_financial_approval_before_any_mutation(monkeypatch, tmp_path):
    deploy = module()
    monkeypatch.setattr(deploy.shutil, "which", lambda _: "/test/az")
    calls = []

    def az(*args, **kwargs):
        calls.append(args)
        return {"id": "approved-sub", "state": "Enabled"}

    monkeypatch.setattr(deploy, "az", az)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "deploy",
            "apply",
            "--subscription",
            "approved-sub",
            "--parameters",
            str(parameters(tmp_path)),
        ],
    )
    with pytest.raises(SystemExit, match="owner-approved estimate"):
        deploy.main()
    assert calls == [("account", "show")]


def test_failed_database_bootstrap_never_creates_public_api_or_foundry_role(
    monkeypatch, tmp_path
):
    deploy = module()
    monkeypatch.setattr(deploy.shutil, "which", lambda _: "/test/az")
    calls = []

    def az(*args, **kwargs):
        calls.append(args)
        if args[:2] == ("account", "show"):
            return {"id": "approved-sub", "state": "Enabled"}
        if args[:3] == ("containerapp", "job", "start"):
            return {"name": "execution-1"}
        if args[:4] == ("containerapp", "job", "execution", "show"):
            return {"properties": {"status": "Failed"}}
        return {}

    monkeypatch.setattr(deploy, "az", az)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "deploy",
            "apply",
            "--subscription",
            "approved-sub",
            "--parameters",
            str(parameters(tmp_path)),
            "--approved-estimate-usd",
            "12",
            "--approved-hours",
            "72",
        ],
    )
    with pytest.raises(SystemExit, match="API was not deployed"):
        deploy.main()
    assert not any(c[:3] == ("role", "assignment", "create") for c in calls)
    creates = [c for c in calls if c[:3] == ("deployment", "group", "create")]
    assert len(creates) == 1
    assert "deployApi=true" not in creates[0]
