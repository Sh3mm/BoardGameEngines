use std::collections::{HashMap, HashSet};
use itertools::{Itertools};
use numpy::{PyArray2};
use ndarray::{Array2};
use pyo3::{IntoPy, Py, pyclass, pymethods, PyObject, Python};
use pyo3::types::{PyList, PySet, PyType};

type Coords = (usize, usize);
type Move = (Coords, Coords);


#[pyclass(subclass, dict)]
pub struct RawUltiTTTState {
    #[pyo3(get)]
    board: Py<PyArray2<i64>>,
    #[pyo3(get)]
    turn: u32,
    #[pyo3(get)]
    curr_pid: u32,
    #[pyo3(get)]
    win_state: [i64; 9],
    #[pyo3(get)]
    active_cell: i64
}

unsafe impl Send for RawUltiTTTState {}

impl RawUltiTTTState {}

#[pymethods]
impl RawUltiTTTState {
    #[new]
    /// Creates the initial UltiTTT State python object
    fn new() -> Self{
        return Python::with_gil(|_py| {
            return RawUltiTTTState {
                board: PyArray2::from_owned_array(_py,Array2::zeros((9, 9))).to_owned(),
                turn: 0,
                win_state: [0; 9],
                active_cell: -1,
                curr_pid: 1
            };
        });
    }

    /// copies and returns a python UltiTTT State object
    fn copy(&self) -> Self{
        return Python::with_gil(|_py|{
            let board = unsafe { PyArray2::new(_py, self.board.as_ref(_py).dims(), false) };
            self.board.as_ref(_py).copy_to(board).expect("");

            return RawUltiTTTState{
                board: board.to_owned(),
                turn: self.turn,
                win_state: self.win_state,
                active_cell: self.active_cell,
                curr_pid: self.curr_pid
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
            let b_ref = new_board.board.as_ref(_py);
            b_ref.set_item((sup_i, sub_i), self.curr_pid).expect("Cell outside expected range");

            new_board.win_state[sup_i] = get_winner_of(
                unsafe { b_ref.as_array() }.row(sup_i).iter()
            );
        });

        new_board.turn += 1;
        new_board.active_cell =
            if new_board.win_state[sub_i] != 0 { -1 }
            else { i64::try_from(sub_i).expect("Cell outside expected range") };

        new_board.curr_pid = (self.curr_pid % 2) + 1;
        return new_board
    }

    /// standard implementation of the `get_legal_moves` python method. it returns the legal
    /// actions the specified player can take. In the case of the UltiTTT game, both players can
    /// play the same set of moves
    fn get_legal_moves(&self) -> PyObject {
        Python::with_gil(|_py| {
            let board = unsafe { self.board.as_ref(_py).as_array() };
            let active_cell = usize::try_from(self.active_cell);

            let condition: Box<dyn Fn(i64, usize) -> bool> = if self.active_cell == -1 || self.win_state[active_cell.unwrap()] != 0 {
                Box::new(|v: i64, i: usize| -> bool { v == 0 && self.win_state[i] == 0 })
            } else {
                Box::new(|v: i64, i: usize| -> bool { v == 0  && i == active_cell.unwrap() })
            };

            return board.indexed_iter().filter_map(|((i,j),&v)| {
                if condition(v, i) { Some(((i / 3, i % 3), (j / 3, j % 3))) } else { None }
            }).collect::<HashSet<Move>>().into_py(_py)
        })
    }

    /// returns the current score of the State in the case of Avalam, this means the number of
    /// towers controlled by each player
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
        return get_winner_of(self.win_state.iter())
    }

    #[classmethod]
    fn _load_data(_: &PyType, data: HashMap<&str, PyObject>) -> Self {
        Python::with_gil(|_py| {
            return RawUltiTTTState{
                board: data.get("board").unwrap().extract(_py).unwrap(),
                turn: data.get("turn").unwrap().extract(_py).unwrap(),
                curr_pid: data.get("active_pid").unwrap().extract(_py).unwrap(),
                win_state: data.get("win_state").unwrap().extract(_py).unwrap(),
                active_cell: data.get("active_cell").unwrap().extract(_py).unwrap(),
            }
        })
    }

    #[getter]
    fn _win_state(&self) -> [i64; 9] {
        return self.win_state.clone()
    }

    #[getter]
    fn _active_cell(&self) -> i64 {
        return self.active_cell
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