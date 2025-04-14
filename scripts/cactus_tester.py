from env.card_utils import hand_to_str
from env.poker_env import OnePlayerPokerEnv

env = OnePlayerPokerEnv()

env.player_hand = [0, 9, 22, 35, 48]
print("Player hand (IDs):", env.player_hand)
print("Player hand (str):", hand_to_str(env.player_hand))
player_score = env.score_hand(env.ids_to_rank_suit(env.player_hand))
print("Player hand score:", player_score)

# Opponent cards
env.opponent_cards = [1, 2, 3, 4, 5, 6, 7]
best_opp_score, best_opp_hand = env.best_opponent_hand_rank()
print("Best opponent hand:", hand_to_str(best_opp_hand))
print("Best opponent score:", best_opp_score)

# Reward check
print("Reward:", env.get_reward())