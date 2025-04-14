import os
import json
import torch

from env.poker_env import OnePlayerPokerEnv
from agent.model import PolicyNetwork, ValueNetwork
from agent.runner import collect_rollouts
from agent.ppo import PPOAgent

# === Config ===
num_iterations = 1000
episodes_per_iter = 150
save_every = 250
checkpoint_dir = "checkpoints-m1"

# === Setup ===
os.makedirs(checkpoint_dir, exist_ok=True)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

policy_net = PolicyNetwork().to(device)
value_net = ValueNetwork().to(device)
agent = PPOAgent(policy_net, value_net)

reward_history = []

# === Training loop ===
for iteration in range(num_iterations):
    buffer = collect_rollouts(
        env_class=OnePlayerPokerEnv,
        policy_net=policy_net,
        value_net=value_net,
        num_episodes=episodes_per_iter,
        device=device
    )

    agent.update(buffer)

    total_reward = buffer["rewards"].sum().item()
    avg_reward = buffer["rewards"].mean().item()
    reward_history.append(avg_reward)

    print(f"Iter {iteration} — total reward: {total_reward:.2f} | avg: {avg_reward:.2f}")

    if iteration > 0 and iteration % save_every == 0:
        torch.save(policy_net.state_dict(), f"{checkpoint_dir}/policy_iter{iteration}.pth")
        torch.save(value_net.state_dict(), f"{checkpoint_dir}/value_iter{iteration}.pth")
        print(f"[Checkpoint saved @ iter {iteration}]")

# === Final save ===
torch.save(policy_net.state_dict(), f"{checkpoint_dir}/policy.pth")
torch.save(value_net.state_dict(), f"{checkpoint_dir}/value.pth")
with open(f"{checkpoint_dir}/reward_history.json", "w") as f:
    json.dump(reward_history, f)
print("✅ Final models and reward history saved.")
