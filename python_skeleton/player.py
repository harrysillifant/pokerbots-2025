from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
# from functions import encode_node, decode_node, find_nearest_point, find_nearest_pip
# from nodedefs import BountyNode
from ranges import RangeGenerator
import eval7
import numpy as np
import random
import pickle

def load(filename):
    with open(f"{filename}.pkl", "rb") as f:
        ds = pickle.load(f)
    # print(f"Loaded from {filename}.pkl")
    return ds
def convert(node_maps): # Convert id:BountyNode -> id: dict of actions
    res_holds = {}
    for street in range(4):
        res = {}
        for id in node_maps[street].keys():
            node = node_maps[street].get(id)
            strat = node.get_avg_strategy()
            res[id] = strat # [(strat[a] if a in node.strategy.keys() else 0) for a in range(7)]
        res_holds[street] = res
    return res_holds

allowed_pips = [1,2,4,6,8,10,12,15,18,20,25,30,50,100,150,200,250,300,350,400]

def strings_to_cards(card_strs):
    cards = []
    for card_str in card_strs:
        try:
            cards.append(eval7.Card(card_str))
        except ValueError:
            print(f"Invalid card string: {card_str}")
    return cards

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



import numpy as np

def find_nearest_point(street, target, disinclude=[]):
    if street == 1:
        points = flop_centroids
    elif street == 2:
        points = turn_centroids
    elif street == 3:
        points = river_centroids
    else:
        raise ValueError("Invalid street value. Must be 1, 2, or 3.")
    print(disinclude)
    if disinclude:
        disinclude = np.array(disinclude)
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
    else:
        # Compute distances directly using all points
        distances = np.sum((points - target) ** 2, axis=1)

        # Find the index of the nearest point
        nearest_index = np.argmin(distances)

        return nearest_index


actions = ["f", "ch", "ca", "sb", "mb", "lb", "ai", "r", None]
pips = [1,2,4,6,8,10,12,15,18,20,25,30,50,100,150,200,250,300,350,400]
class BountyNode:
    def __init__(self, street, cluster, num_actions_at_street, last_action, other_pip, threshold=0.1):
        self.strategy = {}
        self.cum_strategy = {}
        self.cum_regret = {}
        self.threshold = threshold

        if last_action is None:
            if other_pip == 2 and street == 0: # sb acting at start of preflop
                for a in (0,2,3,4,5,6):
                    self.strategy[actions[a]] = 0
                    self.cum_strategy[actions[a]] = 0
                    self.cum_regret[actions[a]] = 0
            else: # Start of other streets, bb acts
                for a in (1,6):
                    self.strategy[actions[a]] = 0
                    self.cum_strategy[actions[a]] = 0
                    self.cum_regret[actions[a]] = 0
                allowed_bets = []
                if 2 <= other_pip + other_pip//2 < 400:
                    allowed_bets.append(3)
                elif 2 <= other_pip + other_pip < 400:
                    allowed_bets.append(4)
                elif 2 <= other_pip + 2*other_pip < 400:
                    allowed_bets.append(5)
                for a in allowed_bets: # add allin
                    self.strategy[actions[a]] = 0
                    self.cum_strategy[actions[a]] = 0
                    self.cum_regret[actions[a]] = 0

        elif last_action == "ch": # last player checked, can now check, bet(4)
            for a in (1,6): # all in and check always allowed
                self.strategy[actions[a]] = 0
                self.cum_strategy[actions[a]] = 0
                self.cum_regret[actions[a]] = 0
            if other_pip <= 10:
                  allowed_bets = [3,4,5,6]
            else:
                allowed_bets = []
                if 2 <= other_pip + other_pip//2 < 400:
                    allowed_bets.append(3)
                elif 2 <= other_pip + other_pip < 400:
                    allowed_bets.append(4)
                elif 2 <= other_pip + 2*other_pip < 400:
                    allowed_bets.append(5)
            for a in allowed_bets: # add allin
                self.strategy[actions[a]] = 0
                self.cum_strategy[actions[a]] = 0
                self.cum_regret[actions[a]] = 0

        elif last_action in ("sb","mb","lb"): # Opp bet, can reraise
            for a in (0,2,6): # Can always fold, call, allin
                self.strategy[actions[a]] = 0
                self.cum_strategy[actions[a]] = 0
                self.cum_regret[actions[a]] = 0
            if 2<= other_pip + other_pip < 400: # can legally raise
                self.strategy[actions[7]] = 0
                self.cum_strategy[actions[7]] = 0
                self.cum_regret[actions[7]] = 0

        elif last_action == "r": # Opp raised, can reraise if num_actions < 3
            for a in (0,2): # Can always fold or call
                self.strategy[actions[a]] = 0
                self.cum_strategy[actions[a]] = 0
                self.cum_regret[actions[a]] = 0
            if num_actions_at_street < 3:
                if 2<= other_pip + other_pip < 400: # can legally raise
                    self.strategy[actions[7]] = 0
                    self.cum_strategy[actions[7]] = 0
                    self.cum_regret[actions[7]] = 0
                self.strategy[actions[6]] = 0
                self.cum_strategy[actions[6]] = 0
                self.cum_regret[actions[6]] = 0


        elif last_action == "ai": # last player went all in, can now fold, call
            for a in (0,2):
                self.strategy[actions[a]] = 0
                self.cum_strategy[actions[a]] = 0
                self.cum_regret[actions[a]] = 0
        else:
            raise ValueError(f"Invalid last_action_taken: {last_action}")

        total = len(self.strategy.keys())
        for a in self.strategy.keys():
            self.strategy[a] = 1/total
            self.cum_strategy[a] = 0
            self.cum_regret[a] = 0

    def get_strategy(self, realization_weight):
        normalizing_factor = 0
        for a in self.strategy.keys():
            self.strategy[a] = max(0, self.cum_regret[a])
            normalizing_factor += self.strategy[a]
        for a in self.strategy.keys():
            if normalizing_factor == 0:
                self.strategy[a] = 1/len(self.strategy)
            else:
                self.strategy[a] /= normalizing_factor
        for a in self.strategy.keys():
            self.cum_strategy[a] += realization_weight*self.strategy[a]
        return self.strategy

    def get_avg_strategy(self):
        normalizing_factor = 0
        for a in self.strategy.keys():
            normalizing_factor += self.cum_strategy[a]
        for a in self.strategy.keys():
            if normalizing_factor == 0:
                self.cum_strategy[a] = 1/len(self.strategy)
            else:
                self.cum_strategy[a] /= normalizing_factor
        return self.cum_strategy

    def threshold_actions(self):
        to_del = []
        for a in self.strategy.keys():
            if self.strategy[a] <= self.threshold:
                to_del.append(a)
        for a in to_del:
            del self.strategy[a]
            del self.cum_strategy[a]
            del self.cum_regret[a]


flop_centroids = load("flop_centroids")
turn_centroids = load("turn_centroids")
river_centroids = load("river_centroids")


class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        self.strategy_profile = convert(load("strategy80000"))
        self.ranges_indexed = RangeGenerator().ranges

        

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        # my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        # game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        # round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        # my_cards = round_state.hands[active]  # your cards
        self.big_blind = bool(active)  # True if you are the big blind
        # my_bounty = round_state.bounties[active]  # your current bounty rank
        self.num_actions_ive_taken = 0
        pass

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        #my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        #previous_state = terminal_state.previous_state  # RoundState before payoffs
        #street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        #my_cards = previous_state.hands[active]  # your cards
        #opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        #opponent_bounty = teriminal_state.bounty_hits # True if opponent hit bounty
        pass

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        # my_cards_str = round_state.hands[active]
        # board_cards_str = round_state.deck[:street]
        my_cards = strings_to_cards(round_state.hands[active])  # your cards
        board_cards = strings_to_cards(round_state.deck[:street])  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_bounty = round_state.bounties[active]  # your current bounty rank
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot
        bounty_hit = (my_bounty in [card.rank for card in my_cards]) or (my_bounty in [card.rank for card in board_cards])

        if my_pip == 0 and opp_pip == 0:
            self.num_actions_ive_taken = 0
    
        if self.big_blind: # Start non preflop streets
            if street == 0:
                if self.num_actions_ive_taken == 0:
                    actions_taken = 1
                else:
                    actions_taken = 3
            else:
                if self.num_actions_ive_taken == 0:
                    actions_taken = 0
                else:
                    actions_taken = 2
        else:
            if street == 0:
                if self.num_actions_ive_taken == 0:
                    actions_taken = 0
                else:
                    actions_taken = 2
            else:
                if self.num_actions_ive_taken == 0:
                    actions_taken = 1
                else:
                    actions_taken = 3
                    


        # Do street conversion (from 3,4,5 -> 1,2,3)
        if street != 0:
            street -= 2

        # Find cluster
        point = self.get_cluster(my_cards, my_bounty, board_cards, (20 if street == 1 else 10), (15 if street == 1 else 10))
        # get_cluster produces the point if not preflop, cluster if preflop
        if street == 0:
            cluster = point
        else:
            cluster = find_nearest_point(street, point) # find nearest point is point -> cluster
            if bounty_hit:
                cluster += 75

        # Sb you bet the other_pip/2
        # mb you bet the other_pip
        # lb you bet the other_pip*2
        # r you bet the other_pip

        # Find last action played
        if actions_taken == 0:
            last_action = None
        else:
            if continue_cost: # opp bet/raised
                if opp_contribution == 400:
                    last_action = "ai"
                else:
                    if continue_cost <= my_contribution/2:
                        last_action = "sb"
                    elif my_contribution/2 < continue_cost <= 3*my_contribution/2:
                        last_action = "mb"
                    else:
                        last_action = "lb"
            else:
                last_action = "ch"

            
        other_pip = find_nearest_pip(opp_contribution)
        other_pip_index = allowed_pips.index(other_pip)
        
        print(f"Street {street}, Cluster {cluster}, Actions taken {actions_taken}, Last Action {last_action} Other pip {other_pip}")
        id = encode_node(cluster, actions_taken, last_action, other_pip)

        og_cluster = cluster
        # Postflop: Attempt to find nearby node by finding nearest cluster
        strat = self.strategy_profile[street].get(id)
        new_point = point
        disinclude = [cluster]
        tracker = 0
        while strat is None and tracker < 200:
            if street == 0: # Idea for finding nearby preflop cluster: check other clusters in the same range
                if cluster > 169: 
                    cluster -= 1
                else:
                    cluster += 1
                # raise TypeError(f"No node preflop! Cluster {cluster}, Actions {actions_taken}, Last action {last_action}, Other pip {other_pip}")
            else:
                cluster = find_nearest_point(street, new_point, disinclude)
                if bounty_hit:
                    if street == 0:
                        cluster += 169
                    else:
                        cluster += 75
            if last_action in ("sb", "mb", "lb"):
                for a in ("sb", "mb", "lb"):
                    id = encode_node(cluster, actions_taken, last_action, other_pip)
                    strat = self.strategy_profile[street].get(id)
                    if strat is not None:
                        print("ye")
                        break
            else:
                id = encode_node(cluster, actions_taken, last_action, other_pip)
                strat = self.strategy_profile[street].get(id)
            disinclude.append(cluster)
            tracker += 1

        if strat is None:
            up = other_pip_index
            down = other_pip
            while strat is None and tracker < 400:
                up_id = encode_node(og_cluster, actions_taken, last_action, allowed_pips[up])
                strat = self.strategy_profile[street].get(up_id)
                if strat is not None:
                    break
                down_id = encode_node(og_cluster, actions_taken, last_action, allowed_pips[down])
                strat = self.strategy_profile[street].get(down_id)
            
        

        if strat is None: 
            raise TypeError("Failed to find infoset!")

        a = random.choices(list(strat.keys()), weights=strat.values(), k=1)[0]

        if RaiseAction in legal_actions:
            min_raise, max_raise = round_state.raise_bounds()
            min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
            max_cost = max_raise - my_pip  # the cost of a maximum bet/raise

        self.num_actions_ive_taken += 1

        if a == "f":
            if FoldAction in legal_actions:
                return FoldAction()
            else:
                raise TypeError("Illegal Fold!")
        elif a == "ch":
            if CheckAction in legal_actions:
                return CheckAction()
            else:
                raise TypeError("Illegal Check!")
        elif a == "ca":
            if CallAction in legal_actions:
                return CallAction()
            else:
                raise TypeError("Illegal Call!")
        else:
            if RaiseAction in legal_actions:
                if a == "sb":
                    bet = opp_contribution + opp_contribution//2
                    if bet <= my_stack: # Can play move
                        amt = max(min_raise, bet)
                        return RaiseAction(amt)
                    else:
                        return RaiseAction(max_raise)   
                elif a == "mb":
                    bet = opp_contribution + opp_contribution
                    if bet <= my_stack: # Can play move
                        amt = max(min_raise, bet)
                        return RaiseAction(amt)
                    else:
                        return RaiseAction(max_raise)
                elif a == "lb":
                    bet = opp_contribution + 2*opp_contribution
                    if bet <= my_stack: # Can play move
                        amt = max(min_raise, bet)
                        return RaiseAction(amt)
                    else:
                        return RaiseAction(max_raise)
                elif a == "r":
                    rais = opp_contribution + opp_contribution
                    if rais <= my_stack: # Can play move
                        amt = max(min_raise, rais)
                        return RaiseAction(amt)
                    else:
                        return RaiseAction(max_raise)
                elif a == "ai":
                    return RaiseAction(max_raise)
                else:
                    raise TypeError("Funky Raise!")
            else:
                raise TypeError("Action invalid!")


    def get_cluster(self, hole, bounty, board,  mc_iters, opp_hand_samples=10, disinclude = []):
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
            isomorphic_groups = load("iso_groups")
            
            rank1 = str(hole_pair[0]).upper()[0]
            rank2 = str(hole_pair[1]).upper()[0]
            suit1 = hole_pair[0].suit
            suit2 = hole_pair[1].suit
            
            if POKER_ORDER[rank1] > POKER_ORDER[rank2]:
                first, second = rank1, rank2
            else:
                first, second = rank2, rank1
            
            if suit1 == suit2:
                hole_string = first + second + "s"
            else:
                hole_string = first + second + "o"
            return isomorphic_groups.index(hole_string)

        
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
        # print(self.ranges_indexed)
        for ran in self.ranges_indexed.keys():
            avg_equity = 0
            hands_in_range = self.ranges_indexed[ran]
            for _ in range(opp_hand_samples):
                opp_hand = list(random.choice(hands_in_range)) # Randomly picks a hand from the range
                # print(opp_hand)
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
        # cluster = find_nearest_point(street, np.array(point).reshape(1,10)) # returns index of the nearest cluster
        return np.array(point).reshape(1,10)
        # if player_bounty_hit:
        #     return cluster + 75, street, np.array(point).reshape(1,10)
        # else:
        #     return cluster

if __name__ == '__main__':
    run_bot(Player(), parse_args())
