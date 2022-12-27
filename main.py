from GameEngines import Game, RandomPlayer
from GameEngines.UltiTTT import BoardState


def main():
    Game(BoardState, RandomPlayer(), RandomPlayer()).play()


if __name__ == '__main__':
    main()
