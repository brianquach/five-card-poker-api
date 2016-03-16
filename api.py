#!/usr/bin/env python
"""
Copyright 2016 Brian Quach
Licensed under MIT (https://github.com/brianquach/udacity-nano-fullstack-conference/blob/master/LICENSE)  # noqa
"""
import endpoints

from protorpc import remote

from form import GameForm
from form import NewGameForm
from game import Poker
from model import User
from resource import StringMessage
from resource import USER_REQUEST


@endpoints.api(name='poker', version='v1')
class FiveCardPokerAPI(remote.Service):
    """An API for a two-player five card poker game."""
    @endpoints.method(
        request_message=USER_REQUEST,
        response_message=StringMessage,
        path='user/create',
        name='createUser',
        http_method='POST'
    )
    def create_user(self, request):
        """Create a player."""
        return self._create_user(request)

    @endpoints.method(
        request_message=NewGameForm,
        response_message=GameForm,
        path='game/new',
        name='newGame',
        http_method='POST'
    )
    def new_game(self, request):
        """Start a game."""
        return self._new_game(request)
        
    def _create_user(self, request):
        """Create a player.

        Username must be unique.

        Code Citation:
          https://github.com/udacity/FSND-P4-Design-A-Game/blob/master/Skeleton%20Project%20Guess-a-Number/api.py  # noqa
        """
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!'
            )
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(
            message='User {} created!'.format(request.user_name)
        )

    def _new_game(self, request):
        """Starts a new five card poker game"""
        player_one = User.query(User.name == request.player_one).get()
        player_two = User.query(User.name == request.player_two).get()
        err_msg = '{0} does not exist!'
        if not player_one:
            raise endpoints.NotFoundException(
                err_msg.format(request.player_one)
            )
        if not player_two:
            raise endpoints.NotFoundException(
                err_msg.format(request.player_two)
            )
        game = Poker.new_game(player_one.key, player_two.key)
        return game.to_form()

api = endpoints.api_server([FiveCardPokerAPI])
