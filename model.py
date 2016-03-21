#!/usr/bin/env python
"""
Copyright 2016 Brian Quach
Licensed under MIT (https://github.com/brianquach/udacity-nano-fullstack-conference/blob/master/LICENSE)  # noqa
"""
from google.appengine.ext import ndb

from form import GameForm
from form import UserForm


class User(ndb.Model):
    """User profile.

    Attributes:
      name: Name of the player; must be unique.
      email: Email address of the player. Used to email player reminders and
        game relevant events.

    Code Citation:
      https://github.com/udacity/FSND-P4-Design-A-Game/blob/master/Sample%20Project%20tic-tac-toe/models.py  # noqa
    """
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()

    def to_form(self):
        """Returns a form representation of the User"""
        form = UserForm(
            name=self.name,
            email=self.email
        )
        return form


class Game(ndb.Model):
    """Respesents a game of five card poker.

    Attributes:
      deck: List of cards representing the deck.
      player_one: Key representing player one in the game.
      player_two: Key representing player two in the game.
      player_one_hand: Key representing player one's current hand.
      player_two_hand: Key representing player two's current hand.
      active_player: Key representing current player's turn.
      game_over: Boolean if game is completed or not.
      winner: Key representing player who has won the game.

    Code Citation:
      https://github.com/udacity/FSND-P4-Design-A-Game/blob/master/Sample%20Project%20tic-tac-toe/models.py  # noqa
    """
    deck = ndb.JsonProperty(required=True)
    player_one = ndb.KeyProperty(required=True, kind='User')
    player_one_hand = ndb.KeyProperty(required=True, kind='Hand')
    player_two = ndb.KeyProperty(required=True, kind='User')
    player_two_hand = ndb.KeyProperty(required=True, kind='Hand')
    active_player = ndb.KeyProperty(required=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    winner = ndb.KeyProperty()

    def to_form(self):
        """Returns a form representation of the Game."""
        form = GameForm(
            player_one=self.player_one.get().name,
            player_two=self.player_two.get().name,
            active_player=self.active_player.get().name,
            game_over=self.game_over,
            urlsafe_key=self.key.urlsafe()
        )
        if self.winner:
            form.winner = self.winner.get().name
        return form


class Hand(ndb.Model):
    """Represents a player's hand in a poker game.

    Attributes:
      player: Key representing the player of the hand.
      game: Key representing the game from where the player had their hand
        delt.
      hand: A list representing the cards in the player's hand.
      state: Enum representing the current hand state in the game.
    """
    player = ndb.KeyProperty(required=True, kind='User')
    game = ndb.KeyProperty(required=True, kind='Game')
    hand = ndb.JsonProperty(required=True)
    state = ndb.StringProperty(required=True, default='STARTING')
