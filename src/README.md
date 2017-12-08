# Game Design

## myShogi.py

`myShogi.py` is the main file in the repository. It handles CLI input, creates an instance of the game, and runs the game.

If there are any unexpected inputs or an incorrect number of arguments, myShogi will display an error message and exit its execution.
 
## GameBoard.py
The GameBoard represents the board on which miniShogi will be played. Upon calling the `__init__` function, a GameBoard instance will be created depending on the mode of the game and beginning state data.

After initialization, the GameBoard doesn't have to worry about the mode of the game anymore and is just treated as a general 2D-array storing the contents of the game board.

## Game.py
The Game object represents the actual game and understands what to do based on **game mode**, **players**, and **game state**.

The driver function for the game is `run()`. If the game is started in `file mode`, then `run()` calls `simulate()`, which will run through all of the moves given in the specified input file. If the simulateion hits any of the terminating conditiions (e.g. `ILLEGAL MOVE` or `CHECKMATE`), then the simulate function will return and the run method will detect that the game is over and also return. However, if the simulation completes all moves given in the input file, then it will check if the current player is in check. If so, it will suggest moves to get out of check. If not, it will proceed with interactive mode until a terminating condition is hit. 

The code to check for checkmate and generate escape moves contains the most expensive operations out of the entire program. There are many conditions under which a player is in checkmate, which causes a lot of checks on the possible escape moves.

#### Generating escape moves for check
Escape moves for the current player are generated in a few distinct steps. First, escape moves for the are generated, then escape moves for other pieces owned by the current player, and finally, escape moves via drop locations. The escape moves for each of those listed are as follows,

**King Moves**: the total possible moves of the opposing player set minus the possible king moves.

**Moves for other pieces**: Any moves that could potentially block a piece or capture a piece owned by the opponent player that could directly capture the king. These are mainly applicable for opposing rook and bishop pieces because they can move the equivalent of many locations.

**Drop Locations**: Drop locations are all of the locations listed in the previous section minus the position of any opposing player pieces actually on the board.

#### Checking for checkmate
Whether or not a player is in checkmate is determine by iterating through all the escape moves generated and checking if the king is still in sight of any other pieces owned by the opposing player. If there is not a single escape move that leads to the current player escaping check, then the player is in checkmate and the game is over.

Although there are functions with many lines like `attempt_to_move_piece` and `is_opponent_in_check_and_checkmate`, a lot of code in those functions pertain to the conditional logic and controlling the flow of execution. Repeated code or just general code pertaining to certain functionality was separated out into specific methods. For example, after an action is entered by the user, read from file, `update_game_with_action` determines what type of action is being taken (`move` or `drop`) and then calls `attempt_to_move_piece` or `attempt_to_drop_piece` to try and execute the action. If the action is executed, the function returns an updated version of the game board and `True`. If not, then the function returns the same version of the board and `False`. If the boolean is `False`, the function will exit and backtrack to `run()` or `simulate()`, where the game over status is set.

Initially, the Game also managed the players and all of their data, using the "dumb object" approach, but I realized it made much more sense for there to be a `Player` object that understood and managed its own data. I thought this makes more sense because the `Game` then doesn't have to ask a player who it is and what it knows but rather game can ask for information related to the player and each instance of the `Player` object will know.

## Player.py
The `Player` object represents a general player in the miniShogi game. It understands its own data and allows others to see and manipulate its data through `getter` and `setter` functions.

One of the most important pieces of data that the `Player` object tracks is its state in the game. The `Game` will tell a player if it is in check or checkmate, so that it knows in the future whether or not it is in either of those states. Thus, the Game doesn't have to keep track of their state.

For example, before the `Player` object, the `Game` object had to keep track of each player's captures and current pieces on the board thus increasing the amount of data that the `Game` object had to manage. 
 
## PieceUtils.py
`PieceUtils` is a collection of functions related any functionality of the pieces on the game board. 

Since there are no `piece` objects that dictate how each piece can move based on its title and promotional status, a dictionary is used that maps piece names to functions. So, when possible moves have to be generated, `generate_moves_by_piece` returns the set of locations to which that piece can move. This seemed simpler and just as functional as implementing an inheritence structure like `Piece > Rook > PromotedRook` that would allow for overriding parent `move()` functions. I also chose this route because I used Python for my implementation. If I used a language that more stronly enforced OOP such as Java, i might have gone with the latter inheritence implementation.

The methods for generating moves for 'rook' and 'bishop' pieces are quite long. I chose verbosity and simplicity over a more clever implementation because each function splits total moves into the four possible directions that the piece can move. Then, when the piece hits either its own piece owned by the same player it will stop and move on. Alternatively, if a piece hits another piece owned by the opposing player and the `skip` flag is set to `False`, it will stop and move on. If the `skip` flag is set to `True` and a piece encounters a piece owned by the opposing player, it will continue until it reaches the bounds of the game board.

The same approach is used when generating attack locations for `rook` and `bishop`. Attack locations are any locations that a piece has in direct path to the opposing king piece. This is a helper function for checking if a player is in checkmate and for generating moves to escape check.

## Utils.py
`Utils` is the collection of functions provided by Box to deal with printing the game board and parsing test cases.