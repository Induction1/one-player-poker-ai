import itertools
import random
from itertools import combinations
from env.card_utils import hand_to_str, id_to_numeric, card_id, id_to_card
from env.poker_data import *

# Cactus Kev encoding setup
_SUITS = [1 << (i + 12) for i in range(4)]
_RANKS = [(1 << (i + 16)) | (i << 8) for i in range(13)]
_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]
_DECK = [_RANKS[r] | _SUITS[s] | _PRIMES[r] for r, s in itertools.product(range(13), range(4))]

SUITS = 'cdhs'
RANKS = '23456789TJQKA'
DECK = [''.join(s) for s in itertools.product(RANKS, SUITS)]
LOOKUP = dict(zip(DECK, _DECK))


class OnePlayerPokerEnv:
    def __init__(self):
        self.reset()

    def reset(self):
        self.deck = list(range(52))
        random.shuffle(self.deck)
        self.player_hand = []
        self.opponent_cards = []
        self.round = 0
        self.done = False
        return self.get_observation()

    def step(self, action_subset):
        """Draw from deck until a target card is found."""
        if self.done:
            raise Exception("Game is over. Call reset().")
        assert all(card in self.deck for card in action_subset), "Invalid action"

        discarded = []
        while self.deck:
            card = self.deck.pop(0)
            if card in action_subset:
                self.player_hand.append(card)
                break
            discarded.append(card)
        self.opponent_cards.extend(discarded)

        self.round += 1
        if len(self.player_hand) == 5 or not self.deck:
            self.done = True

        if self.done:
            reward = self.get_reward()
        else:
            score = self.expected_hand_score()
            reward = 0.08 * (1.0 - score / 7462.0)

        return self.get_observation(), reward, self.done, {}

    def get_observation(self):
        return {
            "round": self.round,
            "player_hand": self.player_hand.copy(),
            "opponent_cards": self.opponent_cards.copy(),
            "deck_size": len(self.deck),
        }

    def get_reward(self):
        """+1 win, 0 draw, -1 loss. Player must complete a hand."""
        if len(self.player_hand) < 5:
            return -1

        while len(self.opponent_cards) < 8 and self.deck:
            self.opponent_cards.append(self.deck.pop(0))

        player_score = self.score_hand(self.ids_to_rank_suit(self.player_hand))
        opp_score, _ = self.best_opponent_hand_rank()

        return int(player_score < opp_score) - int(player_score > opp_score)

    def ids_to_rank_suit(self, card_ids):
        return [id_to_numeric(cid) for cid in card_ids]

    def score_hand(self, hand):
        """Return cactus kev score from 5 (rank, suit) tuples."""

        def hash_function(x):
            x += 0xe91aaa35
            x ^= x >> 16
            x += x << 8
            x &= 0xffffffff
            x ^= x >> 4
            b = (x >> 8) & 0x1ff
            a = (x + (x << 2)) >> 19
            r = (a ^ HASH_ADJUST[b]) & 0x1fff
            return HASH_VALUES[r]

        try:
            card_strs = [self.cactus_to_str(rank, suit) for rank, suit in hand]
            c1, c2, c3, c4, c5 = (LOOKUP[c] for c in card_strs)
        except Exception as e:
            raise ValueError(f"Card conversion failed: {e}")

        q = (c1 | c2 | c3 | c4 | c5) >> 16
        if (0xf000 & c1 & c2 & c3 & c4 & c5):
            return FLUSHES[q]
        s = UNIQUE_5[q]
        if s:
            return s

        p = (c1 & 0xff) * (c2 & 0xff) * (c3 & 0xff) * (c4 & 0xff) * (c5 & 0xff)
        return hash_function(p)

    def cactus_to_str(self, rank, suit):
        return RANKS[rank - 2] + SUITS[suit]

    def evaluate_hand(self, hand):
        """Returns (category, tiebreakers) for standard poker logic."""
        nums = [id_to_numeric(c) for c in hand]
        r = sorted((x[0] for x in nums), reverse=True)
        suits = [x[1] for x in nums]
        flush = len(set(suits)) == 1
        straight = r == [14, 5, 4, 3, 2] or all(r[i] - 1 == r[i + 1] for i in range(4))
        high = 5 if r == [14, 5, 4, 3, 2] else r[0]

        if flush and straight: return (8, [high])
        if r.count(r[0]) == 4 or r.count(r[1]) == 4:
            four = r[1] if r.count(r[1]) == 4 else r[0]
            kicker = r[4] if r.count(r[0]) == 4 else r[0]
            return (7, [four, kicker])
        if (r[0] == r[1] == r[2] and r[3] == r[4]) or (r[0] == r[1] and r[2] == r[3] == r[4]):
            return (6, [r[2], r[0]] if r[2] == r[3] else [r[0], r[3]])
        if flush: return (5, r)
        if straight: return (4, [high])

        for i in range(3):
            if r[i] == r[i + 1] == r[i + 2]:
                kickers = [x for j, x in enumerate(r) if j not in [i, i + 1, i + 2]]
                return (3, [r[i]] + kickers)
        pairs = [x for x in set(r) if r.count(x) == 2]
        if len(pairs) == 2:
            kickers = [x for x in r if x not in pairs]
            return (2, sorted(pairs, reverse=True) + kickers)
        if len(pairs) == 1:
            kickers = [x for x in r if x != pairs[0]]
            return (1, [pairs[0]] + kickers)

        return (0, r)

    def partial_hand_score(self, hand):
        """Simple heuristic for <5-card hands."""
        if not hand: return 0.0
        ranks = [c % 13 for c in hand]
        suits = [c // 13 for c in hand]

        rank_counts = [ranks.count(i) for i in range(13)]
        suit_counts = [suits.count(i) for i in range(4)]

        score = sum(5 if c == 2 else 15 if c == 3 else 40 if c == 4 else 0 for c in rank_counts)
        score += max(suit_counts) * 2

        sorted_ranks = sorted(set(ranks))
        for i in range(len(sorted_ranks) - 1):
            gap = sorted_ranks[i + 1] - sorted_ranks[i]
            score += 3 if gap == 1 else 1 if gap == 2 else 0

        return float(score)

    def expected_hand_score(self, num_samples=100):
        """Monte Carlo estimate of the average completed hand score."""
        if len(self.player_hand) >= 5:
            return self.score_hand(self.ids_to_rank_suit(self.player_hand))

        scores = []
        pool = [c for c in self.deck if c not in self.player_hand]

        for _ in range(num_samples):
            draw = random.sample(pool, 5 - len(self.player_hand))
            full_hand = self.player_hand + draw
            rank_suit = self.ids_to_rank_suit(full_hand)
            scores.append(self.score_hand(rank_suit))

        return sum(scores) / len(scores)

    def best_opponent_hand_rank(self):
        """Return (score, hand) for best opponent 5-card combo."""
        if len(self.opponent_cards) < 5:
            return -1, []
        best = (10 ** 6, [])
        for combo in combinations(self.opponent_cards, 5):
            score = self.score_hand(self.ids_to_rank_suit(combo))
            if score < best[0]:
                best = (score, list(combo))
        return best

    def best_opponent_hand(self):
        """Return string version of best 5-card opponent hand."""
        _, hand = self.best_opponent_hand_rank()
        return " ".join(f"{a}{b}" for a, b in map(id_to_card, hand))

    def render(self):
        print(f"Round: {self.round}")
        print(f"Your hand:     {hand_to_str(self.player_hand)}")
        print(f"Opponent pool: {hand_to_str(self.opponent_cards)}")
        print(f"Cards left in deck: {len(self.deck)}")
