import torch
import torch.nn.functional as F


class PPOAgent:
    """PPO agent for multi-binary action space (52-card selection)."""

    def __init__(self, policy_net, value_net,
                 policy_lr=3e-4, value_lr=1e-3,
                 clip_eps=0.2, value_coef=0.5, entropy_coef=0.01):
        self.policy_net = policy_net
        self.value_net = value_net
        self.clip_eps = clip_eps
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef

        self.policy_optimizer = torch.optim.Adam(policy_net.parameters(), lr=policy_lr)
        self.value_optimizer = torch.optim.Adam(value_net.parameters(), lr=value_lr)

    def compute_returns_and_advantages(self, rewards, values, dones, gamma=0.99, lam=1.0):
        """Compute GAE advantages and bootstrapped returns."""
        returns, advantages = [], []
        gae = 0
        next_value = 0

        for t in reversed(range(len(rewards))):
            mask = 1.0 - dones[t].item()
            delta = rewards[t] + gamma * next_value * mask - values[t]
            gae = delta + gamma * lam * mask * gae
            next_value = values[t]

            advantages.insert(0, gae)
            returns.insert(0, gae + values[t])

        return torch.stack(returns), torch.stack(advantages)

    def update(self, buffer, epochs=4, batch_size=64):
        """Perform PPO update using collected rollout buffer."""
        obs = buffer['obs']
        actions = buffer['actions']
        old_logp = buffer['log_probs']
        rewards = buffer['rewards']
        values = buffer['values']
        dones = buffer['dones']

        returns, advantages = self.compute_returns_and_advantages(rewards, values, dones)
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        indices = torch.arange(len(obs))

        for _ in range(epochs):
            for start in range(0, len(obs), batch_size):
                end = start + batch_size
                idx = indices[start:end]

                batch_obs = obs[idx]
                batch_actions = actions[idx]
                batch_old_logp = old_logp[idx]
                batch_returns = returns[idx]
                batch_advantages = advantages[idx]

                logits = self.policy_net(batch_obs)
                probs = torch.sigmoid(logits)

                # Multi-binary log probs
                logp = (
                        batch_actions * torch.log(probs + 1e-8) +
                        (1 - batch_actions) * torch.log(1 - probs + 1e-8)
                ).sum(dim=-1)

                ratio = torch.exp(logp - batch_old_logp)
                clipped = torch.clamp(ratio, 1 - self.clip_eps, 1 + self.clip_eps)
                policy_loss = -torch.min(ratio * batch_advantages, clipped * batch_advantages).mean()

                values_pred = self.value_net(batch_obs).squeeze()
                value_loss = F.mse_loss(values_pred, batch_returns.squeeze())

                entropy = -(
                        probs * torch.log(probs + 1e-8) +
                        (1 - probs) * torch.log(1 - probs + 1e-8)
                ).sum(dim=-1).mean()
                total_loss = policy_loss + self.value_coef * value_loss - self.entropy_coef * entropy

                self.policy_optimizer.zero_grad()
                self.value_optimizer.zero_grad()
                total_loss.backward()
                self.policy_optimizer.step()
                self.value_optimizer.step()
