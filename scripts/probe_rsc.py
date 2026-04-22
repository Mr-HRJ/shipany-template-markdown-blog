"""Inspect RSC payload structure for a specific local HTML file."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_shipany_docs import js_unescape

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

NAMES = ["ai-platform-tutorial", "how-desgin-webpage"]
for name in NAMES:
    html = open(f"C:/temp/{name}.html", encoding="utf-8").read()
    pushes = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.DOTALL)
    full = js_unescape("".join(pushes))
    print(f"=== {name} ({len(full)} chars) ===")
    # Find all values > 80 chars in simple quoted JSON strings (no escape)
    for m in re.finditer(r'"(children|text|title|description|markdown|body|html|value)":\s*"([^"]{80,})"', full):
        k = m.group(1)
        v = m.group(2)
        if "nano banana" in v.lower() or "image editor" in v.lower() or "Nano Banana" in v:
            continue
        print(f"  {k} ({len(v)}): {v[:200]!r}")
    # Raw signals
    for needle in ["youtube", "youku", "bilibili", ".mp4", "/videos/", "video-url"]:
        if needle in full.lower():
            idx = full.lower().find(needle)
            print(f"  has {needle} at {idx}: {full[max(0,idx-50):idx+100]!r}")
