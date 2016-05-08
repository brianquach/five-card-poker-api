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
      wins: Number of games a player has won.
      ties: Number of games a player has tied.
      losses: Number of games a player has loss.

    Code Citation:
      https://github.com/udacity/FSND-P4-Design-A-Game/blob/master/Sample%20Project%20tic-tac-toe/models.py  # noqa
    """
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    wins = ndb.IntegerProperty(default=0)
    losses = ndb.IntegerProperty(default=0)
    ties = ndb.IntegerProperty(default=0)
    total_games =ndb.ComputedProperty(
        lambda self: self.wins + self.losses + self.ties
    )
    win_percent = ndb.ComputedProperty(
        lambda self:
          0 if self.total_games == 0 else self.wins / self.total_games
    )

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
      active_player: Key representing current player's turn.
      game_over: Boolean if game is completed or not.
      is_forfeit: Boolean if game is forfeited or not.
      winner: Key representing player who has won the game.

    Code Citation:
      https://github.com/udacity/FSND-P4-Design-A-Game/blob/master/Sample%20Project%20tic-tac-toe/models.py  # noqa
    """
    deck = ndb.JsonProperty(required=True)
    player_one = ndb.KeyProperty(required=True, kind='User')
    player_two = ndb.KeyProperty(required=True, kind='User')
    active_player = ndb.KeyProperty()
    game_over = ndb.BooleanProperty(required=True, default=False)
    is_forfeit = ndb.BooleanProperty(required =True, default=False)
    winner = ndb.KeyProperty()

    def to_form(self):
        """Returns a form representation of the Game."""
        form = GameForm(
            player_one=self.player_one.get().name,
            player_two=self.player_two.get().name,
            active_player=self.active_player.get().name,
            game_over=self.game_over,
            is_forfeit=self.is_forfeit,
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
