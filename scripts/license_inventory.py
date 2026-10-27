"""Record installed dependency license metadata without choosing a project license."""

import importlib.metadata as metadata
import json
from pathlib import Path

python = []
for dist in metadata.distributions():
    m = dist.metadata
    license_name = (
        m.get("License-Expression")
        or m.get("License")
        or "See distribution license files"
    )
    python.append(
        {
            "name": m["Name"],
            "version": dist.version,
            "license_metadata": license_name.splitlines()[0][:200],
        }
    )
lock = json.loads(Path("frontend/package-lock.json").read_text())
node = [
    {
        "name": path.removeprefix("node_modules/"),
        "version": value.get("version"),
        "license_metadata": value.get("license", "See package license files"),
    }
    for path, value in lock["packages"].items()
    if path
]
Path("docs/dependency-licenses.json").write_text(
    json.dumps(
        {
            "note": "Inventory only; retain upstream license/notice files in distributions. Project license requires owner decision.",
            "python": sorted(python, key=lambda x: x["name"].lower()),
            "node": node,
        },
        indent=2,
    )
    + "\n"
)
