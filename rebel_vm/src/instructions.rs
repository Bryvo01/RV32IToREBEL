// src/instructions.rs

use crate::vm::Rebel6VM;
use crate::isa::DecodedInstruction;
use crate::assembler::int_to_ternary;

/// Helper function: Converts a balanced ternary string back to a standard integer
pub fn ternary_to_int(trits: &str) -> i64 {
  let mut val: i64 = 0;
  // Iterate backwards (little-endian powers)
  for (i, c) in trits.chars().rev().enumerate() {
    let power = 3_i64.pow(i as u32);
    match c {
      '+' => val += power,
      '-' => val -= power,
      _ => {} // '0' adds nothing
    }
  }
  val
}

/// The Execution Stage: Routes the decoded hardware signals to the ALU / Memory
pub fn execute(cpu: &mut Rebel6VM, decoded: &DecodedInstruction) {
  let opcode = decoded.opcode_trits.as_str();

  // Safely extract the parsed integer values from our hardware slices as i64
  let rd_idx = ternary_to_int(decoded.rd.as_deref().unwrap_or("0")) as usize;
  let rs1_idx = ternary_to_int(decoded.rs1.as_deref().unwrap_or("0")) as usize;
  let rs2_idx = ternary_to_int(decoded.rs2.as_deref().unwrap_or("0")) as usize;
  let imm_val = ternary_to_int(decoded.imm.as_deref().unwrap_or("0"));

  match opcode {
    "++-00" => { // li.t (Load Immediate Ternary)
      if rd_idx != 0 {
        // Strip leading zeros for a cleaner string state
        let imm_str = decoded.imm.as_deref().unwrap_or("0");
        let mut clean_imm = imm_str.trim_start_matches('0').to_string();
        if clean_imm.is_empty() { clean_imm = "0".to_string(); }
        cpu.registers[rd_idx] = clean_imm;
      }
    }
    "++00+" => { // sw (Store Word)
      let base_addr = ternary_to_int(&cpu.registers[rs1_idx]);
      let target_addr = (base_addr + imm_val) as i32; // Cast down to i32 for RAM keys
      let data = cpu.registers[rs2_idx].clone();
      cpu.ram.insert(target_addr, data);
    }
    "++000" => { // lw (Load Word)
      if rd_idx != 0 {
        let base_addr = ternary_to_int(&cpu.registers[rs1_idx]);
        let target_addr = (base_addr + imm_val) as i32;
        // Default to "0" if RAM address is uninitialized
        let data = cpu.ram.get(&target_addr).cloned().unwrap_or_else(|| "0".to_string());
        cpu.registers[rd_idx] = data;
      }
    }
    "+0+-0" => { // slli (Shift Left Logical Immediate)
      if rd_idx != 0 {
        let val1 = ternary_to_int(&cpu.registers[rs1_idx]);
        let shamt = imm_val & 0x1F; // Strict 5-bit mask
        let result = val1 << shamt;

        // Pack it back into a 32-trit string, stripping zeros for readability.
        let mut ternary_result = int_to_ternary(result, 32).trim_start_matches('0').to_string();
        if ternary_result.is_empty() { ternary_result = "0".to_string(); }
        cpu.registers[rd_idx] = ternary_result;
      }
    }
    "+--0+" => { // slti (Set Less Than Immediate)
      if rd_idx != 0 {
        let val1 = ternary_to_int(&cpu.registers[rs1_idx]);
        let result = if val1 < imm_val { 1 } else { 0 };
        cpu.registers[rd_idx] = if result == 1 { "+".to_string() } else { "0".to_string() };
      }
    }
    "-0+00" => { // bne.t (Branch Not Equal)
      let val1 = ternary_to_int(&cpu.registers[rs1_idx]);
      let val2 = ternary_to_int(&cpu.registers[rs2_idx]);
      if val1 != val2 {
        cpu.pc = ((cpu.pc as i64 - 1) + imm_val) as usize;
      }
    }
    "-0000" => { // jal (Jump and Link)
      if rd_idx != 0 {
        let mut ternary_pc = int_to_ternary(cpu.pc as i64, 32).trim_start_matches('0').to_string();
        if ternary_pc.is_empty() { ternary_pc = "0".to_string(); }
        cpu.registers[rd_idx] = ternary_pc;
      }
      cpu.pc = ((cpu.pc as i64 - 1) + imm_val) as usize;
    }
    "+0-00" => { // add
      if rd_idx != 0 {
        let val1 = ternary_to_int(&cpu.registers[rs1_idx]);
        let val2 = ternary_to_int(&cpu.registers[rs2_idx]);
        let mut result = val1 + val2;

        // Artificially enforce 32-bit integer overflow for standard RISC-V tests
        if cpu.compat_mode {
          result = ((result + 0x80000000) % 0x100000000) - 0x80000000;
        }

        let mut ternary_result = int_to_ternary(result, 32).trim_start_matches('0').to_string();
        if ternary_result.is_empty() { ternary_result = "0".to_string(); }
        cpu.registers[rd_idx] = ternary_result;
      }
    }
    "+0000" | "+000+" => { // addi & addi.t
      if rd_idx != 0 {
        let val1 = ternary_to_int(&cpu.registers[rs1_idx]);
        let mut result = val1 + imm_val;

        if cpu.compat_mode {
          result = ((result + 0x80000000) % 0x100000000) - 0x80000000;
        }

        let mut ternary_result = int_to_ternary(result, 32).trim_start_matches('0').to_string();
        if ternary_result.is_empty() { ternary_result = "0".to_string(); }
        cpu.registers[rd_idx] = ternary_result;
      }
    }
    "00000" => { // ecall (System Call / Halt)
      cpu.running = false;
    }
    _ => {
      if cpu.verbosity >= 1 {
        println!("[!] ALU Error: Unimplemented instruction execution for opcode '{}'", opcode);
      }
    }
  }
}
