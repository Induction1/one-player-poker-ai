import torch
from env.poker_env import OnePlayerPokerEnv
from agent.model import PolicyNetwork
from agent.runner import encode_observation
from env.card_utils import hand_to_str

# --- Load trained model ---
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
policy_net = PolicyNetwork().to(device)
policy_net.load_state_dict(torch.load("checkpoints-m1/policy.pth", map_location=device))
policy_net.eval()

# --- Run simulation ---
env = OnePlayerPokerEnv()
obs = env.reset()
done = False

print("\n🎮 Starting policy rollout...\n")

while not done:
    obs_tensor = encode_observation(obs).unsqueeze(0).to(device)
    with torch.no_grad():
        logits = policy_net(obs_tensor).squeeze()

        valid_mask = torch.zeros(52, device=device)
        valid_mask[env.deck] = 1

        masked_logits = logits * valid_mask - 1e9 * (1 - valid_mask)
        probs = torch.softmax(masked_logits, dim=-1)

        action = torch.multinomial(probs, num_samples=5).tolist()

        if isinstance(action, int):
            action = [action]

    print(f"Step {env.round + 1}:")
    print(f"  Action (target IDs): {action}")
    print(f"  Player hand: {hand_to_str(env.player_hand)}")

    obs, reward, done, _ = env.step(action)

    if done:
        print(f"\n🏁 Final Player hand: {hand_to_str(env.player_hand)}")
        print(f"💥 Final reward: {reward}")
        print(f"🎴 Opponent's best hand: {env.best_opponent_hand()}")