import pickle

def load(filename):
  with open(f"{filename}.pkl", "rb") as f:
    ds = pickle.load(f)
  print(f"Loaded from {filename}.pkl")
  return ds

node_maps = load("strategy250000")