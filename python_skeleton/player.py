'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
from strategy import node_maps

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
        self.preflop_nodes = node_maps[0]
        self.postflop_nodes = node_maps[1]
        self.postturn_nodes = node_maps[2]
        self.postriver_nodes = node_maps[3]

    def get_cluster(self, hole, bounty, board,  mc_iters, opp_hand_samples=10):
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
        # big_blind = bool(active)  # True if you are the big blind
        # my_bounty = round_state.bounties[active]  # your current bounty rank


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
        #street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        #my_cards = round_state.hands[active]  # your cards
        #board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        #opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        #my_stack = round_state.stacks[active]  # the number of chips you have remaining
        #opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        #continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        #my_bounty = round_state.bounties[active]  # your current bounty rank
        #my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        #opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot
        if RaiseAction in legal_actions:
           min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
           min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
           max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
        if RaiseAction in legal_actions:
            if random.random() < 0.5:
                return RaiseAction(min_raise)
        if CheckAction in legal_actions:  # check-call
            return CheckAction()
        if random.random() < 0.25:
            return FoldAction()
        return CallAction()


if __name__ == '__main__':
    run_bot(Player(), parse_args())
