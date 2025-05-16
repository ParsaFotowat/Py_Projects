import pandas as pd
import numpy as np

def encode_hand(hand):
    # One-hot encoding for each card in the hand
    deck = ['2H', '2D', '2C', '2S', '3H', '3D', '3C', '3S', '4H', '4D', '4C', '4S',
            '5H', '5D', '5C', '5S', '6H', '6D', '6C', '6S', '7H', '7D', '7C', '7S',
            '8H', '8D', '8C', '8S', '9H', '9D', '9C', '9S', 'TH', 'TD', 'TC', 'TS',
            'JH', 'JD', 'JC', 'JS', 'QH', 'QD', 'QC', 'QS', 'KH', 'KD', 'KC', 'KS',
            'AH', 'AD', 'AC', 'AS']
    
    encoding = np.zeros(len(deck))
    for card in hand:
        index = deck.index(card)
        encoding[index] = 1
    return encoding

# Example usage
hand = ['AH', 'KH']
encoded_hand = encode_hand(hand)