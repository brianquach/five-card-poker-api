#!/usr/bin/env python
"""
Copyright 2016 Brian Quach
Licensed under MIT (https://github.com/brianquach/udacity-nano-fullstack-conference/blob/master/LICENSE)  # noqa
"""
import endpoints

from protorpc import remote

from google.appengine.ext import ndb

from form import GameForm
from form import GameForms
from form import NewGameForm
from form import PlayerMoveForm
from game import Poker
from model import Game
from model import User
from resource import PlayerName
from resource import StringMessage
from resource import USER_REQUEST
from utility import get_by_urlsafe


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
        """Create a player. Username must be unique."""

        # Code Citation:
        #   https://github.com/udacity/FSND-P4-Design-A-Game/blob/master/Skeleton%20Project%20Guess-a-Number/api.py  # noqa

        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!'
            )
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(
            message='User {} created!'.format(request.user_name)
        )

    @endpoints.method(
        request_message=NewGameForm,
        response_message=GameForm,
        path='game/new',
        name='newGame',
        http_method='POST'
    )
    def new_game(self, request):
        """Start a new five card poker game"""
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
        game_id = Game.allocate_ids(size=1)[0]
        game = Poker.new_game(player_one.key, player_two.key, game_id)
        return game.to_form()

    @endpoints.method(
        request_message=PlayerMoveForm,
        response_message=StringMessage,
        path='game/action',
        name='makeMove',
        http_method='POST'
    )
    def make_move(self, request):
        """Make a move."""
        game = get_by_urlsafe(request.game_urlsafe_key, Game)
        player = User.query(User.name == request.player).get()
        if not player:
            raise endpoints.NotFoundException(
                '{0} does not exist!'.format(request.player)
            )
        if game.player_one != player.key and game.player_two != player.key:
            raise endpoints.ForbiddenException(
                '{0} is not part of this game!'.format(request.player)
            )
        if game.active_player != player.key:
            raise endpoints.ForbiddenException(
                'It is not your turn {0}'.format(request.player)
            )

        hand = Poker.make_move(game, player, request.card_ids_to_exchange)
        return StringMessage(
            message='Your move has been made here is your final hand: {0}. '
                    'Good luck!'.format(str(hand))
        )

    @endpoints.method(
        request_message=PlayerName,
        response_message=GameForms,
        path='user/games',
        name='getUserGames',
        http_method='GET'
    )
    def get_user_games(self, request):
        """Get all active user games."""
        player = User.query(User.name == request.player).get()
        if not player:
            raise endpoints.NotFoundException(
                '{0} does not exist!'.format(request.player)
            )

        games = Game.query(
            ndb.AND(
                Game.game_over == False,
                ndb.OR(
                    Game.player_one == player.key,
                    Game.player_two == player.key
                )
            )
        )
        return GameForms(
            games=[game.to_form() for game in games]
        )

api = endpoints.api_server([FiveCardPokerAPI])
