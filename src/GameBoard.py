import sys

import PieceUtils as piece_utils

NUM_ROWS = 5
NUM_COLS = 5

map_char_to_num = {
   "a" : 1,
   "b" : 2,
   "c" : 3,
   "d" : 4,
   "e" : 5,
}

map_num_to_char = {
   1: "a",
   2: "b",
   3: "c",
   4: "d",
   5: "e",
}

class GameBoard(object):

    def __init__(self, defaultConfiguation=True, listOfPiecesAndLocations=None):
        ''' Initializes the game board based on the initial configuration

            The listOfPiecesAndLocations is a list that contains tuples representing a piece
            and a board location. Example: [(p, a4), (S, b3)]
        '''
        self.board, self.kings_and_locations = self.initialize_board(defaultConfiguation, listOfPiecesAndLocations)

    def initialize_board(self, defaultConfiguation, listOfPiecesAndLocations):
        kings_and_locations = dict()

        board = [[' ' for i in range(NUM_COLS)] for j in range(NUM_ROWS)]

        if not defaultConfiguation and listOfPiecesAndLocations:

            for initial_pieces in listOfPiecesAndLocations:
                piece = initial_pieces['piece']
                loc = initial_pieces['position']

                col = piece_utils.convert_board_pos_to_index(loc[1])
                row = piece_utils.convert_board_pos_to_index(map_char_to_num[loc[0]])

                if (col >= 0 and col < NUM_COLS and
                    row >= 0 and row < NUM_ROWS):

                    if piece in ['k', 'K']:
                      kings_and_locations[piece] = loc

                    board[row][col] = piece
                else:
                    # TODO: Should this be here? + Make sure this is the correct way to print this.
                    print("Piece " + str(piece) + " not inserted because of invalid "
                        " board location: (" + str(col) + ", " + str(row) + ")")
                    
        else:
            if not defaultConfiguation and not listOfPiecesAndLocations:
                print("Invalid board configuation... initializing game with default board configuation.")

            board[0][4] = 'k'
            board[1][4] = 'g'
            board[2][4] = 's'
            board[3][4] = 'b'
            board[4][4] = 'r'
            board[0][3] = 'p'

            board[0][0] = 'K'
            board[1][0] = 'G'
            board[2][0] = 'S'
            board[3][0] = 'B'
            board[4][0] = 'R'
            board[4][1] = 'P'

            kings_and_locations = { 'k': 'a5', 'K': 'a1' }

        return board, kings_and_locations
