use std::collections::{HashSet};
use itertools::{Itertools};
use numpy::{PyArray2};
use ndarray::{Array2};
use pyo3::{IntoPy, Py, pyclass, pymethods, PyObject, Python};
use pyo3::basic::CompareOp;
use pyo3::types::{PyType};

type Coords = (usize, usize);
type Move = (Coords, Coords);


#[derive(Clone)]
#[pyclass(subclass, dict)]
pub struct RawUltiTTTState {
    #[pyo3(get, set)]
    _board: Py<PyArray2<i64>>,
    #[pyo3(get, set)]
    _turn: u32,
    #[pyo3(get, set)]
    _curr_pid: u32,
    #[pyo3(get, set)]
    _win_state: [i64; 9],
    #[pyo3(get, set)]
    _active_cell: i64,

    #[pyo3(get, set)]
    _save_mod: Py<PyType>
}

unsafe impl Send for RawUltiTTTState {}

impl RawUltiTTTState {
    fn default_save_mod() -> Py<PyType> {
        Python::with_gil(|_py| {
            let SaveModule = _py.import("GameEngines.UltiTTT.SaveModule").unwrap();
            SaveModule.getattr("UltiTTTSave").unwrap().extract().unwrap()
        })
    }
}

#[pymethods]
impl RawUltiTTTState {
    #[new]
    #[pyo3(signature=(save_module=None))]
    /// Creates the initial UltiTTT State python object
    fn new(save_module: Option<Py<PyType>>) -> Self{
        return Python::with_gil(|_py| {
            let ultittt_save: Py<PyType> = match save_module {
                None => { Self::default_save_mod()}
                Some(save_mod) => {save_mod}
            };

            return RawUltiTTTState {
                _board: PyArray2::from_owned_array(_py, Array2::zeros((9, 9))).to_owned(),
                _turn: 0,
                _win_state: [0; 9],
                _active_cell: -1,
                _curr_pid: 1,
                _save_mod: ultittt_save
            };
        });
    }

    /// copies and returns a python UltiTTT State object
    fn copy(&self) -> Self{
        return Python::with_gil(|_py|{
            let board = unsafe { PyArray2::new(_py, self._board.as_ref(_py).dims(), false) };
            self._board.as_ref(_py).copy_to(board).expect("");

            return RawUltiTTTState{
                _board: board.to_owned(),
                _turn: self._turn,
                _win_state: self._win_state,
                _active_cell: self._active_cell,
                _curr_pid: self._curr_pid,
                _save_mod: self._save_mod.clone()
            };
        });
    }

    /// play an action on the UltiTTT State and returns the following State object
    fn play(&self, c_move: Move) -> Self {
        let sup_cell = c_move.0;
        let sub_cell = c_move.1;

        let sup_i = 3 * sup_cell.0 + sup_cell.1;
        let sub_i = 3 * sub_cell.0 + sub_cell.1;

        let mut new_board = self.copy();

        Python::with_gil(|_py| {
            let b_ref = new_board._board.as_ref(_py);
            b_ref.set_item((sup_i, sub_i), self._curr_pid).expect("Cell outside expected range");

            new_board._win_state[sup_i] = get_winner_of(
                unsafe { b_ref.as_array() }.row(sup_i).iter()
            );
        });

        new_board._turn += 1;
        new_board._active_cell =
            if new_board._win_state[sub_i] != 0 { -1 }
            else { i64::try_from(sub_i).expect("Cell outside expected range") };

        new_board._curr_pid = (self._curr_pid % 2) + 1;
        return new_board
    }

    /// standard implementation of the `get_legal_moves` python method. it returns the legal
    /// actions the specified player can take.
    fn get_legal_moves(&self) -> PyObject {
        Python::with_gil(|_py| {
            let board = unsafe { self._board.as_ref(_py).as_array() };
            let active_cell = usize::try_from(self._active_cell);

            let condition: Box<dyn Fn(i64, usize) -> bool> = if self._active_cell == -1 || self._win_state[active_cell.unwrap()] != 0 {
                Box::new(|v: i64, i: usize| -> bool { v == 0 && self._win_state[i] == 0 })
            } else {
                Box::new(|v: i64, i: usize| -> bool { v == 0  && i == active_cell.unwrap() })
            };

            return board.indexed_iter().filter_map(|((i,j),&v)| {
                if condition(v, i) { Some(((i / 3, i % 3), (j / 3, j % 3))) } else { None }
            }).collect::<HashSet<Move>>().into_py(_py)
        })
    }

    /// returns the current score of the State. In the case of UltiTTT, this means the number of
    /// won sub-boards
    fn score(&self) -> (usize, usize) {
        return (0, 0)
    }

    /// return the current winner of the game.
    ///
    /// If the game is unfinished, it return 0
    ///
    /// If the game is a tie it returns -1
    ///
    /// Otherwise, it returns the player id of the winner
    fn winner(&self) -> i64{
        return get_winner_of(self._win_state.iter())
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

                    let turn_eq = self._turn == other._turn;
                    let curr_pid_eq = self._curr_pid == other._curr_pid;
                    let active_cell_eq = self._active_cell == other._active_cell;
                    let win_state_eq = self._win_state == other._win_state;

                    let res = board_eq && active_cell_eq && turn_eq && curr_pid_eq && win_state_eq;
                    res.into_py(_py)
                },
                _ => { _py.NotImplemented() },
            }
        })
    }
}

///
fn get_winner_of<'z, T: Iterator<Item = &'z i64> + Clone>(section: T) -> i64{
    let g = section.collect_vec();

    if !g.contains(&&0) {
        return -1
    }

    let win_con = [
        // diagonals
        [g[0], g[4], g[8]],
        [g[2], g[4], g[6]],
        // rows
        [g[0], g[1], g[2]],
        [g[3], g[4], g[5]],
        [g[6], g[7], g[8]],
        // cols
        [g[0], g[3], g[6]],
        [g[1], g[4], g[7]],
        [g[2], g[5], g[8]],
    ];

    let result = win_con.iter().find(|v| {
        let val = v.iter().fold(-1, |a: i64, &&v| {
            return if a == -1 { v } else if a == v { a } else { 0 }
        });
        return ![0, -1].contains(&val)
    });

    return match result {
        None => { 0 }
        Some(v) => { *v[0] }
    }
}