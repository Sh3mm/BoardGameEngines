use itertools::{Itertools};
use ndarray::{Array2, Array3, array, ArrayView2};
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

    fn default_save_mod() -> Py<PyType> {
        Python::with_gil(|_py| {
            let SaveModule = _py.import("GameEngines.Avalam.SaveModule").unwrap();
            SaveModule.getattr("AvalamSave").unwrap().extract().unwrap()
        })
    }

    fn _moves_for(abs_board: &Array2<i64>, i: usize, j: usize) -> Vec<Move> {
        let (_i, _j) = (isize::try_from(i).unwrap(), isize::try_from(j).unwrap());
        let v = abs_board[(i, j)];

        return [
            if _i-1 >= 0 && _j-1 >= 0 { Some(((i-1, j-1), abs_board[(i-1, j-1)] + v)) } else { None },
            if _i-1 >= 0              { Some(((i-1, j  ), abs_board[(i-1, j  )] + v)) } else { None },
            if _i-1 >= 0 && _j+1 <= 8 { Some(((i-1, j+1), abs_board[(i-1, j+1)] + v)) } else { None },
            if              _j-1 >= 0 { Some(((i  , j-1), abs_board[(i  , j-1)] + v)) } else { None },
            if              _j+1 <= 8 { Some(((i  , j+1), abs_board[(i  , j+1)] + v)) } else { None },
            if _i+1 <= 8 && _j-1 >= 0 { Some(((i+1, j-1), abs_board[(i+1, j-1)] + v)) } else { None },
            if _i+1 <= 8              { Some(((i+1, j  ), abs_board[(i+1, j  )] + v)) } else { None },
            if _i+1 <= 8 && _j+1 <= 8 { Some(((i+1, j+1), abs_board[(i+1, j+1)] + v)) } else { None },
        ].into_iter().filter_map(|option| match option {
            None => { None }
            Some((end, pos)) => {
                if (v < pos) && (pos <= 5) { Some(((i, j), end)) } else { None }
            }
        }).collect_vec();
    }

    fn _has_moves(&self, py: Python) -> bool {
        let board:ArrayView2<i64> = unsafe { self._board.bind(py).as_array() };
        let abs_board = board.mapv(|v|v.abs());
        let towers = abs_board.map(|&v| ((0 < v) & (v < 5)));

        return towers.indexed_iter().find(|((i, j), &v)| {
            if v { Self::_moves_for(&abs_board, *i, *j).len() > 0 }
            else { false }
        }).is_some();
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

        return Ok(RawAvalamState {
            _board: board.unbind(),
            _ratios: ratios.unbind(),
            _turn: 0,
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

        let board = unsafe { PyArray2::new(py, self._board.bind(py).dims(), false) };
        let ratios = unsafe { PyArray3::new(py, self._ratios.bind(py).dims(), false) };

        self._board.bind(py).copy_to(&board)?;
        self._ratios.bind(py).copy_to(&ratios)?;

        Ok(RawAvalamState {
            _board: board.unbind(),
            _ratios: ratios.unbind(),
            _turn: self._turn,
            _curr_pid: self._curr_pid,
            _save_mod: self._save_mod.clone_ref(py)
        })
    }

    /// play an action on the Avalam State and returns the following State object
    fn play<'py>(&mut self, py: Python<'py>, c_move: Move) -> PyResult<Self> {
        let origin = c_move.0;
        let dest = c_move.1;

        let mut new_board = self.copy(py)?;
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
        let board:ArrayView2<i64> = unsafe { self._board.bind(py).as_array() };
        let abs_board = board.mapv(|v|v.abs());
        let towers = abs_board.map(|&v| ((0 < v) & (v < 5)));

        let moves = towers.indexed_iter().filter_map(|((i, j), &v)| {
            if v {
                Some(Self::_moves_for(&abs_board, i, j))

            } else { None }
        }).flatten();

        return PySet::new(py, moves);
    }

    /// returns the current score of the State. In the case of Avalam, this means the number of
    /// towers controlled by each player
    fn score<'py>(&self, py: Python<'py>) -> (usize, usize){
        let array = unsafe { self._board.bind(py).as_array() };
        array.fold((0, 0), |b, &v| {
            if v > 0 { return (b.0 + 1, b.1); }
            if v < 0 { return (b.0, b.1 + 1); }
            return b;
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
        if self._has_moves(py) { return Ok(0); }

        let (p1, p2) = self.score(py);
        // tie
        if p1 == p2 { return Ok(-1) }
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