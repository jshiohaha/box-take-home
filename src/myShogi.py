import sys
import Game as game


def main():
    filename = None
    debug_mode = False

    arg_length = len(sys.argv)

    if arg_length > 5:
        print("Too many parameters. Exiting...")
        sys.exit()
    else:
        if sys.argv[1][1] == 'd':
            debug_mode = True
            del sys.argv[1]
            arg_length -= 1

        mode = sys.argv[1][1]
        if arg_length > 2:
            filename = sys.argv[2]
        elif arg_length > 1:
            mode = sys.argv[1][1]
        else:
            print("Too few parameters. Exiting...")
            sys.exit()

    game_instance = game.Game(mode, filename, debug_mode)
    game_instance.run()

if __name__ == "__main__":
    main()