#!/usr/bin/env python
"""
Copyright 2016 Brian Quach
Licensed under MIT (https://github.com/brianquach/udacity-nano-fullstack-conference/blob/master/LICENSE)  # noqa
"""
import webapp2

from google.appengine.api import app_identity
from google.appengine.api import mail
from google.appengine.ext import ndb

from api import FiveCardPokerAPI
from model import Game
from model import User
from utility import get_by_urlsafe


class SendMoveEmail(webapp2.RequestHandler):
    def post(self):
        """Send an email to a User that it is their turn"""
        user = get_by_urlsafe(self.request.get('user_key'), User)
        game = get_by_urlsafe(self.request.get('game_key'), Game)
        hand = self.request.get('hand')

        subject = 'Your Turn!'
        body = """Hi {0}!

            It's your turn current turn to play five card poker! Choose the
            cards you want to replace, if any, and respond to us. After your
            move, we will reveal your new hand. Once your opponent does the
            same the game will notify each player the winner by email. May the
            player with the best hand win!

            Here is your hand:
              {1}

            The game key is:
              {2}
        """.format(user.name, hand, game.key.urlsafe())

        print body
        mail.send_mail(
            'noreply@{}.appspotmail.com'.format(
                app_identity.get_application_id()
            ),
            user.email,
            subject,
            body
        )

app = webapp2.WSGIApplication(
    [
        ('/tasks/send_move_email', SendMoveEmail)
    ],
    debug=True
)
