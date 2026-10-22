//! CN.PLMOD.exe engine RE pseudocode crate.
//! Modules:
//!   engine_structs    — data structures (globals, strides, records)
//!   engine_pseudocode — key functions as Rust pseudocode (original set)
//!   production_logic  — production chain model (charcoal burner)
//!   building_production — building operations & resource management (REA)
//!   all_functions     — ALL identified functions as Rust pseudocode

pub mod engine_structs;
pub mod engine_pseudocode;
pub mod production_logic;
pub mod building_production;
pub mod all_functions;
