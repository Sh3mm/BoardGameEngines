from typing import Tuple, Set, Type, List

from GameEngines.Quoridor.utilsTypes import MoveType, WallType, Wall, Move, PlayerInfo
from GameEngines.Quoridor.repr import _repr
from GameEngines.Quoridor.PythonEngine.utils import init_board, validate_walls, cut_wall, _Wall, _Jump, _Move
from GameEngines.Quoridor.SaveModule import QuoridorSave
from GameEngines import BaseBoardState, AbsSaveModule
from GameEngines.cache_utils import cache_moves
import numpy as np
from itertools import chain


class BoardState(BaseBoardState):

    _DEFAULT_SAVE_MOD = QuoridorSave
    def __init__(self, b_size=9, max_wall=10, *, save_module: Type[AbsSaveModule] = _DEFAULT_SAVE_MOD):
        if b_size % 2 == 0 or b_size < 5:
            raise ValueError("Board size must be odd and at least 5")

        self.BOARD_SIZE = b_size
        self.MAX_WALL = max_wall

        super().__init__(save_module=save_module)

        self._board = init_board(b_size)
        self._walls: Set[_Wall] = set()
        self._players = [ # Player position & walls left to play
            PlayerInfo(b_size // 2, max_wall),
            PlayerInfo(b_size**2 - 1 - b_size // 2, max_wall)
        ]

    def __deepcopy__(self, memodict={}):
        cp = BoardState.__new__(BoardState)
        BaseBoardState.__init__(cp, save_module=self._save_mod)

        cp.BOARD_SIZE = self.BOARD_SIZE
        cp.MAX_WALL = self.MAX_WALL

        cp._turn = self._turn
        cp._curr_pid = self._curr_pid

        cp._board = self._board.copy()
        cp._walls = self._walls.copy()
        cp._players = self._players.copy()
        return cp

    def __eq__(self, other: 'BoardState') -> bool:
        return (
            self._players == other._players and
            self._walls == other._walls and
            self._turn == other._turn and
            self._curr_pid == other._curr_pid
        )

    @property
    def board(self) -> Tuple[Set[Wall], Tuple[PlayerInfo, PlayerInfo]]:
        return (
            set(self._from_local((MoveType.WALL, (w[0], (w[1] // 9, w[1] % 9))))[1] for w in self._walls),
            tuple(self._players)
        )

    def __repr__(self):
        return _repr(self)

    def play(self, move: Move) -> 'BoardState':
        move = self._to_local(move)

        old_info: PlayerInfo = self._players[self._curr_pid - 1]

        new_state = self.copy()
        new_state._curr_pid = (self._curr_pid % 2) + 1
        new_state._turn += 1

        if move[0] is MoveType.JUMP:
            new_state._players[self._curr_pid - 1] = PlayerInfo(move[1][1], old_info.walls)
            return new_state

        new_state._walls.add(move[1])
        cut_wall(new_state._board, move[1], inplace=True)
        new_state._players[self._curr_pid - 1] = PlayerInfo(old_info.pos, old_info.walls - 1)

        return new_state

    @cache_moves
    def get_legal_moves(self, *, cache=False) -> Set[Move]:
        moves: Set[Move] = set(self._from_local((MoveType.JUMP, i)) for i in self._get_jumps())
        if self._players[self._curr_pid - 1].walls > 0:
            walls = self._get_potential_walls()
            results = validate_walls(self._board, [p.pos for p in self._players], walls, self._walls)
            moves.update(self._from_local((MoveType.WALL, w)) for w in results)

        return moves

    def _get_potential_walls(self) -> List[_Wall]:
        # getting potential horizontal walls
        top_down = self._board[1, np.ravel([np.arange(0, 71), np.arange(1, 72)])].reshape(2, -1).T
        potential_td = (top_down[:, 0] % 9 != 8) & (top_down[:, 1] != -1) # & (top_down[:, 0] != -1) already included in (% 9 != 8)<

        # getting potential vertical walls
        left_right = self._board[3, np.ravel([np.arange(0, 71), np.arange(9, 80)])].reshape(2, -1).T
        potential_lr = (left_right[:, 0] != -1) & (left_right[:, 1] != -1)

        # removing potential walls where a wall is already positioned
        for w in self._walls:
            if w[0] == WallType.V:
                potential_td[w[1]] = False
            else:
                potential_lr[w[1]] = False

        return list(chain(
            ((WallType.H, int(i)) for i in np.where(potential_td)[0]),
            ((WallType.V, int(i)) for i in np.where(potential_lr)[0])
        ))

    def _get_jumps(self) -> List[_Jump]:
        s_pos = self._players[self._curr_pid - 1      ].pos
        o_pos = self._players[self._curr_pid % 2].pos
        dest = self._board[:, s_pos]

        # if the other player is not next to the active one
        if o_pos not in dest:
            return [(s_pos, int(d)) for d in dest if d != -1]

        jumps = []
        for d in dest:
            if d == o_pos:
                _dest = self._board[:, o_pos]
                jump1 = s_pos + 2 * (o_pos - s_pos)
                if 81 > jump1 >= 0 and jump1 in _dest:
                    jumps.append((s_pos, int(jump1)))
                    continue
                else:
                    _dest = set(_dest).difference((jump1, -1, s_pos))
                    jumps.extend((s_pos, int(d)) for d in _dest)
            elif d != -1:
                jumps.append((s_pos, int(d)))
        return jumps

    def winner(self) -> int:
        # If p2 is in the first row, they wins
        if self._players[1].pos in range(0, 9):
            return 2
        # If p1 is in the last row, they wins
        if self._players[0].pos in range(72, 81):
            return 1
        # If nobody is in their respective win zones, nobody won
        return 0

    def score(self) -> Tuple[int, int]:
        return (
            self._players[0].pos // 9,
            8 - self._players[1].pos // 9
        )

    @staticmethod
    def _from_local(move: _Move) -> Move:
        if move[0] == MoveType.JUMP:
            return MoveType.JUMP, ((move[1][0] // 9, move[1][0] % 9), (move[1][1] // 9, move[1][1] % 9))
        else:
            return MoveType.WALL, (move[1][0], (move[1][1] // 9,  move[1][1] % 9))

    @staticmethod
    def _to_local(move: Move) -> _Move:
        if move[0] == MoveType.JUMP:
            return MoveType.JUMP, ((9 * move[1][0][0] + move[1][0][1]), (9 * move[1][1][0] + move[1][1][1]))
        else:
            return MoveType.WALL, (move[1][0], (9 * move[1][1][0] + move[1][1][1]))