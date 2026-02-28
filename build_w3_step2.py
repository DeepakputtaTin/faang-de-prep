"""Step 2: Load pickle and write kb_week3.py using repr() for reliable serialization."""
import pickle

with open("week3_data.pkl", "rb") as f:
    WEEK3 = pickle.load(f)

print("Loaded keys:", list(WEEK3.keys()))

with open("kb_week3.py", "w", encoding="utf-8") as out:
    out.write("def L(n, emoji, title, body):\n")
    out.write("    return f'<div class=\"level level-{n}\"><div class=\"level-badge\">{emoji} Level {n} \u2014 {title}</div><div class=\"rich\">{body}</div></div>'\n\n")
    out.write("WEEK3 = {\n\n")

    for topic_key, topic_val in WEEK3.items():
        out.write(f"    # {topic_key}\n")
        out.write(f"    {topic_key!r}: {{\n")
        for field_key, field_val in topic_val.items():
            out.write(f"        {field_key!r}: {field_val!r},\n")
        out.write("    },\n\n")

    out.write("}\n")

print("Written. Verifying...")
ns = {}
exec(open("kb_week3.py", encoding="utf-8").read(), ns)
print("Topics:", list(ns["WEEK3"].keys()))
print("Basics sample:", ns["WEEK3"]["dimensional_modeling"]["basics"][:80])
print("✅ Done")
