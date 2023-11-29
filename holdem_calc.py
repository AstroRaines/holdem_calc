import time
import holdem_functions
import holdem_argparser


def main():
    hole_cards, num, exact, board, file_name = holdem_argparser.parse_args()
    run(hole_cards, num, exact, board, file_name, True)

def calculate(board, exact, num, input_file, hole_cards, verbose):
    args = holdem_argparser.LibArgs(board, exact, num, input_file, hole_cards)
    hole_cards, n, e, board, filename = holdem_argparser.parse_lib_args(args)
    return run(hole_cards, n, e, board, filename, verbose)

def determine_preflop_action(hole_cards):
    card_values = {card.value for card in hole_cards if card is not None}
    card_suits = {card.suit for card in hole_cards if card is not None}

    # High cards or face cards
    high_card_values = {11, 12, 13, 14}
    if any(value in high_card_values for value in card_values):
        return "Call or Raise", "You have a high card (Jack, Queen, King, or Ace)."

    # Pairs
    if len(card_values) == 1:
        return "Call or Raise", "You have a pair, which can be strong pre-flop."

    # Cards close enough for a potential straight
    if len(card_values) == 2 and max(card_values) - min(card_values) <= 4:
        return "Call or potentially Raise", "Your cards are close in value, potentially leading to a straight."

    # Suited cards
    if len(card_suits) == 1:
        return "Call or Raise", "Your cards are suited, increasing the chances of a flush."

    # Otherwise
    return "Fold", "Your cards do not indicate a strong hand pre-flop."


def run(hole_cards, num, exact, board, file_name, verbose):
    # Determine the game stage
    num_board_cards = len(board) if board else 0
    if num_board_cards == 0:
        stage = "Pre-flop"
    elif num_board_cards == 3:
        stage = "Flop"
    elif num_board_cards == 4:
        stage = "Turn"
    elif num_board_cards == 5:
        stage = "River"
    else:
        raise ValueError("Invalid number of board cards for a Texas Hold'em game.")

    print(f"Game Stage: {stage}")

    # Check if it is pre-flop
    if board is None or len(board) == 0:
        #print("Pre-flop Analysis:")
        action = determine_preflop_action(hole_cards[0])
        print(f"Suggested action: {action}")

        if action == "Call or Raise":
            print("Consider raising 3 or 4 Big Blinds.")
        
        print("Remember: Poker is about comfort with uncertainty. Be confident in your decisions.")
        return  # Skip the rest of the simulation

    # Rest of the function remains the same...

    if file_name:
        input_file = open(file_name, 'r')
        for line in input_file:
            if line is not None and len(line.strip()) == 0:
                continue
            hole_cards, board = holdem_argparser.parse_file_args(line)
            deck = holdem_functions.generate_deck(hole_cards, board)
            run_simulation(hole_cards, num, exact, board, deck, verbose)
            print ("-----------------------------------")
        input_file.close()
    else:
        deck = holdem_functions.generate_deck(hole_cards, board)
        return run_simulation(hole_cards, num, exact, board, deck, verbose)
    

def run_simulation(hole_cards, num, exact, given_board, deck, verbose):
    num_players = len(hole_cards)
    # Create results data structures which track results of comparisons
    # 1) result_histograms: a list for each player that shows the number of
    #    times each type of poker hand (e.g. flush, straight) was gotten
    # 2) winner_list: number of times each player wins the given round
    # 3) result_list: list of the best possible poker hand for each pair of
    #    hole cards for a given board
    result_histograms, winner_list = [], [0] * (num_players + 1)
    for _ in range(num_players):
        result_histograms.append([0] * len(holdem_functions.hand_rankings))
    # Choose whether we're running a Monte Carlo or exhaustive simulation
    board_length = 0 if given_board is None else len(given_board)
    # When a board is given, exact calculation is much faster than Monte Carlo
    # simulation, so default to exact if a board is given
    if exact or given_board is not None:
        generate_boards = holdem_functions.generate_exhaustive_boards
    else:
        generate_boards = holdem_functions.generate_random_boards
    if (None, None) in hole_cards:
        hole_cards_list = list(hole_cards)
        unknown_index = hole_cards.index((None, None))
        for filler_hole_cards in holdem_functions.generate_hole_cards(deck):
            hole_cards_list[unknown_index] = filler_hole_cards
            deck_list = list(deck)
            deck_list.remove(filler_hole_cards[0])
            deck_list.remove(filler_hole_cards[1])
            holdem_functions.find_winner(generate_boards, tuple(deck_list),
                                         tuple(hole_cards_list), num,
                                         board_length, given_board, winner_list,
                                         result_histograms)
    else:
        holdem_functions.find_winner(generate_boards, deck, hole_cards, num,
                                     board_length, given_board, winner_list,
                                     result_histograms)
    if verbose:
        holdem_functions.print_results(hole_cards, winner_list,
                                       result_histograms)
    return holdem_functions.find_winning_percentage(winner_list)

if __name__ == '__main__':
    start = time.time()
    main()
    print ("\nTime elapsed(seconds): ", time.time() - start)


