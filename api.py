#!/usr/bin/env python
"""
Copyright 2016 Brian Quach
Licensed under MIT (https://github.com/brianquach/udacity-nano-fullstack-conference/blob/master/LICENSE)  # noqa
"""
import endpoints

from protorpc import remote

from resource import StringMessage
from resource import USER_REQUEST


@endpoints.api(name='poker', version='v1')
class FiveCardPokerAPI(remote.Service):
    """An API for a two-player five card poker game."""
    # Players are delt a five card hand and each player has one opportunity,
    # starting with player one, to replace up to 5 cards in their hand with new
    # cards from the top of the deck.

    # Once each player has finished replacing their cards, each hand is then
    # revealed. The player with the highest poker hand wins.

    # Username must be unique.

    # Code Citation:
    #     https://github.com/udacity/FSND-P4-Design-A-Game/blob/master/Skeleton%20Project%20Guess-a-Number/api.py  # noqa
    @endpoints.method(
        request_message=USER_REQUEST,
        response_message=StringMessage,
        path='user/create',
        name='createUser',
        http_method='POST'
    )
    def create_user(self, request):
        """Create a User."""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!'
            )
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

api = endpoints.api_server([FiveCardPokerAPI])
