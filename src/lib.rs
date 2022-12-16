#![allow(non_snake_case)]

extern crate numpy;
extern crate itertools;
mod Avalam;
use pyo3::{pymodule, types::PyModule, PyResult, Python};
use crate::Avalam::{RawAvalamState};

/// A Python module implemented in Rust.

#[pymodule]
#[pyo3(name="GameEngines")]
fn RustEngine(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_submodule(Avalam(_py)?)?;
    Ok(())
}

fn Avalam(_py: Python<'_>) -> PyResult<&PyModule> {
    let avalam_module = PyModule::new(_py, "Avalam")?;
    avalam_module.add_class::<RawAvalamState>()?;
    return Ok(avalam_module)
}