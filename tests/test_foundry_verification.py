"""The opt-in verifier must retain evidence even before inference can start."""
import asyncio
import importlib.util
import json
from pathlib import Path

import pytest


def test_missing_endpoint_preserves_failure_without_secret_values(monkeypatch, tmp_path):
    path = Path(__file__).parents[1] / 'scripts' / 'verify_foundry.py'
    spec = importlib.util.spec_from_file_location('verify_foundry', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.delenv('FOUNDRY_PROJECT_ENDPOINT', raising=False)
    monkeypatch.setenv('TRAJECTAN_FOUNDRY_KEY', 'unit-test-sensitive-placeholder')
    output = tmp_path / 'failure.json'
    with pytest.raises(SystemExit, match='Missing FOUNDRY_PROJECT_ENDPOINT'):
        asyncio.run(module.main(str(output)))
    raw = output.read_text()
    report = json.loads(raw)
    assert report['failure']['stage'] == 'preflight'
    assert report['configuration_present']['TRAJECTAN_FOUNDRY_KEY'] is True
    assert not report['live_inference_observed']
    assert not report['complete_workflow_verified']
    assert report['roles_exercised'] == []
    assert 'unit-test-sensitive-placeholder' not in raw
