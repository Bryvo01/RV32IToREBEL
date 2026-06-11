// src/instructions.rs

use crate::vm::Rebel6VM;
use crate::isa::{DecodedInstruction, Format};
use crate::assembler::int_to_ternary;

/// Helper function: Converts a balanced ternary string back to a standard integer
pub fn ternary_to_int(trits: &str) -> i64 {
  let mut val: i64 = 0;
  for (i, c) in trits.chars().rev().enumerate() {
    let power = 3_i64.pow(i as u32);
    match c {
      '+' => val += power,
      '-' => val -= power,
      _ => {}
    }
  }
  val
}

/// The Execution Stage: Routes the decoded hardware signals based on Format
pub fn execute(cpu: &mut Rebel6VM, decoded: &DecodedInstruction) {
  match decoded.format {
    Format::R   => execute_r_type(cpu, decoded),
    Format::I   => execute_i_type(cpu, decoded),
    Format::S   => execute_s_type(cpu, decoded),
    Format::B   => execute_b_type(cpu, decoded),
    Format::J   => execute_j_type(cpu, decoded),
    Format::LI  => execute_li_type(cpu, decoded),
    Format::SYS => execute_sys_type(cpu, decoded),
    Format::UNKNOWN => {
      if cpu.verbosity >= 1 {
        println!("[!] ALU Error: Unknown hardware format for opcode '{}'", decoded.opcode_trits);
      }
    }
  }
}

// ----------------------------------------------------------------------
// FORMAT-SPECIFIC EXECUTION BLOCKS
// ----------------------------------------------------------------------

fn execute_r_type(cpu: &mut Rebel6VM, decoded: &DecodedInstruction) {
  let rd_idx = ternary_to_int(decoded.rd.as_deref().unwrap_or("0")) as usize;
  let rs1_idx = ternary_to_int(decoded.rs1.as_deref().unwrap_or("0")) as usize;
  let rs2_idx = ternary_to_int(decoded.rs2.as_deref().unwrap_or("0")) as usize;

  if rd_idx == 0 { return; } // x0 is strictly read-only

  let val1 = ternary_to_int(&cpu.registers[rs1_idx]);
  let val2 = ternary_to_int(&cpu.registers[rs2_idx]);

  match decoded.opcode_trits.as_str() {
    "+0-00" => { // add
      let mut result = val1 + val2;
      if cpu.compat_mode { result = result as i32 as i64; } // 32-bit hardware wrapping

      if cpu.verbosity >= 2 {
        println!("      [ALU] add x{} = {} + {} -> {}", rd_idx, val1, val2, result);
      }

      let mut ternary_result = int_to_ternary(result, 32).trim_start_matches('0').to_string();
      if ternary_result.is_empty() { ternary_result = "0".to_string(); }
      cpu.registers[rd_idx] = ternary_result;
    }
    "+0-0+" => { // and
      let result = ((val1 as i32) & (val2 as i32)) as i64;
      if cpu.verbosity >= 2 { println!("      [ALU] and x{} = {} & {} -> {}", rd_idx, val1, val2, result); }
      let mut ternary_result = int_to_ternary(result, 32).trim_start_matches('0').to_string();
      if ternary_result.is_empty() { ternary_result = "0".to_string(); }
      cpu.registers[rd_idx] = ternary_result;
    }
    "+0-+0" => { // or
      let result = ((val1 as i32) | (val2 as i32)) as i64;
      if cpu.verbosity >= 2 { println!("      [ALU] or x{} = {} | {} -> {}", rd_idx, val1, val2, result); }
      let mut ternary_result = int_to_ternary(result, 32).trim_start_matches('0').to_string();
      if ternary_result.is_empty() { ternary_result = "0".to_string(); }
      cpu.registers[rd_idx] = ternary_result;
    }
    "+0-++" => { // xor
      let result = ((val1 as i32) ^ (val2 as i32)) as i64;
      if cpu.verbosity >= 2 { println!("      [ALU] xor x{} = {} ^ {} -> {}", rd_idx, val1, val2, result); }
      let mut ternary_result = int_to_ternary(result, 32).trim_start_matches('0').to_string();
      if ternary_result.is_empty() { ternary_result = "0".to_string(); }
      cpu.registers[rd_idx] = ternary_result;
    }
    "+0--0" => { // sub
      let mut result = val1 - val2;
      if cpu.compat_mode { result = result as i32 as i64; }
      if cpu.verbosity >= 2 { println!("      [ALU] sub x{} = {} - {} -> {}", rd_idx, val1, val2, result); }
      let mut ternary_result = int_to_ternary(result, 32).trim_start_matches('0').to_string();
      if ternary_result.is_empty() { ternary_result = "0".to_string(); }
      cpu.registers[rd_idx] = ternary_result;
    }
    "+0+00" => { // sll
      let shamt = val2 & 0x1F;
      let mut result = val1 << shamt;
      if cpu.compat_mode { result = result as i32 as i64; }
      if cpu.verbosity >= 2 { println!("      [ALU] sll x{} = {} << {} -> {}", rd_idx, val1, shamt, result); }
      let mut ternary_result = int_to_ternary(result, 32).trim_start_matches('0').to_string();
      if ternary_result.is_empty() { ternary_result = "0".to_string(); }
      cpu.registers[rd_idx] = ternary_result;
    }
    "+0+0+" => { // srl
      let shamt = val2 & 0x1F;
      let result = ((val1 as u32) >> shamt) as i64; // u32 enforces Logical shift (zero-fill)
      if cpu.verbosity >= 2 { println!("      [ALU] srl x{} = {} >> {} -> {}", rd_idx, val1, shamt, result); }
      let mut ternary_result = int_to_ternary(result, 32).trim_start_matches('0').to_string();
      if ternary_result.is_empty() { ternary_result = "0".to_string(); }
      cpu.registers[rd_idx] = ternary_result;
    }
    "+0++0" => { // sra
      let shamt = val2 & 0x1F;
      let result = ((val1 as i32) >> shamt) as i64; // i32 enforces Arithmetic shift (sign-extension)
      if cpu.verbosity >= 2 { println!("      [ALU] sra x{} = {} >> {} -> {}", rd_idx, val1, shamt, result); }
      let mut ternary_result = int_to_ternary(result, 32).trim_start_matches('0').to_string();
      if ternary_result.is_empty() { ternary_result = "0".to_string(); }
      cpu.registers[rd_idx] = ternary_result;
    }
    "+--00" => { // slt
      let result = if val1 < val2 { 1 } else { 0 };
      if cpu.verbosity >= 2 { println!("      [ALU] slt x{} = ({} < {}) -> {}", rd_idx, val1, val2, result); }
      cpu.registers[rd_idx] = if result == 1 { "+".to_string() } else { "0".to_string() };
    }
    _ => println!("[!] Unimplemented R-Type opcode: {}", decoded.opcode_trits),
  }
}

fn execute_i_type(cpu: &mut Rebel6VM, decoded: &DecodedInstruction) {
  let rd_idx = ternary_to_int(decoded.rd.as_deref().unwrap_or("0")) as usize;
  let rs1_idx = ternary_to_int(decoded.rs1.as_deref().unwrap_or("0")) as usize;
  let imm_val = ternary_to_int(decoded.imm.as_deref().unwrap_or("0"));

  if rd_idx == 0 { return; }

  let val1 = ternary_to_int(&cpu.registers[rs1_idx]);

  match decoded.opcode_trits.as_str() {
    "+0000" | "+000+" => { // addi & addi.t
      let mut result = val1 + imm_val;
      if cpu.compat_mode { result = result as i32 as i64; }

      if cpu.verbosity >= 2 {
        println!("      [ALU] addi x{} = {} + {} -> {}", rd_idx, val1, imm_val, result);
      }

      let mut ternary_result = int_to_ternary(result, 32).trim_start_matches('0').to_string();
      if ternary_result.is_empty() { ternary_result = "0".to_string(); }
      cpu.registers[rd_idx] = ternary_result;
    }
    "++000" => { // lw
      let target_addr = (val1 + imm_val) as i32;
      let data = cpu.ram.get(&target_addr).cloned().unwrap_or_else(|| "0".to_string());

      if cpu.verbosity >= 2 {
        println!("      [MEM] lw x{} <- RAM[{}] (val: {})", rd_idx, target_addr, data);
      }
      cpu.registers[rd_idx] = data;
    }
    "+0+-0" => { // slli
      let shamt = imm_val & 0x1F;
      let mut result = val1 << shamt;
      if cpu.compat_mode { result = result as i32 as i64; }

      if cpu.verbosity >= 2 {
        println!("      [ALU] slli x{} = {} << {} -> {}", rd_idx, val1, shamt, result);
      }

      let mut ternary_result = int_to_ternary(result, 32).trim_start_matches('0').to_string();
      if ternary_result.is_empty() { ternary_result = "0".to_string(); }
      cpu.registers[rd_idx] = ternary_result;
    }
    "+--0+" => { // slti
      let result = if val1 < imm_val { 1 } else { 0 };
      if cpu.verbosity >= 2 {
        println!("      [ALU] slti x{} = ({} < {}) -> {}", rd_idx, val1, imm_val, result);
      }
      cpu.registers[rd_idx] = if result == 1 { "+".to_string() } else { "0".to_string() };
    }
    "+00-+" => { // andi
      let result = ((val1 as i32) & (imm_val as i32)) as i64;
      if cpu.verbosity >= 2 { println!("      [ALU] andi x{} = {} & {} -> {}", rd_idx, val1, imm_val, result); }
      let mut ternary_result = int_to_ternary(result, 32).trim_start_matches('0').to_string();
      if ternary_result.is_empty() { ternary_result = "0".to_string(); }
      cpu.registers[rd_idx] = ternary_result;
    }
    "+00+0" => { // ori
      let result = ((val1 as i32) | (imm_val as i32)) as i64;
      if cpu.verbosity >= 2 { println!("      [ALU] ori x{} = {} | {} -> {}", rd_idx, val1, imm_val, result); }
      let mut ternary_result = int_to_ternary(result, 32).trim_start_matches('0').to_string();
      if ternary_result.is_empty() { ternary_result = "0".to_string(); }
      cpu.registers[rd_idx] = ternary_result;
    }
    "+00++" => { // xori
      let result = ((val1 as i32) ^ (imm_val as i32)) as i64;
      if cpu.verbosity >= 2 { println!("      [ALU] xori x{} = {} ^ {} -> {}", rd_idx, val1, imm_val, result); }
      let mut ternary_result = int_to_ternary(result, 32).trim_start_matches('0').to_string();
      if ternary_result.is_empty() { ternary_result = "0".to_string(); }
      cpu.registers[rd_idx] = ternary_result;
    }
    "+0+-+" => { // srli
      let shamt = imm_val & 0x1F;
      let result = ((val1 as u32) >> shamt) as i64;
      if cpu.verbosity >= 2 { println!("      [ALU] srli x{} = {} >> {} -> {}", rd_idx, val1, shamt, result); }
      let mut ternary_result = int_to_ternary(result, 32).trim_start_matches('0').to_string();
      if ternary_result.is_empty() { ternary_result = "0".to_string(); }
      cpu.registers[rd_idx] = ternary_result;
    }
    "+0+--" => { // srai
      let shamt = imm_val & 0x1F;
      let result = ((val1 as i32) >> shamt) as i64;
      if cpu.verbosity >= 2 { println!("      [ALU] srai x{} = {} >> {} -> {}", rd_idx, val1, shamt, result); }
      let mut ternary_result = int_to_ternary(result, 32).trim_start_matches('0').to_string();
      if ternary_result.is_empty() { ternary_result = "0".to_string(); }
      cpu.registers[rd_idx] = ternary_result;
    }
    _ => println!("[!] Unimplemented I-Type opcode: {}", decoded.opcode_trits),
  }
}

fn execute_s_type(cpu: &mut Rebel6VM, decoded: &DecodedInstruction) {
  let rs1_idx = ternary_to_int(decoded.rs1.as_deref().unwrap_or("0")) as usize;
  let rs2_idx = ternary_to_int(decoded.rs2.as_deref().unwrap_or("0")) as usize;
  let imm_val = ternary_to_int(decoded.imm.as_deref().unwrap_or("0"));

  let base_addr = ternary_to_int(&cpu.registers[rs1_idx]);

  match decoded.opcode_trits.as_str() {
    "++00+" => { // sw
      let target_addr = (base_addr + imm_val) as i32;
      let data = cpu.registers[rs2_idx].clone();
      if cpu.verbosity >= 2 {
        println!("      [MEM] sw RAM[{}] <- x{} (val: {})", target_addr, rs2_idx, data);
      }
      cpu.ram.insert(target_addr, data);
    }
    _ => println!("[!] Unimplemented S-Type opcode: {}", decoded.opcode_trits),
  }
}

fn execute_b_type(cpu: &mut Rebel6VM, decoded: &DecodedInstruction) {
  let rs1_idx = ternary_to_int(decoded.rs1.as_deref().unwrap_or("0")) as usize;
  let rs2_idx = ternary_to_int(decoded.rs2.as_deref().unwrap_or("0")) as usize;
  let imm_val = ternary_to_int(decoded.imm.as_deref().unwrap_or("0"));

  let val1 = ternary_to_int(&cpu.registers[rs1_idx]);
  let val2 = ternary_to_int(&cpu.registers[rs2_idx]);

  match decoded.opcode_trits.as_str() {
    "-0+00" => { // bne.t
      let branch_taken = val1 != val2;
      if cpu.verbosity >= 2 {
        println!("      [ALU] bne.t ({} != {}) -> Taken: {}", val1, val2, branch_taken);
      }
      if branch_taken {
        cpu.pc = ((cpu.pc as i64 - 1) + imm_val) as usize;
      }
    }
    _ => println!("[!] Unimplemented B-Type opcode: {}", decoded.opcode_trits),
  }
}

fn execute_j_type(cpu: &mut Rebel6VM, decoded: &DecodedInstruction) {
  let rd_idx = ternary_to_int(decoded.rd.as_deref().unwrap_or("0")) as usize;
  let imm_val = ternary_to_int(decoded.imm.as_deref().unwrap_or("0"));

  match decoded.opcode_trits.as_str() {
    "-0000" | "-000+" => { // jal & jal.t
      if rd_idx != 0 {
        let mut ternary_pc = int_to_ternary(cpu.pc as i64, 32).trim_start_matches('0').to_string();
        if ternary_pc.is_empty() { ternary_pc = "0".to_string(); }
        cpu.registers[rd_idx] = ternary_pc;
      }
      if cpu.verbosity >= 2 {
        println!("      [ALU] jal -> jumping by offset {}", imm_val);
      }
      cpu.pc = ((cpu.pc as i64 - 1) + imm_val) as usize;
    }
    _ => println!("[!] Unimplemented J-Type opcode: {}", decoded.opcode_trits),
  }
}

fn execute_li_type(cpu: &mut Rebel6VM, decoded: &DecodedInstruction) {
  let rd_idx = ternary_to_int(decoded.rd.as_deref().unwrap_or("0")) as usize;

  if rd_idx != 0 {
    match decoded.opcode_trits.as_str() {
      "++-00" => { // li.t
        let imm_str = decoded.imm.as_deref().unwrap_or("0");
        let mut clean_imm = imm_str.trim_start_matches('0').to_string();
        if clean_imm.is_empty() { clean_imm = "0".to_string(); }

        if cpu.verbosity >= 2 {
          let imm_val = ternary_to_int(&clean_imm);
          println!("      [ALU] li.t x{} <- {}", rd_idx, imm_val);
        }

        cpu.registers[rd_idx] = clean_imm;
      }
      _ => println!("[!] Unimplemented LI-Type opcode: {}", decoded.opcode_trits),
    }
  }
}

fn execute_sys_type(cpu: &mut Rebel6VM, decoded: &DecodedInstruction) {
  match decoded.opcode_trits.as_str() {
    "00000" => { // ecall
      cpu.running = false;
      let x10_val = ternary_to_int(&cpu.registers[10]);
      if x10_val == 0 {
        println!("\n[✓] ECALL: TEST PASSED! (x10 = 0)");
      } else {
        println!("\n[✗] ECALL: TEST FAILED! (Test Case #{} Failed)", x10_val);
      }
    }
    _ => println!("[!] Unimplemented SYS-Type opcode: {}", decoded.opcode_trits),
  }
}
