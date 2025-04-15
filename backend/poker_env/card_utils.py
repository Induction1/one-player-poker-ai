SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']


def id_to_card(card_id):
    """Convert card ID (0–51) to (rank, suit)."""
    suit = SUITS[card_id // 13]
    rank = RANKS[card_id % 13]
    return rank, suit


def card_to_str(card_id):
    """Return human-readable string like 'A♠'."""
    rank, suit = id_to_card(card_id)
    return f"{rank}{suit}"


def hand_to_str(hand):
    """Convert list of card IDs to a readable hand string."""
    return ' '.join(card_to_str(card) for card in sorted(hand))


def card_id(rank, suit):
    """Convert (rank, suit) to card ID (0–51)."""
    suit_index = SUITS.index(suit)
    rank_index = RANKS.index(rank)
    return suit_index * 13 + rank_index


def id_to_numeric(card_id):
    """Return (rank, suit) where rank ∈ [2–14], suit ∈ [0–3]."""
    rank = (card_id % 13) + 2
    suit = card_id // 13
    return rank, suit
