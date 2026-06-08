# Python-Tools/Assembler/instructions.py

def execute_lit(cpu, decoded: dict) -> None:
  """Load Immediate Ternary (li.t)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  if rd_num != 0:
    clean_imm = decoded['imm'].lstrip('0')
    if not clean_imm: clean_imm = '0'
    cpu.registers[f'x{rd_num}'] = clean_imm
    print(f"[Execute] Loaded '{clean_imm}' into x{rd_num}")

def execute_add(cpu, decoded: dict) -> None:
  """Add Register to Register (add)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  rs1_num = cpu.ternary_to_int(decoded['rs1'])
  rs2_num = cpu.ternary_to_int(decoded['rs2'])

  if rd_num != 0:
    val1 = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
    val2 = cpu.ternary_to_int(cpu.registers[f'x{rs2_num}'])

    result = val1 + val2
    ternary_result = cpu.int_to_ternary(result)

    cpu.registers[f'x{rd_num}'] = ternary_result
    print(f"[Execute] ADD: x{rs1_num}({val1}) + x{rs2_num}({val2}) = {result} ('{ternary_result}') -> x{rd_num}")

def execute_bne_t(cpu, decoded: dict) -> None:
  """Branch Not Equal (bne.t)"""
  rs1_num = cpu.ternary_to_int(decoded['rs1'])
  rs2_num = cpu.ternary_to_int(decoded['rs2'])
  offset = cpu.ternary_to_int(decoded['imm'])

  val1 = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
  val2 = cpu.ternary_to_int(cpu.registers[f'x{rs2_num}'])

  if val1 != val2:
    original_pc = cpu.pc - 1
    cpu.pc = original_pc + offset
    print(f"[Execute] BNE.T: {val1} != {val2}. Branching to PC {cpu.pc}")
  else:
    print(f"[Execute] BNE.T: {val1} == {val2}. No branch taken.")

def execute_ecall(cpu, decoded: dict) -> None:
  """System Halt (ecall)"""
  print('[Execute] ECALL: Halting CPU.')
  cpu.running = False


# ---------------------------------------------------
# The Dispatch Table: Maps Opcode Signatures to Functions
# ---------------------------------------------------
INSTRUCTION_SET = {
  '++-00': execute_lit,
  '+0-00': execute_add,
  '-0+00': execute_bne_t,
  '00000': execute_ecall
}
