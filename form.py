#!/usr/bin/env python
"""
Copyright 2016 Brian Quach
Licensed under MIT (https://github.com/brianquach/udacity-nano-fullstack-conference/blob/master/LICENSE)  # noqa
"""
from protorpc import messages


class UserForm(messages.Message):
    """Outbound - Represents a user."""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2)


class GameForm(messages.Message):
    """Outbound - Represents a game's state."""
    urlsafe_key = messages.StringField(1, required=True)
    player_one = messages.StringField(2, required=True)
    player_two = messages.StringField(3, required=True)
    active_player = messages.StringField(4, required=True)
    game_over = messages.BooleanField(5, required=True)
    winner = messages.StringField(6)


class NewGameForm(messages.Message):
    """Inbound - Used to create a new game."""
    player_one = messages.StringField(1, required=True)
    player_two = messages.StringField(2, required=True)


class PlayerMoveForm(messages.Message):
    """Inbound - Used to accept player move."""
    player = messages.StringField(1, required=True)
    card_ids = messages.StringField(2, repeated=True)
    game_urlsafe_key = messages.StringField(3, required=True)
