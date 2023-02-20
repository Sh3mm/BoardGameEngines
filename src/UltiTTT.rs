use numpy::{PyArray2, PyArray3, ndarray::array};
use pyo3::{IntoPy, Py, pyclass, pymethods, Python};
use pyo3::prelude::PyModule;
use pyo3::types::{PySet};


type Coords = (usize, usize);
type Move = (Coords, Coords);


#[pyclass(subclass)]
pub struct RawUltiTTTState {
    #[pyo3(get)]
    board: Py<PyArray2<u8>>,
    #[pyo3(get)]
    turn: u32,
    moves: Py<PySet>,
    win_state: [u8; 9],
    on_move_call: Option<(Coords, Coords)>
}

unsafe impl Send for RawUltiTTTState {}

impl RawUltiTTTState {}

#[pymethods]
impl RawUltiTTTState {
    // #[new]
    // /// Creates the initial Avalam State python object
    // fn new() -> Self{
    //
    // }
}