# Python-Tools/Assembler/vm.py

from instructions import INSTRUCTION_SET
from isa import CONTROL_ROM, INSTRUCTION_FORMATS

class Rebel6VM:
  def __init__(self, compat_mode: bool = False, verbosity: int = 0) -> None:
    self.pc = 0
    self.registers = {f"x{i}": "0" for i in range(32)}
    self.memory = {}
    self.running = False
    self.compat_mode = compat_mode
    self.verbosity = verbosity

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
    Stage 2: Slices the 32-trit machine code into usable components
    using the Data-Driven wiring specs from isa.py.
    """
    opcode_trits = instruction[0:5]

    inst_type = CONTROL_ROM.get(opcode_trits, 'UNKNOWN')
    decoded = {'opcode': opcode_trits, 'type': inst_type}

    # Fetch the wiring schematic for this instruction type
    format_spec = INSTRUCTION_FORMATS.get(inst_type, {})

    # Slice the instruction string based on the spec
    for field, (start, end) in format_spec.items():
      decoded[field] = instruction[start:end]

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

if __name__ == '__main__':
  import sys
  import argparse
  from assembler import parse_tas_file, resolve_addresses, translate_to_machine_code

  parser = argparse.ArgumentParser(description='REBEL-6 Ternary Virtual Machine')
  parser.add_argument('file', help='The .tas assembly file to execute', default='code/add.tas')
  parser.add_argument('-c', '--compat', action='store_true',
                      help='Enable 32-bit Legacy Compatibility Mode (forces integer oveflow)')
  parser.add_argument('-v', '--verbose', action='count', default=0,
    help='Increase verbosity (-v for basic PC trace, -vv for full execution trace)')
  args = parser.parse_args()

  print('--- [PHASE 1] ASSEMBLER ---')
  try:
    labels, raw_insts = parse_tas_file(args.file)
    resolved_insts = resolve_addresses(raw_insts, labels)
    final_binaries = translate_to_machine_code(resolved_insts)
    machine_code_list = [inst['machine_code'] for inst in final_binaries]
    print(f'Successfully assembled {len(machine_code_list)} instructions.')
  except Exception as e:
    print(f'Assembler Failed: {e}')
    sys.exit(1)

  print('\n--- [PHASE 2] VIRTUAL MACHINE ---')
  cpu = Rebel6VM(compat_mode=args.compat, verbosity=args.verbose)
  cpu.load_program(machine_code_list)
  cpu.running = True

  print('\nStarting CPU Execution Loop...\n')
  while cpu.running:
    # Debug helper
    if cpu.verbosity >= 2:
      print(f'--- PC: {cpu.pc} ---')
    # STAGE 1: FETCH
    current_inst = cpu.fetch()
    if cpu.verbosity >= 3:
      print(f'Fetched 32-Trit String: {current_inst}')

    # STAGE 2: DECODE
    decoded_signals = cpu.decode(current_inst)
    if cpu.verbosity >= 3:
      print(f'Decoded CPU Signals:  {decoded_signals}')

    # STAGE 3: EXECUTE
    cpu.execute(decoded_signals)
    if cpu.verbosity >= 3:
      print(f'Executing {decoded_signals}')
  cpu.dump_registers()
