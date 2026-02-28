"""Combine week3 parts into kb_week3.py using pickle for clean data transfer."""
import importlib.util
import pickle
import re

def load_module(path):
    spec = importlib.util.spec_from_file_location("m", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

p1 = load_module("week3_content_p1.py")
p2 = load_module("week3_content_p2.py")

WEEK3 = {}
WEEK3.update(p1.WEEK3_PARTIAL)
WEEK3.update(p2.WEEK3_PARTIAL2)

print("All keys:", list(WEEK3.keys()))
assert len(WEEK3) == 6

# Save to pickle
with open("week3_data.pkl", "wb") as f:
    pickle.dump(WEEK3, f)
print("Pickled.")
