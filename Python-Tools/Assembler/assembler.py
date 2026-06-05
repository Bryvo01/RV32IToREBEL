# Python-Tools/Assembler/assembler.py
import sys
import os

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

def normalize_arg(arg: str) -> str:
  """
  Converts an ABI register name to its hardware designation (e.g., 'gp' to
  'x3'). Leaves immediate values and 'x' registers unmodified.

  :param arg: The string argument to check against the ABI dictionary.
  :return: The hardware register string, or the original string if not found.
  """
  return ABI_TO_REG.get(arg, arg)

def tokenize_instruction(inst_str: str) -> dict:
  """
  Splits a raw assembly instruction into its opcode and arguments.
  Example: 'add x14,x1,x2' -> {'opcode': 'add', 'args': ['x14', 'x1', 'x2']}

  :param inst_str: The raw instruction string from the assembly file.
  :return: A dictionary containing the parsed 'opcode' and 'args' list.
  """
  # Split on the first chunk of whitespace
  parts = inst_str.split(None, 1)
  opcode = parts[0]
  args = []

  if len(parts) > 1:
    # Split by comma, strip whitespace, and normalize ABI names
    args = [normalize_arg(arg.strip()) for arg in parts[1].split(',')]

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

if __name__ == '__main__':
  # TODO: Hardcoded for testing, use argparse later
  test_file = 'code/add.tas'

  labels, insts = parse_tas_file(test_file)

  print(f'Parsing Complete!')

  print('--- First 5 tokenized instructions ---')
  for i in range(5):
    if i < len(insts):
      print(f"[{i}] Opcode: {insts[i]['opcode'].ljust(8)} | Args: {insts[i]['args']}")
