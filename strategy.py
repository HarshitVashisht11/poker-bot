import random
from collections import defaultdict

class Strategy:
    def __init__(self, initial_stack):
        self.initial_stack = initial_stack
        self.regret_sum = defaultdict(lambda: [0.0, 0.0, 0.0])  # Fold, Call, Raise
        self.strategy_sum = defaultdict(lambda: [0.0, 0.0, 0.0])
        self.num_actions = 3  # Fold, Call, Raise

    def get_strategy(self, info_set):
        regrets = self.regret_sum[info_set]
        positive_regrets = [max(regret, 0) for regret in regrets]
        total_positive = sum(positive_regrets)

        if total_positive > 0:
            strategy = [regret / total_positive for regret in positive_regrets]
        else:
            strategy = [0.1, 0.4, 0.5]  # Default to aggressive strategy

        for i in range(self.num_actions):
            self.strategy_sum[info_set][i] += strategy[i]

        return strategy

    def choose_action(self, hand, community_cards, pot, to_call, min_raise, max_raise, round_name, previous_action, previous_raise_amount, stack, position):
        hand_strength = hand.strength(community_cards)
        pot_odds = to_call / (pot + to_call) if (pot + to_call) > 0 else 0

        info_set = self.get_abstracted_info_set(hand_strength, pot_odds, round_name, previous_action, previous_raise_amount, pot, stack, position)

        strategy = self.get_strategy(info_set)
        
        # Adjust strategy to never fold
        strategy[0] = 0  # Set fold probability to 0
        total = sum(strategy)
        strategy = [s / total for s in strategy]  # Normalize strategy

        action_index = random.choices(range(self.num_actions), weights=strategy, k=1)[0]
        action = self.action_from_index(action_index)

        if action == "Fold":
            action = "Call"  # Ensure the bot never folds

        if action == "Call":
            return "Call", to_call
        else:  # Raise
            raise_amount = self.calculate_raise_amount(hand_strength, pot, to_call, min_raise, max_raise, previous_raise_amount, stack)
            return "Raise", raise_amount

    def action_from_index(self, index):
        mapping = {0: "Fold", 1: "Call", 2: "Raise"}
        return mapping.get(index, "Call")

    def get_abstracted_info_set(self, hand_strength, pot_odds, round_name, previous_action, previous_raise_amount, pot, stack, position):
        strength_bucket = self.bucket_strength(hand_strength)
        odds_bucket = self.bucket_pot_odds(pot_odds)
        action_bucket = self.bucket_previous_action(previous_action)
        raise_bucket = self.bucket_raise_amount(previous_raise_amount, pot, previous_action)
        return f"{strength_bucket}-{odds_bucket}-{action_bucket}-{raise_bucket}-{round_name}"

    def bucket_strength(self, hand_strength):
        if hand_strength >= 7:
            return 'S'  # Strong
        elif hand_strength >= 4:
            return 'M'  # Medium
        else:
            return 'W'  # Weak

    def bucket_pot_odds(self, pot_odds):
        if pot_odds > 0.7:
            return 'H'  # High
        elif pot_odds > 0.3:
            return 'M'  # Medium
        else:
            return 'L'  # Low

    def bucket_previous_action(self, previous_action):
        return previous_action[0] if previous_action else 'N'  # N for None

    def bucket_raise_amount(self, previous_raise_amount, pot, previous_action):
        if previous_action == 'Raise':
            if previous_raise_amount <= pot * 0.25:
                return 'S'  # Small
            elif previous_raise_amount <= pot * 0.5:
                return 'M'  # Medium
            else:
                return 'L'  # Large
        else:
            return 'N'  # No raise

    def calculate_raise_amount(self, hand_strength, pot, to_call, min_raise, max_raise, previous_raise_amount, stack):
        if previous_raise_amount > 0:
            base_raise = previous_raise_amount * 2
        else:
            base_raise = pot * 0.5

        if hand_strength >= 7:
            raise_fraction = 2.0
        elif hand_strength >= 4:
            raise_fraction = 1.5
        else:
            raise_fraction = 1.0

        raise_amount = int(base_raise * raise_fraction)

        raise_amount = max(raise_amount, min_raise)
        raise_amount = min(raise_amount, max_raise)

        return raise_amount

    def update_strategy_after_hand(self, info_set, action, reward):
        current_strategy = self.get_strategy(info_set)
        average_reward = sum(current_strategy[i] * reward for i in range(self.num_actions))
        for i in range(self.num_actions):
            regret = reward - average_reward if i == action else -current_strategy[i] * average_reward
            self.update_regrets(info_set, i, regret)

    def update_regrets(self, info_set, action, regret):
        self.regret_sum[info_set][action] += regret

    def reset_strategies(self):
        self.regret_sum.clear()
        self.strategy_sum.clear()