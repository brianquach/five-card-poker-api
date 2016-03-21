#!/usr/bin/env python
"""
Copyright 2016 Brian Quach
Licensed under MIT (https://github.com/brianquach/udacity-nano-fullstack-conference/blob/master/LICENSE)  # noqa
"""
import random

from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from enum import HandState
from model import Game
from model import Hand


class Card(object):
    """Represents a regular card from standard 52-card deck.

    Card suits are Diamond, Hearts, Spades, and Clubs. Card names are Two,
    Three, Four, Five, Six, Seven, Eight, Nine, Ten, Jack, Queen, King, and
    Ace.

    The cards value will be used to determine which card beats which and a
    card's ID is what the player will use to let the game know which card(s)
    he/she wants to exchange.

    Attributes:
      value: An integer value of a playing card.
      name: A string of the card name.
      suit: A string of the card suit.
      card_id: A string identifying the card.
    """
    def __init__(self, name='joker', suit=None):
        self.name = name
        self.suit = suit
        self.value = self._get_card_value(name)
        self.id = self._get_card_id(name, suit)

    def __repr__(self):
        """Returns a string representing the card."""
        return '{0} of {1}'.format(self.name, self.suit)

    def _get_card_value(self, name):
        """Gets value of a card based on the name.

        Args:
          name: a string representing the name of the card.

        Returns:
          The value of a card in a standard 52 card deck. If the card name
          cannot be found, the vaue of the card will be 0.

        Raises:
          KeyError: An error occured trying to find the value of a card.
        """
        try:
            card_values = {
                'joker': 0,
                'two': 2,
                'three': 3,
                'four': 4,
                'five': 5,
                'six': 6,
                'seven': 7,
                'eight': 8,
                'nine': 9,
                'ten': 10,
                'jack': 11,
                'queen': 12,
                'king': 13,
                'ace': 14
            }
            return card_values[name]
        except KeyError:
            return 0

    def _get_card_id(self, name, suit):
        """Creates a card's ID.

        Args:
          name: A string of the card name.
          suit: A string of the card suit.

        Returns:
          A card's ID created from the card name and suit.
        """
        return '{0}_{1}'.format(suit, name)

    def serialize(self):
        """Convert card into a JSON string."""
        card_json = '{{"name": "{0}", "suit": "{1}"}}'.\
            format(self.name, self.suit)
        return card_json


class Deck(object):
    """Represents a collection of cards.

    Attributes:
      cards: a list of Cards.
    """
    def __init__(self, cards=None):
        self.cards = cards
        if self.cards is None:
            self.cards = self._get_standard_deck()

    def _get_standard_deck(self):
        """Returns the standard 52 card deck unsorted."""
        cards = []
        names_of_cards = [
            'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
            'nine', 'ten', 'jack', 'queen', 'king', 'ace'
        ]
        suit = ['spade', 'heart', 'diamond', 'club']
        for card_name in names_of_cards:
            cards.extend(
                [
                    Card(name=card_name, suit=suit[i]) for i in range(4)
                ]
            )
        return cards

    def shuffle(self):
        """Shuffles the card positions in the deck."""
        random.shuffle(self.cards)

    def draw(self, number_of_draws=1):
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
        return cards

    def serialize(self):
        """Convert deck of cards into a JSON string."""
        deck_json = '['
        for card in self.cards:
            deck_json += '{0},'.format(card.serialize())
        deck_json = deck_json[:-1]
        deck_json += ']'
        return deck_json


class Poker(object):
    """Operates the five card poker game mechanics.

    Players are delt a five card hand and each player has one opportunity,
    starting with player one, to replace up to 5 cards in their hand with new
    cards from the top of the deck.

    Once each player has finished replacing their cards, each hand is then
    revealed. The player with the highest poker hand wins.

    Args:
      player_one: poker player; takes the first turn
      player_two: poker player
    """
    @staticmethod
    @ndb.transactional(xg=True)
    def new_game(player_one, player_two, game_id):
        """Creates and returns a new game.

        Args:
          player_one: A key representing player one.
          player_two: A key representing player two.
          game_id: A string representing a game_id for generating a Game.key.

        Returns:
          A game detailing the players, the active player, and the deck.
        """
        game_key = ndb.Key(Game, game_id)

        game = Game(
            key=game_key,
            player_one=player_one,
            player_two=player_two,
            active_player=player_one,
            game_over=False
        )
        deck = Deck()
        deck.shuffle()

        # Deal out each player's starting hand

        player_one_hand = Poker.serialize_hand(deck.draw(5))
        hand = Hand(
            player=player_one,
            game=game.key,
            hand=player_one_hand,
            state=str(HandState.STARTING)
        )
        hand.put()

        player_two_hand = Poker.serialize_hand(deck.draw(5))
        hand = Hand(
            player=player_two,
            game=game.key,
            hand=player_two_hand,
            state=str(HandState.STARTING)
        )
        hand.put()

        game.deck = deck.serialize()
        game.put()

        # Send email to active player signaling the start of the game

        taskqueue.add(
            url='/tasks/send_move_email',
            params={
                'game_key': game.key.urlsafe(),
                'user_key': game.active_player.urlsafe()
            },
            transactional=True
        )
        return game

    @staticmethod
    def make_move(game, player, card_ids):
        """Record and respond to player's move.

        Record player card exchanges if any requeted. An empty card_ids means
        the player does not want to exchange any of his/her cards.

        Args:
          game: An entity representing the game state.
          player: An entity representing the active player.
          card_ids: A list with the cards the player wants to exchange.

        Returns:
          The player's final hand.
        """
        current_hand = Hand.query(
            ndb.AND(Hand.game == game.key, Hand.player == player.key)
        ).get()
        final_hand = current_hand.hand
        # if len(card_ids) > 0:
        #     get_new_cards()

        final_hand = Hand(
            player=player.key,
            game=game.key,
            hand=final_hand,
            state=str(HandState.ENDING)
        )
        final_hand.put()
        return ['ACE', 'ACE', 'ACE', 'ACE', 'KING']

    @staticmethod
    def serialize_hand(hand):
        """Serialize player's hand of cards into JSON."""
        hand_json = '['
        for card in hand:
            hand_json += '{0},'.format(card.serialize())
        hand_json = hand_json[:-1]
        hand_json += ']'
        return hand_json
