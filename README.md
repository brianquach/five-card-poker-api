# Five-Card Poker Game

Fourth project for Full-Stack Web Devloper Nanodegree course; Five-Card Poker is a web game that pits two players agaisnt each other in a game of a little luck and strategy. Each player is first delt five cards from a standard 52 card deck and is then able to exchange up to five cards for new cards to form their final hands. Both players' hands are then compared and the winner is the player with the best hand.

Poker hand rankings (greatest to least):

1. Royal Flush - A straight from Ten to Ace all in the same suit.
2. Straight Flush - Any straight with cards in the same suit.
3. Four of a Kind - Four of the same kind of card paired with any left-over card.
4. Full House - A three of a kind paired with a pair.
5. Flush - Any five cards all with the same suit.
6. Straight - Five cards in consecutive order.
7. Three of a Kind - Three of the same kind of card paired with any left-over cards.
8. Two Pair - Two different pairs paired with any left-over card.
9. Pair - Two of the same kind of card paired with any left-over cards.
10. High Card - A hand that does not consist of any of the above.

This game is influenced by the [five-card draw](https://en.wikipedia.org/wiki/Five-card_draw) poker rules.

## Table of Contents

* [Dependancies](#dependancies)
* [Setup Instructions](#setup-instructions)
* [How To Play](#how-to-play)
* [Endpoints](#endpoints)
* [Files](#files)
* [Models](#models)
* [Forms](#forms)
* [Creator](#creator)
* [Copyright and license](#copyright-and-license)

## Dependancies

Five-Card Poker is built using Python, and depends on the Google App Engine (GAE) for development and testing.
* [Python 2.7](https://www.python.org/downloads/)
* [Google App Engine](https://cloud.google.com/appengine/)

## Setup Instructions

1. Open GAE and add application under **File -> New Application**.
2. Update the application ID in app.yaml to the app ID you have registered in the GAE admin console.
3. Run the application through GAE to run and test a local version of Five-Card Poker.
    - Default port should be **8080** and admin port should be **8000** (ports can be changed).
4. Load API via API Explorer by visiting `localhost:8080/_ah/api/explorer` (If you changed the default port, change the port in the URL).
    - More details on locally testing an API backend can be found [here](https://cloud.google.com/appengine/docs/python/endpoints/test_deploy#running_and_testing_api_backends_locally).
5. Once ready to deploy, run the deploy function in GAE to deploy application onto Google's App Engine platform
    - Make sure the application ID in app.yaml matches the project ID created in [Google Cloud Platform Console](https://console.developers.google.com/)

**Note:** If locally testing the API in chrome, launch Chrome using the console as follows: [path-to-Chrome] --user-data-dir=test --unsafely-treat-insecure-origin-as-secure=http://localhost:port

## How to Play

The following instrutions will detail how to start and play a game of five-card poker.

1. Each player must create a user with a unique name and provide an email address.
2. Start a new game and specify the player names of the two players who will face off in a match.
3. An email should be sent to a player when the game is created detailing game information and their hand.
    - An email will contain game information and a list of cards that consist of a user's hand that looks like this:
    ```
    The game key is:
    ahBkZXZ-cG9rZXItYnF1YWNocgsLEgRHYW1lGLkXDA

    Here is your hand:
    Card: four of spade
    Card Id: spade_four

    Card: three of spade
    Card Id: spade_three

    Card: four of diamond
    Card Id: diamond_four

    Card: five of club
    Card Id: club_five

    Card: ace of diamond
    Card Id: diamond_ace
    ```

    The card should describe the value of the card and it's suit.
    The card Id is what the user will use to notify the game which cards they want to exchange.
4. The player receiving the email should then make their move by providing the urlsafe web key of the current game, their user name, and a list of card Ids of the cards the user wants to exchange for new cards (up to 5 cards may be exchanged).
5. Once a player has submitted their move, the game should respond with a list of cards that will consist of their final hand.
6. After both players have made their move, the game will email both players with the game result and with each players' respective hands.

## Endpoints

- **create_user**
    - Path: 'user/create'
    - Method: POST
    - Parameters: user_name, email
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. email is required because it is main communication method between the user and the game.
    - Raises: ConflictException if a User with that user_name already exists.
    
- **new_game**
    - Path: 'game/new'
    - Method: POST
    - Parameters: player_one, player_two
    - Returns: GameForm with initial game state.
    - Description: Creates a new five-card poker game and deals five cards to each player as their starting hand.
    - Raises: NotFoundException if either player does not exist.
     
- **make_move**
    - Path: 'game/action'
    - Method: PUT
    - Parameters: player, card_ids_to_exchange, game_urlsafe_key
    - Returns: Message confirming player move with a list of cards representing their final hand.
    - Description: Determines players final hand based on the cards if any the player want to exchange and emails the next player of their turn. If both players have made a move, then the game will email both players of the game outcome.
    - Raises: NotFoundException if player does not exist. ForbiddenException if player is not part of the game or if it is not the player's turn. BadRequestException if game key is not valid.
    
- **get_user_games**
    - Path: 'user/games'
    - Method: GET
    - Parameters: player
    - Returns: A lsit of GameForms. 
    - Description: Returns all active games that a player is currently in (unordered).
    - Raises: NotFoundException if player does not exist.
    
- **cancel_game**
    - Path: 'user/cancel-game'
    - Method: PUT
    - Parameters: game_urlsafe_key, player
    - Returns: Message confirming that a player has forfeit the game and that their opponent has won.
    - Description: Cancel game does not actually cancel the game, but forfeits the player that is canceling the game; giving the win to the cancelling player's opponent. The name of this endpoint is kept for consistency with the project rubric. The player's opponent will be sent an email notifying them of player's forfeiture and their win.
    - Raises: NotFoundException if player does not exist. ForbiddenException if player is not part of the game. BadRequestException is game key is not valid.
    
- **get_user_rankings**
    - Path: 'user/ranking'
    - Method: GET
    - Parameters: player
    - Returns: Messaging detailing a player's name and record (wins-ties-losses) and their rank out of all the players.
    - Description: Players stats are tracked and players are ranked by their number of wins over total games.
    - Raises: NotFoundException if a player does not exist.

- **get_game_history**
    - Path: 'user/history'
    - Method: GET
    - Parameters: player
    - Returns: A list of GameHistoryForms.
    - Description: Returns a list of all completed games (unordered) along with the move history for each game for each player in the game and the game information.
    - Raises: NotFoundException if player does not exist.

## Files

 - api.py: Contains endpoints logic.
 - game.py: Contains game logic.
 - app.yaml: Application configurations.
 - cron.yaml: Cronjob configurations.
 - main.py: Handler for taskqueue handler.
 - model.py: Entities including their helper methods.
 - form.py: Message definitions .
 - utils.py: Helper function for retrieving Game model by urlsafe Key string.

## Models

- **User**
    - Stores unique user_name, email address, and game states (wins, losses, and ties)
- **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
- **Hand**
    - Records a players starting and ending hand for every game. Associated with User and Game model via KeyProperty.
    
## Forms

- **UserForm**
    - Represents a player (name, email).
- **GameForm**
    - Representation of a Game's state (game_urlsafe_key, player_one, player_two, active_player, game_over, is_forfeit, winner).
- **NewGameForm**
    - Used to create a new game (player_one, player_two).
- **PlayerMoveForm**
    - Used to detail desired player move (player, card_ids_to_exchange, game_urlsafe_key).
- **GameForms**
    - Represents a list of GameForms.
- **CancelGameForm**
    - Used by a player to forfeit a game (game_urlsafe_key, player)
- **GameHistoryForm**
    - Details a game's outcome, and the starting and ending hands of each player participating in that game (game_urlsafe_key, player_one, player_one_start_hand, player_one_end_hand, player_two, player_two_start_hand, player_two_end_hand, is_forfeit, winner).
- **GameHistoryForms**
    - Represents a list of GameHistoryForms.
- **StringMessage**
    - Represents a general purpose message to user.
- **PlayerName**
    - Represents a player's user name.

## Creator

Brian Quach
* <https://github.com/brianquach>

## Copyright and license

Code copyright 2016 Brian Quach. Code released under [the MIT license](https://github.com/brianquach/udacity-nano-fullstack-catalog/blob/master/LICENSE).