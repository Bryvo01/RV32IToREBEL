# Python-Tools/Assembler/vm.py

from instructions import INSTRUCTION_SET

class Rebel6VM:
  def __init__(self) -> None:
    self.pc = 0
    self.registers = {f"x{i}": "0" for i in range(32)}
    self.memory = {}
    self.running = False
    # Hardware control ROM: maps 5-trit opcodes to their instruction set format
    self.control_rom = {
      '+0-00': 'R', # add
      '++-00': 'I', # li.t
      '-0+00': 'B', # bne.t
      '00000': 'SYS' # ecall
    }

  def load_program(self, machine_code_list: list) -> None:
    """
    Loads a list of 32-trit machine code strings into the VM's memory.
    """
    for i, instruction in enumerate(machine_code_list):
      self.memory[i] = instruction

    print(f"[*] Loaded {len(machine_code_list)} instructions into ROM.")

  def dump_registers(self) -> None:
    """
    Prints the current state of all registers for debugging.
    """
    print("-" * 30)
    print("REBEL-6 REGISTER DUMP")
    print("-" * 30)
    for i in range(32):
      reg = f"x{i}"
      val = self.registers[reg]
      # Only print registers that have been modified
      if val != "0":
        print(f"{reg.ljust(4)} : {val}")
    print("-" * 30)

  def fetch(self) -> str:
    """
    Stage 1: Fetches the instruction at the Program Counter (PC)
    and increments the PC to point to the next instruction.
    :return: the instruction from memory
    """
    if self.pc not in self.memory:
      self.running = False
      return "0" * 32 # return a blank instruction if memory is empty
    instruction = self.memory[self.pc]
    # Advance the program counter
    # NOTE: Standard RISC-V increments by 4 bytes, but our memory array is
    # indexed by instruction line, so we just increment by 1.
    self.pc += 1
    return instruction

  def decode(self, instruction: str) -> dict:
    """
    Stage 2: Slices the 32-trit machine code into usable components based on
    its opcode signature from the Control ROM
    :return: the decoded instruction
    """
    opcode_trits = instruction[0:5]
    inst_type = self.control_rom.get(opcode_trits, 'UNKNOWN')
    decoded = {'opcode': opcode_trits, 'type': inst_type}

    if inst_type == 'R':
      # R-Type: Opcode(5) | rd(4) | rs1(4) | rs2(4) | padding(15)
      decoded['rd']  = instruction[5:9]
      decoded['rs1'] = instruction[9:13]
      decoded['rs2'] = instruction[13:17]
    elif inst_type == 'I':
      decoded['rd']  = instruction[5:9]
      decoded['imm'] = instruction[9:19]
    elif inst_type == 'B':
      decoded['rs1'] = instruction[5:9]
      decoded['rs2'] = instruction[9:13]
      decoded['imm'] = instruction[13:23]

    return decoded

  def execute(self, decoded: dict) -> None:
    """
    Stage 3: Executes the decoded instruction and updates CPU state.
    """
    opcode = decoded['opcode']
    operation = INSTRUCTION_SET.get(opcode)
    if operation:
      operation(self, decoded)
    else:
      print(f"[Execute] ERROR: Unimplemented opcode '{opcode}")
      self.running = False

  def ternary_to_int(self, trit_string: str) -> int:
    """
    Converts a balanced ternary string (e.g., '+-0') back into a base-10 integer.
    :return: the interger value of the ternary string.
    """
    val = 0
    # Reverse the string so the index matches the power of 3
    for i, trit in enumerate(reversed(trit_string)):
      if trit == '+':
        val += 3**i
      elif trit == '-':
        val -= 3**i
    return val

  def int_to_ternary(self, val: int) -> str:
    """
    Converts a base-10 integer into a balanced ternary string.
    :return: the ternary string for the integer value.
    """
    if val == 0:
      return "0"
    trits = []
    temp_val = val
    while temp_val != 0:
      remainder = temp_val % 3
      if remainder == 0:
        trits.append('0')
        temp_val = temp_val // 3
      elif remainder == 1:
        trits.append('+')
        temp_val = temp_val // 3
      elif remainder == 2:
        trits.append('-')
        temp_val = (temp_val // 3) + 1
    return ''.join(reversed(trits))

if __name__ == "__main__":
  cpu = Rebel6VM()

  # This is the output from our assembler for: li.t x3, 2
  mock_rom = [
    '++-000+-000000000+00000000000000',
    '00000000000000000000000000000000'
  ]
  cpu.load_program(mock_rom)
  cpu.running = True

  print('\nStarting CPU Execution Loop...')
  while cpu.running:
    print(f'\n--- PC: {cpu.pc} ...')

    # STAGE 1: FETCH
    current_inst = cpu.fetch()
    print(f'Fetched 32-Trit String: {current_inst}')

    # STAGE 2: DECODE
    decoded_signals = cpu.decode(current_inst)
    print(f'Decoded CPU Signals:  {decoded_signals}')

    # STAGE 3: EXECUTE
    cpu.execute(decoded_signals)
    print(f'Executing {decoded_signals}')

  cpu.dump_registers()
