// src/isa.rs

/// Represents the physical wiring formats of the REBEL-6 Architecture
#[derive(Debug, PartialEq, Clone, Copy, Default)]
pub enum Format {
  R,   // Register-to-Register
  LI,  // Load Immediate
  I,   // Immediate
  S,   // Store
  B,   // Branch
  J,   // Jump
  SYS, // System / Environment Calls
  #[default]
  UNKNOWN,
}

/// A data struct holding the sliced components of an instruction
#[derive(Debug, Default)]
pub struct DecodedInstruction {
  pub format: Format,
  pub opcode_trits: String,
  pub rd: Option<String>,
  pub rs1: Option<String>,
  pub rs2: Option<String>,
  pub imm: Option<String>,
}

/// Hardware Control ROM: Maps a 5-trit opcode to its physical wiring format.
/// This replaces the Python CONTROL_ROM dictionary with compile-time mapping.
pub fn decode_format(trit_code: &str) -> Format {
  match trit_code {
    // R-Type: add, sll, srl, sra, sub, and, or, xor, slt
    "+0-00" | "+0+00" | "+0+0+" | "+0++0" | "+0--0" |
    "+0-0+" | "+0-+0" | "+0-++" | "+--00" => Format::R,

    // I-Type: addi, addi.t, lw, slli, srli, srai, andi, ori, xori, slti, slti.t, jalr, jalr.t
    "+0000" | "+000+" | "++000" | "+0+-0" | "+0+-+" | "+0+--" |
    "+00-+" | "+00+0" | "+00++" | "+--0+" | "+--+0" | "-00+0" | "-00++" => Format::I,

    // LI-Type: li.t
    "++-00" => Format::LI,

    // S-Type: sw
    "++00+" => Format::S,

    // B-Type: bne.t
    "-0+00" => Format::B,

    // J-Type: jal, jal.t
    "-0000" | "-000+" => Format::J,

    // SYS-Type: ecall
    "00000" => Format::SYS,

    _ => Format::UNKNOWN,
  }
}
