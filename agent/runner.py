import torch
from collections import defaultdict


def encode_observation(obs_dict):
    """Convert env observation into a (157,) tensor."""
    deck_mask = torch.zeros(52)
    hand_mask = torch.zeros(52)
    opponent_mask = torch.zeros(52)

    for card in obs_dict['player_hand']:
        hand_mask[card] = 1.0
    for card in obs_dict['opponent_cards']:
        opponent_mask[card] = 1.0
    for card in range(52):
        if card not in obs_dict['player_hand'] and card not in obs_dict['opponent_cards']:
            deck_mask[card] = 1.0

    round_one_hot = torch.zeros(5)
    if 1 <= obs_dict['round'] <= 5:
        round_one_hot[obs_dict['round'] - 1] = 1.0
    return torch.cat([deck_mask, hand_mask, opponent_mask, round_one_hot], dim=0)


def collect_rollouts(env_class, policy_net, value_net, num_episodes=10, device='cpu'):
    """Run episodes and collect rollout data for PPO."""
    buffer = defaultdict(list)

    for _ in range(num_episodes):
        env = env_class()
        obs_dict = env.reset()
        done = False

        while not done:
            obs_tensor = encode_observation(obs_dict).to(device)
            logits = policy_net(obs_tensor)
            value = value_net(obs_tensor)

            probs = torch.sigmoid(logits)
            for c in range(52):
                if c not in env.deck:
                    probs[c] = 0.0

            action_mask = (torch.rand(52, device=device) < probs).float()
            if action_mask.sum() == 0:
                action_mask[torch.argmax(probs)] = 1.0

            log_prob = (
                    action_mask * torch.log(probs + 1e-8) +
                    (1 - action_mask) * torch.log(1 - probs + 1e-8)
            ).sum()

            action_subset = [i for i in range(52) if action_mask[i] == 1.0]
            obs_dict_next, reward, done, _ = env.step(action_subset)

            buffer['obs'].append(obs_tensor.detach())
            buffer['actions'].append(action_mask.detach())
            buffer['log_probs'].append(log_prob.detach())
            buffer['rewards'].append(torch.tensor([reward], dtype=torch.float32))
            buffer['values'].append(value.detach())
            buffer['dones'].append(torch.tensor([done], dtype=torch.float32))

            obs_dict = obs_dict_next

    for key in buffer:
        buffer[key] = torch.stack(buffer[key])

    return buffer
