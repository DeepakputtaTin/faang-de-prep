"""Combine all 3 parts into kb_weeks4to12.py using pickle."""
import importlib.util
import pickle

def load(path):
    spec = importlib.util.spec_from_file_location("m", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

p1 = load("weeks4to12_content_p1.py")
p2 = load("weeks4to12_content_p2.py")
p3 = load("weeks4to12_content_p3.py")

DATA = {}
DATA.update(p1.WEEKS4_PARTIAL)
DATA.update(p2.WEEKS4_PARTIAL2)
DATA.update(p3.WEEKS4_PARTIAL3)

print("Combined keys:", list(DATA.keys()))
assert len(DATA) == 8, f"Expected 8, got {len(DATA)}"

with open("weeks4to12_data.pkl", "wb") as f:
    pickle.dump(DATA, f)
print("Pickled OK.")
