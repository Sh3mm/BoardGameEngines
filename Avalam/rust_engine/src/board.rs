use std::cmp::min;
use std::collections::HashSet;
use itertools::{iproduct};
use ndarray::{Array2, Array3, s};
use numpy::{PyArray2, PyArray3, ndarray::array};
use pyo3::{IntoPy, Py, pyclass, pymethods, Python};
use pyo3::types::{PySet};
use crate::pyfunction;


type Coords = (usize, usize);
type Move = (Coords, Coords);


#[pyclass]
pub struct BoardState {
    #[pyo3(get, set)]
    board: Py<PyArray2<i32>>,
    #[pyo3(get, set)]
    ratios: Py<PyArray3<i32>>,
    #[pyo3(get, set)]
    moves: Py<PySet>,
}

unsafe impl Send for BoardState{}

impl BoardState{
    fn base_array() -> Array2<i32>{
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

    fn base_ratios() -> Array3<i32>{
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
}

#[pymethods]
impl BoardState {
    #[new]
    fn new() -> Self{
        return Python::with_gil(|_py|{
            let board = PyArray2::from_owned_array(_py, BoardState::base_array()).to_owned();
            let ratios = PyArray3::from_owned_array(_py, BoardState::base_ratios()).to_owned();
            let moves = gen_moves(board.as_ref(_py));
            return BoardState{board, ratios, moves}
        });
    }

    fn copy(&self) -> Self{
        Python::with_gil(|_py| {
            let x = unsafe { PyArray2::new(_py, self.board.as_ref(_py).dims(), false) };
            let y = unsafe { PyArray3::new(_py, self.ratios.as_ref(_py).dims(), false) };

            self.board.as_ref(_py).copy_to(x).expect("");
            self.ratios.as_ref(_py).copy_to(y).expect("");

            BoardState {
                board: x.to_owned(),
                ratios: y.to_owned(),
                moves: self.moves.clone(),
            }
        })
    }

    fn stack(&self, origin: Coords, dest: Coords) -> Self{
        let new_board = self.copy();

        Python::with_gil(|_py| {
            // board Update
            let b_ref = new_board.board.as_ref(_py);
            let top = unsafe{ *b_ref.uget(origin) };
            let bottom = unsafe{ *b_ref.uget(dest) };
            let final_val = if top >= 0 { top + bottom.abs() } else { top - bottom.abs() };

            b_ref.set_item(origin, 0).expect("Origin outside expected range");
            b_ref.set_item(dest, final_val).expect("Destination outside expected range");

            // Ratios Update
            let r_ref = new_board.ratios.as_ref(_py);
            let top_0 = unsafe{ *r_ref.uget((0, origin.0, origin.1)) };
            let top_1 = unsafe{ *r_ref.uget((1, origin.0, origin.1)) };

            let bottom_0 = unsafe{ *r_ref.uget((0, dest.0, dest.1)) };
            let bottom_1 = unsafe{ *r_ref.uget((1, dest.0, dest.1)) };

            r_ref.set_item((0, origin.0, origin.1), 0).expect("Origin outside expected range");
            r_ref.set_item((0, origin.0, origin.1), 0).expect("Origin outside expected range");

            r_ref.set_item((0, dest.0, dest.1), top_0 + bottom_0).expect("Destination outside expected range");
            r_ref.set_item((0, dest.0, dest.1), top_1 + bottom_1).expect("Destination outside expected range");

            // Moves Update
            let move_set: &PySet = new_board.moves.as_ref(_py);
            // Impossible origin
            let i_range = origin.0.checked_sub(1).unwrap_or(0)..min(origin.0 + 2, 9);
            let j_range = origin.1.checked_sub(1).unwrap_or(0)..min(origin.1 + 2, 9);
            for (i, j) in iproduct!(i_range, j_range) {
                move_set.discard((origin, (i, j)));
                move_set.discard(((i, j), origin));
            }
            // Impossible dest
            let i_range = dest.0.checked_sub(1).unwrap_or(0)..min(dest.0 + 2, 9);
            let j_range = dest.1.checked_sub(1).unwrap_or(0)..min(dest.1 + 2, 9);
            for (i, j) in iproduct!(i_range, j_range){
                move_set.discard((origin, (i, j)));
                move_set.discard(((i, j), origin));
                if unsafe{ b_ref.uget(dest).abs() + b_ref.uget((i, j)).abs() } > 5 {
                    move_set.discard(((i, j), dest));
                    move_set.discard((dest, (i, j)));
                }
            }
        });
        return new_board;
    }
}

#[pyfunction]
pub fn gen_moves(board: &PyArray2<i32>) -> Py<PySet>{
    Python::with_gil(|_py|{
        let board = unsafe { board.as_array() }.mapv(|v| { v.abs() });
        let mut moves = HashSet::<Move>::new();

        for (i, j) in iproduct!(0..9, 0..9) {
            if *board.get([i, j]).unwrap() == 0 { continue; }
            let sub = board.slice(s![
                    i.checked_sub(1).unwrap_or(0)..min(i + 2, 9),
                    j.checked_sub(1).unwrap_or(0)..min(j + 2, 9)
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
        return moves.into_py(_py).cast_as::<PySet>(_py).unwrap().into();
    })
}