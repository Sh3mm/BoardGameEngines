from Avalam import Avalam
from Players import MiniMaxPlayer
from Players.minimax_utils import Heuristics as hs


def main():
    Avalam(MiniMaxPlayer(2, hs.sure_ratio_dif), MiniMaxPlayer(2, hs.sure_ratio_dif)).play()


if __name__ == '__main__':
    main()
