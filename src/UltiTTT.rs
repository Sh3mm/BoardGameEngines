use numpy::{PyArray2};
use ndarray::{Array2};
use pyo3::{Py, pyclass, pymethods, Python};


type Coords = (u32, u32);
type Move = (Coords, Coords);


#[pyclass(subclass)]
pub struct RawUltiTTTState {
    #[pyo3(get)]
    board: Py<PyArray2<u8>>,
    #[pyo3(get)]
    turn: u32,
    #[pyo3(get)]
    win_state: [u8; 9],
    #[pyo3(get)]
    active_cell: i8
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
                active_cell: -1
            };
        });
    }

    fn copy(&self) -> Self{
        return Python::with_gil(|_py|{
            let board = unsafe { PyArray2::new(_py, self.board.as_ref(_py).dims(), false) };
            self.board.as_ref(_py).copy_to(board).expect("");

            return RawUltiTTTState{
                board: board.to_owned(),
                turn: self.turn,
                win_state: self.win_state,
                active_cell: self.active_cell
            };
        });
    }

    fn play(&self, c_move: Move, pid: usize) -> Self{
        let sup_cell = c_move.0;
        let sub_cell = c_move.1;

        let mut new_board = self.copy();
        new_board.turn += 1;
        new_board.active_cell = i8::try_from(3 * sub_cell.0 + sub_cell.1).expect("Cell outside expected range");

        Python::with_gil(|_py| {
            let b_ref = new_board.board.as_ref(_py);
            b_ref.set_item(
                (3 * sup_cell.0 + sup_cell.1, 3 * sub_cell.0 + sub_cell.1),
                pid
            ).expect("Cell outside expected range");
        });

        return new_board;
    }
}

fn get_winner_of<T: Iterator>() -> u8{
    todo!()
}