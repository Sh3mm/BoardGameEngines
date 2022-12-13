#![allow(non_snake_case)]

extern crate numpy;
extern crate itertools;
mod board;
use pyo3::{pymodule, types::PyModule, PyResult, Python};
use crate::board::{BoardState, gen_moves};

use pyo3::prelude::*;

/// A Python module implemented in Rust.

#[pymodule]
fn RustEngine(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<BoardState>()?;
    m.add_function(wrap_pyfunction!(gen_moves, m)?)?;
    Ok(())
}
