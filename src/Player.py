PLAYER = [LOWER, UPPER] = [0, 1]

map_player_enum_to_name = { LOWER: "lower", UPPER: "UPPER" }
map_player_name_to_enum = { "lower": LOWER, "UPPER": UPPER}

class Player():

	def __init__(self, name, initial_captures=None):
		self.name = name
		self.pieces = None
		if not initial_captures:
			self.captures = []
		else:
			self.captures = initial_captures
		self.in_check = False
		self.in_checkmate = False
		self.escape_moves = None
		self.moves_to_go_in_check = None

	def is_in_check(self):
		return self.in_check

	def is_in_checkmate(self):
		return self.in_checkmate

	def set_pieces(self, pieces):
		self.pieces = pieces

	def get_pieces(self):
		return self.pieces

	def update_piece_locations(self, key, val):
		self.pieces[key] = val

	def get_escape_moves(self):
		return self.escape_moves