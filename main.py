from GameEngines import Game, RandomPlayer
from GameEngines.Avalam import BoardState


def main():
    Game(BoardState, RandomPlayer(), RandomPlayer()).play_full()


if __name__ == '__main__':
    main()
