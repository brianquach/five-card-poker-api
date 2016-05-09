# Five-Card Poker Game

Fourth project for Full-Stack Web Devloper Nanodegree course; Five-Card Poker is a web game that pits two players agaisnt each other in a game of a little luck and strategy. Each player is first delt five cards from a standard 52 card deck and is then able to exchange up to five cards for new cards to form their final hands. Both players' hands are then compared and the winner is the player with the best hand.

Poker hand rankings (greatest to least):
1) Royal Flush - A straight from Ten to Ace all in the same suit.
2) Straight Flush - Any straight with cards in the same suit.
3) Four of a Kind - Four of the same kind of card paired with any left-over card.
4) Full House - A three of a kind paired with a pair.
5) Flush - Any five cards all with the same suit.
6) Straight - Five cards in consecutive order.
7) Three of a Kind - Three of the same kind of card paired with any left-over cards.
8) Two Pair - Two different pairs paired with any left-over card.
9) Pair - Two of the same kind of card paired with any left-over cards.
10) High Card - A hand that does not consist of any of the above.

This game is influenced by the [five-card draw](https://en.wikipedia.org/wiki/Five-card_draw) poker rules.

Feature list:
* Player rankings
* Game history
* Player triggered forfeits
* Turn-based email notifications
* Scheduled player turn email reminder

## Table of Contents

* [Dependancies](#dependancies)
* [Setup Instructions](#setup-instructions)
* [How To Play](#how-to-play)
* [Endpoints](#endpoints)
* [Creator](#creator)
* [Copyright and license](#copyright-and-license)

## Dependancies

Five-Card Poker is built using Python, and depends on the Google App Engine (GAE) for development and testing.
* [Python 2.7](https://www.python.org/downloads/)
* [Google App Engine](https://cloud.google.com/appengine/)

## Setup Instructions:
1. Open GAE and add application under **File -> New Application**.
2. Update the application ID in app.yaml to the app ID you have registered in the GAE admin console.
3. Run the application through GAE to run and test a local version of Five-Card Poker.
    - Default port should be 8080 and admin port should be 8000 (ports can be changed).
4. Once ready to deploy, run the deploy function in GAE to deploy application onto Google's App Engine platform
    - Make sure the application ID in app.yaml matches the project ID created in [Google Cloud Platform Console](https://console.developers.google.com/)

## Creator

Brian Quach
* <https://github.com/brianquach>

## Copyright and license

Code copyright 2016 Brian Quach. Code released under [the MIT license](https://github.com/brianquach/udacity-nano-fullstack-catalog/blob/master/LICENSE).