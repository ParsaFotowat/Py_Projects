import pandas as pd

# Example of one-hot encoding for cards
def one_hot_encode_cards(hands):
    card_columns = [f'card_{rank}_{suit}' for rank in range(13) for suit in range(4)]
    encoded_hands = pd.DataFrame(0, index=hands.index, columns=card_columns)

    for i, hand in enumerate(hands):
        for card in hand:
            rank, suit = card  # Assuming card is a tuple (rank, suit)
            encoded_hands.loc[i, f'card_{rank}_{suit}'] = 1

    return encoded_hands

# Example hands
hands = [(0, 1), (2, 3), (4, 5)]  # Example card tuples
encoded_hands = one_hot_encode_cards(pd.Series(hands))