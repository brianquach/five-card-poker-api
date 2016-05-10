#!/usr/bin/env python
"""
Copyright 2016 Brian Quach
Licensed under MIT (https://github.com/brianquach/udacity-nano-fullstack-conference/blob/master/LICENSE)  # noqa
"""
from protorpc import messages


class UserForm(messages.Message):
    """Outbound - Represents a user."""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2, required=True)


class GameForm(messages.Message):
    """Outbound - Represents a game's state."""
    urlsafe_key = messages.StringField(1, required=True)
    player_one = messages.StringField(2, required=True)
    player_two = messages.StringField(3, required=True)
    active_player = messages.StringField(4, required=True)
    game_over = messages.BooleanField(5, required=True)
    is_forfeit = messages.BooleanField(6, required=True)
    winner = messages.StringField(7)


class NewGameForm(messages.Message):
    """Inbound - Used to create a new game."""
    player_one = messages.StringField(1, required=True)
    player_two = messages.StringField(2, required=True)


class PlayerMoveForm(messages.Message):
    """Inbound - Used to accept player move."""
    player = messages.StringField(1, required=True)
    card_ids_to_exchange = messages.StringField(2, repeated=True)
    game_urlsafe_key = messages.StringField(3, required=True)


class PlayerRankForm(messages.Message):
    """Outbound - Represents a player's stats."""
    name = messages.StringField(1)
    stats = messages.StringField(2)
    points = messages.IntegerField(3)
    rank = messages.IntegerField(4)


class PlayerRankForms(messages.Message):
    """Outbound - Represents a list of PlayerRankForms."""
    player_ranks = messages.MessageField(PlayerRankForm, 1, repeated=True)


class GameForms(messages.Message):
    """Outbound - Represents a list of games."""
    games = messages.MessageField(GameForm, 1, repeated=True)


class CancelGameForm(messages.Message):
    """Inbound - Used to forfeit an active game."""
    game_urlsafe_key = messages.StringField(1, required=True)
    player = messages.StringField(2, required=True)


class GameHistoryForm(messages.Message):
    """Outbound - Represents a game's history."""
    game_urlsafe_key = messages.StringField(1)
    player_one = messages.StringField(2)
    player_one_start_hand = messages.StringField(3)
    player_one_end_hand = messages.StringField(4)
    player_two = messages.StringField(5)
    player_two_start_hand = messages.StringField(6)
    player_two_end_hand = messages.StringField(7)
    is_forfeit = messages.BooleanField(8)
    winner = messages.StringField(9)


class GameHistoryForms(messages.Message):
    """Outbound - Represents a list of a player's game history."""
    games = messages.MessageField(GameHistoryForm, 1, repeated=True)


class StringMessage(messages.Message):
    """Outbound response string message"""
    message = messages.StringField(1, required=True)


class PlayerName(messages.Message):
    """Outbound response string message"""
    player = messages.StringField(1, required=True)
