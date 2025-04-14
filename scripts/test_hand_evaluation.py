from env.poker_env import OnePlayerPokerEnv
from env.card_utils import card_id

env = OnePlayerPokerEnv()


def test_hand(name, cards, expected_rank):
    result = env.evaluate_hand(cards)
    passed = result[0] == expected_rank
    print(f"{name}: {'PASS' if passed else 'FAIL'} | Output: {result}")
    if not passed:
        print(f"  Expected rank: {expected_rank}")


def make_hand(ranks, suits):
    return [card_id(ranks[i], suits[i]) for i in range(5)]


# Test hands
test_hand("Royal Flush", make_hand(['10', 'J', 'Q', 'K', 'A'], ['♠', '♠', '♠', '♠', '♠']), 8)
test_hand("Straight Flush", make_hand(['5', '6', '7', '8', '9'], ['♥', '♥', '♥', '♥', '♥']), 8)
test_hand("Four of a Kind", [
    card_id('9', '♠'), card_id('9', '♥'), card_id('9', '♦'), card_id('9', '♣'), card_id('K', '♠')
], 7)
test_hand("Full House", [
    card_id('Q', '♠'), card_id('Q', '♥'), card_id('Q', '♦'), card_id('8', '♣'), card_id('8', '♥')
], 6)
test_hand("Flush", make_hand(['2', '6', '9', 'J', 'K'], ['♦', '♦', '♦', '♦', '♦']), 5)
test_hand("Straight", make_hand(['4', '5', '6', '7', '8'], ['♠', '♣', '♠', '♠', '♠']), 4)
test_hand("Three of a Kind", [
    card_id('3', '♠'), card_id('3', '♥'), card_id('3', '♣'), card_id('9', '♦'), card_id('J', '♠')
], 3)
test_hand("Two Pair", [
    card_id('10', '♠'), card_id('10', '♦'), card_id('6', '♥'), card_id('A', '♠'), card_id('6', '♦')
], 2)
test_hand("One Pair", [
    card_id('K', '♠'), card_id('K', '♦'), card_id('9', '♥'), card_id('5', '♣'), card_id('2', '♠')
], 1)
test_hand("High Card", make_hand(['3', '6', '9', 'J', 'A'], ['♠', '♠', '♣', '♥', '♥']), 0)
