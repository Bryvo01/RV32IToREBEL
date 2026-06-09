// src/main.rs

use clap::Parser;
use crate::vm::Rebel6VM;

// Declare our architectural modules
mod isa;
mod assembler;
mod instructions;
mod vm;

/// REBEL-6 Ternary Virtual Machine (Rust Engine)
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// The .tas assembly file to execute
    file: String,

    /// Enable 32-bit Legacy Compatibility Mode (forces integer overflow)
    #[arg(short, long)]
    compat: bool,

    /// Increase verbosity (-v for basic PC trace, -vv for full execution trace)
    #[arg(short, long, action = clap::ArgAction::Count)]
    verbose: u8,
}

fn main() {
    // Parse the command line arguments
    let args = Args::parse();

    println!("--- [PHASE 2] REBEL-6 RUST ENGINE ---");

    // Boot the Virtual Machine
    let cpu = Rebel6VM::new(args.compat, args.verbose);

    // Print the CPU status (This proves to the compiler that we are using the struct!)
    if cpu.verbosity >= 1 {
        println!("[*] CPU Initialized.");
        println!("    Compat Mode : {}", cpu.compat_mode);
        println!("    Verbosity   : {}", cpu.verbosity);
    }
}
