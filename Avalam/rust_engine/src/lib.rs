#![allow(non_snake_case)]

extern crate numpy;
extern crate itertools;
mod board;
use pyo3::{pymodule, types::PyModule, PyResult, Python};
use crate::board::{RawBoardState};

/// A Python module implemented in Rust.

#[pymodule]
fn RustEngine(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<RawBoardState>()?;
    Ok(())
}
