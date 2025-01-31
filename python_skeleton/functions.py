from itertools import combinations_with_replacement
from centroids import flop_centroids, turn_centroids, river_centroids
import eval7
import numpy as np

import random




def encode_node(cluster, num_actions, last_action, pip):
    """
    Compute the local_index for (cluster, num_actions, last_action, pip) using allowed pips and actions.

    :param cluster:      Integer, 0..337 if street=0, else 0..149
    :param num_actions:  Integer, 0..3
    :param last_action:  String from actions or None
    :param pip:          Integer, one of the allowed pips
    :return:             local_index
    """
    allowed_pips = [1,2,4,6,8,10,12,15,18,20,25,30,50,100,150,200,250,300,350,400]
    actions = ["f","ch","ca","sb","mb","lb","ai","r",None]
    # Validate inputs
    if pip not in allowed_pips:
        raise ValueError("Pip size not in allowed_pips.")
    if num_actions < 0 or num_actions > 3:
        raise ValueError("num_actions must be an integer between 0 and 3.")

    # Actions, extended to include None
    actions = ["f", "ch", "ca", "sb", "mb", "lb", "ai", "r"]
    extended_actions = actions + [None]

    if last_action not in extended_actions:
        raise ValueError("last_action must be a valid action from the actions list or None.")

    # Get the index of the last_action
    la_idx = extended_actions.index(last_action)  # Convert action string or None to index

    # Find the pip index in allowed_pips
    pip_idx = allowed_pips.index(pip)

    # Calculate the local_index
    local_index = (cluster * len(allowed_pips) * len(extended_actions) * 4) + \
                  (num_actions * len(allowed_pips) * len(extended_actions)) + \
                  (la_idx * len(allowed_pips)) + pip_idx

    return local_index

def decode_node(local_index):
    """
    Decode the local_index back into (cluster, num_actions, last_action, pip).

    :param local_index: Encoded index.
    :return:            A tuple (cluster, num_actions, last_action, pip).
    """
    allowed_pips = [1,2,4,6,8,10,12,15,18,20,25,30,50,100,150,200,250,300,350,400]
    actions = ["f","ch","ca","sb","mb","lb","ai","r",None]
    # Actions, extended to include None
    actions = ["f", "ch", "ca", "sb", "mb", "lb", "ai", "r"]
    extended_actions = actions + [None]

    # Constants for decoding
    ACTION_SIZE = len(extended_actions)  # Includes None
    PIP_SIZE = len(allowed_pips)
    NUM_ACTIONS_SIZE = 4  # num_actions is in 0..3

    # Decode pip index
    pip_idx = local_index % PIP_SIZE
    local_index //= PIP_SIZE

    # Decode last_action index
    la_idx = local_index % ACTION_SIZE
    local_index //= ACTION_SIZE

    # Decode num_actions
    num_actions = local_index % NUM_ACTIONS_SIZE
    local_index //= NUM_ACTIONS_SIZE

    # Decode cluster
    cluster = local_index

    # Map pip_idx back to pip size
    pip = allowed_pips[pip_idx]

    # Map la_idx back to last_action string or None
    last_action = extended_actions[la_idx]

    return cluster, num_actions, last_action, pip


def find_nearest_pip(pip):
    allowed_pips = [1,2,4,6,8,10,12,15,18,20,25,30,50,100,150,200,250,300,350,400]
    return min(allowed_pips, key=lambda p: abs(p - pip))



def find_nearest_point(self, street, target, disinclude=[]):
    if street == 1:
        points = flop_centroids
    elif street == 2:
        points = turn_centroids
    elif street == 3:
        points = river_centroids
    else:
        raise ValueError("Invalid street value. Must be 1, 2, or 3.")
    
    disinclude = np.array(disinclude)
    print(disinclude)
    # Create a mask to exclude points in disinclude
    mask = np.ones(len(points), dtype=bool)
    mask[disinclude] = False  # Set False for indices in disinclude

    # Filter points using the mask
    filtered_points = points[mask]

    # Calculate distances only for filtered points
    distances = np.sum((filtered_points - target) ** 2, axis=1)

    # Find the index of the nearest point in the filtered points
    nearest_index_filtered = np.argmin(distances)
    
    # Map back to the original indices
    original_indices = np.where(mask)[0]
    nearest_index = original_indices[nearest_index_filtered]

    return nearest_index

