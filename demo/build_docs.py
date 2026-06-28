"""
Regenerate the demo's pinned data + the static GitHub-Pages mirror from the live engine,
so they can never drift from scenarios.py.

Run:  python3 demo/build_docs.py
- injects scenarios.run_all() into demo/index.html's `const PINNED = ...;` (record-safe fallback)
- writes the same file to docs/index.html (static page; its fetch() fails on Pages and falls
  back to PINNED automatically)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scenarios  # noqa: E402

data = json.dumps(scenarios.run_all())
idx = os.path.join(HERE, "index.html")
html = open(idx).read()
html, n = re.subn(r"const PINNED = .*?;", lambda m: f"const PINNED = {data};", html, count=1)
if n != 1:
    sys.exit("could not find `const PINNED = ...;` in demo/index.html")
open(idx, "w").write(html)
open(os.path.join(HERE, "..", "docs", "index.html"), "w").write(html)
print(f"injected PINNED ({len(data)} bytes) into demo/index.html and regenerated docs/index.html")
