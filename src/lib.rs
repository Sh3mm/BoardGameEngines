#![allow(non_snake_case)]
#![allow(clippy::needless_return)]

extern crate numpy;
extern crate itertools;
mod Avalam;
use pyo3::{pymodule, types::PyModule, PyResult, Python};
use crate::Avalam::{RawAvalamState};

/// The rust implementation of engines for multiple games
#[pymodule]
#[pyo3(name="GameEngines")]
fn RustEngine(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_submodule(Avalam(_py)?)?;
    Ok(())
}
/// The rust implementation of an Avalam engine
fn Avalam(_py: Python<'_>) -> PyResult<&PyModule> {
    let avalam_module = PyModule::new(_py, "Avalam")?;
    avalam_module.add_class::<RawAvalamState>()?;
    return Ok(avalam_module)
}