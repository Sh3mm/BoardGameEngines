from Avalam import Game, BoardState
from Players import MiniMaxPlayer
from Players.minimax_utils import Heuristics as hs


def main():
    b = BoardState()
    #b = b.stack((5, 0), (4, 0))
    #b = b.stack((4, 5), (3, 5))
    #print(b)
    #print(b.ratios)
    Game(MiniMaxPlayer(2, hs.sure_ratio_dif), MiniMaxPlayer(2, hs.sure_ratio_dif)).play()


if __name__ == '__main__':
    main()
