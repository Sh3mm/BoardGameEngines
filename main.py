from Avalam import Game
from Players import RandomPlayer


def main():
    Game(RandomPlayer(), RandomPlayer()).play()


if __name__ == '__main__':
    main()
