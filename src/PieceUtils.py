import GameBoard as game_board
import Player as player
import Utils as util

import operator
import sys

PLAYER = [LOWER, UPPER] = [0, 1]

def convert_board_pos_to_index(position):
    ''' Returns an index position of a piece given a board location '''
    return int(position) - 1

# could potentially be refactored to remove upper_captures and lower_captures as params
def piece_owned_by_player(current_player, piece_name):
    ''' Returns a boolean regarding whether a player can move a piece '''
    if piece_name == '':
        return False
    
    piece_name_value = ord(piece_name) if len(piece_name) == 1 else ord(piece_name[1:])

    if player.map_player_name_to_enum[current_player.name] is UPPER:
        if piece_name_value > 64 and piece_name_value < 91:
            return True
        return False

    else:
        if piece_name_value > 96 and piece_name_value < 123:
            return True
        return False


def get_piece_at_location(board, location):
    ''' Returns the name of a piece as a string or None if there is no piece at that location '''
    
    col, row = convert_board_pos_to_index(location[1]), convert_board_pos_to_index(game_board.map_char_to_num[location[0]])
    
    if board[row][col] == '':
        return None

    return board[row][col]


def promote_piece(piece_name):
    ''' Return an updated piece_name to indicate a promoted piece

    Given the current state of the board, a piece name, and a location,
    this function creates a promoted piece and inserts it at the given
    location. This function operates under the assumption that the piece 
    can be promoted by the current player.
    '''

    return'+' + piece_name


def can_be_promoted(piece_name, piece_origin, piece_dstination):
    ''' Returns a boolean regarding whether or not a piece can be promoted
    '''

    if piece_name[0] == '+':
        return False

    piece = piece_name.lower()

    if piece == "k" or piece == "g":
        return False

    if ord(piece_name) < 97:
        if piece_origin[1] == '1' or piece_dstination[1] == '1':
            return True
        return False

    else:
        if piece_origin[1] == '5' or piece_dstination[1] == '5':
            return True
        return False


def should_pawn_be_promoted(piece_name, current_player, board_destination):
    if piece_name.lower() != "p":
        return False

    col = convert_board_pos_to_index(board_destination[1])

    if player.map_player_name_to_enum[current_player.name] is UPPER and col+1 == 1:
        return True
    elif player.map_player_name_to_enum[current_player.name] is LOWER and col+1 == 5:
        return True

    return False


def can_make_move(board, current_player, piece_name, origin_location, destination_location):
    ''' Returns a boolean of whether or not the destination is in list of possible moves
    
    This functions checks to make sure a player is legally allowed to move his or her piece
    into the destination_location position. If the player does not own the piece trying to be
    moved, the function returns False. If the player already owns the destination piece, the 
    function returns False.
    '''

    if not piece_owned_by_player(current_player, piece_name):
        return False

    destination_piece = get_piece_at_location(board, destination_location)
    if destination_piece is not None:
        if piece_owned_by_player(current_player, destination_piece):
            return False
    
    return True


def make_move(board, piece_name, origin, destination):
    origin_col, origin_row = convert_board_pos_to_index(origin[1]), convert_board_pos_to_index(game_board.map_char_to_num[origin[0]])
    destination_col, destination_row = convert_board_pos_to_index(destination[1]), convert_board_pos_to_index(game_board.map_char_to_num[destination[0]])

    board[origin_row][origin_col] = ''
    board[destination_row][destination_col] = piece_name

    return board


def can_drop_piece(board, piece_name, current_player, drop_location, lower_captures, upper_captures):
    # TODO........
    # A pawn may not be dropped onto a square onto a square that results in checkmate

    col, row = convert_board_pos_to_index(drop_location[1]), convert_board_pos_to_index(game_board.map_char_to_num[drop_location[0]])

    if board[row][col] != '':
        return False

    # is_owner = piece_owned_by_player(current_player, drop_location)

    if player.map_player_name_to_enum[current_player.name] is UPPER:
        if piece_name.upper() not in upper_captures:
            return False

        if piece_name is 'p' and not can_drop_pawn(board, 'P', current_player, drop_location):
            return False
    else:
        if piece_name not in lower_captures:
            return False 

        if piece_name is 'p' and not can_drop_pawn(board, 'p', current_player, drop_location):
            return False

    return True


def can_drop_pawn(board, piece_name, current_player, drop_location):
    promotion_zone = 1 if player.map_player_name_to_enum[current_player.name] is UPPER else 5
    pawn_to_check_for = 'P' if player.map_player_name_to_enum[current_player.name] is UPPER else 'p'

    drop_row_idx = convert_board_pos_to_index(drop_location[1])

    # Will player drop pawn into the promotion zone
    if drop_row_idx+1 == promotion_zone:
        return False

    # Are there any other pawns in the same column that the player wants to drop the pawn into?
    column = convert_board_pos_to_index(game_board.map_char_to_num[drop_location[0]])
    for idx in range(0,game_board.NUM_ROWS):
        if board[column][idx] == pawn_to_check_for:
            return False

    # will pawn next move generate opposing player be in check?
    move = generate_moves_by_piece(piece_name, drop_location, current_player, board, False)[0]
    pawn_next_row = convert_board_pos_to_index(game_board.map_char_to_num[move[0]])
    pawn_next_col = convert_board_pos_to_index(move[1])
    king_to_check_for = 'k' if player.map_player_name_to_enum[current_player.name] is UPPER else 'K'
    
    if board[pawn_next_col][pawn_next_row] is king_to_check_for:
        return False

    return True

def drop_piece(board, current_player, piece_name, drop_location):
    if player.map_player_name_to_enum[current_player.name] is UPPER:
        piece_name = str(piece_name).upper()

    col, row = convert_board_pos_to_index(drop_location[1]), convert_board_pos_to_index(game_board.map_char_to_num[drop_location[0]])
    board[row][col] = piece_name

    return board

# 
# ALL FUNCTIONS TO GENERATE PLAYER MOVES
#


def generate_moves_by_piece(piece_name, origin, player, board, skip):
    ''' Return a list of potential moves based on the piece name and direction

    The piece can be facing upwards or downwards on the board and can be promoted. 
    All of those can affect the way in which a piece can move. When generating moves,
    each is added to a set of potential moves, as the set preserves unique elements.
    At the end of the function, the set is converted to a list and sorted.

    Facing 'up' the board means the piece is moving toward the nth row. Facing down
    the board means the piece is moving toward the 0th row.
    '''
    direction = None
    potential_moves = list()

    # if direction = l, player is UPPER
    if len(piece_name) > 1:
        direction = 'l' if ord(piece_name[1]) < 97 else 'u'
    else:
        direction = 'l' if ord(piece_name) < 97 else 'u'

    origin_col, origin_row = convert_board_pos_to_index(origin[1]), convert_board_pos_to_index(game_board.map_char_to_num[origin[0]])
    piece_name = piece_name.lower()

    for move in map_piece_to_moves[piece_name]:
        potential_moves += move(piece_name, origin_col, origin_row, player, board, skip)

    try:
        potential_moves = set(potential_moves)
        potential_moves = ["".join([game_board.map_num_to_char[i[1]], str(i[0])]) for i in potential_moves]
        potential_moves = sorted(potential_moves, key=lambda x: (x[0], x[1]))
    except:
        print("Failed to convert potential_moves... ")
        sys.exit()
    return potential_moves


def generate_king_moves(piece_name, origin_col, origin_row, current_player, board, skip):
    potential_moves = set()

    col_lower_bound = max(1, origin_col)
    col_upper_bound = min(game_board.NUM_COLS, origin_col+2)

    row_lower_bound = max(1, origin_row)
    row_upper_bound = min(game_board.NUM_ROWS, origin_row+2)

    for i in range(col_lower_bound, col_upper_bound+1):
        for j in range(row_lower_bound, row_upper_bound+1):
            if j-1 == origin_row and i-1 == origin_col:
                continue
            else:
                potential_moves.add((i,j))

    # print("Moves after generating moves for king... " + str(["".join([game_board.map_num_to_char[i[1]], str(i[0])]) for i in potential_moves]))
    return potential_moves


# figure out how to stop rooks from jumping over pieces -- probably take in the board and check values
def generate_rook_moves(piece_name, origin_col, origin_row, current_player, board, skip):
    potential_moves = set()


    # start from location and go u,d,l,r until reach max range or a player
    idx = origin_col-1
    while idx >= 0:
        if not piece_owned_by_player(current_player, board[origin_row][idx]):
            potential_moves.add((idx+1, origin_row+1))

            if not skip and board[origin_row][idx] != '':
                break
        else:
            break

        idx -= 1

    idx = origin_col+1

    while idx < game_board.NUM_COLS:
        if not piece_owned_by_player(current_player, board[origin_row][idx]):
            potential_moves.add((idx+1, origin_row+1))

            if not skip and board[origin_row][idx] != '':
                break
        else:
            break        

        idx += 1


    idx = origin_row-1
    while idx >= 0:
        if not piece_owned_by_player(current_player, board[idx][origin_col]):
            potential_moves.add((origin_col+1, idx+1))

            if not skip and board[idx][origin_col] != '':
                break
        else:
            break
        idx -= 1

    idx = origin_row+1
    while idx < game_board.NUM_ROWS:
        if not piece_owned_by_player(current_player, board[idx][origin_col]):
            potential_moves.add((origin_col+1, idx+1))

            if not skip and board[idx][origin_col] != '':
                break
        else:
            break

        idx += 1

    # print("Moves after generating moves for rook... " + str(["".join([game_board.map_num_to_char[i[1]], str(i[0])]) for i in potential_moves]))
    return potential_moves


# figure out how to stop bishop from jumping over pieces -- probably take in the board and check values
def generate_bishop_moves(piece_name, origin_col, origin_row, current_player, board, skip):
    potential_moves = set()
    col, row = origin_col+1, origin_row+1

    # lowerLeft
    offset = 1
    # print("lower left")
    while 1 <= col-offset  and 1 <= row-offset:
        if not piece_owned_by_player(current_player, board[row-offset-1][col-offset-1]):
            potential_moves.add((col-offset, row-offset))
            if not skip and board[row-offset-1][col-offset-1] != '':
                break
        else:
            break

        offset += 1

    # lowerRight
    offset = 1
    # print("lower right")
    while 1 <= col-offset  and game_board.NUM_COLS >= row+offset:
        if not piece_owned_by_player(current_player, board[row+offset-1][col-offset-1]):
        

            potential_moves.add((col-offset, row+offset))

            if not skip and board[row+offset-1][col-offset-1] != '':
                break
        else:
            break

        offset += 1

    # upperLeft
    offset = 1
    # print("upper left")
    while game_board.NUM_COLS >= col+offset  and 1 <= row-offset: 
        if not piece_owned_by_player(current_player, board[row-offset-1][col+offset-1]):
            potential_moves.add((col+offset, row-offset))

            if not skip and board[row-offset-1][col+offset-1] != '':
                break
        else:
            break

        offset += 1

    # upperRight
    offset = 1
    # print("upper right")
    while game_board.NUM_COLS >= col+offset  and game_board.NUM_ROWS >= row+offset: 
        if not piece_owned_by_player(current_player, board[row+offset-1][col+offset-1]):
            potential_moves.add((col+offset, row+offset))

            if not skip and board[row+offset-1][col+offset-1] != '':
                break
        else:
            break

        offset += 1

    # print("Moves after generating moves for bishop... " + str(["".join([game_board.map_num_to_char[i[1]], str(i[0])]) for i in potential_moves]))
    return potential_moves


def generate_gold_general_moves(piece_name, origin_col, origin_row, current_player, board, skip):
    potential_moves = set()
    void_spots = [(origin_col+1, origin_row+1)]

    col_lower_bound, col_upper_bound = max(1, origin_col), min(game_board.NUM_COLS, origin_col+2)
    row_lower_bound, row_upper_bound = max(1, origin_row), min(game_board.NUM_ROWS, origin_row+2)

    if player.map_player_name_to_enum[current_player.name] is LOWER:
        # print("lower")
        void_spots += [(origin_col, origin_row), 
                       (origin_col, origin_row+2)]

    else:
        # print("upper")
        void_spots += [(origin_col+2, origin_row), 
                       (origin_col+2, origin_row+2)]

    for i in range(col_lower_bound, col_upper_bound+1):
        # print("i: " + str(i))
        for j in range(row_lower_bound, row_upper_bound+1):
            # print("j: " + str(j))
            if (i,j) in void_spots:
                continue
            else:
                potential_moves.add((i,j))

    return potential_moves


def generate_silver_general_moves(piece_name, origin_col, origin_row, current_player, board, skip):
    potential_moves = set()
    void_spots = [(origin_col+1, origin_row+1)]

    col_lower_bound, col_upper_bound = max(1, origin_col), min(game_board.NUM_COLS, origin_col+2)
    row_lower_bound, row_upper_bound = max(1, origin_row), min(game_board.NUM_ROWS, origin_row+2)

    if player.map_player_name_to_enum[current_player.name] is LOWER:
        # print("lower")
        void_spots += [(origin_col+1, origin_row+2), 
                       (origin_col+1, origin_row),
                       (origin_col, origin_row+1)]
    else:
        # print("upper")
        void_spots += [(origin_col+1, origin_row), 
                       (origin_col+1, origin_row+2),
                       (origin_col+2, origin_row+1)]

    for i in range(col_lower_bound, col_upper_bound+1):
        # print("i: " + str(i))
        for j in range(row_lower_bound, row_upper_bound+1):
            # print("j: " + str(j))
            if (i,j) in void_spots:
                continue
            else:
                potential_moves.add((i,j))

    # print("Moves after generating moves for silver general... " + str(["".join([game_board.map_num_to_char[i[1]], str(i[0])]) for i in potential_moves]))
    return potential_moves


def generate_pawn_moves(piece_name, origin_col, origin_row, current_player, board, skip):
    potential_moves = set()

    if ord(piece_name) > 97:
        if current_player.name == 'UPPER' and origin_col >= 1:
            potential_moves.add((origin_col, origin_row+1))
        else:
            if origin_col+1 <= game_board.NUM_ROWS:
                potential_moves.add((origin_col+2, origin_row+1))

    return potential_moves


map_piece_to_moves = {
    "k": [generate_king_moves],
    "r": [generate_rook_moves],
    "+r": [generate_king_moves, generate_rook_moves],
    "b": [generate_bishop_moves],
    "+b": [generate_king_moves, generate_bishop_moves],
    "g": [generate_gold_general_moves],
    "s": [generate_silver_general_moves],
    "+s": [generate_gold_general_moves],
    "p": [generate_pawn_moves],
    "+p": [generate_gold_general_moves],
}
