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

  // Boot the Virtual Machine (Notice the 'mut' keyword!)
  let mut cpu = Rebel6VM::new(args.compat, args.verbose);

  if cpu.verbosity >= 1 {
    println!("[*] CPU Initialized.");
    println!("    Compat Mode : {}", cpu.compat_mode);
    println!("    Verbosity   : {}", cpu.verbosity);
  }

  // --- RUN THE ASSEMBLER ---
  let program = match assembler::assemble(&args.file) {
    Ok(code) => code,
    Err(e) => {
      eprintln!("Fatal Error: {}", e);
      std::process::exit(1);
    }
  };

  cpu.load_program(program);
  cpu.running = true;

  println!("\nStarting CPU Execution Loop...\n");

  while cpu.running {
    if cpu.verbosity >= 1 {
      println!("--- PC: {} ---", cpu.pc);
    }

    // STAGE 1: FETCH
    let current_inst = cpu.fetch();

    if cpu.verbosity >= 3 {
      println!("Fetched 32-Trit String: {}", current_inst);
    }

    // STAGE 2: DECODE
    let decoded_signals = cpu.decode(&current_inst);

    // STAGE 3: EXECUTE
    crate::instructions::execute(&mut cpu, &decoded_signals);
  }

  // Print the final state
  cpu.dump_registers();
}
