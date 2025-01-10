import numpy as np

def learn_strategy():
    regret_table = np.zeros((rows,cols)) # 2d array, first dim = information sets, second dim = regret for taking action a. Rows, cols will depend on abstraction
    cumulative_strategy_table = np.zeros((rows,cols)) # 2d array, first dim = informatoin sets, second dim = 
    initial_strategy_profile = [[1/size(infoset) for a in actions_allowed_at_infoset]]

    def CFR(h, i, t, pi1, pi2):
        if 


