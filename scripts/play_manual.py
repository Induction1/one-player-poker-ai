import random
from env.poker_env import OnePlayerPokerEnv
from env.card_utils import hand_to_str

env = OnePlayerPokerEnv()
obs = env.reset()

while not env.done:
    print("Deck size:", obs['deck_size'])
    print("Your hand:", hand_to_str(obs['player_hand']))

    # Dumb policy: pick 3 random cards from the deck
    action = random.sample(env.deck, min(3, len(env.deck)))
    action = list(set(action))  # ensure no duplicates

    obs, reward, done, _ = env.step(action)
    env.render()

print("Game Over!")
print("Final Reward:", reward)