from GameEngines.UltiTTT import UltiTTTGame
from Players.UltiTTT import RandomPlayer


def main():
    UltiTTTGame(RandomPlayer(), RandomPlayer()).play()


if __name__ == '__main__':
    main()
