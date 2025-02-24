from colorama import Fore, Back


def _repr(self):
    size: int = self.BOARD_SIZE
    board = self._board

    print(self._players)
    all_rows = []
    for i in range(size):
        row = []
        for j in range(size):
            pos = i * size + j

            symbol = '   '  if self._players[0].pos != pos else f'{Fore.CYAN} X {Fore.RESET}'
            symbol = symbol if self._players[1].pos != pos else f'{Fore.YELLOW} X {Fore.RESET}'

            if   board[1][pos] == -1: # Top -> Bottom = Red
                row.append(f'{Back.RED}{symbol}{Back.RESET}')
            elif board[3][pos] == -1: # Left -> Right = Blue
                row.append(f'{Back.BLUE}{symbol}{Back.RESET}')
            elif board[0][pos] == -1: # Bottom -> Top = Light Red
                row.append(f'{Back.LIGHTRED_EX}{symbol}{Back.RESET}')
            elif board[2][pos] == -1: # Right -> Left = Light Blue
                row.append(f'{Back.LIGHTBLUE_EX}{symbol}{Back.RESET}')
            else:
                row.append(f'{symbol}')

        all_rows.append(''.join(row))
    return '\n'.join(all_rows)

def _repr(self):
    size: int = self.BOARD_SIZE
    board = self._board
    player_pos = [self._players[0].pos, self._players[1].pos]

    index = '  ' + ''.join(f' {c} ' for c in range(size))
    all_rows = [index]
    for i in range(size):
        row = [f'{i} ']
        for j in range(size):
            pos = i * size + j

            # Bottom connection
            if board[1][pos] == -1 and i < size - 1:
                string = ' ͟ ͟' if pos not in player_pos else ' ͟X͟'
            else:
                string = '  '  if pos not in player_pos else ' X'

            # Right connection
            string += '|' if board[3][pos] == -1 and j < size - 1 else ' '

            if   pos == player_pos[0]:
                row.append(f"{Fore.CYAN}{string}{Fore.RESET}")
            elif pos == player_pos[1]:
                row.append(f"{Fore.YELLOW}{string}{Fore.RESET}")
            else:
                row.append(string)

        all_rows.append(''.join(row))
    all_rows.append(f"p1 walls: {self._players[0].walls:<2} | p2 walls: {self._players[1].walls: <2}")
    return '\n'.join(all_rows)