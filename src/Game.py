import sys
from copy import copy, deepcopy

import GameBoard as game_board
import Utils as utils
import PieceUtils as piece_util
import Player as player

END_GAME = [CHECKMATE, ILLEGAL_MOVE, TOO_MANY_MOVES] = ['Checkmate', 'Illegal move', 'Too many moves']


class Game(object):
    def __init__(self, mode='i', filename=None, debug_mode=False):
        self.game_board = None
        self.mode = mode
        self.num_moves = 0
        self.lower_player = None
        self.upper_player = None
        self.is_game_over = False
        self.game_over_message = None
        self.debug_mode = debug_mode

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
            print("Game mode '" + str(mode) + "' not recognized.")
            sys.exit()

        self.lower_player.set_pieces(self.game_board.lower_pieces)
        self.upper_player.set_pieces(self.game_board.upper_pieces)
        self.game_board.clear_player_pieces()
        self.game_board = self.game_board.board
        self.current_player = self.lower_player

    def increment_num_moves(self):
        self.num_moves += 1


    def switch_current_player(self):
        self.current_player = self.upper_player if self.current_player is self.lower_player else self.lower_player


    def get_opposing_player(self):
        return self.lower_player if self.current_player is self.upper_player else self.upper_player


    def get_and_print_escape_moves(self, current_player):
        escape_moves = current_player.get_escape_moves()
        current_player_escape_moves = self.generate_possible_escape_move_strings(current_player, escape_moves)
        print(current_player.get_name() + " player is in check!")
        print("Available moves:")
        for move in current_player_escape_moves:
            print(move)


    def get_possible_piece_moves(self, current_player, board):
        moves = []
        for piece_name, location in current_player.get_pieces().items():
            moves += piece_util.generate_moves_by_piece(piece_name, location, current_player, board, False)
        return moves


    def simulate(self):
        ''' Return type void

        In simulation(), the a partial game is begun from a file. All of the
        same rules apply to the list of moves provided in the input file. If the game is
        not over by the end of the simulation, interactive mode will begin.
        '''

        for move in self.moves:
            if self.debug_mode:
                print()
            if self.current_player.is_in_checkmate():
                self.set_game_over_status(CHECKMATE)
                break
            if self.num_moves >= 400:
                self.set_game_over_status(TOO_MANY_MOVES)
                break

            action, action_param_1, action_param_2, action_param_3 = self.parse_move_input(move)
            self.game_board, move_was_made = self.update_game_with_action(self.game_board, action, action_param_1, action_param_2, action_param_3)
            
            if not move_was_made:
                self.set_game_over_status(ILLEGAL_MOVE)

            self.is_opponent_in_check(self.game_board, self.current_player)
            self.switch_current_player()
            self.increment_num_moves()

            if self.is_game_over:
                self.print_last_action(self.game_board, self.lower_player.captures, self.upper_player.captures, move)
                break

        # after running simulate(), we want to print the current status of the game before the next move
        # in interactive mode
        if not self.is_game_over:
            self.print_last_action(self.game_board, self.lower_player.captures, self.upper_player.captures, move)
        self.moves = None


    def run(self):
        ''' Return type void

        Regardless of game mode, run() is called an an instance of game to execute the playing of miniShogi. 
        If the game is started in file mode with -f, then simulation() is called to run the moves to start 
        a partial game. After fully executing simulation(), if the game is not over, interactive mode will
        begin and two players can continue playing.

        If the game is started in interactive mode with -i, then the game will start from the beginning state.
        '''

        if self.mode == 'f':
            self.simulate()
        else:
            self.print_last_action(self.game_board, self.lower_player.captures, self.upper_player.captures)

        while not self.is_game_over:
            if self.current_player.is_in_checkmate():
                self.set_game_over_status(CHECKMATE)
                break

            if self.current_player.is_in_check():
                self.get_and_print_escape_moves(self.current_player)

            if self.num_moves >= 400:
                self.set_game_over_status(TOO_MANY_MOVES)
                break

            if self.mode == 'f':
                # NOTE: This is here for the purpose of testing output in -f mode to make sure that the game would
                # continue to interactive mode.
                print(self.current_player.get_name() + "> ")
                return
            else:
                move = input(self.current_player.get_name() + "> ")
                action, action_param_1, action_param_2, action_param_3 = self.parse_move_input(move)
                # attempts to take an action that does not allow the current player to get out of check
                if self.current_player.is_in_check() and action_param_2 not in self.current_player.get_escape_moves():
                    if self.debug_mode:
                        print(self.current_player.get_name() + " is in check and did not make a move to get them out.")
                    self.set_game_over_status(ILLEGAL_MOVE)
                    break

                self.game_board, move_was_made = self.update_game_with_action(self.game_board, action, action_param_1, action_param_2, action_param_3)
                
                if not move_was_made:
                    self.set_game_over_status(ILLEGAL_MOVE)

                self.is_opponent_in_check(self.game_board, self.current_player)
                self.switch_current_player()
                self.increment_num_moves()
                self.print_last_action(self.game_board, self.lower_player.captures, self.upper_player.captures, move)

                if move is None:
                    self.set_game_over_status(ILLEGAL_MOVE)
                    return

        print(self.game_over_message)


    def update_game_with_action(self, board, action, action_param_1, action_param_2, action_param_3=None):
        ''' Return type 2D-array of updated game board and boolean indicating whether an action was taken

        This function handles deciding which action is trying to be taken by the current player and attempts
        to execute that action. This function lets the functions it calls tell it whether or not the move was successful.
        '''
        if action == 'move':
            board_origin = action_param_1
            board_destination = action_param_2
            promotion_move = action_param_3

            if self.debug_mode:
                print(self.current_player.get_name() + " wants to make the following move: " + " ".join([action, action_param_1, action_param_2]))

            piece_name = piece_util.get_piece_at_location(board, board_origin)

            if not piece_name:
                if self.debug_mode:
                    print("There was no piece at board location " + str(board_origin))
                return board, False

            move = [action, action_param_1, action_param_2, action_param_3]
            board, move_was_made  = self.attempt_to_move_piece(board, piece_name, move, board_origin, board_destination)
            return board, move_was_made

        elif action == 'drop':
            
            piece_name = action_param_1
            drop_location = action_param_2
            
            board, drop_was_made = self.attempt_to_drop_piece(piece_name, drop_location, board)
            return board, drop_was_made


    def attempt_to_move_piece(self, board, piece_name, move, board_origin, board_destination):
        ''' Return type 2D-array of updated game board and boolean indicating whether an move was made

        This function explicitly handles the logic for making a move. It checks all the extensive set of
        rules regarding whether a move can be made or not.
        '''
        move = move[:-1] if move[3] is None else move

        if piece_util.can_make_move(board, self.current_player, piece_name, board_origin, board_destination):
            potential_moves = piece_util.generate_moves_by_piece(piece_name, board_origin, self.current_player, board, False)

            if self.debug_mode:
                print("Player " + self.current_player.get_name() + " has piece " + str(piece_name) + ", and potential moves: " + str(potential_moves))

            opposing_player_moves = []
            if piece_name.lower() == 'k':
                opposing_player = self.get_opposing_player()
                opposing_player_moves = self.get_possible_piece_moves(opposing_player, board)
            if board_destination in opposing_player_moves:
                if self.debug_mode:
                    print("Player " + self.current_player.get_name() + " was going to make a move to put them in check.")
                return board, False
            else:
                if board_destination in potential_moves:
                    if len(move) > 3 or piece_util.should_pawn_be_promoted(piece_name, self.current_player, board_destination):
                        if piece_util.can_be_promoted(piece_name, board_origin, board_destination):
                            temp_piece_name = piece_name
                            piece_name = piece_util.promote_piece(piece_name)

                            self.update_player_piece(self.current_player, temp_piece_name, board_destination)
                        else:
                            if self.debug_mode:
                                print(self.current_player.name + " tried to illegally promote " + str(piece_name) + ".")
                            return board, False
                    else:
                        if self.debug_mode:
                            print("Promotion of " + str(piece_name) + " invalid...")
                    
                    destination_piece = piece_util.get_piece_at_location(board, board_destination)
                    if destination_piece is not None:
                        if not piece_util.piece_owned_by_player(self.current_player, destination_piece):
                            
                            # "unpromotes" a promoted piece upon capturing
                            captured_piece = destination_piece if len(destination_piece) == 1 else destination_piece[1:]
                            
                            if captured_piece is not '':
                                self.update_player_captures(self.current_player, captured_piece, destination_piece)
                        else:
                            if self.debug_mode:
                                print("Move (" + str(move) + ") attempted by " + self.current_player.name + ", but they already own " + str(destination_piece))
                            return board, False
                    opposing_player = self.get_opposing_player()
                    board = piece_util.make_move(board, piece_name, board_origin, board_destination)
                    self.update_player_piece(self.current_player, piece_name, board_destination)
                else:
                    if self.debug_mode:
                        print("Destination (" + str(board_destination) + ") not in potential moves: " + str(potential_moves))
                    return board, False
        else:
            if self.debug_mode:
                print(self.current_player.name + " cannot move " + str(piece_name))
            return board, False
        return board, True


    def update_player_piece(self, current_player, piece_name, location):
        if current_player is self.lower_player:
            self.lower_player.update_pieces(piece_name, location)
            if self.debug_mode:
                print(str(piece_name) + " updated in lower_pieces at " + location)
        else:
            self.upper_player.update_pieces(piece_name, location)
            if self.debug_mode:
                print(str(piece_name) + " updated in upper_pieces at " + location)


    def update_player_captures(self, current_player, captured_piece, destination_piece):
        if current_player is self.lower_player:
            captured_piece = captured_piece.lower()
            self.upper_player.remove_from_pieces(destination_piece)
            self.lower_player.add_to_captures(captured_piece)
        else:
            captured_piece = captured_piece.upper()
            self.lower_player.remove_from_pieces(destination_piece)
            self.upper_player.add_to_captures(captured_piece)


    def parse_move_input(self, action):
        try:
            action = action.split(' ')
            # The max action can be is 4 because of a promotion
            if len(action) > 4 or len(action) < 2:
                return None, None, None, None
            if action[0].lower() != 'move' and action[0].lower() != 'drop':
                if self.debug_mode:
                    print(self.current_player.get_name() + " tried to take an unrecognized action: " + action[0])
                return None, None, None, None
            if len(action) == 3:
                return action[0], action[1], action[2], None
            else:
                return action[0], action[1], action[2], action[3]
        except:
            return None, None, None, None


    def attempt_to_drop_piece(self, piece_name, drop_location, board):
        ''' Return type 2D-array of updated game board and boolean indicating whether a drop was made

        This function explicitly handles the logic for dropping a piece out of captures. It checks all 
        the extensive set of rules regarding whether a drop can be made or not.
        '''
        if piece_util.can_drop_piece(self.game_board, piece_name, self.current_player, drop_location, self.lower_player.captures, self.upper_player.captures):
            self.game_board = piece_util.drop_piece(board, self.current_player, piece_name, drop_location)

            if self.current_player is self.upper_player:
                piece_name = piece_name.upper()
                self.upper_player.captures.remove(piece_name)
                self.upper_player.update_pieces(piece_name, drop_location)
            else:
                self.lower_player.captures.remove(piece_name)
                self.lower_player.update_pieces(piece_name, drop_location)
        else:
            if self.debug_mode:
                print(self.current_player.name + " cannot drop " + str(piece_name))
            return board, False
        return board, True


    def is_opponent_in_check(self, board, current_player):
        ''' Return type void

        This function checks whether or not the opposing player is in check.
        If the player is in check, then moves are generated to escape check. 
        If there exist moves to escape check, then is_opponent_in_checkmate
        to validate that the moves will actually result in avoiding checkmate.
        '''
        opposing_player, king = (self.upper_player, 'K') if current_player is self.lower_player else (self.lower_player, 'k')
        current_player_moves = self.get_possible_piece_moves(self.current_player, board)
        current_player_moves = [x for x in list(set(current_player_moves)) if x not in current_player.get_pieces().values()]
        king_loc = opposing_player.get_piece_location(king)

        if king_loc in current_player_moves:
            escape_moves, drop_moves = self.find_moves_to_escape_check(king, king_loc, opposing_player, current_player, board)
            opposing_player.in_check = True

            if not escape_moves:
                opposing_player.in_checkmate = True
            else:
                self.is_opponent_in_checkmate(board, king, current_player, current_player_moves, escape_moves, drop_moves)


    def is_opponent_in_checkmate(self, board, king, current_player, current_player_moves, escape_moves, drop_moves):
        ''' Return type void

        This function only gets called when the opposing player is in check.
        Thus, this function checks whether or not the opposing player is in
        checkmate based on the moves to escape check generated in the
        is_opponent_in_check function. If the opposing player is in checkmate,
        then the in_checkmate attribute of the opposing player is set to True,
        If the opposing player is not in checkmate, the escape_moves attribute
        is set to the escape moves generated.
        '''
        num_pieces_in_checkmate = 0
        for move_from, end_locs in escape_moves.items():
            for move_to in end_locs:
                temp_board = deepcopy(board)
                temp_pieces = copy(current_player.get_pieces())
                temp_moves = current_player_moves
                col, row = piece_util.convert_board_pos_to_index(move_to[1]), piece_util.convert_board_pos_to_index(game_board.map_char_to_num[move_to[0]])

                if temp_board[row][col] != '':
                    piece_to_remove = temp_board[row][col]
                    temp_pieces.pop(piece_to_remove, None)
                    piece_name =  piece_util.get_piece_at_location(temp_board, move_from)
                    temp_board = piece_util.make_move(temp_board, piece_name, move_from, move_to)

                    for temp_piece_name, temp_loc in temp_pieces.items():
                        temp_moves += piece_util.generate_moves_by_piece(temp_piece_name, temp_loc, current_player, temp_board, False)
                    if move_to in temp_moves:
                        num_pieces_in_checkmate += 1
        opposing_player = self.get_opposing_player()
        king_loc = opposing_player.get_piece_location(king)
        # void any drop locations that the current player already has pieces at
        drop_moves = [x for x in drop_moves if x not in current_player.get_pieces().values()]
        for piece in opposing_player.captures:
            for drop in drop_moves:
                temp_board = deepcopy(board)
                temp_captures = copy(opposing_player.captures)
                temp_moves = list()
                temp_board = piece_util.drop_piece(temp_board, current_player, piece, drop)
                
                for temp_piece_name, temp_loc in current_player.get_pieces().items():
                    temp = piece_util.generate_moves_by_piece(temp_piece_name, temp_loc, current_player, temp_board, False)
                    temp_moves += temp
                temp_moves = [x for x in list(set(temp_moves)) if x not in current_player.get_pieces().values()]

                if king_loc in temp_moves:
                    drop_moves.remove(drop)
        # if number of pieces in checkmates are equal to the number of moves to escape, 
        # then there is no place to go and game is over
        if num_pieces_in_checkmate == (len(escape_moves.values()) + len(drop_moves)):
            opposing_player.in_checkmate = True
        else:
            opposing_player.escape_moves = { 'drop_moves': drop_moves, 'escape_moves': escape_moves }


    def generate_possible_escape_move_strings(self, current_player, escape_moves):
        drop_moves = escape_moves['drop_moves']
        list_of_escape_moves = list()
        for piece_name in current_player.captures:
            for drop_loc in drop_moves:
                list_of_escape_moves.append('drop ' + piece_name.lower() + " " + str(drop_loc))

        escape_moves = escape_moves['escape_moves']
        escape_moves = sorted(escape_moves.items())
        for start_loc, end_locs in escape_moves:
            for end_loc in end_locs:
                list_of_escape_moves.append('move ' + str(start_loc) + " " + str(end_loc))

        return list_of_escape_moves


    def find_moves_to_escape_check(self, king, king_loc, current_player, opposing_player, board):
        escape_moves = dict()
        dangerous_moves = list()
        list_of_escape_moves = list()

        next_king_moves = self.find_king_escape_moves(king, king_loc, current_player, board)

        opposing_player_moves = []
        for piece_name, location in opposing_player.get_pieces().items():
            opposing_player_moves += piece_util.generate_moves_by_piece(piece_name, location, opposing_player, board, True)

            if piece_name.lower() in ['r', '+r', 'b', '+b'] and len([x for x in next_king_moves if x in opposing_player_moves]) > 0:
                dangerous_moves += piece_util.generate_attacks_by_piece(piece_name, location, king_loc, current_player, board)

                if self.debug_mode:
                    print("Moves after generating dangerous moves for " + piece_name + "... " + str(dangerous_moves))

        # void all of the opposing player moves where the player already has pieces
        opposing_player_moves = [x for x in list(set(opposing_player_moves)) if x not in opposing_player.get_pieces().values()]
        king_escape_moves = [x for x in next_king_moves if x not in opposing_player_moves]
        escape_moves[king_loc] = king_escape_moves

        for piece_name, location in current_player.get_pieces().items():
            # Avoid changing the king's escape positions 
            if piece_name != king:
                current_player_moves = piece_util.generate_moves_by_piece(piece_name, location, current_player, board, False)

                # Find moves that other pieces other than the king can make to move out of check
                intersecting_moves = [x for x in dangerous_moves if x in current_player_moves]
                if len(intersecting_moves) > 0:
                    escape_moves[location] = intersecting_moves
        return escape_moves, dangerous_moves


    def find_king_escape_moves(self, king, king_loc, current_player, board):
        next_king_moves = piece_util.generate_moves_by_piece(king, king_loc, current_player, board, False)
        next_king_moves = [x for x in next_king_moves if x not in current_player.get_pieces().values()]
        return next_king_moves


    def set_game_over_status(self, game_over_reason):
        if game_over_reason is TOO_MANY_MOVES:
            self.is_game_over = True
            self.game_over_message = "Tie game.  Too many moves."

        else:
            winning_player = self.upper_player if player.map_player_name_to_enum[self.current_player.get_name()] is player.LOWER else self.lower_player

            self.is_game_over = True
            self.game_over_message = winning_player.get_name() + " player wins.  " + game_over_reason + "."


    def print_last_action(self, game_board, lower_captures, upper_captures, move=None):
        next_player = self.get_opposing_player()
        if move:
            print(next_player.get_name() + " player action: " + move)
        print(utils.stringifyBoard(game_board))
        print("Captures UPPER: " + str(" ".join(upper_captures)))
        print("Captures lower: " + str(" ".join(lower_captures)))
        print("")
