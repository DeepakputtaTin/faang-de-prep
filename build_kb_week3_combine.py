"""Combine week3 parts into kb_week3.py"""
import importlib.util, sys, os

def load(path):
    spec = importlib.util.spec_from_file_location("m", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

p1 = load("week3_content_p1.py")
p2 = load("week3_content_p2.py")

# Merge both partial dicts
WEEK3 = {}
WEEK3.update(p1.WEEK3_PARTIAL)
WEEK3.update(p2.WEEK3_PARTIAL2)

print("All keys:", list(WEEK3.keys()))
assert len(WEEK3) == 6, f"Expected 6 topics, got {len(WEEK3)}"

# Now write the kb_week3.py file
lines = [
    "def L(n, emoji, title, body):\n",
    "    return f'<div class=\"level level-{n}\"><div class=\"level-badge\">{emoji} Level {n} — {title}</div><div class=\"rich\">{body}</div></div>'\n\n",
    "# Content built by week3_content_p1.py + week3_content_p2.py\n",
    "# Run build_kb_week3_combine.py to regenerate\n\n",
    "WEEK3 = {\n",
]

import json

for key, val in WEEK3.items():
    lines.append(f"    {json.dumps(key)}: {{\n")
    for subkey, subval in val.items():
        if isinstance(subval, str):
            # Escape for Python string literal
            escaped = subval.replace("\\", "\\\\").replace("'", "\\'")
            lines.append(f"        {json.dumps(subkey)}: '{escaped}',\n")
        elif isinstance(subval, list):
            items_str = json.dumps(subval, ensure_ascii=False, indent=8)
            lines.append(f"        {json.dumps(subkey)}: {items_str},\n")
        else:
            lines.append(f"        {json.dumps(subkey)}: {json.dumps(subval)},\n")
    lines.append("    },\n\n")

lines.append("}\n")

with open("kb_week3.py", "w", encoding="utf-8") as f:
    f.writelines(lines)

print("kb_week3.py written, verifying...")

# Verify
exec(open("kb_week3.py", encoding="utf-8").read())
print("✅ Syntax OK. Topics:", list(WEEK3.keys()))
