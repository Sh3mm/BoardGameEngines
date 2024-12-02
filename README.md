# Board Game Engines

BoardGameEngines is a Python3 library that provides a variety of simple and fast board game engines. 

The Goal of this project is to provide a simple and standard API that allows to easily train and test AI agents on multiple games.

Games are implemented in both native python for use on all platforms and Rust for better performances. By default, The engine is the Rust one, but the python one is always available under the `PythonEngine` of each game package.

## Available games

- [Ultimate Tic-Tac-Toe](https://en.wikipedia.org/wiki/Ultimate_tic-tac-toe)
- [Checkers](https://en.wikipedia.org/wiki/Checkers)
- [Avalam](https://www.elo-games.com/en/games/967540-avalam) 

## Planned games
- [Chess](https://en.wikipedia.org/wiki/Chess)
- [Quoridor](https://en.wikipedia.org/wiki/Quoridor)
- [Go](https://en.wikipedia.org/wiki/Go_(game))

## Usage
The Library provide the engines in the form of a `BoardState` class for each game and a generic `Game` class. 

To create AI players for the games, an Abstract class `AbsPlayer` is given as a base for custom players. A random player `RandomPlayer` is also provided as an example and benchmark for custom players. 

### Running a game
Here's a code sample to run a game between two random players:
```Python
from GameEngines import Game, RandomPlayer
from GameEngines.Avalam import BoardState as AvalamBoard
# To get the python engine instead of the default one
# from GameEngines.Avalam.PythonEngine import BoardState as AvalamBoard

game = Game(AvalamBoard, RandomPlayer(), RandomPlayer())
game.play(5) # plays the next 5 moves
game.play_full() # plays the rest of the game

print(game.winner) # shows the winner of the game
```

### Creating a player

A to create a player, it must implement the `play` method. You can also give a name to your player by putting it in the `_name` parameter or by implementing the `name` property.
```python
from GameEngines import AbsPlayer, AbsBoardState
from random import choice


class RandomPlayer(AbsPlayer):
    def __init__(self, p_name: str = None):
        self._name = p_name # giving a name to the player

    def play(self, board: AbsBoardState, moves: set, pid: int):
        return choice(list(moves)) # randomly choosing a move

    @property
    def name(self) -> str:
        return self._name
```
The `play` method gets the relevant `BoardState`, the list of legal move for it's next turn and it's player number.

## Building the Rust Library
The binding between Python and Rust is done using [PyO3](https://pyo3.rs/v0.22.5/) and the [Maturin](https://www.maturin.rs/) toolchain.

once Maturin is installed, building the library can be done using
```Bash
maturin develop
```

To build the python library, simply use  
```Bash
maturin build -r
```
