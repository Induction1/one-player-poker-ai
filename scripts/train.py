import os
import torch
from env.poker_env import OnePlayerPokerEnv
from agent.model import PolicyNetwork, ValueNetwork
from agent.runner import collect_rollouts
from agent.ppo import PPOAgent

# Make sure checkpoints folder exists
os.makedirs("checkpoints", exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

policy_net = PolicyNetwork().to(device)
value_net = ValueNetwork().to(device)
agent = PPOAgent(policy_net, value_net)

num_iterations = 1000
num_episodes_per_iter = 5
save_every = 100
reward_history = []

for iteration in range(num_iterations):
    buffer = collect_rollouts(
        env_class=OnePlayerPokerEnv,
        policy_net=policy_net,
        value_net=value_net,
        num_episodes=num_episodes_per_iter,
        k=3,
        device=device
    )

    agent.update(buffer)

    total_reward = buffer["rewards"].sum().item()
    avg_reward = buffer["rewards"].mean().item()
    reward_history.append(avg_reward)

    print(f"Iter {iteration} — total reward: {total_reward:.2f} | avg: {avg_reward:.2f}")

    # Save periodically
    if iteration % save_every == 0 and iteration > 0:
        torch.save(policy_net.state_dict(), f"checkpoints/policy_iter{iteration}.pth")
        torch.save(value_net.state_dict(), f"checkpoints/value_iter{iteration}.pth")
        print(f"[Saved model to checkpoints/ at iter {iteration}]")

# Final save
torch.save(policy_net.state_dict(), "checkpoints/policy.pth")
torch.save(value_net.state_dict(), "checkpoints/value.pth")
print("✅ Final models saved to checkpoints/")