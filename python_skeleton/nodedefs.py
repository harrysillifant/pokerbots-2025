class BountyNode:
    def __init__(self, cluster, num_actions_at_street, last_action_taken, pot, threshold=0.05): 
        # all actions are fold, check1, check2, call, smallbet, midbet, largebet, allin
        self.cum_regret = [0]*7
        self.strategy= [0]*7
        self.cum_strategy = [0]*7
        self.cluster = cluster
        self.pot = pot
        self.threshold = threshold

        if last_action_taken is None:
            if pot == 3: # This is first action of game
                self.valid_actions = [0,2,4,5,6] # can fold, call, midbet, largebet, allin
            else: # Start of other streets
                self.valid_actions = [1]
                new_pot = pot + 2*pot//3
                for a, bet in enumerate([new_pot//3, 2*new_pot//3, new_pot]):
                    if bet >= 2 and bet+new_pot//2 < 400:
                        self.valid_actions.append(a+3)
                self.valid_actions.append(6)

        elif last_action_taken == 1: # last player checked, can now bet(4)
            self.valid_actions = [1]
            for a, bet in enumerate([pot//3, 2*pot//3, pot]):
                if bet >= 2 and bet+pot//2 < 400:
                    self.valid_actions.append(a+3)
            self.valid_actions.append(6)
        elif last_action_taken == 3: # last player small bet, can now raise(4), fold, call
            if num_actions_at_street < 3:
                new_pot = pot + 2*pot//3 # This is bringing us up to the opponents raise
                self.valid_actions = [0,2]
                for a, bet in enumerate([new_pot//3, 2*new_pot//3, new_pot]):
                    if bet >= 2 and bet+new_pot//2 < 400:
                        self.valid_actions.append(a+3)
                self.valid_actions.append(6)
            else: # at the max actions, can only fold or call
                self.valid_actions = [0,2]
        elif last_action_taken == 4: # last player mid bet, can now raise(4), fold, call
            if num_actions_at_street < 3:
                new_pot = pot + 2*pot//3
                self.valid_actions = [0,2]
                for a, bet in enumerate([new_pot//3, 2*new_pot//3, new_pot]):
                    if bet >= 2 and bet+new_pot//2 < 400:
                        self.valid_actions.append(a+3)
                self.valid_actions.append(6)
            else:
                self.valid_actions = [0,3]
        elif last_action_taken == 5: # last player large bet, can now raise(4), fold, call
            if num_actions_at_street < 3:
                new_pot = pot + 2*pot//3
                self.valid_actions = [0,3]
                for a, bet in enumerate([new_pot//3, 2*new_pot//3, new_pot]):
                    if bet >= 2 and bet+new_pot//2 < 400:
                        self.valid_actions.append(a+3)
                self.valid_actions.append(6)
            else:
                self.valid_actions = [0,2]
        elif last_action_taken == 6: # last player went all in, can now fold, call
            self.valid_actions = [0,2]

        # Actions: [fold, check, call, smallbet, midbet, largebet, allin]


    def get_strategy(self, realization_weight):
        normalizing_factor = 0
        for a in self.valid_actions:
            self.strategy[a] = max(0, self.cum_regret[a])
            normalizing_factor += self.strategy[a]
        for a in self.valid_actions:
            if normalizing_factor == 0:
                self.strategy[a] = 1/len(self.valid_actions)
            else:
                self.strategy[a] /= normalizing_factor
        for a in self.valid_actions:
            self.cum_strategy[a] += realization_weight*self.strategy[a]
        return self.strategy

    def get_avg_strategy(self):
        normalizing_factor = 0
        for a in self.valid_actions:
            normalizing_factor += self.cum_strategy[a]
        for a in self.valid_actions:
            if normalizing_factor == 0:
                self.cum_strategy[a] = 1/len(self.valid_actions)
            else:
                self.cum_strategy[a] /= normalizing_factor
        return self.cum_strategy

    def threshold_actions(self):
        for a in self.valid_actions[:]:  # Create a shallow copy
            if self.strategy[a] <= self.threshold:
                self.strategy[a] = 0
                self.valid_actions.remove(a)

