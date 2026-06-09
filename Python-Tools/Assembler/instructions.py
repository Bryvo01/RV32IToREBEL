# Python-Tools/Assembler/instructions.py

def execute_lit(cpu, decoded: dict) -> None:
  """Load Immediate Ternary (li.t)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  if rd_num != 0:
    clean_imm = decoded['imm'].lstrip('0')
    if not clean_imm: clean_imm = '0'
    cpu.registers[f'x{rd_num}'] = clean_imm
    if cpu.verbosity >=2:
      print(f"[Execute] Loaded '{clean_imm}' into x{rd_num}")

def execute_and(cpu, decoded: dict) -> None:
  """Bitwise AND (and)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  rs1_num = cpu.ternary_to_int(decoded['rs1'])
  rs2_num = cpu.ternary_to_int(decoded['rs2'])

  if rd_num != 0:
    val1 = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
    val2 = cpu.ternary_to_int(cpu.registers[f'x{rs2_num}'])

    result = val1 & val2
    if cpu.compat_mode:
      result = (result + 0x80000000) % 0x100000000 - 0x80000000

    ternary_result = cpu.int_to_ternary(result)
    cpu.registers[f'x{rd_num}'] = ternary_result

    if cpu.verbosity >=2:
      print(f"[Execute] AND: x{rs1_num}({val1}) & x{rs2_num}({val2}) = {result} ('{ternary_result}') -> x{rd_num}")

def execute_or(cpu, decoded: dict) -> None:
  """Bitwise OR (or)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  rs1_num = cpu.ternary_to_int(decoded['rs1'])
  rs2_num = cpu.ternary_to_int(decoded['rs2'])

  if rd_num != 0:
    val1 = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
    val2 = cpu.ternary_to_int(cpu.registers[f'x{rs2_num}'])

    result = val1 | val2
    if cpu.compat_mode:
      result = (result + 0x80000000) % 0x100000000 - 0x80000000

    ternary_result = cpu.int_to_ternary(result)
    cpu.registers[f'x{rd_num}'] = ternary_result

    if cpu.verbosity >=2:
      print(f"[Execute] OR: x{rs1_num}({val1}) | x{rs2_num}({val2}) = {result} ('{ternary_result}') -> x{rd_num}")

def execute_xor(cpu, decoded: dict) -> None:
  """Bitwise xor (xor)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  rs1_num = cpu.ternary_to_int(decoded['rs1'])
  rs2_num = cpu.ternary_to_int(decoded['rs2'])

  if rd_num != 0:
    val1 = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
    val2 = cpu.ternary_to_int(cpu.registers[f'x{rs2_num}'])

    result = val1 ^ val2
    if cpu.compat_mode:
      result = (result + 0x80000000) % 0x100000000 - 0x80000000

    ternary_result = cpu.int_to_ternary(result)
    cpu.registers[f'x{rd_num}'] = ternary_result

    if cpu.verbosity >=2:
      print(f"[Execute] XOR: x{rs1_num}({val1}) ^ x{rs2_num}({val2}) = {result} ('{ternary_result}') -> x{rd_num}")


def execute_add(cpu, decoded: dict) -> None:
  """Add Register to Register (add)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  rs1_num = cpu.ternary_to_int(decoded['rs1'])
  rs2_num = cpu.ternary_to_int(decoded['rs2'])

  if rd_num != 0:
    val1 = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
    val2 = cpu.ternary_to_int(cpu.registers[f'x{rs2_num}'])

    result = val1 + val2
    if cpu.compat_mode:
      result = (result + 0x80000000) % 0x100000000 - 0x80000000

    ternary_result = cpu.int_to_ternary(result)
    cpu.registers[f'x{rd_num}'] = ternary_result

    if cpu.verbosity >=2:
      print(f"[Execute] ADD: x{rs1_num}({val1}) + x{rs2_num}({val2}) = {result} ('{ternary_result}') -> x{rd_num}")

def execute_sll(cpu, decoded: dict) -> None:
  """Shift Left Logical (sll)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  rs1_num = cpu.ternary_to_int(decoded['rs1'])
  rs2_num = cpu.ternary_to_int(decoded['rs2'])

  if rd_num != 0:
    val1 = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
    val2 = cpu.ternary_to_int(cpu.registers[f'x{rs2_num}'])

    shamt = val2 & 0x1F  # Only use bottom 5 bits
    result = val1 << shamt

    if cpu.compat_mode:
      result = (result + 0x80000000) % 0x100000000 - 0x80000000

    ternary_result = cpu.int_to_ternary(result)
    cpu.registers[f'x{rd_num}'] = ternary_result

    if cpu.verbosity >= 2:
      print(f"[Execute] SLL: x{rs1_num}({val1}) << {shamt} = {result} ('{ternary_result}') -> x{rd_num}")

def execute_srl(cpu, decoded: dict) -> None:
  """Shift Right Logical (srl)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  rs1_num = cpu.ternary_to_int(decoded['rs1'])
  rs2_num = cpu.ternary_to_int(decoded['rs2'])

  if rd_num != 0:
    val1 = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
    val2 = cpu.ternary_to_int(cpu.registers[f'x{rs2_num}'])

    shamt = val2 & 0x1F
    # Mask val1 to 32-bit unsigned before shifting, so 1s don't carry over
    result = (val1 & 0xFFFFFFFF) >> shamt

    if cpu.compat_mode:
      result = (result + 0x80000000) % 0x100000000 - 0x80000000

    ternary_result = cpu.int_to_ternary(result)
    cpu.registers[f'x{rd_num}'] = ternary_result

    if cpu.verbosity >= 2:
      print(f"[Execute] SRL: x{rs1_num}({val1}) >> {shamt} (logical) = {result} ('{ternary_result}') -> x{rd_num}")

def execute_sra(cpu, decoded: dict) -> None:
  """Shift Right Arithmetic (sra)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  rs1_num = cpu.ternary_to_int(decoded['rs1'])
  rs2_num = cpu.ternary_to_int(decoded['rs2'])

  if rd_num != 0:
    val1 = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
    val2 = cpu.ternary_to_int(cpu.registers[f'x{rs2_num}'])

    shamt = val2 & 0x1F
    # Python natively preserves the sign bit on >>
    result = val1 >> shamt

    if cpu.compat_mode:
      result = (result + 0x80000000) % 0x100000000 - 0x80000000

    ternary_result = cpu.int_to_ternary(result)
    cpu.registers[f'x{rd_num}'] = ternary_result

    if cpu.verbosity >= 2:
      print(f"[Execute] SRA: x{rs1_num}({val1}) >> {shamt} (arithmetic) = {result} ('{ternary_result}') -> x{rd_num}")

def execute_andi(cpu, decoded: dict) -> None:
  """Bitwise AND Immediate (andi)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  rs1_num = cpu.ternary_to_int(decoded['rs1'])
  imm_val = cpu.ternary_to_int(decoded['imm'])

  if rd_num != 0:
    val1 = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
    result = val1 & imm_val
    if cpu.compat_mode:
      result = (result + 0x80000000) % 0x100000000 - 0x80000000
    ternary_result = cpu.int_to_ternary(result)
    cpu.registers[f'x{rd_num}'] = ternary_result
    if cpu.verbosity >=2:
      print(f"[Execute] ANDI: x{rs1_num}({val1}) & {imm_val} = {result} ('{ternary_result}') -> x{rd_num}")

def execute_ori(cpu, decoded: dict) -> None:
  """Bitwise OR Immediate (ori)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  rs1_num = cpu.ternary_to_int(decoded['rs1'])
  imm_val = cpu.ternary_to_int(decoded['imm'])

  if rd_num != 0:
    val1 = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
    result = val1 | imm_val
    if cpu.compat_mode:
      result = (result + 0x80000000) % 0x100000000 - 0x80000000
    ternary_result = cpu.int_to_ternary(result)
    cpu.registers[f'x{rd_num}'] = ternary_result
    if cpu.verbosity >=2:
      print(f"[Execute] ORI: x{rs1_num}({val1}) | {imm_val} = {result} ('{ternary_result}') -> x{rd_num}")

def execute_xori(cpu, decoded: dict) -> None:
  """Bitwise XOR Immediate (xori)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  rs1_num = cpu.ternary_to_int(decoded['rs1'])
  imm_val = cpu.ternary_to_int(decoded['imm'])

  if rd_num != 0:
    val1 = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
    result = val1 ^ imm_val
    if cpu.compat_mode:
      result = (result + 0x80000000) % 0x100000000 - 0x80000000
    ternary_result = cpu.int_to_ternary(result)
    cpu.registers[f'x{rd_num}'] = ternary_result
    if cpu.verbosity >=2:
      print(f"[Execute] XORI: x{rs1_num}({val1}) ^ {imm_val} = {result} ('{ternary_result}') -> x{rd_num}")

def execute_addi(cpu, decoded: dict) -> None:
  """Add Immediate (addi)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  rs1_num = cpu.ternary_to_int(decoded['rs1'])
  imm_val = cpu.ternary_to_int(decoded['imm'])

  if rd_num != 0:
    val1 = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
    result = val1 + imm_val
    if cpu.compat_mode:
      result = (result + 0x80000000) % 0x100000000 - 0x80000000
    ternary_result = cpu.int_to_ternary(result)
    cpu.registers[f'x{rd_num}'] = ternary_result
    if cpu.verbosity >=2:
      print(f"[Execute] ADDI: x{rs1_num}({val1}) + {imm_val} = {result} ('{ternary_result}') -> x{rd_num}")

def execute_slli(cpu, decoded: dict) -> None:
  """Shift Left Logical Immediate (slli)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  rs1_num = cpu.ternary_to_int(decoded['rs1'])
  imm_val = cpu.ternary_to_int(decoded['imm'])

  if rd_num != 0:
    val1 = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
    shamt = imm_val & 0x1F
    result = val1 << shamt

    if cpu.compat_mode:
      result = (result + 0x80000000) % 0x100000000 - 0x80000000

    ternary_result = cpu.int_to_ternary(result)
    cpu.registers[f'x{rd_num}'] = ternary_result

    if cpu.verbosity >= 2:
      print(f"[Execute] SLLI: x{rs1_num}({val1}) << {shamt} = {result} ('{ternary_result}') -> x{rd_num}")

def execute_srli(cpu, decoded: dict) -> None:
  """Shift Right Logical Immediate (srli)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  rs1_num = cpu.ternary_to_int(decoded['rs1'])
  imm_val = cpu.ternary_to_int(decoded['imm'])
  if rd_num != 0:
    val1 = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
    shamt = imm_val & 0x1F
    result = (val1 & 0xFFFFFFFF) >> shamt

    if cpu.compat_mode:
      result = (result + 0x80000000) % 0x100000000 - 0x80000000

    ternary_result = cpu.int_to_ternary(result)
    cpu.registers[f'x{rd_num}'] = ternary_result

    if cpu.verbosity >= 2:
      print(f"[Execute] SRLI: x{rs1_num}({val1}) >> {shamt} (logical) = {result} ('{ternary_result}') -> x{rd_num}")

def execute_srai(cpu, decoded: dict) -> None:
  """Shift Right Arithmetic Immediate (srai)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  rs1_num = cpu.ternary_to_int(decoded['rs1'])
  imm_val = cpu.ternary_to_int(decoded['imm'])

  if rd_num != 0:
    val1 = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
    shamt = imm_val & 0x1F
    result = val1 >> shamt

    if cpu.compat_mode:
      result = (result + 0x80000000) % 0x100000000 - 0x80000000

    ternary_result = cpu.int_to_ternary(result)
    cpu.registers[f'x{rd_num}'] = ternary_result

    if cpu.verbosity >= 2:
      print(f"[Execute] SRAI: x{rs1_num}({val1}) >> {shamt} (arithmetic) = {result} ('{ternary_result}') -> x{rd_num}")

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
    if cpu.verbosity >=2:
      print(f"[Execute] BNE.T: {val1} != {val2}. Branching to PC {cpu.pc}")
  else:
    if cpu.verbosity >=2:
      print(f"[Execute] BNE.T: {val1} == {val2}. No branch taken.")

def execute_sub(cpu, decoded: dict) -> None:
  """Subtract Register from Register (sub)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  rs1_num = cpu.ternary_to_int(decoded['rs1'])
  rs2_num = cpu.ternary_to_int(decoded['rs2'])

  if rd_num != 0:
    val1 = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
    val2 = cpu.ternary_to_int(cpu.registers[f'x{rs2_num}'])

    result = val1 - val2

    if cpu.compat_mode:
      result = (result + 0x80000000) % 0x100000000 - 0x80000000

    ternary_result = cpu.int_to_ternary(result)
    cpu.registers[f'x{rd_num}'] = ternary_result

    if cpu.verbosity >= 2:
      print(f"[Execute] SUB: x{rs1_num}({val1}) - x{rs2_num}({val2}) = {result} ('{ternary_result}') -> x{rd_num}")

def execute_lw(cpu, decoded: dict) -> None:
  """Load Word from RAM (lw)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  rs1_num = cpu.ternary_to_int(decoded['rs1'])
  imm_val = cpu.ternary_to_int(decoded['imm'])

  if rd_num != 0:
    base_addr = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
    target_addr = base_addr + imm_val

    # Read from RAM (default to '0' if the address is uninitialized)
    fetched_data = cpu.ram.get(target_addr, "0")

    cpu.registers[f'x{rd_num}'] = fetched_data

    if cpu.verbosity >= 2:
      print(f"[Execute] LW: Read '{fetched_data}' from RAM[{target_addr}] -> x{rd_num}")

def execute_sw(cpu, decoded: dict) -> None:
  """Store Word to RAM (sw)"""
  rs1_num = cpu.ternary_to_int(decoded['rs1']) # Base Address
  rs2_num = cpu.ternary_to_int(decoded['rs2']) # Data to store
  imm_val = cpu.ternary_to_int(decoded['imm']) # Offset

  base_addr = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
  target_addr = base_addr + imm_val

  data_to_store = cpu.registers[f'x{rs2_num}']

  # Write directly to the RAM dictionary
  cpu.ram[target_addr] = data_to_store

  if cpu.verbosity >= 2:
    print(f"[Execute] SW: Wrote '{data_to_store}' (from x{rs2_num}) to RAM[{target_addr}]")

def execute_slt(cpu, decoded: dict) -> None:
    """Set Less Than (slt)"""
    rd_num = cpu.ternary_to_int(decoded['rd'])
    rs1_num = cpu.ternary_to_int(decoded['rs1'])
    rs2_num = cpu.ternary_to_int(decoded['rs2'])

    if rd_num != 0:
        val1 = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])
        val2 = cpu.ternary_to_int(cpu.registers[f'x{rs2_num}'])

        # Returns 1 if val1 < val2, otherwise 0
        result = 1 if val1 < val2 else 0

        ternary_result = cpu.int_to_ternary(result)
        cpu.registers[f'x{rd_num}'] = ternary_result

        if cpu.verbosity >= 2:
            print(f"[Execute] SLT: {val1} < {val2} = {result} -> x{rd_num}")

def execute_slti(cpu, decoded: dict) -> None:
    """Set Less Than Immediate (slti)"""
    rd_num = cpu.ternary_to_int(decoded['rd'])
    rs1_num = cpu.ternary_to_int(decoded['rs1'])
    imm_val = cpu.ternary_to_int(decoded['imm'])

    if rd_num != 0:
        val1 = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])

        result = 1 if val1 < imm_val else 0

        ternary_result = cpu.int_to_ternary(result)
        cpu.registers[f'x{rd_num}'] = ternary_result

        if cpu.verbosity >= 2:
            print(f"[Execute] SLTI: {val1} < {imm_val} = {result} -> x{rd_num}")

def execute_jal(cpu, decoded: dict) -> None:
  """Jump and Link (jal)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  offset = cpu.ternary_to_int(decoded['imm'])

  # Save the return address (the already-incremented PC)
  if rd_num != 0:
    cpu.registers[f'x{rd_num}'] = cpu.int_to_ternary(cpu.pc)

  # Calculate the jump target from the original instruction line
  original_pc = cpu.pc - 1
  cpu.pc = original_pc + offset

  if cpu.verbosity >= 2:
    print(f"[Execute] JAL: Saved return PC to x{rd_num}. Jumping to PC {cpu.pc}")

def execute_jalr(cpu, decoded: dict) -> None:
  """Jump and Link Register (jalr)"""
  rd_num = cpu.ternary_to_int(decoded['rd'])
  rs1_num = cpu.ternary_to_int(decoded['rs1'])
  offset = cpu.ternary_to_int(decoded['imm'])

  base_addr = cpu.ternary_to_int(cpu.registers[f'x{rs1_num}'])

  if rd_num != 0:
    cpu.registers[f'x{rd_num}'] = cpu.int_to_ternary(cpu.pc)

  # JALR jumps to the absolute address of (rs1 + offset)
  cpu.pc = base_addr + offset

  if cpu.verbosity >= 2:
    print(f"[Execute] JALR: Saved return PC to x{rd_num}. Jumping to absolute PC {cpu.pc}")

def execute_ecall(cpu, decoded: dict) -> None:
  """System Halt (ecall)"""
  if cpu.verbosity >=2:
    print('[Execute] ECALL: Halting CPU.')
  cpu.running = False

# ---------------------------------------------------
# The Dispatch Table: Maps Opcode Signatures to Functions
# ---------------------------------------------------
INSTRUCTION_SET = {
  '++-00': execute_lit,   # load immediate address
  '+0-0+': execute_and,   # and
  '+0-+0': execute_or,    # or
  '+0-++': execute_xor,   # xor
  '+0+00': execute_sll,   # sll
  '+0+0+': execute_srl,   # srl
  '+0++0': execute_sra,   # sra
  '+0+-0': execute_slli,  # slli
  '+0+-+': execute_srli,  # srli
  '+0+--': execute_srai,  # srai
  '+00-+': execute_andi,  # andi
  '+00+0': execute_ori,   # ori
  '+00++': execute_xori,  # xori
  '+0000': execute_addi,  # add (legacy binary immediate)
  '+000+': execute_addi,  # add.t (native ternary immediate)
  '+0-00': execute_add,   # add
  '+0--0': execute_sub,   # sub
  '++000': execute_lw,    # lw
  '++00+': execute_sw,    # sw
  '-0+00': execute_bne_t, # branch not equal
  '+--00': execute_slt,   # slt
  '+--0+': execute_slti,  # slti
  '+--+0': execute_slti,  # slti.t
  '-0000': execute_jal,   # jal
  '-000+': execute_jal,   # jal.t
  '-00+0': execute_jalr,  # jalr
  '-00++': execute_jalr,  # jalr.t
  '00000': execute_ecall  # halt system
}
