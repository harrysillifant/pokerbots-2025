import pickle

def load(filename):
  with open(f"{filename}.pkl", "rb") as f:
    ds = pickle.load(f)
  print(f"Loaded from {filename}.pkl")
  return ds


flop_centroids = load("flop_centroids")
turn_centroids = load("turn_centroids")
river_centroids = load("river_centroids")