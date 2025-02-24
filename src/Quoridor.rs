use std::collections::{HashSet};
use itertools::{Itertools};
use numpy::{PyArray2};
use ndarray::{Array2};
use pyo3::{IntoPy, Py, pyclass, pymethods, PyObject, Python};
use pyo3::basic::CompareOp;
use pyo3::types::{PyType};

type Move = todo!();


#[derive(Clone)]
#[pyclass(subclass, dict)]
pub struct RawQuoridorState {
    // #[pyo3(get, set)]
    // _board: Py<PyArray2<i64>>, todo
    #[pyo3(get, set)]
    _turn: u32,
    #[pyo3(get, set)]
    _curr_pid: u32,

    #[pyo3(get, set)]
    _save_mod: Py<PyType>
}

unsafe impl Send for RawQuoridorState {}

impl RawQuoridorState {
    fn default_save_mod() -> Py<PyType> {
        Python::with_gil(|_py| {
            let SaveModule = _py.import("GameEngines.Quoridor.SaveModule").unwrap();
            SaveModule.getattr("QuoridorSave").unwrap().extract().unwrap()
        })
    }
}

#[pymethods]
impl RawQuoridorState {
    #[new]
    #[pyo3(signature=(save_module=None))]
    fn new(save_module: Option<Py<PyType>>) -> Self{
        return Python::with_gil(|_py| {
            let Quoridor_save: Py<PyType> = match save_module {
                None => { Self::default_save_mod()}
                Some(save_mod) => {save_mod}
            };

            return Self {
                // _board: PyArray2::from_owned_array(_py, Array2::zeros((9, 9))).to_owned(), todo
                _turn: 0,
                _curr_pid: 1,
                _save_mod: Quoridor_save
            };
        });
    }

    /// copies and returns a python Quoridor State object
    fn copy(&self) -> Self{
        return Python::with_gil(|_py|{
            return Self {
                // _board: board.to_owned(), todo
                _turn: self._turn,
                _curr_pid: self._curr_pid,
                _save_mod: self._save_mod.clone()
            };
        });
    }

    /// play an action on the Quoridor State and returns the following State object
    fn play(&self, c_move: Move) -> Self {
        todo!()
    }

    /// standard implementation of the `get_legal_moves` python method. it returns the legal
    /// actions the specified player can take. In the case of the Quoridor game, todo
    fn get_legal_moves(&self) -> PyObject {
        todo!()
    }

    /// returns the current score of the State in the case of Quoridor, this means the number of
    /// towers controlled by each player
    fn score(&self) -> () {
        todo!()
    }

    /// return the current winner of the game.
    ///
    /// If the game is unfinished, it return 0
    ///
    /// If the game is a tie it returns -1
    ///
    /// Otherwise, it returns the player id of the winner
    fn winner(&self) -> i64 {
        todo!()
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
        let Quoridor_save: Py<PyType> = match save_module {
            None => { Self::default_save_mod()}
            Some(save_mod) => {save_mod}
        };

        Python::with_gil(|_py|{
            Quoridor_save.call_method(
                _py, "load_state", (file, _py.get_type::<Self>()), None
            ).unwrap()
        })
    }

    #[getter]
    fn turn(&self) -> u32 { return self._turn }

    #[getter]
    fn curr_pid(&self) -> u32 { return self._curr_pid }

    #[getter]
    fn board(&self) -> ()) { todo!() }

    fn __richcmp__(&self, other: &Self, op: CompareOp) -> PyObject {
        Python::with_gil(|_py| {
            return match op {
                CompareOp::Eq => {
                    todo!()
                },
                _ => { _py.NotImplemented() },
            }
        })
    }
}