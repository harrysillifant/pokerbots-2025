import pickle

def save(ds, filename):
  with open(f"{filename}.pkl", "wb") as f:
    pickle.dump(ds, f)
  print(f"Saved to {filename}.pkl")

def load(filename):
  with open(f"{filename}.pkl", "rb") as f:
    ds = pickle.load(f)
  print(f"Loaded from {filename}.pkl")
  return ds



node_maps = load("node_maps")