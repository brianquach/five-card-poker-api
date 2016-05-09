#!/usr/bin/env python
"""
Copyright 2016 Brian Quach
Licensed under MIT (https://github.com/brianquach/udacity-nano-fullstack-conference/blob/master/LICENSE)  # noqa
"""
import endpoints
import json
import webapp2

from google.appengine.api import app_identity
from google.appengine.api import mail
from google.appengine.ext import ndb

from api import FiveCardPokerAPI
from enum import HandState
from game import Card
from model import Game
from model import Hand
from model import User
from utility import get_by_urlsafe


class SendMoveEmail(webapp2.RequestHandler):
    def post(self):
        """Send an email to a User that it is their turn."""
        user = get_by_urlsafe(self.request.get('user_key'), User)
        game = get_by_urlsafe(self.request.get('game_key'), Game)

        player_hand = Hand.query(
            ndb.AND(
                Hand.player == user.key,
                Hand.game == game.key,
                Hand.state == HandState.STARTING.name
            )
        ).get()

        if not player_hand:
            raise endpoints.NotFoundException(
                'Hand not found for player key {0} and game key {1}'.format(
                    user.key, game.key
                )
            )

        hand = json.loads(player_hand.hand)
        cards = [Card(name=card['name'], suit=card['suit']) for card in hand]
        hand_information = ''
        for card in cards:
            hand_information += 'Card: {0}\nCard Id: {1}\n\n'.format(
                repr(card),
                card.id
            )

        subject = 'Your Turn!'
        body = '''
Hi {0}!

It's your turn current turn to play five card poker! Choose the cards you want
to replace, if any, and respond to us. After your move, we will reveal your new
hand. After each player makes their move, the game will notify each player the
winner by email. May the player with the best hand win!

The game key is:
{2}

Here is your hand:
{1}

Notice, below each listed card is a "Card Id"; this is what you will use to
identify to the server which cards you want to exchange when you make your next
move to the server.
        '''.format(user.name, hand_information, game.key.urlsafe())

        print body
        mail.send_mail(
            'noreply@{}.appspotmail.com'.format(
                app_identity.get_application_id()
            ),
            user.email,
            subject,
            body
        )

class SendGameResultEmail(webapp2.RequestHandler):
    def post(self):
        """Send an email to the players to notify them the game results."""
        game = get_by_urlsafe(self.request.get('game_key'), Game)

        player_one_hand = Hand.query(
            ndb.AND(
                Hand.player == game.player_one,
                Hand.game == game.key,
                Hand.state == HandState.ENDING.name
            )
        ).get()
        if not player_one_hand:
            raise endpoints.NotFoundException(
                'Hand not found for player key {0} and game key {1}'.format(
                    game.player_one, game.key
                )
            )

        player_two_hand = Hand.query(
            ndb.AND(
                Hand.player == game.player_two,
                Hand.game == game.key,
                Hand.state == HandState.ENDING.name
            )
        ).get()
        if not player_two_hand:
            raise endpoints.NotFoundException(
                'Hand not found for player key {0} and game key {1}'.format(
                    game.player_two, game.key
                )
            )
        
        player_one = game.player_one.get()
        hand = json.loads(player_one_hand.hand)
        cards = [Card(name=card['name'], suit=card['suit']) for card in hand]
        p1_hand_information = ''
        for card in cards:
            p1_hand_information += 'Card: {0}\n'.format(repr(card))

        player_two = game.player_two.get()
        hand = json.loads(player_two_hand.hand)
        cards = [Card(name=card['name'], suit=card['suit']) for card in hand]
        p2_hand_information = ''
        for card in cards:
            p2_hand_information += 'Card: {0}\n'.format(repr(card))


        subject = 'It''s a tie!'
        if game.winner == game.player_one:
            subject = '{0} Wins'.format(player_one.name)
        elif game.winner == game.player_two:
            subject = '{0} Wins!'.format(player_two.name)
        
        body = '''
Game finished! {0} 

{1}'s hand:
{2}

{3}'s hand:
{4}
        '''.format(
            subject,
            player_one.name,
            p1_hand_information,
            player_two.name,
            p2_hand_information
        )

        print body
        mail.send_mail(
            'noreply@{}.appspotmail.com'.format(
                app_identity.get_application_id()
            ),
            player_one.email,
            subject,
            body
        )
        mail.send_mail(
            'noreply@{}.appspotmail.com'.format(
                app_identity.get_application_id()
            ),
            player_two.email,
            subject,
            body
        )

class SendPlayerForfeitEmail(webapp2.RequestHandler):
    def post(self):
        """Send an email to a player to nofity an opponent forfeit."""
        game_websafe_url = self.request.get('game_key')
        winner = get_by_urlsafe(self.request.get('winner_key'), User)
        loser_name = self.request.get('loser_name')

        subject = '{0} has forfeit the game!'.format(loser_name)
        
        body = '''Hi {2},

Your opponent {0} for game {1} has forfeited. You are the winner!
        '''.format(
            loser_name,
            game_websafe_url,
            winner.name
        )

        print body
        mail.send_mail(
            'noreply@{}.appspotmail.com'.format(
                app_identity.get_application_id()
            ),
            winner.email,
            subject,
            body
        )

class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to users with a game in progress."""
        players = User.query(User.email != None)
        for player in players:
            games = Game.query(
                ndb.AND(
                    Game.game_over == False,
                    Game.active_player == player.key
                )
            )
            game_keys = ', '.join(game.key.urlsafe() for game in games)
            number_of_games = games.count()
            if number_of_games > 0:
                subject = 'This is a reminder!'
                body = '''Hey {0}, you have {1} games in progress. It is your
 turn to make a move in these games! Their url safe keys are: {2}'''.format(
                    player.name,
                    number_of_games,
                    game_keys
                )
                
                print body
                mail.send_mail(
                    'noreply@{}.appspotmail.com'.format(
                        app_identity.get_application_id()
                    ),
                    player.email,
                    subject,
                    body
                )

app = webapp2.WSGIApplication(
    [
        ('/tasks/send_move_email', SendMoveEmail),
        ('/tasks/send_game_result_email', SendGameResultEmail),
        ('/tasks/send_player_forfeit_email', SendPlayerForfeitEmail),
        ('/crons/send_reminder', SendReminderEmail)
    ],
    debug=True
)
