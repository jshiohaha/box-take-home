import operator
import sys

import GameBoard as game_board
import Player as player
import Utils as util


def convert_board_pos_to_index(position):
    ''' Returns an index position of a piece given a board location '''
    return int(position) - 1


def piece_owned_by_player(current_player, piece_name):
    ''' Returns a boolean regarding whether a player can move a piece '''
    if piece_name == '':
        return False

    if piece_name in current_player.get_pieces().keys():
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

    if player.map_player_name_to_enum[current_player.name] is player.UPPER and col+1 == 1:
        return True
    elif col+1 == 5:
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
    if player.map_player_name_to_enum[current_player.name] is player.UPPER:
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
    drop_row_idx = convert_board_pos_to_index(drop_location[1])
    promotion_zone = 1 if player.map_player_name_to_enum[current_player.name] is player.UPPER else 5
    pawn_to_check_for = 'P' if player.map_player_name_to_enum[current_player.name] is player.UPPER else 'p'
    
    # Can player drop pawn into the promotion zone
    if drop_row_idx+1 == promotion_zone:
        return False

    # Check for other pawns in the same column as the desired drop location.
    column = convert_board_pos_to_index(game_board.map_char_to_num[drop_location[0]])
    for idx in range(0,game_board.NUM_ROWS):
        if board[column][idx] == pawn_to_check_for:
            return False

    # will pawn next move generate opposing player be in check?
    move = generate_moves_by_piece(piece_name, drop_location, current_player, board, False)[0]
    pawn_next_row = convert_board_pos_to_index(game_board.map_char_to_num[move[0]])
    pawn_next_col = convert_board_pos_to_index(move[1])
    king_to_check_for = 'k' if player.map_player_name_to_enum[current_player.name] is player.UPPER else 'K'
    
    if board[pawn_next_col][pawn_next_row] is king_to_check_for:
        return False

    return True


def drop_piece(board, current_player, piece_name, drop_location):
    if player.map_player_name_to_enum[current_player.name] is player.UPPER:
        piece_name = str(piece_name).upper()

    col, row = convert_board_pos_to_index(drop_location[1]), convert_board_pos_to_index(game_board.map_char_to_num[drop_location[0]])
    board[row][col] = piece_name

    return board

# 
# ALL FUNCTIONS TO GENERATE PLAYER MOVES
#


def generate_moves_by_piece(piece_name, origin, current_player, board, skip):
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
    direction = 'l' if player.map_player_name_to_enum[current_player.name] is player.UPPER else 'u'
    origin_col, origin_row = convert_board_pos_to_index(origin[1]), convert_board_pos_to_index(game_board.map_char_to_num[origin[0]])
    piece_name = piece_name.lower()

    for move in map_piece_to_moves[piece_name]:
        potential_moves += move(piece_name, origin_col, origin_row, current_player, board, skip)
    try:
        potential_moves = set(potential_moves)
        potential_moves = ["".join([game_board.map_num_to_char[i[1]], str(i[0])]) for i in potential_moves]
        potential_moves = sorted(potential_moves, key=lambda x: (x[0], x[1]))
    except:
        print("Failed to convert potential_moves to board positions: " + str(list(set(potential_moves))))
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
    return potential_moves


def generate_rook_moves(piece_name, origin_col, origin_row, current_player, board, skip):
    potential_moves = set()

    # Checking in the up direction
    idx = origin_col-1
    while idx >= 0:
        if not piece_owned_by_player(current_player, board[origin_row][idx]):
            potential_moves.add((idx+1, origin_row+1))
            if not skip and board[origin_row][idx] != '':
                break
        else:
            break
        idx -= 1

    # Checking in the down direction
    idx = origin_col+1
    while idx < game_board.NUM_COLS:
        if not piece_owned_by_player(current_player, board[origin_row][idx]):
            potential_moves.add((idx+1, origin_row+1))
            if not skip and board[origin_row][idx] != '':
                break
        else:
            break
        idx += 1

    # Checking in the left direction
    idx = origin_row-1
    while idx >= 0:
        if not piece_owned_by_player(current_player, board[idx][origin_col]):
            potential_moves.add((origin_col+1, idx+1))
            if not skip and board[idx][origin_col] != '':
                break
        else:
            break
        idx -= 1

    # Checking in the right direction
    idx = origin_row+1
    while idx < game_board.NUM_ROWS:
        if not piece_owned_by_player(current_player, board[idx][origin_col]):
            potential_moves.add((origin_col+1, idx+1))
            if not skip and board[idx][origin_col] != '':
                break
        else:
            break
        idx += 1

    return potential_moves


# figure out how to stop bishop from jumping over pieces -- probably take in the board and check values
def generate_bishop_moves(piece_name, origin_col, origin_row, current_player, board, skip):
    potential_moves = set()
    col, row = origin_col+1, origin_row+1

    # Checking the LOWER LEFT direction
    offset = 1
    while 1 <= col-offset  and 1 <= row-offset:
        if not piece_owned_by_player(current_player, board[row-offset-1][col-offset-1]):
            potential_moves.add((col-offset, row-offset))
            if not skip and board[row-offset-1][col-offset-1] != '':
                break
        else:
            break
        offset += 1

    # Checking the LOWER RIGHT direction
    offset = 1
    while 1 <= col-offset  and game_board.NUM_COLS >= row+offset:
        if not piece_owned_by_player(current_player, board[row+offset-1][col-offset-1]):
            potential_moves.add((col-offset, row+offset))
            if not skip and board[row+offset-1][col-offset-1] != '':
                break
        else:
            break
        offset += 1

    # Checking the UPPER LEFT direction
    offset = 1
    while game_board.NUM_COLS >= col+offset  and 1 <= row-offset: 
        if not piece_owned_by_player(current_player, board[row-offset-1][col+offset-1]):
            potential_moves.add((col+offset, row-offset))
            if not skip and board[row-offset-1][col+offset-1] != '':
                break
        else:
            break
        offset += 1

    # Checking the UPPER RIGHT direction
    offset = 1
    while game_board.NUM_COLS >= col+offset  and game_board.NUM_ROWS >= row+offset: 
        if not piece_owned_by_player(current_player, board[row+offset-1][col+offset-1]):
            potential_moves.add((col+offset, row+offset))
            if not skip and board[row+offset-1][col+offset-1] != '':
                break
        else:
            break
        offset += 1

    return potential_moves


def generate_gold_general_moves(piece_name, origin_col, origin_row, current_player, board, skip):
    potential_moves = set()
    void_spots = [(origin_col+1, origin_row+1)]

    col_lower_bound, col_upper_bound = max(1, origin_col), min(game_board.NUM_COLS, origin_col+2)
    row_lower_bound, row_upper_bound = max(1, origin_row), min(game_board.NUM_ROWS, origin_row+2)

    if player.map_player_name_to_enum[current_player.name] is player.LOWER:
        void_spots += [(origin_col, origin_row), 
                       (origin_col, origin_row+2)]
    else:
        void_spots += [(origin_col+2, origin_row), 
                       (origin_col+2, origin_row+2)]

    for i in range(col_lower_bound, col_upper_bound+1):
        for j in range(row_lower_bound, row_upper_bound+1):
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

    if player.map_player_name_to_enum[current_player.name] is player.LOWER:
        void_spots += [(origin_col+1, origin_row+2), 
                       (origin_col+1, origin_row),
                       (origin_col, origin_row+1)]
    else:
        void_spots += [(origin_col+1, origin_row), 
                       (origin_col+1, origin_row+2),
                       (origin_col+2, origin_row+1)]

    for i in range(col_lower_bound, col_upper_bound+1):
        for j in range(row_lower_bound, row_upper_bound+1):
            if (i,j) in void_spots:
                continue
            else:
                potential_moves.add((i,j))
    return potential_moves


def generate_pawn_moves(piece_name, origin_col, origin_row, current_player, board, skip):
    potential_moves = set()

    if ord(piece_name) > 97:
        if player.map_player_name_to_enum[current_player.name] is player.UPPER and origin_col >= 1:
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


# 
# ALL FUNCTIONS TO GENERATE DANGEROUS PIECE IMMEDIATE FUTURE LOCATIONS
#


def generate_attacks_by_piece(piece_name, origin, king_loc, player, board):
    ''' Return a list of potential attack moves by a dangerous piece

    A dangerous piece is one of the following players: r,+r,b,+b. These
    players are dangerous because they have been determined to have a direct
    route to the king and are within more than +/- positions of the current
    dangerous piece location.

    The range of attack locations is needed to help determine moves for escaping
    check for players.
    '''
    direction = None
    attack_moves = list()
    piece_name = piece_name.lower()

    origin_col, origin_row = convert_board_pos_to_index(origin[1]), convert_board_pos_to_index(game_board.map_char_to_num[origin[0]])
    king_col, king_row = convert_board_pos_to_index(king_loc[1]), convert_board_pos_to_index(game_board.map_char_to_num[king_loc[0]])

    attack_func = map_dangerous_pieces_to_moves[piece_name]
    attack_moves = attack_func(origin_col, origin_row, king_col, king_row, player, board)

    try:
        attack_moves = set(attack_moves)
        attack_moves = ["".join([game_board.map_num_to_char[i[1]], str(i[0])]) for i in attack_moves]
        attack_moves = sorted(attack_moves, key=lambda x: (x[0], x[1]))
    except:
        print("Failed to convert potential_moves to board positions: " + str(list(set(potential_moves))))
        sys.exit()
    return attack_moves


def generate_rook_attack(origin_col, origin_row, king_col, king_row, player, board):
    attack_moves = set()

    col, row = origin_col+1, origin_row+1
    king_col, king_row = king_col+1, king_row+1

    if row == king_row:
        if col > king_col:
            attack_moves.add((origin_col+1, origin_row+1))
            idx = origin_col-1
            while idx > king_col:
                if board[origin_row][idx] == '':
                    attack_moves.add((idx+1, origin_row+1))
                else:
                    break
                idx -= 1

        if col < king_col:
            attack_moves.add((origin_col+1, origin_row+1))
            idx = origin_col+1
            while idx < king_col:
                if board[origin_row][idx] == '':
                    attack_moves.add((idx+1, origin_row+1))
                else:
                    break
                idx += 1

    if col == king_col:
        if row > king_row:
            attack_moves.add((origin_col+1, origin_row+1))
            idx = origin_row-1
            while idx > king_row:
                if board[idx][origin_col] == '':
                    attack_moves.add((origin_col+1, idx+1))
                else:
                    break
                idx -= 1
        if row < king_row:
            attack_moves.add((origin_col+1, origin_row+1))
            idx = origin_row+1
            while idx < king_row:
                if board[idx][origin_col] == '':
                    attack_moves.add((origin_col+1, idx+1))
                else:
                    break
                idx += 1
    return attack_moves


def generate_bishop_attack(origin_col, origin_row, king_col, king_row, player, board):
    attack_moves = set()
    col, row = origin_col+1, origin_row+1
    king_col, king_row = king_col+1, king_row+1
    offset = 1

    # Checking the UPPER RIGHT direction
    if king_col > col and king_row > row:
        if king_col - col == king_row - row:
            attack_moves.add((origin_col+1, origin_row+1))
            while game_board.NUM_COLS >= col+offset  and game_board.NUM_ROWS >= row+offset: 
                if board[row+offset-1][col+offset-1] == '':
                    attack_moves.add((col+offset, row+offset))
                else:
                    break
                offset += 1
    # Checking the LOWER RIGHT direction
    elif king_col < col and king_row > row:
        difference = col - king_col
        if row + difference == king_row:
            attack_moves.add((origin_col+1, origin_row+1))
            while 1 <= col-offset  and game_board.NUM_COLS >= row+offset:
                if board[row+offset-1][col-offset-1] == '':
                    attack_moves.add((col-offset, row+offset))
                else:
                    break
                offset += 1
    # Checking the UPPER LEFT direction
    elif king_col > col and king_row < row:
        difference = row - king_row
        if king_col - difference == col:
            attack_moves.add((col, row))
            while game_board.NUM_COLS >= col+offset  and 1 <= row-offset: 
                if board[row-offset-1][col+offset-1] == '':
                    attack_moves.add((col+offset, row-offset))
                offset += 1
    # Checking the LOWER LEFT direction
    elif king_col < col and king_row < row:
        if col - king_col == row - king_col:
            attack_moves.add((col, row))
            while 1 <= col-offset  and 1 <= row-offset:
                if board[row-offset-1][col-offset-1] == '':
                    attack_moves.add((col+offset, row+offset))
                else:
                    break
                offset += 1
    return attack_moves


map_dangerous_pieces_to_moves = {
    "r": generate_rook_attack,
    "+r": generate_rook_attack,
    "b": generate_bishop_attack,
    "+b": generate_bishop_attack,
}
