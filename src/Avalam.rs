use std::cmp::min;
use std::collections::{HashSet};
use itertools::{iproduct};
use ndarray::{Array2, Array3, s, array};
use numpy::{PyArray2, PyArray3, PyArrayMethods};
use pyo3::prelude::*;
use pyo3::{Py, pyclass, pymethods, Python, PyTypeInfo};
use pyo3::types::{PyBool, PyNotImplemented, PySet, PyString, PyType};
use pyo3::class::basic::CompareOp;


type Coords = (usize, usize);
type Move = (Coords, Coords);

#[derive(Clone)]
#[pyclass(subclass, dict)]
pub struct RawAvalamState {
    #[pyo3(get, set)]
    _board: Py<PyArray2<i64>>,
    #[pyo3(get, set)]
    _ratios: Py<PyArray3<i64>>,
    #[pyo3(get, set)]
    _curr_pid: u32,
    #[pyo3(get, set)]
    _turn: u32,
    #[pyo3(get, set)]
    _moves: Py<PySet>,
    #[pyo3(get, set)]
    _on_move_call: Option<Move>,

    #[pyo3(get, set)]
    _save_mod: Py<PyType>
}

unsafe impl Send for RawAvalamState {}

impl RawAvalamState {
    /// returns a raw avalam board in the initial state
    fn base_array() -> Array2<i64>{
        return array![
            [ 0,  0,  1, -1,  0,  0,  0,  0,  0],
            [ 0,  1, -1,  1, -1,  0,  0,  0,  0],
            [ 0, -1,  1, -1,  1, -1,  1,  0,  0],
            [ 0,  1, -1,  1, -1,  1, -1,  1, -1],
            [ 1, -1,  1, -1,  0, -1,  1, -1,  1],
            [-1,  1, -1,  1, -1,  1, -1,  1,  0],
            [ 0,  0,  1, -1,  1, -1,  1, -1,  0],
            [ 0,  0,  0,  0, -1,  1, -1,  1,  0],
            [ 0,  0,  0,  0,  0, -1,  1,  0,  0],
        ]
    }

    /// returns the ration table of an avalam board in the initial state
    fn base_ratios() -> Array3<i64>{
        return array![[
            [0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 1, 0, 1, 0, 0],
            [0, 1, 0, 1, 0, 1, 0, 1, 0],
            [1, 0, 1, 0, 0, 0, 1, 0, 1],
            [0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 1, 0, 1, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0],
        ], [
            [0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 1, 0, 0, 0, 0],
            [0, 1, 0, 1, 0, 1, 0, 0, 0],
            [0, 0, 1, 0, 1, 0, 1, 0, 1],
            [0, 1, 0, 1, 0, 1, 0, 1, 0],
            [1, 0, 1, 0, 1, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0],
        ],
        ]
    }

    /// returns a set of all legal actions that can be used in a specific state
    fn _get_legal_moves<'py>(&mut self, py: Python<'py>) -> PyResult<Bound<'py, PySet>> {
        if let Some((origin, dest)) = self._on_move_call {
            self._on_move_call = None;
            self._update_move(py, origin, dest)?;
        }
        Ok(self._moves.bind(py).to_owned())
    }

    fn default_save_mod() -> Py<PyType> {
        Python::with_gil(|_py| {
            let SaveModule = _py.import("GameEngines.Avalam.SaveModule").unwrap();
            SaveModule.getattr("AvalamSave").unwrap().extract().unwrap()
        })
    }
}

#[pymethods]
impl RawAvalamState {
    #[new]
    #[pyo3(signature=(save_module=None))]
    /// Creates the initial Avalam State python object
    fn new<'py>(py: Python<'py>, save_module: Option<Bound<'_, PyType>>) -> PyResult<Self>{
        let avalam_save: Py<PyType> = match save_module {
            None => { Self::default_save_mod()}
            Some(save_mod) => {save_mod.unbind()}
        };

        let board = PyArray2::from_owned_array(py, RawAvalamState::base_array());
        let ratios = PyArray3::from_owned_array(py, RawAvalamState::base_ratios());
        let moves = gen_moves(py, &board)?;

        return Ok(RawAvalamState {
            _board: board.unbind(),
            _ratios: ratios.unbind(),
            _turn: 0,
            _moves: moves.unbind(),
            _on_move_call: None,
            _curr_pid: 1,
            _save_mod: avalam_save
        })
    }

    fn __richcmp__<'py>(&self, py: Python<'py>, other: &Self, op: CompareOp) -> PyResult<Bound<'py, PyBool>> {
        return match op {
            CompareOp::Eq => {
                let board_eq = std::iter::zip(
                    self._board.bind(py).to_owned_array(),
                    other._board.bind(py).to_owned_array()
                ).all(|(a, b)| a == b);

                let ratios_eq = std::iter::zip(
                    self._ratios.bind(py).to_owned_array(),
                    other._ratios.bind(py).to_owned_array()
                ).all(|(a, b)| a == b);

                let turn_eq = self._turn == other._turn;
                let curr_pid_eq = self._curr_pid == other._curr_pid;

                let res = board_eq && ratios_eq && turn_eq && curr_pid_eq;
                Ok(PyBool::new(py, res).to_owned())
            },
            _ => { Err(PyErr::new::<PyNotImplemented, _>("")) },
        }
    }

    /// copies and returns a python avalam State object
    fn copy<'py>(&self, py: Python<'py>) -> PyResult<Self> {
        let copy_module = PyModule::import(py, "copy")?;
        let moves = copy_module.call_method1("copy", (self._moves.bind(py),))?.downcast::<PySet>()?.to_owned();

        let board = unsafe { PyArray2::new(py, self._board.bind(py).dims(), false) };
        let ratios = unsafe { PyArray3::new(py, self._ratios.bind(py).dims(), false) };

        self._board.bind(py).copy_to(&board).expect("");
        self._ratios.bind(py).copy_to(&ratios).expect("");

        Ok(RawAvalamState {
            _board: board.unbind(),
            _ratios: ratios.unbind(),
            _moves: moves.unbind(),
            _turn: self._turn,
            _on_move_call: None,
            _curr_pid: self._curr_pid,
            _save_mod: self._save_mod.clone_ref(py)
        })
    }

    /// play an action on the Avalam State and returns the following State object
    fn play<'py>(&mut self, py: Python<'py>, c_move: Move) -> PyResult<Self> {
        if let Some(m) = self._on_move_call {
            self._update_move(py, m.0, m.1)?;
            self._on_move_call = None;
        }

        let origin = c_move.0;
        let dest = c_move.1;

        let mut new_board = self.copy(py)?;
        new_board._on_move_call = Some((origin, dest));
        new_board._turn += 1;

        // board Update
        let b_ref = new_board._board.bind(py);
        let top = unsafe{ *b_ref.uget(origin) };
        let bottom = unsafe{ *b_ref.uget(dest) };
        let final_val = top.signum() * bottom.abs() + top;

        b_ref.set_item(origin, 0).expect("Origin outside expected range");
        b_ref.set_item(dest, final_val).expect("Destination outside expected range");

        // Ratios Update
        let r_ref = new_board._ratios.bind(py);
        let top_0 = unsafe{ *r_ref.uget((0, origin.0, origin.1)) };
        let top_1 = unsafe{ *r_ref.uget((1, origin.0, origin.1)) };

        let bottom_0 = unsafe{ *r_ref.uget((0, dest.0, dest.1)) };
        let bottom_1 = unsafe{ *r_ref.uget((1, dest.0, dest.1)) };

        r_ref.set_item((0, origin.0, origin.1), 0).expect("Origin outside expected range");
        r_ref.set_item((1, origin.0, origin.1), 0).expect("Origin outside expected range");

        r_ref.set_item((0, dest.0, dest.1), top_0 + bottom_0).expect("Destination outside expected range");
        r_ref.set_item((1, dest.0, dest.1), top_1 + bottom_1).expect("Destination outside expected range");

        new_board._curr_pid = (self._curr_pid % 2) + 1;
        return Ok(new_board);
    }

    /// standard implementation of the `get_legal_moves` python method. it returns the legal
    /// actions the specified player can take. In the case of the Avalam game, both players can
    /// play the same set of moves
    fn get_legal_moves<'py>(&mut self, py: Python<'py>) -> PyResult<Bound<'py, PySet>> {
        return self._get_legal_moves(py)
    }

    /// updates the current State move cache upon it's creation. Usually by copy.
    fn _update_move(&self, _py: Python, origin: Coords, dest: Coords) -> PyResult<()> {
        // Moves Update
        let move_set = self._moves.bind(_py).downcast::<PySet>()?;
        let b_ref = self._board.bind(_py);
        // Impossible origin
        let i_range = origin.0.saturating_sub(1)..min(origin.0 + 2, 9);
        let j_range = origin.1.saturating_sub(1)..min(origin.1 + 2, 9);
        for (i, j) in iproduct!(i_range, j_range) {
            move_set.discard((origin, (i, j)))?;
            move_set.discard(((i, j), origin))?;
        }
        // Impossible dest
        let i_range = dest.0.saturating_sub(1)..min(dest.0 + 2, 9);
        let j_range = dest.1.saturating_sub(1)..min(dest.1 + 2, 9);
        for (i, j) in iproduct!(i_range, j_range) {
            move_set.discard((origin, (i, j)))?;
            move_set.discard(((i, j), origin))?;
            if unsafe { b_ref.uget(dest).abs() + b_ref.uget((i, j)).abs() } > 5 {
                move_set.discard(((i, j), dest))?;
                move_set.discard((dest, (i, j)))?;
            }
        }
        Ok(())
    }

    /// returns the current score of the State. In the case of Avalam, this means the number of
    /// towers controlled by each player
    fn score(&self) -> (usize, usize){
        Python::with_gil(|_py| {
            let array = unsafe { self._board.bind(_py).as_array() };
            array.fold((0, 0), |b, &v| {
                if v > 0 { return (b.0 + 1, b.1); }
                if v < 0 { return (b.0, b.1 + 1); }
                return b;
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
    fn winner<'py>(&mut self, py: Python<'py>) -> PyResult<isize> {
        // unfinished
        if self._get_legal_moves(py)?
            .call_method0("__len__")?
            .call_method1("__gt__", (2,))?
            .is_truthy()? {
            return Ok(0);
        }

        let (p1, p2) = self.score();
        // tie
        if p1 == p2 {
            return Ok(-1)
        }
        // winner
        return Ok(isize::from(p1 < p2) + 1)
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

    #[getter]
    fn ratios(&self) -> &Py<PyArray3<i64>> { return &self._ratios }
}


/// generates all possible action given a specific raw Avalam board configuration
pub fn gen_moves<'py>(py: Python<'py>, board: &Bound<'py, PyArray2<i64>>) -> PyResult<Bound<'py, PySet>>{
    let board = unsafe { board.as_array() }.mapv(|v| { v.abs() });
    let mut moves = HashSet::<Move>::new();

    for (i, j) in iproduct!(0..9, 0..9) {
        if *board.get([i, j]).unwrap() == 0 { continue; }
        let sub = board.slice(s![
                i.saturating_sub(1)..min(i + 2, 9),
                j.saturating_sub(1)..min(j + 2, 9)
            ]);

        let legit = sub.indexed_iter()
            .filter_map(|((_i, _j), &v)| {
                let _i = _i + (i - (if i != 0 { 1 } else { 0 }));
                let _j = _j + (j - (if j != 0 { 1 } else { 0 }));

                if (_i, _j).eq(&(i, j)) { return None; }
                if (v == 0) || (v + *board.get([i, j]).unwrap() > 5) { return None; }

                return Some(((_i, _j), (i, j)));
            });
        moves.extend(legit);
    }
    return PySet::new(py, moves);
}