import sys
import logging as logger
from pathlib import Path

import MyShogiGame as my_shogi_game

def main():
    logger.basicConfig(filename='../MyShogiGame.log', level=logger.DEBUG)
    mode = sys.argv[1][1]

    filename = None
    if len(sys.argv) > 2:
        filename = sys.argv[2]

    my_file = Path(filename)
    if my_file.is_file():
        game = my_shogi_game.MyShogiGame(mode, filename)
        game.run(logger)
    else:
        print("Filename given (" + filename + ") could not be found. Exiting...")
        sys.exit()

if __name__ == "__main__":
    main()