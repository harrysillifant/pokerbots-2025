from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
from strategy import node_maps
from itertools import combinations_with_replacement # NOT ALLOWED
import eval7
import numpy as np

import random

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

def hole_pair_index(hole_pair):
    # NEEDS TESTING
    isomorphic_groups = generate_isomorphic_groups()
    rank1 = str(hole_pair[0]).upper()[0]
    rank2 = str(hole_pair[1]).upper()[0]
    suit1 = hole_pair[0].suit
    suit2 = hole_pair[1].suit
    ranks = sorted([rank1, rank2], reverse=True)
    if suit1 == suit2:
        hole_string = ranks[0] + ranks[1] + "s"
    else:
        hole_string = ranks[0] + ranks[1] + "o" 
    return isomorphic_groups.index(hole_string)


def find_nearest_point(street, target):
        if street == 1:
            points = allflopclusters 
        elif street == 2:
            points = allturnclusters
        elif street == 3:
            points = allriverclusters
        # points is a 100x10 np array, target is a 1x10 np array
        distances = np.sum((points - target) ** 2, axis=1)
        nearest_index = np.argmin(distances)
        return nearest_index

def get_cluster(hole, bounty, board,  mc_iters, opp_hand_samples=10):
    # Do the EV MC simulation against the 10 ranges.
    # Find nearest cluster neighbor
    player_bounty_hit = (True if (bounty in hole) or (bounty in board) else False)
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
            opp_hand = random.choice(ran) # Randomly picks a hand from the range
            wins = 0
            deck = eval7.Deck()
            deck.cards = [card for card in deck.cards if (card not in hole and card not in opp_hand and card not in board)]
            # Begin simulation for this our hole vs theirs with the flop down
            if street == 3: # River
                # print(hole, cards[2:])
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
    cluster = self.find_nearest_point(np.array(point).reshape(1,10)) # returns index of the nearest cluster
    
    if player_bounty_hit:
        return cluster + 100
    else:
        return cluster