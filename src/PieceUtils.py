import GameBoard as game_board
import sys

PLAYER = [LOWER, UPPER] = [0, 1]

def convert_board_pos_to_index(position):
    ''' Returns an index position of a piece given a board location '''
    return int(position) - 1

# 
# ALL FUNCTIONS TO GENERATE PLAYER MOVES
#

def generate_moves_by_piece(piece_name, origin):
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

    if len(piece_name) > 1:
        direction = 'l' if ord(piece_name[1]) < 97 else 'u'
    else:
        direction = 'l' if ord(piece_name) < 97 else 'u'

    origin_col, origin_row = convert_board_pos_to_index(origin[1]), convert_board_pos_to_index(game_board.map_char_to_num[origin[0]])
    piece_name = piece_name.lower()

    for move in map_piece_to_moves[piece_name]:
        potential_moves += move(piece_name, origin_col, origin_row, direction)

    try:
        potential_moves = set(potential_moves)
        potential_moves = ["".join([game_board.map_num_to_char[i[1]], str(i[0])]) for i in potential_moves]
    except:
        print("Failed to convert potential_moves... ")
        print(potential_moves)
        sys.exit()

    return potential_moves

def generate_king_moves(piece_name, origin_col, origin_row, direction):
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

def generate_rook_moves(piece_name, origin_col, origin_row, direction):
    potential_moves = set()

    for j in range(game_board.NUM_COLS):
        if j != origin_col:
            potential_moves.add((j+1, origin_row+1))

    for i in range(game_board.NUM_ROWS):
        if i != origin_row:
            potential_moves.add((origin_col+1, i+1))

    # print("Moves after generating moves for rook... " + str(["".join([game_board.map_num_to_char[i[1]], str(i[0])]) for i in potential_moves]))
    return potential_moves


# ['b', '+b']:
def generate_bishop_moves(piece_name, origin_col, origin_row, direction):
    potential_moves = set()
    col, row = origin_col+1, origin_row+1
    leftLowerStart, leftUpperStart = [col, row], [col, row]

    # calculate the upperLeft startPos
    while leftLowerStart[0] > 1 and leftLowerStart[1] > 1:
        leftLowerStart[0] -= 1
        leftLowerStart[1] -= 1

    if leftLowerStart[0] != col and leftLowerStart[1] != row:
        potential_moves.add((leftLowerStart[0], leftLowerStart[1]))

    while leftLowerStart[0] < game_board.NUM_ROWS and leftLowerStart[1] < game_board.NUM_COLS:
        leftLowerStart[0] += 1
        leftLowerStart[1] += 1 

        if leftLowerStart[0] == col and leftLowerStart[1] == row:
            continue

        else:
            potential_moves.add((leftLowerStart[0], leftLowerStart[1]))

    # calculate the lowerLeft startPos
    while leftUpperStart[0] < game_board.NUM_ROWS and leftUpperStart[1] > 1:
        leftUpperStart[0] += 1
        leftUpperStart[1] -= 1

    if leftUpperStart[0] != col and leftUpperStart[1] != row:
        potential_moves.add((leftUpperStart[0], leftUpperStart[1]))

    while leftUpperStart[0] > 1 and leftUpperStart[1] < game_board.NUM_COLS:
        leftUpperStart[0] -= 1
        leftUpperStart[1] += 1 

        if leftUpperStart[0] == col and leftUpperStart[1] == row:
            continue

        else:
            potential_moves.add((leftUpperStart[0], leftUpperStart[1]))

    # print("Moves after generating moves for bishop... " + str(["".join([game_board.map_num_to_char[i[1]], str(i[0])]) for i in potential_moves]))
    return potential_moves


def generate_gold_general_moves(piece_name, origin_col, origin_row, direction):
    potential_moves = set()
    void_spots = [(origin_col+1, origin_row+1)]

    col_lower_bound, col_upper_bound = max(1, origin_col), min(game_board.NUM_COLS, origin_col+2)
    row_lower_bound, row_upper_bound = max(1, origin_row), min(game_board.NUM_ROWS, origin_row+2)

    if direction == 'u':
        void_spots += [(origin_col-1, origin_row-1), 
                       (origin_col-1, origin_row+1)]
    else:
        void_spots += [(origin_row+1, origin_col-1), 
                       (origin_row+1, origin_col+1)]

    for i in range(col_lower_bound, col_upper_bound+1):
        for j in range(row_lower_bound, row_upper_bound+1):
            if (i,j) in void_spots:
                continue
            else:
                potential_moves.add((i,j))

    # print("Moves after generating moves for gold general... " + str(["".join([game_board.map_num_to_char[i[1]], str(i[0])]) for i in potential_moves]))
    return potential_moves


def generate_silver_general_moves(piece_name, origin_col, origin_row, direction):
    potential_moves = set()
    void_spots = [(origin_col+1, origin_row+1)]
    
    col_lower_bound, col_upper_bound = max(1, origin_col), min(game_board.NUM_COLS, origin_col+2)
    row_lower_bound, row_upper_bound = max(1, origin_row), min(game_board.NUM_ROWS, origin_row+2)

    if direction == 'u':
        void_spots += [(origin_col+1, origin_row+2), 
                       (origin_col+1, origin_row),
                       (origin_col, origin_row+1)]
    else:
        void_spots += [(origin_col, origin_row), 
                       (origin_col, origin_row),
                       (origin_col, origin_row)]

    for i in range(col_lower_bound, col_upper_bound+1):
        for j in range(row_lower_bound, row_upper_bound+1):
            
            if (i,j) in void_spots:
                continue
            else:
                potential_moves.add((i,j))

    # print("Moves after generating moves for silver general... " + str(["".join([game_board.map_num_to_char[i[1]], str(i[0])]) for i in potential_moves]))
    return potential_moves


# TODO: check the pawn logic
def generate_pawn_moves(piece_name, origin_col, origin_row, direction):
    if piece_name in ['p']:
        
        if direction == 'l' and origin_col >= 1:
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
    "+s": [generate_gold_general_moves, generate_silver_general_moves],
    "p": [generate_pawn_moves],
    "+p": [generate_gold_general_moves],
}
