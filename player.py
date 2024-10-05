from hand import Hand
from strategy import Strategy

class PokerBot:
    def __init__(self, initial_stack, strategy=None, name=""):
        self.stack = initial_stack
        self.hand = None
        self.strategy = strategy or Strategy(initial_stack)
        self.name = name

    def make_decision(self, community_cards, pot, to_call, min_raise, max_raise, round_name, previous_action, previous_raise_amount):
        action, amount = self.strategy.choose_action(
            self.hand, community_cards, pot, to_call, min_raise, max_raise, round_name, previous_action, previous_raise_amount, self.stack, None
        )
        
        # Ensure the bot never folds
        if action == "Fold":
            action = "Call"
            amount = to_call

        if action != "Fold":
            self.update_stack(-amount)
        
        reward = self.evaluate_reward(action, amount, pot)
        
        self.strategy.update_strategy_after_hand(
            self.strategy.get_abstracted_info_set(
                self.hand.strength(community_cards),
                to_call / (pot + to_call) if (pot + to_call) > 0 else 0,
                round_name,
                previous_action,
                previous_raise_amount,
                pot,
                self.stack,
                None
            ),
            self.get_action_index(action),
            reward
        )
        
        return action, amount

    def evaluate_reward(self, action, amount, pot):
        if action == "Call":
            return amount
        elif action == "Raise":
            return amount

    def get_action_index(self, action):
        mapping = {"Fold": 0, "Call": 1, "Raise": 2}
        return mapping.get(action, 1)

    def update_hand(self, new_hand):
        self.hand = Hand(new_hand)

    def update_stack(self, amount):
        self.stack += amount

    def get_stack(self):
        return self.stack

    def __str__(self):
        return self.name
