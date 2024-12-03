#![allow(non_snake_case)]
#![allow(clippy::needless_return)]

extern crate numpy;
extern crate itertools;
mod Avalam;
mod Checkers;
mod UltiTTT;
use pyo3::{pymodule, types::PyModule, PyResult};
use pyo3::prelude::*;

use crate::Avalam::{RawAvalamState};
use crate::Checkers::{RawCheckersState};
use crate::UltiTTT::{RawUltiTTTState};

/// The rust implementation of engines for multiple games
#[pymodule]
#[pyo3(name="GameEngines")]
fn RustEngine(m: &Bound<'_, PyModule>) -> PyResult<()> {
    Avalam(m)?;
    Checkers(m)?;
    UltiTTT(m)?;
    Ok(())
}

/// The rust implementation of an Avalam engine
fn Avalam(main_module: &Bound<'_, PyModule>) -> PyResult<()> {
    let avalam_module = PyModule::new(main_module.py(), "Avalam")?;
    avalam_module.add_class::<RawAvalamState>()?;
    main_module.add_submodule(&avalam_module)
}

/// The rust implementation of a Checkers engine
fn Checkers(main_module: &Bound<'_, PyModule>) -> PyResult<()> {
    let checkers_module = PyModule::new(main_module.py(), "Checkers")?;
    checkers_module.add_class::<RawCheckersState>()?;
    main_module.add_submodule(&checkers_module)
}


/// The rust implementation of an Ultimate Tic-tac-toe engine
fn UltiTTT(main_module: &Bound<'_, PyModule>) -> PyResult<()> {
    let ultiTTT_module = PyModule::new(main_module.py(), "UltiTTT")?;
    ultiTTT_module.add_class::<RawUltiTTTState>()?;
    main_module.add_submodule(&ultiTTT_module)

}