import time
import urllib.request

for attempt in range(30):
    try:
        with urllib.request.urlopen(
            "http://127.0.0.1:8000/api/health", timeout=2
        ) as response:
            if response.status == 200:
                break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit("API did not become ready")
