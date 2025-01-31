from itertools import combinations
import eval7
class RangeGenerator:
    def __init__(self):
        self.ranges = {
        "Premium": [],
        "Strong": [],
        "Medium": [],
        "Low Pocket Pair": [],
        "High Ace": [],
        "Medium-Low Suited Connector": [],
        "High King/Queen": [],
        "Low Suited Ace": [],
        "Low Suited Gapper": [],
        "Trash": []
    }
        self.RANK_MAP = {
        0: '2', 1: '3', 2: '4', 3: '5', 4: '6', 5: '7', 6: '8', 7: '9',
        8: 'T', 9: 'J', 10: 'Q', 11: 'K', 12: 'A'
    }

        self.deck = list(eval7.Deck())
        self.holes = [c for c in combinations(self.deck, 2)]

        for hole_cards in self.holes:
            if self.is_premium(hole_cards):
                self.ranges["Premium"].append(hole_cards)
            elif self.is_strong(hole_cards):
                self.ranges["Strong"].append(hole_cards)
            elif self.is_medium(hole_cards):
                self.ranges["Medium"].append(hole_cards)
            elif self.is_low_pocket(hole_cards):
                self.ranges["Low Pocket Pair"].append(hole_cards)
            elif self.is_high_ace(hole_cards):
                self.ranges["High Ace"].append(hole_cards)
            elif self.is_medium_suited_connector(hole_cards):
                self.ranges["Medium-Low Suited Connector"].append(hole_cards)
            elif self.is_high_king_or_queen(hole_cards):
                self.ranges["High King/Queen"].append(hole_cards)
            elif self.is_low_suited_ace(hole_cards):
                self.ranges["Low Suited Ace"].append(hole_cards)
            elif self.is_low_suited_gapper(hole_cards):
                self.ranges["Low Suited Gapper"].append(hole_cards)
            else:
                self.ranges["Trash"].append(hole_cards)

    def is_premium(self, cards):
        """Premium hands: AA, KK, QQ, AKs"""
        ranks = {self.RANK_MAP[cards[0].rank], self.RANK_MAP[cards[1].rank]}
        pair = cards[0].rank == cards[1].rank
        suited = cards[0].suit == cards[1].suit
        return (
            (pair and 'A' in ranks) or
            (pair and 'K' in ranks) or
            (pair and 'Q' in ranks) or
            (suited and {'A', 'K'} <= ranks)
        )

    def is_strong(self, cards):
        """Strong hands: JJ, TT, 99, AQs, AJs, KQs, AQo, KQo"""
        ranks = {self.RANK_MAP[cards[0].rank], self.RANK_MAP[cards[1].rank]}
        pair = cards[0].rank == cards[1].rank
        suited = cards[0].suit == cards[1].suit
        strong_pairs = {'J', 'T', '9'}
        strong_suited = [{'A', 'Q'}, {'A', 'J'}, {'K', 'Q'}]
        strong_offsuit = [{'A', 'Q'}, {'K', 'Q'}]
        return (
            (pair and ranks.pop() in strong_pairs) or
            (suited and ranks in strong_suited) or
            (not suited and ranks in strong_offsuit)
        )

    def is_medium(self, cards):
        """Medium strength: 88, 77, 66, AJo, KJo, QJo, KJs, QJs, JTs"""
        ranks = {self.RANK_MAP[cards[0].rank], self.RANK_MAP[cards[1].rank]}
        pair = cards[0].rank == cards[1].rank
        suited = cards[0].suit == cards[1].suit
        medium_pairs = {'8', '7', '6'}
        medium_suited = [{'K', 'J'}, {'Q', 'J'}, {'J', 'T'}]
        medium_offsuit = [{'A', 'J'}, {'K', 'J'}, {'Q', 'J'}]
        return (
            (pair and ranks.pop() in medium_pairs) or
            (suited and ranks in medium_suited) or
            (not suited and ranks in medium_offsuit)
        )

    def is_low_pocket(self, cards):
        """Low pocket pairs: 55, 44, 33, 22"""
        return cards[0].rank == cards[1].rank and self.RANK_MAP[cards[0].rank] in {'5', '4', '3', '2'}

    def is_high_ace(self, cards):
        """High Aces: ATs-A8s, ATo-A8o"""
        ranks = {self.RANK_MAP[cards[0].rank], self.RANK_MAP[cards[1].rank]}
        high_aces = [{'A', 'T'}, {'A', '9'}, {'A', '8'}]
        return ranks in high_aces

    def is_medium_suited_connector(self, cards):
        """Medium-Low Suited Connectors: T9s, 98s, 87s, 76s, 65s"""
        suited = cards[0].suit == cards[1].suit
        ranks = sorted([self.RANK_MAP[cards[0].rank], self.RANK_MAP[cards[1].rank]], reverse=True)
        connectors = ['T9', '98', '87', '76', '65']
        return suited and ''.join(ranks) in connectors

    def is_high_king_or_queen(self, cards):
        """High Kings/Queens: KTs, K9s, QTs, Q9s, KTo, QTo"""
        suited = cards[0].suit == cards[1].suit
        ranks = {self.RANK_MAP[cards[0].rank], self.RANK_MAP[cards[1].rank]}
        high_suited = [{'K', 'T'}, {'K', '9'}, {'Q', 'T'}, {'Q', '9'}]
        high_offsuit = [{'K', 'T'}, {'Q', 'T'}]
        return (suited and ranks in high_suited) or (not suited and ranks in high_offsuit)

    def is_low_suited_ace(self, cards):
        """Low Suited Aces: A7s-A2s"""
        suited = cards[0].suit == cards[1].suit
        ranks = {self.RANK_MAP[cards[0].rank], self.RANK_MAP[cards[1].rank]}
        return suited and 'A' in ranks and ranks & {'7', '6', '5', '4', '3', '2'}

    def is_low_suited_gapper(self, cards):
        """Low Suited Gappers: J9s, T8s, 97s, 86s, 75s"""
        suited = cards[0].suit == cards[1].suit
        ranks = sorted([self.RANK_MAP[cards[0].rank], self.RANK_MAP[cards[1].rank]], reverse=True)

        gappers = ['J9', 'T8', '97', '86', '75']
        return suited and ''.join(ranks) in gappers

    def is_trash(self, cards):
        """Trash hands: Hands that don't fit into any other range."""
        return not (self.is_premium(cards) or self.is_strong(cards) or self.is_medium(cards) or
                    self.is_low_pocket(cards) or self.is_high_ace(cards) or
                    self.is_medium_suited_connector(cards) or
                    self.is_high_king_or_queen(cards) or
                    self.is_low_suited_ace(cards) or self.is_low_suited_gapper(cards))

