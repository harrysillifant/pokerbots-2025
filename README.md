# Entry for MIT PokerBots 2025 (Bounty Holdem Poker)

This repo contains the code for my entry into the 2025 PokerBots competition. The code for the bot is contained in python_skeleton. You can run the bot by updating the config.py file with the appropriate diretories. You can run the bot with

python3 engine.py

# Counterfactual Regret Minimization
The strategy for the bot was learned using the popular Counterfactual Regret Minimization concept for extensive games like Poker. I implemented a recursive version of this algorithm, and ran it for 4 days on the Colab v5e1 TPU. The algorithm did not quite reach convergence, and a lot of game states were not reached (mostly ones that don't usually appear if both players are playing optimally), so there are still some bugs when running the code. These will be fixed shortly.
