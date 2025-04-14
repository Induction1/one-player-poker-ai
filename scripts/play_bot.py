import torch
from env.poker_env import OnePlayerPokerEnv
from agent.model import PolicyNetwork
from agent.runner import encode_observation, select_action_topk
from env.card_utils import hand_to_str

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load trained policy
policy_net = PolicyNetwork().to(device)
policy_net.load_state_dict(torch.load("policy.pth", map_location=device))
policy_net.eval()

# Create environment
env = OnePlayerPokerEnv()
obs_dict = env.reset()
done = False

print("Starting game (BOT):")
env.render()

while not done:
    obs_tensor = encode_observation(obs_dict).to(device)

    with torch.no_grad():
        logits = policy_net(obs_tensor)

    action_mask, _ = select_action_topk(logits, k=3)
    action_subset = [i for i in range(52) if action_mask[i] == 1.0 and i in env.deck]

    print(f"\nBot picked subset: {hand_to_str(action_subset)}")

    obs_dict, reward, done, _ = env.step(action_subset)
    env.render()

print("\nGame Over!")
if reward == 1:
    print("✅ Bot won!")
elif reward == 0:
    print("⚖️ Draw.")
else:
    print("❌ Bot lost.")