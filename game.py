#!/usr/bin/env python
"""
Copyright 2016 Brian Quach
Licensed under MIT (https://github.com/brianquach/udacity-nano-fullstack-conference/blob/master/LICENSE)  # noqa
"""
import random

from model import Game


class Card(object):
    """Represents the value of the different card types in a deck."""
    two = 2
    three = 3
    four = 4
    five = 5
    six = 6
    seven = 7
    eight = 8
    nine = 9
    ten = 10
    jack = 11
    queen = 12
    king = 13
    ace = 14


class Deck(object):
    """Represents a collection of cards."""
    def __init__(self, cards=None):
        self.cards = cards
        if self.cards is None:
            self.cards = self._get_standard_deck()

    def _get_standard_deck(self):
        """Returns the standard 52 card deck unsorted"""
        cards = []
        types_of_cards = [
            'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
            'nine', 'ten', 'jack', 'queen', 'king', 'ace'
        ]
        for card_type in types_of_cards:
            cards.extend([card_type for i in range(4)])
        return cards

    def shuffle(self):
        """Shuffles the card positions in the deck"""
        random.shuffle(self.cards)

    def draw_cards(self, number_of_draws=1):
        """Draw card(s) from the top of the deck.

        Cannot draw more than the number of cards currently in the deck.

        Args:
          number_of_draws: optional variable; integer of how many cards to draw
            from the deck.

        Returns:
          An array of cards from the top of the deck.
        """
        cards_in_deck = len(self.cards)
        if cards_in_deck < number_of_draws:
            error_message = '''
                Not enough cards in deck to draw {0}. Deck has {1} cards left.
            '''
            return error_message.format(number_of_draws, cards_in_deck)
        cards = [self.cards.pop() for i in range(number_of_draws)]
        print cards
        return cards


class Poker(object):
    """Operates the five card poker game mechanics.

    Players are delt a five card hand and each player has one opportunity,
    starting with player one, to replace up to 5 cards in their hand with new
    cards from the top of the deck.

    Once each player has finished replacing their cards, each hand is then
    revealed. The player with the highest poker hand wins.
    """
    @staticmethod
    def new_game(player_one, player_two):
        """Creates and returns a new game"""
        game = Game(
            player_one=player_one,
            player_two=player_two,
            active_player=player_one
        )
        deck = Deck()
        deck.shuffle()
        game.deck = deck.cards
        #game.put()

        return game
