#!/usr/bin/env python
"""
Copyright 2016 Brian Quach
Licensed under MIT (https://github.com/brianquach/udacity-nano-fullstack-conference/blob/master/LICENSE)  # noqa
"""
import endpoints
import json
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

    @classmethod
    def create_from_id(cls, card_id=None):
        if card_id is not None:
            tokens = card_id.split('_')
            suit = tokens[0]
            name = tokens[1]
            return cls(name, suit)

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

    @classmethod
    def construct_json_deck(cls, json_deck=None):
        if json_deck is not None:
            cards = json.loads(json_deck)
            cards = [
                Card(name=card['name'], suit=card['suit']) for card in cards
            ]
            return cls(cards)

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

        Raises:
          ForbiddenException: Player is trying to exchange more than the
            max hand size; 5 cards.
        """
        current_hand = Hand.query(
            ndb.AND(Hand.game == game.key, Hand.player == player.key)
        ).get()
        current_hand = Poker.load_player_hand(current_hand.hand)
        deck = Deck.construct_json_deck(game.deck)

        if len(card_ids) > 0:
            if len(card_ids) < 6:
                final_hand = Poker.get_new_cards(deck, current_hand, card_ids)
            else:
                raise endpoints.ForbiddenException(
                    '''It is not possible to exchange more cards than your hand
                     size'''
                )

        Poker.save_game_state(game, deck, player, final_hand)
        return final_hand

    @staticmethod
    def serialize_hand(hand):
        """Serialize player's hand of cards into JSON."""
        hand_json = '['
        for card in hand:
            hand_json += '{0},'.format(card.serialize())
        hand_json = hand_json[:-1]
        hand_json += ']'
        return hand_json

    @staticmethod
    def get_new_cards(deck, current_hand, card_ids):
        """Exchange the cards the player has selected for new cards.

        Player must have the card they want to exchange. Cards must be delt
        from the deck the game started off with.

        Args:
          deck: the game's ndrawn cards.
          current_hand: the cards the player is currently holding.
          card_ids: the card ids of the cards the player wants to exchange.

        Returns:
          The final state of the player's hand after the desired cards have
          been switched for new ones.
        """
        cards_to_remove = []
        for card_id in card_ids:
            card = Poker.is_card_id_valid(current_hand, card_id)
            if card is None:
                raise endpoints.NotFoundException(
                    'Player does not have a card with ID: {0}'.format(card_id)
                )
            else:
                current_hand.remove(card)

        number_of_cards_to_draw = len(card_ids)
        new_cards = deck.draw(number_of_cards_to_draw)
        current_hand.extend(new_cards)
        return current_hand

    @staticmethod
    def is_card_id_valid(current_hand, selected_card_id):
        """Validate card ids that player is requesting to exchange.

        Args:
          current_hand: the cards the player is currently holding.
          selected_card_id: the card id of the card the player wants to
            exchange.

        Returns:
          The card that is being removed from the player's hand. If the card
          cannot be found then None will be returned.
        """
        is_valid = False
        for card in current_hand:
            is_valid = card.id == selected_card_id
            if is_valid:
                return card
        return None

    @staticmethod
    def load_player_hand(hand):
        """Convert the player's hand from JSON into a list of cards objects."""
        cards = json.loads(hand)
        return [Card(name=card['name'], suit=card['suit']) for card in cards]

    @staticmethod
    @ndb.transactional(xg=True)
    def save_game_state(game, deck, player, hand):
        """Save the state of the game after the player has made a move.

        Args:
          game: current game the player is playing in.
          deck: the deck state after the player has drawn cards for the card_id
            exchange phase.
          player: the active player.
          hand: the final hand the player has after the desired cards have been
            replaced.
        """
        hand = Poker.serialize_hand(hand)
        final_hand = Hand(
            player=player.key,
            game=game.key,
            hand=hand,
            state=str(HandState.ENDING)
        )
        final_hand.put()

        game.deck = deck.serialize()
        if game.player_one == game.active_player:
            game.active_player = game.player_two
        game.put()

        if not game.game_over:
            taskqueue.add(
                url='/tasks/send_move_email',
                params={
                    'game_key': game.key.urlsafe(),
                    'user_key': game.active_player.urlsafe()
                },
                transactional=True
            )
