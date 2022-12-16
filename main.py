from GameEngines.Avalam import AvalamGame
from Players.Avalam import MiniMaxPlayer
from Players.Avalam import Heuristics as hs


def main():
    AvalamGame(MiniMaxPlayer(2, hs.sure_ratio_dif), MiniMaxPlayer(2, hs.sure_ratio_dif)).play()


if __name__ == '__main__':
    main()
