import numpy as np

class GameTree:
    def __init__():
        

class Node:
    def __init__():



def preflop_to_bucket():


def flop_to_bucket():


def turn_to_bucket():


def river_to_bucket():



def learn_strategy():
    regret = np.zeros((rows,cols)) # 2d array, first dim = information sets, second dim = regret for taking action a. Rows, cols will depend on abstraction
    cumulative_strategy = np.zeros((rows,cols)) # 2d array, first dim = informatoin sets, second dim = 
    sigmas = [[[1/size(infoset) for a in actions_allowed_at_infoset]]] # 3d jagged array, first dim = time, first_dim = infoset, second_dim = actions available at infoset



    def CFR(h, i, t, pi1, pi2):
        if h is terminal:
            return utility(h) # Need the utility calculator function
        else:
            if h is chance_node:
                sample single action in sigma(h)
                return CFR(h + [a], i, t, pi1, pi2)
            

        # FORWARD PASS: Compute cfvalues
        cfvalue = 0
        cfvalue_for_action = [0 for a in infoset]
        for a in infoset:
            if player(h) == 1:
                cfvalue_for_action[a] = CFR(h + [a], i, t, sigma[t][I][a]*pi1, pi2)
            else: # player 2
                cfvalue_for_action[a] = CFR(h + [a], i, t, pi1, sigma[t][I][a]*pi2)

            cfvalue += sigma[t][I][a]*cfvalue_for_action[a]


        # BACKWARD PASS: Update regrets, strategies, strategy profiles
        if player(h) == i: # Player i's turn at this history
            for a in infoset:
                regret[I][a] += pi(-i)*(cfvalue_for_action[a] - cfvalue)
                cumulative_strategy[I][a] += pi(i)*sigma[t][I][a]

            total_cfregret = sum([max(0, regret[I][a]) for a in regret[I]])
                                 
            for a in infoset:
                if total_cfregret > 0: # Use counterfactual update
                    sigma[t+1][I][a] = max(0,regret[I][a])/total_cfregret
                else:
                    sigma[t+1][I][a] = 1/size(infoset)
        
        
        return cfvalue
    
    def MCCFR():
        pass




    def run(T):
        for t in range(T):
            for i in [1,2]:
                CFR(emptyset, i, t, 1, 1)

    
    return regret, cumulative_strategy, sigmas