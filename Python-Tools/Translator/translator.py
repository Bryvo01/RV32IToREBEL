# Python-Tools/Translator/translator.py

import argparse
import logging
import os
import sys
from typing import List, Tuple

# Instructions we can safely ignore from GCC output
IGNORED_DIRECTIVES = {
  ".file", ".option", ".attribute", ".ident", ".size", ".type",
  ".cfi_startproc", ".cfi_endproc", ".cfi_def_cfa_offset", ".cfi_offset"
}

# 1-to-1 mapping to REBEL-6 native ternary instructions
INSTRUCTION_MAP = {
  "li": "li.t",
  "bne": "bne.t",
  "jal": "jal.t",
  "jalr": "jalr.t",
}

def setup_logger(verbosity: int) -> None:
  """
  Configures the global logging level based on the verbosity flag.

  :param verbosity: The count of '-v' flags provided by the user.
                    0 = WARNING/ERROR only.
                    1 = INFO (Basic translation stats).
                    2 = DEBUG (Granular line-by-line translation tracing).
  """
  if verbosity == 0:
    level = logging.WARNING
  elif verbosity == 1:
    level = logging.INFO
  else:
    level = logging.DEBUG

  # Set a clean format for the terminal
  logging.basicConfig(
    level=level,
    format="%(message)s"
  )

def clean_line(line: str) -> str:
  """
  Strips comments and normalizes whitespace from a single line of assembly.

  param line: The raw line of assembly code read from the file.
  :return: The cleaned string with comments removed and leading/trailing
           whitespace stripped. Returns an empty string if the line contained
           only a comment or whitespace.
  """
  line = line.split('#')[0]       # Remove standard comments
  line = line.split('//')[0]      # Remove C-style comments
  return line.strip()

def translate_instruction(opcode: str, args: List[str]) -> Tuple[str, List[str]]:
  """
  Expands pseudo-instructions and maps standard RV32I opcodes to REBEL-6
  ternary equivalents.

  :param opcode: The base assembly mnemonic (e.g., 'mv', 'nop', 'bne').
  :param args: A list of string arguments associated with the instruction.
  :return: A tuple containing:
           - The translated opcode string.
           - A list of the translated argument strings.
  """

  # 1. Expand Pseudo-Instructions
  if opcode == "mv":
    logging.debug(f"      [DEBUG] Expanded pseudo-instruction: mv -> addi {args[0]}, {args[1]}, 0")
    return "addi", [args[0], args[1], "0"]
  elif opcode == "nop":
    logging.debug("      [DEBUG] Expanded pseudo-instruction: nop -> addi x0, x0, 0")
    return "addi", ["x0", "x0", "0"]
  elif opcode == "ret":
    logging.debug("      [DEBUG] Expanded pseudo-instruction: ret -> jalr x0, ra, 0")
    return "jalr", ["x0", "ra", "0"]

  # 2. Map directly to Ternary counterparts
  new_opcode = INSTRUCTION_MAP.get(opcode, opcode)

  if new_opcode != opcode:
    logging.debug(f"      [DEBUG] Mapped native ternary: {opcode} -> {new_opcode}")

  return new_opcode, args

def translate_file(input_path: str, output_path: str) -> None:
  """
  Main parsing loop. Reads an RV32I assembly file, translates it, and writes to a REBEL-6 .tas file.

  :param input_path:  The file path to the input GCC-generated .s file.
  :param output_path: The file path to write the translated .tas output to.
  :return: None
  """
  if not os.path.exists(input_path):
    logging.error(f"[!] ERROR: Could not find input file '{input_path}'")
    sys.exit(1)

  logging.info(f"[*] Starting translation of '{input_path}'...")

  with open(input_path, 'r') as infile:
    lines = infile.readlines()

  translated_lines = []
  ignored_count = 0
  expanded_count = 0

  for line in lines:
    clean = clean_line(line)
    if not clean:
      continue

    # Keep labels exactly as they are
    if clean.endswith(':'):
      translated_lines.append(clean)
      logging.debug(f"   [LABEL] {clean}")
      continue

    # Handle compiler directives
    if clean.startswith('.'):
      directive = clean.split()[0]
      if directive in IGNORED_DIRECTIVES:
        ignored_count += 1
        logging.debug(f"   [STRIPPED] Ignored GCC directive: {directive}")
        continue

      # Keep .text, .data, .word, etc.
      translated_lines.append(clean)
      logging.debug(f"   [DIRECTIVE] Preserved: {directive}")
      continue

    # Tokenize the instruction
    parts = clean.replace(',', ' ').split()
    opcode = parts[0]
    args = parts[1:]

    # Run it through the translator
    new_opcode, new_args = translate_instruction(opcode, args)
    if new_opcode != opcode:
      expanded_count += 1

    # Rebuild the string
    translated_lines.append(f"    {new_opcode} {', '.join(new_args)}")

  # Write the output
  with open(output_path, 'w') as outfile:
    outfile.write("\n".join(translated_lines) + "\n")

  logging.info(f"[*] Translation complete: '{output_path}'")
  logging.info(f"    - Stripped Directives: {ignored_count}")
  logging.info(f"    - Modified/Expanded Opcodes: {expanded_count}")

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="RV32I to REBEL-6 Assembly Translator")
  parser.add_argument("input", help="The input .s file generated by GCC")
  parser.add_argument("-o", "--output", help="The output .tas file", default="out.tas")

  # Add our tiered verbosity flag!
  parser.add_argument("-v", "--verbose", action="count", default=0,
                      help="Increase logging verbosity (-v for INFO, -vv for DEBUG)")

  args = parser.parse_args()

  # Initialize the logger before doing anything else
  setup_logger(args.verbose)

  translate_file(args.input, args.output)
