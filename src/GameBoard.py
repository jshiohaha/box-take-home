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
        self.kings_and_locations = None
        self.lower_pieces = None
        self.upper_pieces = None
        self.board = self.initialize_board(defaultConfiguation, listOfPiecesAndLocations)
    
    def set_kings_and_locations(self, arr):
      self.kings_and_locations = arr

    def set_lower_pieces(self, arr):
      self.lower_pieces = arr

    def set_upper_pieces(self, arr):
      self.upper_pieces = arr
    
    def initialize_board(self, defaultConfiguation, listOfPiecesAndLocations):
        kings_and_locations = dict()
        lower_pieces = []
        upper_pieces = []

        board = [[' ' for i in range(NUM_COLS)] for j in range(NUM_ROWS)]

        if not defaultConfiguation and listOfPiecesAndLocations:

            for initial_pieces in listOfPiecesAndLocations:
                piece_name = initial_pieces['piece']
                loc = initial_pieces['position']

                col = piece_utils.convert_board_pos_to_index(loc[1])
                row = piece_utils.convert_board_pos_to_index(map_char_to_num[loc[0]])

                if (col >= 0 and col < NUM_COLS and
                    row >= 0 and row < NUM_ROWS):

                    if piece_name in ['k', 'K']:
                      kings_and_locations[piece_name] = loc

                    piece_name_value = ord(piece_name) if len(piece_name) == 1 else ord(piece_name[1:])

                    if piece_name_value > 64 and piece_name_value < 91:
                      upper_pieces.append(piece_name)

                    elif piece_name_value > 96 and piece_name_value < 123:
                      lower_pieces.append(piece_name)

                    board[row][col] = piece_name
                else:
                    # TODO: Should this be here? + Make sure this is the correct way to print this.
                    print("Piece " + str(piece_name) + " not inserted because of invalid "
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

            lower_pieces = { 'k', 'g', 's', 'b', 'r', 'p' }
            upper_pieces = { 'K', 'G', 'S', 'B', 'R', 'P' }
            kings_and_locations = { 'k': 'a5', 'K': 'a1' }

        self.set_kings_and_locations(kings_and_locations)
        self.set_lower_pieces(lower_pieces)
        self.set_upper_pieces(upper_pieces)

        return board
