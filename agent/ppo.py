import torch
import torch.nn.functional as F


class PPOAgent:
    def __init__(self, policy_net, value_net, policy_lr=3e-4, value_lr=1e-3, clip_eps=0.2, value_coef=0.5,
                 entropy_coef=0.01):
        self.policy_net = policy_net
        self.value_net = value_net
        self.clip_eps = clip_eps
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef

        self.policy_optimizer = torch.optim.Adam(self.policy_net.parameters(), lr=policy_lr)
        self.value_optimizer = torch.optim.Adam(self.value_net.parameters(), lr=value_lr)

    def compute_returns_and_advantages(self, rewards, values, dones, gamma=0.99, lam=1.0):
        """Compute advantages and discounted returns using GAE or basic delta method."""
        returns = []
        advantages = []
        gae = 0
        next_value = 0

        for t in reversed(range(len(rewards))):
            mask = 1.0 - dones[t].item()
            delta = rewards[t] + gamma * next_value * mask - values[t]
            gae = delta + gamma * lam * mask * gae
            advantage = gae
            next_value = values[t]

            advantages.insert(0, advantage)
            returns.insert(0, advantage + values[t])

        return torch.stack(returns), torch.stack(advantages)

    def update(self, buffer, epochs=4, batch_size=64):
        obs = buffer['obs']
        actions = buffer['actions']
        old_log_probs = buffer['log_probs']
        rewards = buffer['rewards']
        values = buffer['values']
        dones = buffer['dones']

        returns, advantages = self.compute_returns_and_advantages(rewards, values, dones)

        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        dataset_size = len(obs)
        indices = torch.arange(dataset_size)

        for _ in range(epochs):
            for start in range(0, dataset_size, batch_size):
                end = start + batch_size
                batch_idx = indices[start:end]

                batch_obs = obs[batch_idx]
                batch_actions = actions[batch_idx]
                batch_old_log_probs = old_log_probs[batch_idx]
                batch_returns = returns[batch_idx]
                batch_advantages = advantages[batch_idx]

                # Forward pass
                logits = self.policy_net(batch_obs)
                probs = torch.softmax(logits, dim=-1)

                new_log_probs = torch.log((probs * batch_actions).sum(dim=-1) + 1e-8)
                entropy = -(probs * torch.log(probs + 1e-8)).sum(dim=-1).mean()

                ratio = torch.exp(new_log_probs - batch_old_log_probs)
                clipped_ratio = torch.clamp(ratio, 1 - self.clip_eps, 1 + self.clip_eps)

                policy_loss = -torch.min(ratio * batch_advantages, clipped_ratio * batch_advantages).mean()

                # Value function loss
                values_pred = self.value_net(batch_obs).squeeze()
                value_loss = F.mse_loss(values_pred, batch_returns.squeeze())

                total_loss = policy_loss + self.value_coef * value_loss - self.entropy_coef * entropy

                # Optimize
                self.policy_optimizer.zero_grad()
                self.value_optimizer.zero_grad()
                total_loss.backward()
                self.policy_optimizer.step()
                self.value_optimizer.step()
