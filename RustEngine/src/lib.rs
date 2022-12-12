extern crate numpy;
extern crate itertools;

mod board;

use pyo3::prelude::*;
use pyo3::{pymodule, types::PyModule, PyResult, Python};
use crate::board::{BoardState, gen_moves};

/// A Python module implemented in Rust.
#[pymodule]
fn rust_engine(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<BoardState>()?;
    m.add_function(wrap_pyfunction!(gen_moves, m)?)?;
    Ok(())
}