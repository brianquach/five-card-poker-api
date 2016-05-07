#!/usr/bin/env python
"""
Copyright 2016 Brian Quach
Licensed under MIT (https://github.com/brianquach/udacity-nano-fullstack-conference/blob/master/LICENSE)  # noqa
"""
from collections import Counter
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

    Poker hand rankings (greatest to least):
      1) Royal Flush
      2) Straight Flush
      3) Four of a Kind
      4) Full House
      5) Flush
      6) Straight
      7) Three of a Kind
      8) Two Pair
      9) Pair
      10) High Card

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
        final_hand = Hand.query(
            ndb.AND(Hand.game == game.key, Hand.player == player.key)
        ).get()
        final_hand = Poker.load_player_hand(final_hand.hand)
        deck = Deck.construct_json_deck(game.deck)

        if len(card_ids) > 0:
            if len(card_ids) < 6:
                final_hand = Poker.get_new_cards(deck, final_hand, card_ids)
            else:
                raise endpoints.ForbiddenException(
                    '''It is not possible to exchange more cards than your hand
                     size'''
                )

        if game.active_player == game.player_one:
            Poker.save_turn_one_game_state(game, deck, final_hand)
        else:
            player_one_hand = Hand.query(
                ndb.AND(Hand.game == game.key, Hand.player == game.player_one)
            ).get()
            player_one_hand = Poker.load_player_hand(player_one_hand.hand)
            Poker.save_turn_two_game_state(
                game,
                deck,
                final_hand,
                player_one_hand
            )

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
    def save_turn_one_game_state(game, deck, player_one_hand):
        """Save the state of the game after player one has made a move.

        Args:
          game: current game the player is playing in.
          deck: the deck state after the player has drawn cards for the card_id
            exchange phase.
          hand: the final hand the player has after the desired cards have been
            replaced.
        """

        # Save player one's final hand

        hand = Poker.serialize_hand(player_one_hand)
        final_hand = Hand(
            player=game.player_one,
            game=game.key,
            hand=hand,
            state=str(HandState.ENDING)
        )
        final_hand.put()

        game.active_player = game.player_two
        game.deck = deck.serialize()
        game.put()
        taskqueue.add(
            url='/tasks/send_move_email',
            params={
                'game_key': game.key.urlsafe(),
                'user_key': game.active_player.urlsafe()
            },
            transactional=True
        )

    @staticmethod
    @ndb.transactional(xg=True)
    def save_turn_two_game_state(game, deck, player_two_hand, player_one_hand):
        """Save the state of the game after player two has made a move.

        This should signal the end of the game.

        Args:
          game: current game the player is playing in.
          deck: the deck state after the player has drawn cards for the card_id
            exchange phase.
          player_two_hand: the final hand player two has after the desired
            cards have been replaced.
          player_one_hand: player one's final hand.
        """

        # Save player two's final hand

        hand = Poker.serialize_hand(player_two_hand)
        final_hand = Hand(
            player=game.player_two,
            game=game.key,
            hand=hand,
            state=str(HandState.ENDING)
        )
        final_hand.put()

        # Check game outcome and send email to players with results.
        
        game_outcome = Poker.game_outcome(player_one_hand, player_two_hand)
        game.game_over = True
        game.active_player = None

        if game_outcome == 0:
            game.winner = None
        elif game_outcome == 1:
            game.winner = game.player_one
        else:
            game.winner = game.player_two
        game.deck = deck.serialize()
        game.put()
        taskqueue.add(
            url='/tasks/send_game_result_email',
            params={
                'game_key': game.key.urlsafe()
            },
            transactional=True
        )

    @staticmethod
    def game_outcome(player_one_hand, player_two_hand):
        """Compare player hands and determine the outcome of the poker game.

        Args:
          player_one_hand: first player's hand.
          player_two_hand: second player's hand.

        Returns:
          An integer indicating the outcome:
            Game tie: 0
            Player One Wins: 1
            Player Two Wins: 2
        """
        def sort_by_card_value(card):
            """Sort key by Card value."""
            return card.value

        def is_ace_low(lowest_card, highest_card):
            """Determine if Ace is used as the lowest card in a straight."""
            return (lowest_card.value == 2 and highest_card.value == 14)

        def are_cards_same_suit(hand):
            """Check if there is a flush."""
            is_same_suit = True
            suit = None
            for card in hand:
                if (suit is None):
                    suit = card.suit
                elif (suit == card.suit):
                    is_same_suit = True
                else:
                    is_same_suit = False
                    break
            return is_same_suit

        def are_cards_in_consecutive_order(hand):
            """Check if there is a straight.

            Ace low rule: if the lowest card is a Two and the highest card is
            an Ace then temporarily assign a value of 1 to the Ace because a
            straight can be created from Ace, Two, Three, Four, Five.
            """
            is_consecutive_order = True
            sorted_hand = sorted(hand, key=sort_by_card_value)
            index = 0
            lowest_card = sorted_hand[0]
            highest_card = sorted_hand[-1]
            is_ace_low_rule = is_ace_low(lowest_card, highest_card)
            if (is_ace_low_rule):
                highest_card.value = 1
                sorted_hand = sorted(hand, key=sort_by_card_value)
                lowest_card = sorted_hand[0]

            for card in sorted_hand:
                is_consecutive_order = (
                    (card.value - lowest_card.value) == index
                )
                if (not is_consecutive_order):
                    break
                index += 1

            # Set back the original value of the Ace card

            if is_ace_low_rule:
                lowest_card.value = 14

            return is_consecutive_order

        def determine_hand_type(hand):
            """Determine the type of a player's hand.

            Number left of the hyphen is the score of the hand.

            Poker hand rankings:
              10 - Royal Flush
              9 - Straight Flush
              8 - Four of a Kind
              7 - Full House
              6 - Flush
              5 - Straight
              4 - Three of a Kind
              3 - Two Pair
              2 - Pair
              1 - High Card

            Args:
              hand: the collection of five cards to score.

            Returns:
              A number representing the value of the hand (higher is better).
            """
            sorted_hand = sorted(hand, key=sort_by_card_value)

            # Check card frequencies to determine groupings (pairs, triple,
            # etc).

            card_frequencies = Counter([card.value for card in sorted_hand])
            has_four_of_kind = False
            has_three_of_kind = False
            has_two_pairs = False
            has_pair = False
            for card_frequency in card_frequencies.most_common():
                card_value = card_frequency[0]
                card_count = card_frequency[1]
                if (card_count == 4):
                    has_four_of_kind = True
                elif (card_count == 3):
                    has_three_of_kind = True
                elif (card_count == 2):
                    if (has_pair):
                        has_two_pairs = True
                    else:
                        has_pair = True

            is_flush = are_cards_same_suit(sorted_hand)
            is_straight = are_cards_in_consecutive_order(sorted_hand)

            if (is_flush and is_straight):
                lowest_card = sorted_hand[0]
                highest_card = sorted_hand[-1]
                is_ace_low_rule = is_ace_low(lowest_card, highest_card)

                # If highest card is an Ace then it's a Royal Flush, otherwise
                # it's a straight flush.

                if (highest_card.value == 14 and not is_ace_low_rule):
                    return 10  # Royal Flush
                else:
                    return 9  # Straight Flush
            elif (has_four_of_kind):
                return 8  # Four of a Kind
            elif (has_three_of_kind and has_pair):
                return 7  # Full House
            elif (is_flush):
                return 6  # Flush
            elif (is_straight):
                return 5  # Straight
            elif (has_three_of_kind):
                return 4  # Three of a Kind
            elif (has_two_pairs):
                return 3  # Two Pairs
            elif (has_pair):
                return 2  # Pair
            else:
                return 1  # High Card

        def determine_higher_hand_value(
                player_one_hand, player_two_hand, hand_type):
            """Determine higher hand value of hands with same hand score.

            If both the player have the same hand type (score), whoever has the
            higher hand value wins.

            Args:
              player_one_hand: player one's hand.
              player_two_hand: player two's hand.
              hand_type: the type of hand both players are holding.

            Returns:
              A number representing the player with higher hand value:
                Tie: 0.
                Player one has higher value: 1.
                Player two has higher value: 2.
            """
            def highest_card_check(
                    p1_highest_card_value, p2_highest_card_value):
                """Determine tie breaker by high card value."""
                if (p1_highest_card_value == p2_highest_card_value):
                    return 0
                if (p1_highest_card_value > p2_highest_card_value):
                    return 1
                else:
                    return 2

            def most_common_card_check(
                    p1_most_common_card_value, p2_most_common_card_value):
                """Determine tie breaker by most common card value."""
                if (p1_most_common_card_value > p2_most_common_card_value):
                    return 1
                else:
                    return 2

            p1_card_counter = Counter(
                [card.value for card in player_one_hand]
            )
            p1_card_frequencies = p1_card_counter.most_common()
            p1_sorted_hand = sorted(player_one_hand, key=sort_by_card_value)
            p1_lowest_card = p1_sorted_hand[0]
            p1_highest_card = p1_sorted_hand[-1]

            p2_card_counter = Counter(
                [card.value for card in player_two_hand]
            )
            p2_card_frequencies = p2_card_counter.most_common()
            p2_sorted_hand = sorted(player_two_hand, key=sort_by_card_value)
            p2_lowest_card = p2_sorted_hand[0]
            p2_highest_card = p2_sorted_hand[-1]

            # Straight Flush, Flush, Straight, High Card
            if (hand_type in [9, 6, 5, 1]):
                if (hand_type in [9, 5]):
                    is_p1_ace_low = is_ace_low(p1_lowest_card, p1_highest_card)
                    if (is_p1_ace_low):
                        p1_highest_card.value = 1
                        p1_sorted_hand = sorted(
                            p1_sorted_hand, key=sort_by_card_value
                        )
                        p1_highest_card = p1_sorted_hand[-1]

                    is_p2_ace_low = is_ace_low(p2_lowest_card, p2_highest_card)
                    if (is_p2_ace_low):
                        p2_highest_card.value = 1
                        p2_sorted_hand = sorted(
                            p2_sorted_hand, key=sort_by_card_value
                        )
                        p2_highest_card = p2_sorted_hand[-1]

                return highest_card_check(
                    p1_highest_card.value, p2_highest_card.value)
            # Four of a Kind, Full House, Three of a Kind
            elif (hand_type in [8, 7, 4]):
                return most_common_card_check(
                    p1_card_frequencies[0][0], p2_card_frequencies[0][0])
            # Two Pairs
            elif (hand_type == 3):
                def sort_freq(card):
                    """Use card value in card frequency tuple to sort."""
                    return card[0]

                p1_card_frequencies = p1_card_counter.most_common(2)
                p1_card_frequencies = sorted(
                    p1_card_frequencies, key=sort_freq)
                p1_high_pair = p1_card_frequencies[1]
                p1_low_pair = p1_card_frequencies[0]
                p2_card_frequencies = p2_card_counter.most_common(2)
                p2_card_frequencies = sorted(
                    p2_card_frequencies, key=sort_freq)
                p2_high_pair = p2_card_frequencies[1]
                p2_low_pair = p2_card_frequencies[0]

                if (p1_high_pair[0] == p2_high_pair[0]):
                    if (p1_low_pair[0] == p2_low_pair[0]):
                        return 0
                    elif (p1_low_pair[0] > p2_low_pair[0]):
                        return 1
                    else:
                        return 2
                elif (p1_high_pair[0] > p2_high_pair[0]):
                    return 1
                else:
                    return 2
            # Pair
            elif (hand_type == 2):
                p1_pair = p1_card_frequencies[0]
                p2_pair = p2_card_frequencies[0]

                p1_single_cards = [c[0] for c in p1_card_frequencies[1:]]
                p1_single_cards = sorted(p1_single_cards)
                p1_highest_card_value = p1_single_cards[-1]
                p2_single_cards = [c[0] for c in p2_card_frequencies[1:]]
                p2_single_cards = sorted(p2_single_cards)
                p2_highest_card_value = p2_single_cards[-1]

                if (p1_pair[0] == p2_pair[0]):
                    if (p1_highest_card_value == p2_highest_card_value):
                        return 0
                    elif (p1_highest_card_value > p2_highest_card_value):
                        return 1
                    else:
                        return 2
                elif (p1_pair[0] > p2_pair[0]):
                    return 1
                else:
                    return 2
            # Royal Flush
            else:
                return 0

        p1_hand_type = determine_hand_type(player_one_hand)
        p2_hand_type = determine_hand_type(player_two_hand)

        if (p1_hand_type > p2_hand_type):
            return 1
        if (p1_hand_type < p2_hand_type):
            return 2
        else:
            return determine_higher_hand_value(
                player_one_hand, player_two_hand, p1_hand_type)
