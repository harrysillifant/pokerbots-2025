from itertools import combinations_with_replacement
from centroids import flop_centroids, turn_centroids, river_centroids
import eval7
import numpy as np

import random

POKER_ORDER = {
    'A': 14,
    'K': 13,
    'Q': 12,
    'J': 11,
    'T': 10,
    '9': 9,
    '8': 8,
    '7': 7,
    '6': 6,
    '5': 5,
    '4': 4,
    '3': 3,
    '2': 2
}

def hole_pair_index(hole_pair):
    isomorphic_groups = generate_isomorphic_groups()
    
    rank1 = str(hole_pair[0]).upper()[0]
    rank2 = str(hole_pair[1]).upper()[0]
    suit1 = hole_pair[0].suit
    suit2 = hole_pair[1].suit
    
    # Compare based on poker values, not alphabetical
    if POKER_ORDER[rank1] > POKER_ORDER[rank2]:
        first, second = rank1, rank2
    else:
        first, second = rank2, rank1
    
    # Suited or offsuit
    if suit1 == suit2:
        hole_string = first + second + "s"
    else:
        hole_string = first + second + "o"
    # Now hole_string should match what generate_isomorphic_groups() produced
    return isomorphic_groups.index(hole_string)

def generate_isomorphic_groups():
    res = []
    cards = [str(i) for i in range(2, 10)] + ["T", "J", "Q", "K", "A"]
    cards = cards[::-1]
    combos = combinations_with_replacement(cards, 2)
    for cards in combos:
        hole = cards[0] + cards[1]
        if cards[0] != cards[1]:
            res.append(hole + "s")
        res.append(hole + "o")
    return res


def find_nearest_point(self, street, target):
        if street == 1:
            points = flop_centroids
        elif street == 2:
            points = turn_centroids
        elif street == 3:
            points = river_centroids
        # points is a 100x10 np array, target is a 1x10 np array
        distances = np.sum((points - target) ** 2, axis=1)
        nearest_index = np.argmin(distances)
        return nearest_index
  
def encode_node( cluster, last_action, pot):
    """
    Compute (street_index, local_index) so you can do:
        self.node_maps[street_index][local_index]

    :param street:       0=preflop, 1=flop, 2=turn, 3=river
    :param cluster:      0..337 if street=0, else 0..149
    :param last_action:  integer in 0..6 or None
    :param pot:          3..800
    :return:             (street, local_index)
    """
    # Map None -> 7, else keep integer as is.
    if last_action is None:
        la_idx = 7
    else:
        la_idx = last_action  # should be 0..6
    
    # pot zero-based
    pot_idx = pot - 3  # 0..797

    # local_index = cluster*(8*798) + la_idx*798 + pot_idx
    local_index = (cluster * 6384) + (la_idx * 798) + pot_idx
    
    return local_index

def get_cluster(hole, bounty, board,  mc_iters, opp_hand_samples=10):
        player_bounty_hit = (True if (bounty in [card.rank for card in hole]) or (bounty in [card.rank for card in board]) else False)
        if len(board) == 0:
            street = 0
        else:
            street = len(board)-2

        if street == 0: # Preflop, here clusters are a number from 0-168 representing the number of isomorphic holes
            cluster = hole_pair_index(hole)
            if player_bounty_hit:
                return cluster + 169
            else:
                return cluster

        point = []
        for ran in self.ranges_indexed:
            avg_equity = 0
            for _ in range(opp_hand_samples):
                opp_hand = list(random.choice(ran)) # Randomly picks a hand from the range
                wins = 0
                deck = eval7.Deck()
                deck.cards = [card for card in deck.cards if (card not in hole and card not in opp_hand and card not in board)]
                # Begin simulation for this our hole vs theirs with the flop down
                if street == 3: # River
                    hand_strength = eval7.evaluate(hole + board)
                    opp_strength = eval7.evaluate(opp_hand + board)
                    if hand_strength > opp_strength:
                        avg_equity += 1
                    elif hand_strength == opp_strength:
                        avg_equity += 0.5
                else:
                    for _ in range(mc_iters):
                        deck.shuffle()
                        full_board = board + deck.peek(5-len(board))
                        hand_strength = eval7.evaluate(hole + full_board)
                        opp_strength = eval7.evaluate(opp_hand + full_board)
                        if hand_strength > opp_strength:
                            wins += 1
                        elif hand_strength == opp_strength:
                            wins += 0.5
                    avg_equity += wins/mc_iters
            point.append(avg_equity/opp_hand_samples)

        # Now have point, which is a point in 10d space, now want to find the closest cluster
        cluster = self.find_nearest_point(street, np.array(point).reshape(1,10)) # returns index of the nearest cluster
        
        if player_bounty_hit:
            return cluster + 75
        else:
            return cluster