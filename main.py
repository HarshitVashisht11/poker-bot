from player import PokerBot
import random

def get_community_cards(round_name):
    if round_name == "Pre-flop":
        return []
    elif round_name in ["Flop", "Turn", "River"]:
        card_count = 3 if round_name == "Flop" else 1
        return input(f"Enter the {'3 community cards' if card_count == 3 else 'community card'} for the {round_name}: ").split()

def get_current_game_state(current_pot, current_bet):
    while True:
        try:
            new_pot = int(input(f"Enter the current pot size (was {current_pot}): "))
            if new_pot < current_pot:
                print("New pot size cannot be smaller than the previous pot size.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a numerical value for the pot size.")
    
    while True:
        try:
            new_bet = int(input(f"Enter the current bet amount (was {current_bet}): "))
            if new_bet < current_bet:
                print("New bet amount cannot be smaller than the previous bet amount.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a numerical value for the bet amount.")
    
    return new_pot, new_bet

def play_round(bot, round_name, community_cards, pot, current_bet, small_blind):
    print(f"\n--- {round_name} ---")
    
    betting_round = 0
    players_in_hand = 2  # Assuming heads-up play (bot vs one opponent)
    last_raiser = None
    
    while players_in_hand > 1 and betting_round < 2:  # Allow up to 2 betting rounds
        betting_round += 1
        print(f"\nBetting round {betting_round}")
        
        for player in range(2):  # Assuming heads-up play
            if player == 0:  # Bot's turn
                to_call = current_bet - (pot // 2)  # Assuming the pot includes the bot's previous bet
                min_raise = max(current_bet * 2, small_blind * 2)
                max_raise = bot.get_stack()
                
                action, amount = bot.make_decision(
                    community_cards, pot, to_call, min_raise, max_raise, round_name,
                    "Check" if last_raiser is None else "Raise",
                    current_bet if last_raiser is not None else 0
                )
                
                print(f"Bot's decision: {action}")
                if action != "Fold":
                    print(f"Amount: {amount}")
                    pot += amount
                    if action == "Raise":
                        current_bet = amount
                        last_raiser = 0
                
                if action == "Fold":
                    players_in_hand -= 1
                    break
                
            else:  # Opponent's turn
                action = input("Opponent's action (Check/Call/Raise/Fold): ").capitalize()
                while action not in ['Check', 'Call', 'Raise', 'Fold']:
                    action = input("Invalid input. Enter Check, Call, Raise, or Fold: ").capitalize()
                
                if action == "Raise":
                    raise_amount = int(input("Enter the raise amount: "))
                    while raise_amount <= current_bet:
                        raise_amount = int(input("Raise amount must be greater than the current bet. Enter again: "))
                    pot += raise_amount
                    current_bet = raise_amount
                    last_raiser = 1
                elif action == "Call":
                    pot += current_bet
                elif action == "Fold":
                    players_in_hand -= 1
                    break
        
        if last_raiser is None:  # All players checked
            break
        
        last_raiser = None  # Reset for the next betting round
    
    return players_in_hand > 1, pot, action, current_bet

def rotate_position(current_position, num_players):
    return (current_position % num_players) + 1

def main():
    print("=== Texas Hold'em Poker Bot ===")
    
    # Initialize game settings
    initial_stack = int(input("Enter the bot's initial stack size: "))
    bot = PokerBot(initial_stack)
    
    num_players = int(input("Enter the total number of players (including the bot): "))
    bot_position = int(input(f"Enter bot's initial position (1-{num_players}, 1 is Small Blind): "))
    small_blind = int(input("Enter the small blind value: "))
    big_blind = small_blind * 2
    
    while bot.get_stack() > 0:
        print("\n=== New Hand ===")
        
        hand = input("Enter your hand (e.g., 'Ah Kd'): ").split()
        if len(hand) != 2:
            print("Invalid hand input. Please enter exactly two cards.")
            continue
        bot.update_hand(hand)
        
        # Initialize pot and handle blinds
        pot = small_blind + big_blind
        current_bet = big_blind
        
        # Handle Small Blind and Big Blind
        if bot_position == 1:
            bot.update_stack(-min(bot.get_stack(), small_blind))
        elif bot_position == 2:
            bot.update_stack(-min(bot.get_stack(), big_blind))
        
        # Handle Pre-flop and subsequent rounds
        rounds = ["Pre-flop", "Flop", "Turn", "River"]
        
        for round_name in rounds:
            community_cards = get_community_cards(round_name)
            is_active, pot, action, current_bet = play_round(bot, round_name, community_cards, pot, current_bet, small_blind)
            
            if not is_active:
                print("Bot has folded.")
                break
            
            # Reset current bet after each betting round except when bot raises
            if round_name != "River":
                current_bet = 0
        
        if is_active:
            winner_input = input("Did the bot win the hand? (yes/no): ").lower()
            if winner_input == 'yes':
                bot.update_stack(pot)
                print(f"Bot won the pot of {pot}")
            else:
                print("Bot lost the pot.")
        
        print(f"Bot's current stack: {bot.get_stack()}")
        
        if bot.get_stack() <= 0:
            print("Bot is out of money. Game over.")
            break
        
        play_again = input("Play another hand? (yes/no): ").lower()
        if play_again != 'yes':
            break
        
        bot_position = rotate_position(bot_position, num_players)
        print(f"Bot's new position: {bot_position}")
    
    print(f"\nFinal stack: {bot.get_stack()}")

if __name__ == "__main__":
    main()
