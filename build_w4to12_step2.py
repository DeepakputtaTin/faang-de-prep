"""Step 2: Write kb_weeks4to12.py from pickle using repr()."""
import pickle

with open("weeks4to12_data.pkl", "rb") as f:
    DATA = pickle.load(f)

print("Loaded keys:", list(DATA.keys()))

with open("kb_weeks4to12.py", "w", encoding="utf-8") as out:
    out.write("def L(n, emoji, title, body):\n")
    out.write("    return f'<div class=\"level level-{n}\"><div class=\"level-badge\">{emoji} Level {n} \u2014 {title}</div><div class=\"rich\">{body}</div></div>'\n\n")
    out.write("WEEKS4_TO_7 = {\n\n")

    for topic_key, topic_val in DATA.items():
        out.write(f"    # {topic_key}\n")
        out.write(f"    {topic_key!r}: {{\n")
        for field_key, field_val in topic_val.items():
            out.write(f"        {field_key!r}: {field_val!r},\n")
        out.write("    },\n\n")

    out.write("}\n")

print("Written. Verifying...")
ns = {}
exec(open("kb_weeks4to12.py", encoding="utf-8").read(), ns)
keys = list(ns["WEEKS4_TO_7"].keys())
print("Topics:", keys)
print("Sample (hash_maps Level 1 exists):", 'hash_maps' in ns['WEEKS4_TO_7'])
print("✅ Done")
