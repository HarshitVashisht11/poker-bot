from collections import Counter

class Hand:
    RANKS = '23456789TJQKA'
    SUITS = 'hdcs'

    def __init__(self, cards):
        self.cards = cards

    def __str__(self):
        return ' '.join(self.cards)

    def strength(self, community_cards=None):
        all_cards = self.cards + (community_cards or [])
        return self.evaluate_hand(all_cards)

    def evaluate_hand(self, cards):
        ranks = [card[0] for card in cards if len(card) >= 2]
        suits = [card[1] for card in cards if len(card) >= 2]
        rank_counts = Counter(ranks)
        suit_counts = Counter(suits)

        is_flush = max(suit_counts.values(), default=0) >= 5
        is_straight = self.is_straight(ranks)

        if is_straight and is_flush:
            return 8  # Straight Flush
        elif 4 in rank_counts.values():
            return 7  # Four of a Kind
        elif 3 in rank_counts.values() and 2 in rank_counts.values():
            return 6  # Full House
        elif is_flush:
            return 5  # Flush
        elif is_straight:
            return 4  # Straight
        elif 3 in rank_counts.values():
            return 3  # Three of a Kind
        elif list(rank_counts.values()).count(2) == 2:
            return 2  # Two Pair
        elif 2 in rank_counts.values():
            return 1  # One Pair
        else:
            return 0  # High Card

    @staticmethod
    def is_straight(ranks):
        valid_ranks = [r for r in ranks if r in Hand.RANKS]
        values = sorted(set(Hand.card_value(r) for r in valid_ranks))
        if len(values) < 5:
            return False

        # Check for standard straights
        for i in range(len(values) - 4):
            window = values[i:i + 5]
            if window == list(range(window[0], window[0] + 5)):
                return True

        # Check for Ace-low straight (A-2-3-4-5)
        ace_low_values = {Hand.card_value('A'), Hand.card_value('2'), Hand.card_value('3'),
                          Hand.card_value('4'), Hand.card_value('5')}
        if ace_low_values.issubset(set(values)):
            return True

        return False

    @staticmethod
    def card_value(rank):
        return Hand.RANKS.index(rank) if rank in Hand.RANKS else -1