use std::collections::{HashSet};
use itertools::{Itertools};
use numpy::{PyArray2};
use ndarray::{Array2};
use pyo3::{IntoPy, Py, pyclass, pymethods, PyObject, Python};
use pyo3::basic::CompareOp;
use pyo3::types::{PySet, PyType};

type Coords = (usize, usize);
type Move = (Coords, Coords);


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
    _cached_moves: Py<PySet>,
    #[pyo3(get, set)]
    _save_mod: Py<PyType>
}

unsafe impl Send for RawCheckersState {}

impl RawCheckersState {
    fn default_save_mod() -> Py<PyType> {
        Python::with_gil(|_py| {
            let SaveModule = _py.import("GameEngines.Checkers.SaveModule").unwrap();
            SaveModule.getattr("CheckersSave").unwrap().extract().unwrap()
        })
    }
}

#[pymethods]
impl RawCheckersState {
    #[new]
    #[pyo3(signature=(save_module=None))]
    /// Creates the initial Checkers State python object
    fn new(save_module: Option<Py<PyType>>) -> Self{
        todo!()
    }

    /// copies and returns a python Checkers State object
    fn copy(&self) -> Self{
        todo!()
    }

    /// play an action on the Checkers State and returns the following State object
    fn play(&self, c_move: Move) -> Self {
       todo!()
    }

    /// standard implementation of the `get_legal_moves` python method. it returns the legal
    /// actions the specified player can take.
    fn get_legal_moves(&self) -> PyObject {
        todo!()
    }

    /// returns the current score of the State. In the case of Checkers, this means the number of
    /// pieces on the board
    fn score(&self) -> (usize, usize) {
        todo!()
    }

    /// return the current winner of the game.
    ///
    /// If the game is unfinished, it return 0
    ///
    /// If the game is a tie it returns -1
    ///
    /// Otherwise, it returns the player id of the winner
    fn winner(&self) -> i64{ todo!() }

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
    fn board(&self) -> &Py<PyArray2<i64>> { todo!() }

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