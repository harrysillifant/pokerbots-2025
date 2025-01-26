from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
from strategy import node_maps
from functions import get_cluster, encode_node
from nodedefs import BountyNode
import eval7
import numpy as np
import random


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
        self.node_maps = node_maps
        

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
        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_bounty = round_state.bounties[active]  # your current bounty rank
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot
        if street != 0:
            street -= 2
        cluster = get_cluster(my_cards, my_bounty, board_cards, (20 if street == 1 else 10), (15 if street == 1 else 10))
        # actions_taken = self.actions_taken
        # last_action = self.last_action
        pot = self.pot #### HOW IS POT WORKING HERE
        id = encode_node(street, cluster, self.last_action, self.pot)
        strat = self.node_maps[street].get(id) ### NEED TO CONVERT ALL THE NODE OBJECTS INTO JUST THE AVG STRATEGY
        inc_pot = pot+1
        dec_pot = pot-1
        # HANDLE UNVISITED NODE
        while strat is None and inc_pot <= 800 and dec_pot >= 3: # Ended up in an unseen node
            id = encode_node(street, cluster, self.last_action, inc_pot)
            strat = self.node_maps[street].get(id)
            inc_pot += 1
            id = encode_node(street, cluster, self.last_action, dec_pot)
            strat = self.node_maps[street].get(id)
            dec_pot -= 1

        if strat is None: print("BRUH")

        actions = list(range(len(strat)))
        idx = random.choices(actions, weights=strat, k=1)[0]
        action = valid_actions[idx]

        if RaiseAction in legal_actions:
            min_raise, max_raise = round_state.raise_bounds()
            min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
            max_cost = max_raise - my_pip  # the cost of a maximum bet/raise

        if action == 0:
            return FoldAction()
        elif action == 1:
            return CheckAction()
        elif action == 2:
            return CallAction()
        elif action == 3:
            if continue_cost + pot//3 <= my_stack: # Can play move
                amt = max(min_raise, pot//3)
                amt = min(max_raise, amt)
                return RaiseAction(amt)
            else:
                return RaiseAction(max_raise)
        elif action == 4:
            if continue_cost + 2*pot//3 <= my_stack: # Can play move
                amt = max(min_raise, 2*pot//3)
                amt = min(max_raise, amt)
                return RaiseAction(amt)
            else:
                return RaiseAction(max_raise)
        elif action == 5:
            if continue_cost + pot <= my_stack: # Can play move
                amt = max(min_raise, pot)
                amt = min(max_raise, amt)
                return RaiseAction(amt)
            else:
                return RaiseAction(max_raise)
        else:
            return RaiseAction(max_raise)



        # if RaiseAction in legal_actions:
        #    min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
        #    min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
        #    max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
        # if RaiseAction in legal_actions:
        #     if random.random() < 0.5:
        #         return RaiseAction(min_raise)
        # if CheckAction in legal_actions:  # check-call
        #     return CheckAction()
        # if random.random() < 0.25:
        #     return FoldAction()
        # return CallAction()


if __name__ == '__main__':
    run_bot(Player(), parse_args())
