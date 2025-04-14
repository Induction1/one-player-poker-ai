import json
import matplotlib.pyplot as plt
import numpy as np

# Load rewards
with open("checkpoints/reward_history.json", "r") as f:
    rewards = json.load(f)

# Apply smoothing
def smooth(data, weight=0.9):
    smoothed = []
    last = data[0]
    for point in data:
        smoothed_val = last * weight + (1 - weight) * point
        smoothed.append(smoothed_val)
        last = smoothed_val
    return smoothed

smoothed_rewards = smooth(rewards)

# Plot
plt.figure(figsize=(10, 5))
plt.plot(rewards, alpha=0.3, label="Raw Reward")
plt.plot(smoothed_rewards, color="royalblue", label="Smoothed Reward")
plt.xlabel("Iteration")
plt.ylabel("Avg Reward (per episode)")
plt.title("Training Progress (Smoothed)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()