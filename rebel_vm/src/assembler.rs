// src/assembler.rs

use std::collections::HashMap;
use std::fs;

/// A structured representation of a single line of assembly
#[derive(Debug, Clone)]
pub struct ParsedInst {
  pub opcode: String,
  pub args: Vec<String>,
}

/// Translates ABI names to registers, and safely parses hex/decimal immediates.
/// Enforces standard 32-bit hardware boundaries.
pub fn normalize_arg(arg: &str) -> String {
  let arg = arg.trim();

  // 1. Translate ABI names (e.g., 'gp' -> 'x3')
  let mapped = match arg {
    "zero" => "x0", "ra" => "x1", "sp" => "x2", "gp" => "x3", "tp" => "x4",
    "t0" => "x5", "t1" => "x6", "t2" => "x7", "s0" | "fp" => "x8", "s1" => "x9",
    "a0" => "x10", "a1" => "x11", "a2" => "x12", "a3" => "x13", "a4" => "x14",
    "a5" => "x15", "a6" => "x16", "a7" => "x17", "s2" => "x18", "s3" => "x19",
    "s4" => "x20", "s5" => "x21", "s6" => "x22", "s7" => "x23", "s8" => "x24",
    "s9" => "x25", "s10" => "x26", "s11" => "x27", "t3" => "x28", "t4" => "x29",
    "t5" => "x30", "t6" => "x31",
    _ => arg,
  };

  // 2. Attempt to parse as an immediate number (handles "0x" hex and standard decimal)
  let parsed_num = if mapped.starts_with("0x") || mapped.starts_with("-0x") {
    let without_prefix = mapped.trim_start_matches('-').trim_start_matches("0x");
    i64::from_str_radix(without_prefix, 16)
      .map(|n| if mapped.starts_with('-') { -n } else { n })
  } else {
    mapped.parse::<i64>()
  };

  // 3. Apply 32-bit overflow boundaries or pass through strings (like labels)
  match parsed_num {
    Ok(mut num) => {
      if num >= 0x80000000 {
        num -= 0x100000000;
      }
      num.to_string()
    }
    Err(_) => mapped.to_string(), // If parsing fails, it's a register or label string
  }
}

/// Pass 1 (Parsing): Reads file, strips comments, handles directives, extracts labels.
pub fn parse_tas_file(filepath: &str) -> Result<(HashMap<String, usize>, Vec<ParsedInst>, HashMap<i32, String>), String> {
  let content = fs::read_to_string(filepath)
    .map_err(|e| format!("Assembler Failed: Could not read file '{}'. Error: {}", filepath, e))?;

  let mut labels = HashMap::new();
  let mut raw_insts = Vec::new();
  let mut initial_ram = HashMap::new(); // Store static variables here
  let mut pc_counter = 0;
  let mut ram_pointer = 8192;           // Start RAM at 0x2000 to avoid low-integer collisions
  let mut in_text_section = true;

  for line in content.lines() {
    let clean_line = line.split('#').next().unwrap_or("").trim();
    if clean_line.is_empty() { continue; }

    // --- DIRECTIVE HANDLING ---
    if clean_line.starts_with('.') {
      let directive = clean_line.split_whitespace().next().unwrap_or("");
      if directive == ".text" {
        in_text_section = true;
      } else if directive == ".data" || directive == ".rodata" || directive == ".bss" {
        in_text_section = false;
      } else if !in_text_section && directive == ".word" {
        // Parse .word directives into our RAM hashmap
        let parts: Vec<&str> = clean_line.split_whitespace().collect();
        if parts.len() > 1 {
          let val_str = normalize_arg(parts[1]);
          let val_int = val_str.parse::<i64>().unwrap_or(0);
          let mut ternary_val = int_to_ternary(val_int, 32).trim_start_matches('0').to_string();
          if ternary_val.is_empty() { ternary_val = "0".to_string(); }

          initial_ram.insert(ram_pointer, ternary_val);
          ram_pointer += 4; // Standard RISC-V byte-aligned addressing!
        }
      }
      continue;
    }

    // --- LABEL HANDLING ---
    if clean_line.ends_with(':') {
      let label_name = clean_line.trim_end_matches(':').to_string();
      if in_text_section {
        labels.insert(label_name, pc_counter); // Text labels map to PC
      } else {
        labels.insert(label_name, ram_pointer as usize); // Data labels map to RAM address
      }
      continue;
    }

    if !in_text_section { continue; }

    // --- INSTRUCTION TOKENIZATION ---
    let clean_commas = clean_line.replace(',', " ");
    let parts: Vec<&str> = clean_commas.split_whitespace().collect();
    if parts.is_empty() { continue; }

    let opcode = parts[0].to_string();
    let args: Vec<String> = parts[1..].iter().map(|&arg| normalize_arg(arg)).collect();

    raw_insts.push(ParsedInst { opcode, args });
    pc_counter += 1;
  }

  Ok((labels, raw_insts, initial_ram))
}

/// Matches an assembly mnemonic to its 5-trit REBEL-6 hardware opcode
pub fn get_opcode_trits(mnemonic: &str) -> Result<&'static str, String> {
  match mnemonic {
    "bne.t"  => Ok("-0+00"),
    "sw"     => Ok("++00+"),
    "slt"    => Ok("+--00"),
    "and"    => Ok("+0-0+"),
    "or"     => Ok("+0-+0"),
    "xor"    => Ok("+0-++"),
    "add"    => Ok("+0-00"),
    "sll"    => Ok("+0+00"),
    "srl"    => Ok("+0+0+"),
    "sra"    => Ok("+0++0"),
    "sub"    => Ok("+0--0"),
    "jal"    => Ok("-0000"),
    "jal.t"  => Ok("-000+"),
    "slti"   => Ok("+--0+"),
    "slti.t" => Ok("+--+0"),
    "slli"   => Ok("+0+-0"),
    "srli"   => Ok("+0+-+"),
    "srai"   => Ok("+0+--"),
    "andi"   => Ok("+00-+"),
    "ori"    => Ok("+00+0"),
    "xori"   => Ok("+00++"),
    "addi"   => Ok("+0000"),
    "addi.t" => Ok("+000+"),
    "li.t"   => Ok("++-00"),
    "lw"     => Ok("++000"),
    "jalr"   => Ok("-00+0"),
    "jalr.t" => Ok("-00++"),
    "ecall"  => Ok("00000"),
    _ => Err(format!("Unknown instruction '{}'", mnemonic)),
  }
}

/// Converts a base-10 integer into a balanced ternary string of a specific width
pub fn int_to_ternary(mut val: i64, width: usize) -> String {
  if val == 0 {
    return "0".repeat(width);
  }

  let mut trits = String::new();
  while val != 0 {
    let remainder = val % 3;
    val /= 3;

    match remainder {
      0 => trits.push('0'),
      1 | -2 => { trits.push('+'); if remainder == -2 { val -= 1; } },
      2 | -1 => { trits.push('-'); if remainder == 2 { val += 1; } },
      _ => unreachable!(),
    }
  }

  // The algorithm generates little-endian (backwards), so we reverse it
  let mut result: String = trits.chars().rev().collect();

  // Pad or truncate to fit the hardware bus width
  if result.len() > width {
    result = result[result.len() - width..].to_string(); // Truncate top trits (overflow)
  } else {
    let padding = "0".repeat(width - result.len());
    result = format!("{}{}", padding, result);
  }

  result
}

/// The Master Assembler function. Runs all three passes.
pub fn assemble(filepath: &str) -> Result<(Vec<String>, HashMap<i32, String>), String> {
  let (labels, mut parsed_insts, initial_ram) = parse_tas_file(filepath)?;

  // PASS 2: Label Substitution
  for (i, inst) in parsed_insts.iter_mut().enumerate() {
    // We must check the instruction format to know how to calculate the label address!
    let opcode_trits = get_opcode_trits(&inst.opcode).unwrap_or("");
    let format = crate::isa::decode_format(opcode_trits);

    for arg in inst.args.iter_mut() {
      if let Some(&target_addr) = labels.get(arg) {
        if format == crate::isa::Format::J || format == crate::isa::Format::B {
          // Relative PC offset for Jumps and Branches
          let offset = (target_addr as i64) - (i as i64);
          *arg = offset.to_string();
        } else {
          // Absolute RAM Address for Data Loads
          *arg = target_addr.to_string();
        }
      }
    }
  }

  // PASS 3: Code Emission
  let mut machine_code = Vec::new();
  for inst in parsed_insts {
    let opcode = get_opcode_trits(&inst.opcode)?;
    let mut emit = opcode.to_string();

    let format = crate::isa::decode_format(opcode);

    match format {
      crate::isa::Format::R => {
        emit.push_str(&int_to_ternary(inst.args.get(0).unwrap_or(&"x0".to_string())[1..].parse().unwrap_or(0), 4)); // rd
        emit.push_str(&int_to_ternary(inst.args.get(1).unwrap_or(&"x0".to_string())[1..].parse().unwrap_or(0), 4)); // rs1
        emit.push_str(&int_to_ternary(inst.args.get(2).unwrap_or(&"x0".to_string())[1..].parse().unwrap_or(0), 4)); // rs2
        emit.push_str(&"0".repeat(15)); // padding
      }
      crate::isa::Format::I => {
        emit.push_str(&int_to_ternary(inst.args.get(0).unwrap_or(&"x0".to_string())[1..].parse().unwrap_or(0), 4)); // rd
        emit.push_str(&int_to_ternary(inst.args.get(1).unwrap_or(&"x0".to_string())[1..].parse().unwrap_or(0), 4)); // rs1
        emit.push_str(&int_to_ternary(inst.args.get(2).unwrap_or(&"0".to_string()).parse().unwrap_or(0), 19));    // imm
      }
      crate::isa::Format::S | crate::isa::Format::B => {
        emit.push_str(&int_to_ternary(inst.args.get(0).unwrap_or(&"x0".to_string())[1..].parse().unwrap_or(0), 4)); // rs1
        emit.push_str(&int_to_ternary(inst.args.get(1).unwrap_or(&"x0".to_string())[1..].parse().unwrap_or(0), 4)); // rs2
        emit.push_str(&int_to_ternary(inst.args.get(2).unwrap_or(&"0".to_string()).parse().unwrap_or(0), 19));    // imm
      }
      crate::isa::Format::J | crate::isa::Format::LI => {
        emit.push_str(&int_to_ternary(inst.args.get(0).unwrap_or(&"x0".to_string())[1..].parse().unwrap_or(0), 4)); // rd
        emit.push_str(&int_to_ternary(inst.args.get(1).unwrap_or(&"0".to_string()).parse().unwrap_or(0), 23));    // imm
      }
      crate::isa::Format::SYS => {
        emit.push_str(&"0".repeat(27)); // padding
      }
      crate::isa::Format::UNKNOWN => {
        return Err(format!("Compilation failed. Unknown hardware format for {}", inst.opcode));
      }
    }

    machine_code.push(emit);
  }

  Ok((machine_code, initial_ram))
}
