# Python-Tools/Assembler/assembler.py
import sys
import os
# from turtle import width

# Standard RISC-V ABI to Hardware Register mapping
ABI_TO_REG = {
  'zero': 'x0', 'ra': 'x1', 'sp': 'x2', 'gp': 'x3', 'tp': 'x4',
  't0': 'x5', 't1': 'x6', 't2': 'x7', 's0': 'x8', 'fp': 'x8', 's1': 'x9',
  'a0': 'x10', 'a1': 'x11', 'a2': 'x12', 'a3': 'x13', 'a4': 'x14',
  'a5': 'x15', 'a6': 'x16', 'a7': 'x17', 's2': 'x18', 's3': 'x19',
  's4': 'x20', 's5': 'x21', 's6': 'x22', 's7': 'x23', 's8': 'x24',
  's9': 'x25', 's10': 'x26', 's11': 'x27', 't3': 'x28', 't4': 'x29',
  't5': 'x30', 't6': 'x31'
}

# ---------------------------------------------------
# REBEL-6 Ternary Opcode Dictionary
# Format: 'opcode_name': {'type': 'format_type', 'trit_code': 'ternary_string'}
# ---------------------------------------------------
OPCODES = {
  # R-Type: Register-to-Register (e.g., add rd, rs1, rs2)
  'add':   {'type': 'R', 'trit_code': '+0-00'},

  # I-Type: Register-to-Immediate (e.g., addi rd, rs1, imm)
  'addi':  {'type': 'I', 'trit_code': '+0000'},

  # Custom Ternary I-Type (Load Immediate Ternary)
  'li.t':  {'type': 'I', 'trit_code': '++-00'},

  # B-Type: Branching (e.g., bne.t rs1, rs2, offset)
  'bne.t': {'type': 'B', 'trit_code': '-0+00'},

  # Environment Call (Halt / System)
  'ecall': {'type': 'I', 'trit_code': '00000'}
}

def normalize_arg(arg: str) -> str:
  """
  Converts an ABI register name to its hardware designation (e.g., 'gp' to
  'x3'). Leaves immediate values and 'x' registers unmodified.

  :param arg: The string argument to check against the ABI dictionary.
  :return: The hardware register string, or the original string if not found.
  """
  return ABI_TO_REG.get(arg, arg)

def parse_immediate(val: str) -> int | str:
  """
  Attempts to convert a string representation of a number (hex or decimal)
  into a Python integer. Returns the original string if it is not a number.

  :param val: The string to convert.
  :return: An integer if conversion succeeds, otherwise the original string.
  """
  try:
    return int(val, 0)
  except ValueError:
    # If it fails, it must be a register ('x1') or label ('fail')
    return val

def tokenize_instruction(inst_str: str) -> dict:
  """
  Splits a raw assembly instruction into its opcode and arguments.
  Example: 'add x14,x1,x2' -> {'opcode': 'add', 'args': ['x14', 'x1', 'x2']}

  :param inst_str: The raw instruction string from the assembly file.
  :return: A dictionary containing the parsed 'opcode' and 'args' list.
  """
  # Split on the first whitespace
  parts = inst_str.split(None, 1)
  opcode = parts[0]
  args = []

  if len(parts) > 1:
    # Split by comma, strip whitespace, normalize ABI names, and parse integers
    args = [parse_immediate(normalize_arg(arg.strip())) for arg in parts[1].split(',')]

  return {'opcode': opcode, 'args': args}

def parse_tas_file(filepath: str) -> tuple[dict, list]:
  """
  Reads a ternary assembly (.tas) file, strips directives and empty lines, and
  extracts instructions and labels. Labels map to the instruction's index.

  :param filepath: The path to the .tas file to be parsed.
  :return: A tuple containing a dict of labels and a list of tokenized
           instruction dictionaries.
  """
  if not os.path.exists(filepath):
    print(f'Error: Could not find {filepath}')
    sys.exit(1)

  with open(filepath, 'r') as file:
    lines = file.readlines()

  instructions = []
  labels = {}

  for line in lines:
    clean_line = line.strip()

    # TODO: Skip empty lines and assembler directives (for now)
    if not clean_line or clean_line.startswith('.'):
      continue

    if clean_line.endswith(':'):
      label_name = clean_line[:-1]  # Remove the colon
      # Record that this label points to the NEXT instruction to be added
      labels[label_name] = len(instructions)
    else:
      tokenized = tokenize_instruction(clean_line)
      instructions.append(tokenized)

  return labels, instructions

def resolve_addresses(instructions: list, labels: dict) -> list:
  """
  Pass 2 (Address Resolution): Iterates through the parsed instructions and
  replaces any label arguments with their relative integer jump offsets.

  :param instructions: The list of tokenized instruction dicts from Pass 1.
  :param labels: The symbol table mapping label names to instruction indices.
  :return: The fully resolved list of instructions.
  """
  for i, inst in enumerate(instructions):
    # Loop through each argument in the current instruction
    for j, arg in enumerate(inst['args']):
      # If the argument is a string and it exists in our Symbol Table
      if isinstance(arg, str) and arg in labels:
        target_index = labels[arg]
        relative_offset = target_index - i

        # Replace the text label with the calculated integer offset
        inst['args'][j] = relative_offset

  return instructions

def int_to_ternary(val, width: int = 0) -> str:
  """
  Converts a base-10 integer (or register string like 'x14') into a
  balanced ternary string using '+', '0', and '-'. If width is specified, pads
  the left side with '0's to match the required length.

  :param val: the integer to convert (could be a string).
  :param width: the width of the instruction (32 trits)
  :return: the instruction converted to trit machine code.
  """
  # If it's a register string like 'x14', extract just the integer
  if isinstance(val, str) and val.startswith('x'):
    val = int(val[1:])
  else:
    val = int(val)

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
      temp_val = (temp_val // 3) + 1  # The balanced ternary carry step

  # The algorithm calculates from least-significant to most-significant trit,
  # so we must reverse the list to read it correctly left-to-right.
  result = "".join(reversed(trits))
  if width > 0 and len(result) < width:
    # pad with leading zeros
    result = "0" * (width - len(result)) + result
  return result

def translate_to_machine_code(resolved_insts: list, opcodes: dict) -> list:
  """
  Pass 3 (Emission): Converts resolved instructions into raw ternary machine code.

  :param resolved_insts: The list of instructions with resolved jump offsets.
  :param opcodes: The dictionary mapping instruction names to ternary signatures.
  :return: A list of strings representing the final executable ternary code.
  """
  machine_code = []

  for inst in resolved_insts:
    opcode = inst['opcode']
    args = inst['args']

    # Handle opcodes we haven't added to the dictionary yet
    op_data = opcodes.get(opcode, {'type': 'UNKNOWN', 'trit_code': '00000'})
    trit_code = op_data['trit_code']

    # Convert all arguments to balanced ternary
    ternary_args = []
    for arg in args:
      if isinstance(arg, str) and arg.startswith('x'):
        # registers are 4 trits wide
        ternary_args.append(int_to_ternary(arg, width=4))
      else:
        # Immediates/Offsets can be wider, default to 10 trits for now
        ternary_args.append(int_to_ternary(arg, width=10))
    raw_instruction = trit_code + ''.join(ternary_args)

    if len(raw_instruction) < 32:
      raw_instruction = raw_instruction.ljust(32,'0')
    elif len(raw_instruction) > 32:
      # TODO: throw an overflow error
      raw_instruction = raw_instruction[:32]

    machine_code.append({'original_op': opcode, 'machine_code': raw_instruction})

  return machine_code

if __name__ == '__main__':
  # TODO: Hardcoded for testing, use argparse later
  test_file = 'code/add.tas'

  # Pass 1: Symbol Resolution
  labels, raw_insts = parse_tas_file(test_file)

  # Pass 2: Address Resolution
  resolved_insts = resolve_addresses(raw_insts, labels)

  # Pass 3: Machine Code Emission
  final_binaries = translate_to_machine_code(resolved_insts, OPCODES)

  print('Assembler Pipeline Complete!\n')

  print('--- Final Mocked Ternary Machine Code ---')
  # Print instructions 5 through 10
  for i in range(5, 11):
    if i < len(final_binaries):
      op = final_binaries[i]['original_op']
      code = final_binaries[i]['machine_code']
      print(f"[{i}] {op.ljust(8)} -> {code}")
