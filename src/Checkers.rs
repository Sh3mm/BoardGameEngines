use std::cmp::{max, min};
use std::collections::HashSet;
use itertools::{sorted, Itertools};
use numpy::{PyArray2};
use ndarray::{array, Array2, s, Ix2, ArrayViewMut};
use pyo3::{IntoPy, Py, pyclass, pymethods, PyObject, Python};
use pyo3::basic::CompareOp;
use pyo3::types::{PySet, PyType};

trait Isize<T> {
    fn to_isize(&self) -> T;
    fn from_isize(v: T) -> Self;
}

type Coords = (usize, usize);
impl Isize<(isize, isize)> for Coords {
    fn to_isize(&self) -> (isize, isize) {
        (isize::try_from(self.0).unwrap(), isize::try_from(self.1).unwrap())
    }

    fn from_isize(v: (isize, isize)) -> Self {
        (usize::try_from(v.0).unwrap(), usize::try_from(v.1).unwrap())
    }
}
type Move = (Coords, Coords);

impl Isize<((isize, isize), (isize, isize))> for Move {
    fn to_isize(&self) -> ((isize, isize), (isize, isize)) {
        (self.0.to_isize(), self.1.to_isize())
    }

    fn from_isize(v: ((isize, isize), (isize, isize))) -> Self {
        (Coords::from_isize(v.0), Coords::from_isize(v.1))
    }
}


#[derive(Clone)]
#[pyclass(subclass, dict)]
pub struct RawCheckersState {
    #[pyo3(get, set)]
    _board: Py<PyArray2<i64>>,
    #[pyo3(get, set)]
    _turn: u32,
    #[pyo3(get, set)]
    _curr_pid: u32,
    #[pyo3(get, set)]
    _cached_moves: Option<Py<PySet>>,
    #[pyo3(get, set)]
    _save_mod: Py<PyType>
}

unsafe impl Send for RawCheckersState {}

impl RawCheckersState {
    fn base_array() -> Array2<i64> {
        return array![
            [ 3, 3, 3, 1, 1, 3, 3, 3],
            [ 3, 3, 0, 1, 1, 1, 3, 3],
            [ 3,-1, 0, 0, 1, 1, 1, 3],
            [-1,-1,-1, 0, 0, 1, 1, 1],
            [ 3,-1,-1,-1, 0, 0, 1, 3],
            [ 3, 3,-1,-1,-1, 0, 3, 3],
            [ 3, 3, 3,-1,-1, 3, 3, 3],
        ]
    }

    fn default_save_mod() -> Py<PyType> {
        Python::with_gil(|_py| {
            let SaveModule = _py.import("GameEngines.Checkers.SaveModule").unwrap();
            SaveModule.getattr("CheckersSave").unwrap().extract().unwrap()
        })
    }

    fn _has_moves(&self) -> bool {
        return Python::with_gil(|_py| {
            let new_board = self.copy();
            let board = unsafe { new_board._board.as_ref(_py).as_array_mut() };

            return board.indexed_iter().filter_map(|(index, &v)| {
                let condition = if self._curr_pid == 1 { v > 0 } else { v < 0 } && v < 3;
                if condition { Some(index) } else { None }
            }).find(|&coord| {
                Self::_get_moves(&board, coord, false).0.len() > 0
            }).is_some();
        });
    }

    fn _get_moves(board: &ArrayViewMut<i64, Ix2>, pos: Coords, capture_found: bool) -> (Vec<Coords>, bool) {
        let val = board.get(pos).unwrap();
        let piece_type = val.abs();
        let piece_sign = val.signum();

        let normalized = board * piece_sign;

        let pos = pos.to_isize();
        let s = normalized.shape().into_iter().map(|&v| isize::try_from(v).unwrap()).collect_vec();
        let mut directions = vec![
            ((0, -1), normalized.slice(s![pos.0, max(pos.1 - 2, 0)..pos.1; -1]  ),  1),
            ((0,  1), normalized.slice(s![pos.0, (pos.1 + 1)..min(pos.1 + 3, s[1])]), -1),
            ((-1, 0), normalized.slice(s![max(pos.0 - 2, 0)..pos.0; -1, pos.1]  ), -1),
            (( 1, 0), normalized.slice(s![(pos.0 + 1)..min(pos.0 + 3, s[0]), pos.1]),  1),
        ];

        // If the piece is not a king, only keep allowed diagonals
        if piece_type == 1 {
            directions = directions.into_iter().filter(|v| piece_sign == i64::from(v.2)).collect_vec();
        }

        // Filtering out directions if no adjacent spaces
        directions = directions.into_iter().filter(|&v| v.1.len() >= 1).collect_vec();

        let captures = directions.iter().filter_map(|(c,arr, _)| {
            // If there is space for a jump, the next space is an enemy and the jump space is open
            if arr.len() >= 2 && arr[0] < 0 && arr[1] == 0 {
                Some((
                    usize::try_from(pos.0 + 2 * c.0).unwrap(),
                    usize::try_from(pos.1 + 2 * c.1).unwrap()
                ))
            } else { None }
        }).collect_vec();

         if captures.len() > 0 || capture_found {
             return (captures, true);
        }

        let moves = directions.iter().filter_map(|(c, arr, _)| {
            if arr[0] == 0 {
                Some((
                    usize::try_from(pos.0 + c.0).unwrap(),
                    usize::try_from(pos.1 + c.1).unwrap()
                ))
            } else { None }
        }).collect_vec();

        return (moves, false);
    }

    fn _from_local(m: Move) -> Move {
        let m = m.to_isize();
        return Move::from_isize((
            ((4 + m.0.0) - m.0.1, (m.0.0 + m.0.1) - 3),  // x_res = (4 + x - y)
            ((4 + m.1.0) - m.1.1, (m.1.0 + m.1.1) - 3)   // y_res = (x + y - 3)
        ))
    }

    fn _to_local(m: Move) -> Move {
        let m = m.to_isize();
        return Move::from_isize((
            ((m.0.0 + m.0.1 - 1) / 2, (m.0.1 - m.0.0 + 7) / 2),  // x_res = (x + y - 1) // 2
            ((m.1.0 + m.1.1 - 1) / 2, (m.1.1 - m.1.0 + 7) / 2)   // y_res = (y - x + 7) // 2
        ))
    }
}

#[pymethods]
impl RawCheckersState {
    #[new]
    #[pyo3(signature=(save_module=None))]
    /// Creates the initial Checkers State python object
    fn new(save_module: Option<Py<PyType>>) -> Self{
        return Python::with_gil(|_py| {
            let checkers_save: Py<PyType> = match save_module {
                None => { Self::default_save_mod()}
                Some(save_mod) => {save_mod}
            };

            let board = PyArray2::from_owned_array(_py, RawCheckersState::base_array()).to_owned();

            return RawCheckersState{
                _board: board,
                _turn: 0,
                _curr_pid: 1,
                _cached_moves: None,
                _save_mod: checkers_save,
            }
        });
    }

    /// copies and returns a python Checkers State object
    fn copy(&self) -> Self{
        return Python::with_gil(|_py|{
            let board = unsafe { PyArray2::new(_py, self._board.as_ref(_py).dims(), false) };
            self._board.as_ref(_py).copy_to(board).expect("");

            return RawCheckersState{
                _board: board.to_owned(),
                _turn: self._turn,
                _curr_pid: self._curr_pid,
                _cached_moves: None,
                _save_mod: self._save_mod.clone()
            }
        });
    }

    /// play an action on the Checkers State and returns the following State object
    fn play(&self, c_move: Move) -> Self {
        Python::with_gil(|_py| {
            let l_move = Self::_to_local(c_move);

            let origin = l_move.0;
            let dest = l_move.1;

            let xs = sorted(vec![origin.0, dest.0]).collect_vec();
            let ys = sorted(vec![origin.1, dest.1]).collect_vec();

            let mut new_board = self.copy();
            let mut board = unsafe { new_board._board.as_ref(_py).as_array_mut() };
            new_board._turn += 1;

            let beg_val = board[[origin.0, origin.1]];

            // removes all between origin and dest
            board.slice_mut(s![xs[0]..(xs[1] + 1), ys[0]..(ys[1] + 1)]).fill(0);

            // setting the final
            board[[dest.0, dest.1]] = beg_val;

            // change from 1 -> 2 on the end row
            if c_move.1.0 == [0, 7][usize::try_from(self._curr_pid % 2).unwrap()] && beg_val.abs() == 1 {
                board[[dest.0, dest.1]] *= 2;
            }

            // If the played move is a capture, check if multi jump available
            let is_capture = (xs[1] - xs[0] + ys[1] - ys[0]) > 1;
            if is_capture {
                // If multi jump available, cache them for next step
                let (moves, _) = Self::_get_moves(&board, dest, true);
                if moves.len() > 0 {
                    let move_set: HashSet<Move> = HashSet::from_iter(
                        moves.into_iter().map(|d| Self::_from_local((dest, d)) )
                    );
                    new_board._cached_moves = Some(
                            move_set
                            .into_py(_py)
                            .downcast::<PySet>(_py).unwrap().into_py(_py)
                    );
                    return new_board
                }
            }
            new_board._cached_moves = None;
            new_board._curr_pid = (self._curr_pid % 2) + 1;
            return new_board;
        })
    }

    /// standard implementation of the `get_legal_moves` python method. it returns the legal
    /// actions the specified player can take.
    fn get_legal_moves(&self) -> PyObject {
        return Python::with_gil(|_py| {
            if let Some(moves) = &self._cached_moves {
                return moves.into_py(_py).clone();
            }

            let new_board = self.copy();
            let board = unsafe { new_board._board.as_ref(_py).as_array_mut() };

            let coords = board.indexed_iter().filter_map(|(index, &v)| {
                    let condition = if self._curr_pid == 1 {v > 0} else {v < 0} && v < 3;
                    if condition { Some(index) } else {None} })
                .collect_vec();

            let mut moves: Vec<Move> = Vec::new();
            let mut capture = false;
            for coord in coords {
                let (destinations, _capture) = Self::_get_moves(&board, coord, capture);
                // If a capture is detected, drop normal moves and only keep captures
                if _capture && !capture {
                    moves = Vec::new();
                    capture = true;
                }
                moves.extend(destinations.into_iter().map(|d| Self::_from_local((coord, d)) ))
            }
            let move_set: HashSet<Move> = HashSet::from_iter(moves.into_iter());
            return move_set.into_py(_py)
                    .downcast::<PySet>(_py)
                    .unwrap().into_py(_py)
        });
    }

    /// returns the current score of the State. In the case of Checkers, this means the number of
    /// pieces on the board
    fn score(&self) -> (usize, usize) {
        Python::with_gil(|_py| {
            let array = self._board.as_ref(_py).to_owned_array();
            return array.fold((0, 0), |r, &v| {
                return match v {
                     1 |  2 => (r.0 + 1, r.1),
                    -1 | -2 => (r.0, r.1 + 1),
                    _ => r,
                }
            })
        })
    }

    /// return the current winner of the game.
    ///
    /// If the game is unfinished, it returns 0
    ///
    /// If the game is a tie it returns -1
    ///
    /// Otherwise, it returns the player id of the winner
    fn winner(&self) -> u32{
        let (p1, p2) = self.score();

        if p1 <= 0 || p2 <= 0 {
            return if p1 > 0 { 1 } else { 2 }
        }

        if !self._has_moves() {
            return (self._curr_pid % 2) + 1
        }

        return 0
    }

    fn save(slf: PyObject, file: PyObject) {
        Python::with_gil(|_py|{
            let save_mod = slf.getattr(_py, "_save_mod").unwrap();
            save_mod.call_method(
                _py, "save_state", (file, slf), None
            ).unwrap();
        })
    }

    #[staticmethod]
    #[pyo3(signature=(file, save_module=None))]
    fn load(file: PyObject, save_module: Option<Py<PyType>>) -> PyObject {
        let avalam_save: Py<PyType> = match save_module {
            None => { Self::default_save_mod()}
            Some(save_mod) => {save_mod}
        };

        Python::with_gil(|_py|{
            avalam_save.call_method(
                _py, "load_state", (file, _py.get_type::<Self>()), None
            ).unwrap()
        })
    }

    #[getter]
    fn turn(&self) -> u32 { return self._turn }

    #[getter]
    fn curr_pid(&self) -> u32 { return self._curr_pid }

    #[getter]
    fn board(&self) -> &Py<PyArray2<i64>> { return &self._board }

    fn __richcmp__(&self, other: &Self, op: CompareOp) -> PyObject {
        Python::with_gil(|_py| {
            return match op {
                CompareOp::Eq => {
                    let board_eq = std::iter::zip(
                        self._board.as_ref(_py).to_owned_array(),
                        other._board.as_ref(_py).to_owned_array()
                    ).all(|(a, b)| a == b);

                    let cache_eq = match (&self._cached_moves, &other._cached_moves)  {
                        (None, None) => true,
                        (None, Some(_)) | (Some(_), None) => false,
                        (Some(s_moves), Some(o_moves)) => {
                            s_moves.as_ref(_py).eq(o_moves.as_ref(_py)).unwrap()
                        }
                    };

                    let turn_eq = self._turn == other._turn;
                    let curr_pid_eq = self._curr_pid == other._curr_pid;

                    let res = board_eq && cache_eq && turn_eq && curr_pid_eq;
                    res.into_py(_py)
                },
                _ => { _py.NotImplemented() },
            }
        })
    }
}