import torch
from collections import defaultdict


def encode_observation(obs_dict):
    """Convert env observation dict into a 157-dim tensor"""
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

    round_tensor = torch.tensor([obs_dict['round'] / 5.0])

    return torch.cat([deck_mask, hand_mask, opponent_mask, round_tensor], dim=0)  # Shape (157,)


def select_action_topk(logits, k=3):
    """Select top-k cards based on logits"""
    probs = torch.softmax(logits, dim=-1)
    topk_indices = torch.topk(probs, k=k).indices
    action_mask = torch.zeros(52)
    action_mask[topk_indices] = 1.0
    log_probs = torch.log(probs[topk_indices]).sum()
    return action_mask, log_probs


def collect_rollouts(env_class, policy_net, value_net, num_episodes=10, k=3, device='cpu'):
    """
    Play episodes with the current policy and return a buffer of transitions.
    """
    buffer = defaultdict(list)

    for _ in range(num_episodes):
        env = env_class()
        obs_dict = env.reset()
        done = False

        while not done:
            obs_tensor = encode_observation(obs_dict).to(device)
            logits = policy_net(obs_tensor)
            value = value_net(obs_tensor)

            action_mask, log_prob = select_action_topk(logits, k=k)
            action_subset = [i for i in range(52) if action_mask[i] == 1.0 and i in env.deck]

            obs_dict_next, reward, done, _ = env.step(action_subset)

            # Save transition
            buffer['obs'].append(obs_tensor.detach())
            buffer['actions'].append(action_mask.detach())
            buffer['log_probs'].append(log_prob.detach())
            buffer['rewards'].append(torch.tensor([reward], dtype=torch.float32))
            buffer['values'].append(value.detach())
            buffer['dones'].append(torch.tensor([done], dtype=torch.float32))

            obs_dict = obs_dict_next

    # Convert to stacked tensors
    for key in buffer:
        buffer[key] = torch.stack(buffer[key])

    return buffer
