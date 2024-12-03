use std::collections::{HashSet};
use itertools::{Itertools};
use ndarray::{Array2};
use numpy::{PyArray2, PyArrayMethods};
use pyo3::prelude::*;
use pyo3::{Py, pyclass, pymethods, Python, PyTypeInfo};
use pyo3::types::{PyBool, PyNotImplemented, PySet, PyString, PyType};
use pyo3::basic::CompareOp;
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
    fn new<'py>(py: Python<'py>, save_module: Option<Bound<'py, PyType>>) -> PyResult<Self> {
        let ultittt_save: Py<PyType> = match save_module {
            None => { Self::default_save_mod()}
            Some(save_mod) => {save_mod.unbind()}
        };

        let board = PyArray2::from_owned_array(py, Array2::zeros((9, 9)));

        return Ok(RawUltiTTTState {
            _board: board.unbind(),
            _turn: 0,
            _win_state: [0; 9],
            _active_cell: -1,
            _curr_pid: 1,
            _save_mod: ultittt_save
        });
    }

    /// copies and returns a python UltiTTT State object
    fn copy<'py>(&self, py: Python<'py>) -> PyResult<Self> {
        let board = unsafe { PyArray2::new(py, self._board.bind(py).dims(), false) };
        self._board.bind(py).copy_to(&board).expect("");

        return Ok(RawUltiTTTState{
            _board: board.unbind(),
            _turn: self._turn,
            _win_state: self._win_state,
            _active_cell: self._active_cell,
            _curr_pid: self._curr_pid,
            _save_mod: self._save_mod.clone()
        });
    }

    /// play an action on the UltiTTT State and returns the following State object
    fn play<'py>(&self, py: Python<'py>, c_move: Move) -> PyResult<Self> {
        let sup_cell = c_move.0;
        let sub_cell = c_move.1;

        let sup_i = 3 * sup_cell.0 + sup_cell.1;
        let sub_i = 3 * sub_cell.0 + sub_cell.1;

        let mut new_board = self.copy(py)?;

        let b_ref = new_board._board.bind(py);
        b_ref.set_item((sup_i, sub_i), self._curr_pid).expect("Cell outside expected range");

        new_board._win_state[sup_i] = get_winner_of(
            unsafe { b_ref.as_array() }.row(sup_i).iter()
        );

        new_board._turn += 1;
        new_board._active_cell =
            if new_board._win_state[sub_i] != 0 { -1 }
            else { i64::try_from(sub_i).expect("Cell outside expected range") };

        new_board._curr_pid = (self._curr_pid % 2) + 1;
        return Ok(new_board)
    }

    /// standard implementation of the `get_legal_moves` python method. it returns the legal
    /// actions the specified player can take.
    fn get_legal_moves<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PySet>> {
        let board = unsafe { self._board.bind(py).as_array() };
        let active_cell = usize::try_from(self._active_cell);

        let condition: Box<dyn Fn(i64, usize) -> bool> = if self._active_cell == -1 || self._win_state[active_cell?] != 0 {
            Box::new(|v: i64, i: usize| -> bool { v == 0 && self._win_state[i] == 0 })
        } else {
            Box::new(|v: i64, i: usize| -> bool { v == 0  && i == active_cell.unwrap() })
        };

        let moves = board.indexed_iter().filter_map(|((i,j),&v)| {
            if condition(v, i) { Some(((i / 3, i % 3), (j / 3, j % 3))) } else { None }
        }).collect::<HashSet<Move>>();

        return PySet::new(py, &moves)
    }

    /// returns the current score of the State. In the case of UltiTTT, this means the number of
    /// won sub-boards
    fn score(&self) -> (usize, usize) {
        let w = self.winner();
        return match w {
            1 => (1, 0),
            2 => (0, 1),
            _ => (0, 0),
        };
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

    fn save<'py>(slf: Bound<'py, Self>, file: Bound<'py, PyAny>) {
        let save_mod = slf.getattr("_save_mod").unwrap();
        save_mod.call_method("save_state", (file, slf), None).unwrap();
    }

    #[staticmethod]
    #[pyo3(signature=(file, save_module=None))]
    fn load<'py>(file: Bound<'py, PyString>, save_module: Option<Bound<'py, PyType>>) -> PyResult<Bound<'py, PyAny>> {
        let avalam_save: Py<PyType> = match save_module {
            None => { Self::default_save_mod()}
            Some(save_mod) => {save_mod.unbind()}
        };

        let py = file.py();
        avalam_save.bind(py.clone()).call_method(
            "load_state",  (file, Self::type_object(py.clone())), None
        )
    }

    #[getter]
    fn turn(&self) -> u32 { return self._turn }

    #[getter]
    fn curr_pid(&self) -> u32 { return self._curr_pid }

    #[getter]
    fn board(&self) -> &Py<PyArray2<i64>> { return &self._board }

    fn __richcmp__<'py>(&self, py: Python<'py>, other: &Self, op: CompareOp) -> PyResult<Bound<'py, PyBool>> {
        return match op {
            CompareOp::Eq => {
                let board_eq = std::iter::zip(
                    self._board.bind(py).to_owned_array(),
                    other._board.bind(py).to_owned_array()
                ).all(|(a, b)| a == b);

                let turn_eq = self._turn == other._turn;
                let curr_pid_eq = self._curr_pid == other._curr_pid;
                let active_cell_eq = self._active_cell == other._active_cell;
                let win_state_eq = self._win_state == other._win_state;

                let res = board_eq && active_cell_eq && turn_eq && curr_pid_eq && win_state_eq;
                Ok(PyBool::new(py, res).to_owned())
            },
            _ => { Err(PyErr::new::<PyNotImplemented, _>("")) },
        }
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