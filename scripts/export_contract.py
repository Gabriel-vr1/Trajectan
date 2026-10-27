import json
from pathlib import Path
from trajectan.api import app

Path("docs/openapi.json").write_text(json.dumps(app.openapi(), indent=2) + "\n")
