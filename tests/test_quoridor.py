from GameEngines.Avalam import BoardState as RustBoardState
from GameEngines.Avalam.PythonEngine import BoardState as PyBoardState

import numpy as np
import pytest


rust_python = pytest.mark.parametrize(
    "board_state",
    [RustBoardState, PyBoardState] if RustBoardState is not PyBoardState else [PyBoardState]
)

@rust_python
def test_init(board_state):
    pass
