from colorama import Fore


__VOIDS = [
    (0, 0), (0, 1), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (1, 0), (1, 5), (1, 6), (1, 7), (1, 8), (2, 0), (2, 7),
    (2, 8), (3, 0), (5, 8), (6, 0), (6, 1), (6, 8), (7, 0), (7, 1), (7, 2), (7, 3), (7, 8), (8, 0), (8, 1),
    (8, 2), (8, 3), (8, 4), (8, 7), (8, 8)
]


def _repr(self):
    board = self.board

    line_acc = []
    for i in range(9):
        val_acc = []
        for j in range(9):
            val = board[i, j]
            if (i, j) in __VOIDS:
                val_acc.append(' ')
            elif (i, j) == (4, 4):
                val_acc.append('\u2588')
            elif 5 >= val > 0:
                val_acc.append(fr'{Fore.LIGHTBLUE_EX}{val}{Fore.RESET}')
            elif -5 <= val < 0:
                val_acc.append(fr'{Fore.LIGHTYELLOW_EX}{abs(val)}{Fore.RESET}')
            elif val == 0:
                val_acc.append('-')
            else:
                val_acc.append(fr'{Fore.LIGHTRED_EX}{val}{Fore.RESET}')
        line_acc.append(' '.join(val_acc))
    return '\n'.join(line_acc)

