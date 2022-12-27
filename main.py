from GameEngines.Avalam import AvalamGame
from Players.Avalam import RandomPlayer


def main():
    AvalamGame(RandomPlayer(), RandomPlayer()).play()


if __name__ == '__main__':
    main()
