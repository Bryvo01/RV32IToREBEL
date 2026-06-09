// src/vm.rs

use std::collections::HashMap;
use crate::isa::{decode_format, DecodedInstruction, Format};

/// The main CPU Core for the REBEL-6 Virtual Machine
pub struct Rebel6VM {
    pub pc: usize,
    pub registers: [String; 32],
    pub memory: Vec<String>,       // Read-Only Memory (Instruction ROM)
    pub ram: HashMap<i32, String>, // Read/Write Memory (Variables)
    pub running: bool,
    pub compat_mode: bool,
    pub verbosity: u8,
}

impl Rebel6VM {
    /// Boot up a new CPU instance
    pub fn new(compat_mode: bool, verbosity: u8) -> Self {
        // Initialize an array of 32 strings, all set to "0"
        let registers: [String; 32] = core::array::from_fn(|_| String::from("0"));

        Self {
            pc: 0,
            registers,
            memory: Vec::new(),
            ram: HashMap::new(),
            running: false,
            compat_mode,
            verbosity,
        }
    }

    /// Load a compiled program into ROM
    pub fn load_program(&mut self, machine_code: Vec<String>) {
        self.memory = machine_code;
        if self.verbosity >= 1 {
            println!("[*] Loaded {} instructions into ROM.", self.memory.len());
        }
    }

    /// STAGE 1: FETCH
    pub fn fetch(&mut self) -> String {
        if self.pc >= self.memory.len() {
            self.running = false;
            return String::from("00000"); // ecall to safely halt
        }

        let inst = self.memory[self.pc].clone();
        self.pc += 1;
        inst
    }

    /// STAGE 2: DECODE (Placeholder)
    pub fn decode(&self, instruction: &str) -> DecodedInstruction {
        // We will implement the exact trit-slicing logic here next!
        let opcode = &instruction[0..5];
        let format = decode_format(opcode);

        DecodedInstruction {
            format,
            opcode_trits: opcode.to_string(),
            ..Default::default()
        }
    }
}
