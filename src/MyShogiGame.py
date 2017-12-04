import sys

import GameBoard as game_board
import Utils as utils
import PieceUtils as piece_util
import Player as player

class MyShogiGame(object):
    def __init__(self, mode='i', filename=None):
        self.game_board = None
        self.mode = mode
        self.num_moves = 0
        self.lower_player = None
        self.upper_player = None
        self.is_game_over = False
        self.game_over_message = None

        if mode is 'f' and filename:
            try:
                contents = utils.parseTestCase(filename)
            except:
                print("There was an error parsing the input file: " + str(filename) + ". Exiting...")
                sys.exit()

            initialPieces = contents['initialPieces']
            self.moves = contents['moves']
            self.lower_player = player.Player('lower', contents['lowerCaptures'])
            self.upper_player = player.Player('UPPER', contents['upperCaptures'])
            self.game_board = game_board.GameBoard(False, initialPieces)

        elif mode is 'i':
            self.game_board = game_board.GameBoard()
            self.lower_player = player.Player('lower')
            self.upper_player = player.Player('UPPER')
        else:
            print("Game mode '" + str(mode) + "' not recognized. Exiting...")
            sys.exit()

        self.lower_player.set_pieces(self.game_board.lower_pieces)
        self.upper_player.set_pieces(self.game_board.upper_pieces)
        self.game_board = self.game_board.board
        self.current_player = self.lower_player

    def run(self, logger):
        return
