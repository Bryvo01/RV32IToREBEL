# Python-Tools/Assembler/isa.py

# ---------------------------------------------------
# Standard RISC-V ABI to Hardware Register mapping
# ---------------------------------------------------
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
# REBEL-6 Ternary Opcode Dictionary (Used by Assembler)
# ---------------------------------------------------
OPCODES = {
  'bne.t':  {'type': 'B', 'trit_code': '-0+00'},
  'sw':     {'type': 'S', 'trit_code': '++00+'},
  'slt':    {'type': 'R', 'trit_code': '+--00'},
  'and':    {'type': 'R', 'trit_code': '+0-0+'},
  'or':     {'type': 'R', 'trit_code': '+0-+0'},
  'xor':    {'type': 'R', 'trit_code': '+0-++'},
  'add':    {'type': 'R', 'trit_code': '+0-00'},
  'sll':    {'type': 'R', 'trit_code': '+0+00'},
  'srl':    {'type': 'R', 'trit_code': '+0+0+'},
  'sra':    {'type': 'R', 'trit_code': '+0++0'},
  'sub':    {'type': 'R', 'trit_code': '+0--0'},
  'jal':    {'type': 'J', 'trit_code': '-0000'},
  'jal.t':  {'type': 'J', 'trit_code': '-000+'},
  'slti':   {'type': 'I', 'trit_code': '+--0+'},
  'slti.t': {'type': 'I', 'trit_code': '+--+0'},
  'slli':   {'type': 'I', 'trit_code': '+0+-0'},
  'srli':   {'type': 'I', 'trit_code': '+0+-+'},
  'srai':   {'type': 'I', 'trit_code': '+0+--'},
  'andi':   {'type': 'I', 'trit_code': '+00-+'},
  'ori':    {'type': 'I', 'trit_code': '+00+0'},
  'xori':   {'type': 'I', 'trit_code': '+00++'},
  'addi':   {'type': 'I', 'trit_code': '+0000'},
  'addi.t': {'type': 'I', 'trit_code': '+000+'},
  'li.t':   {'type': 'I', 'trit_code': '++-00'},
  'lw':     {'type': 'I', 'trit_code': '++000'},
  'jalr':   {'type': 'I', 'trit_code': '-00+0'},
  'jalr.t': {'type': 'I', 'trit_code': '-00++'},
  'ecall':  {'type': 'I', 'trit_code': '00000'}
}

# ---------------------------------------------------
# Hardware Control ROM (Used by VM Decoder)
# Maps 5-trit opcodes to instruction set formats
# ---------------------------------------------------
CONTROL_ROM = {
  '-0000': 'J',   # X-Type: jal
  '-000+': 'J',   # X-Type: jal.t
  '+0-0+': 'R',   # R-Type: and
  '+0-+0': 'R',   # R-Type: or
  '+0-++': 'R',   # R-Type: xor
  '+0-00': 'R',   # R-Type: Register-to-Register (e.g., add rd,rs1,rs2)
  '+0+00': 'R',   # R-Type: sll
  '+0+0+': 'R',   # R-Type: srl
  '+0++0': 'R',   # R-Type: sra
  '+0--0': 'R',   # R-Type: sub
  '+--00': 'R',   # R-Type: slt
  '++000': 'I',   # I-Type: lw
  '+0+-0': 'I',   # I-Type: slli
  '+0+-+': 'I',   # I-Type: srli
  '+0+--': 'I',   # I-Type: srai
  '+00-+': 'I',   # I-Type: andi
  '+00+0': 'I',   # I-Type: ori
  '+00++': 'I',   # I-Type: xori
  '+--0+': 'I',   # X-Type: slti
  '+--+0': 'I',   # X-Type: slti.t
  '-00+0': 'I',   # X-Type: jalr
  '-00++': 'I',   # X-Type: jalr.t
  '+0000': 'I',   # I-Type: Register-to-Immediate (e.g., addi rd,rs1,imm)
  '+000+': 'I',   # I-Type: Add Immediate Ternary (e.g., addi.t x0,x9,0)
  '++-00': 'LI',  # I-Type: Load Immediate Ternary (e.g., li.t x2,11)
  '-0+00': 'B',   # B-Type: Branching (e.g., bne.t rs1, rs2, offset)
  '++00+': 'S',   # S-Type: sw
  '00000': 'SYS'  # Environment Call (Halt / System) (e.g. ecall)
}

# ---------------------------------------------------
# Hardware Wiring Specs (Instruction Formats)
# Maps instruction types to their slice indices: (start, end)
# ---------------------------------------------------
INSTRUCTION_FORMATS = {
  'R':   {'rd': (5, 9), 'rs1': (9, 13), 'rs2': (13, 17)},
  'LI':  {'rd': (5, 9), 'imm': (9, 32)},
  'I':   {'rd': (5, 9), 'rs1': (9, 13), 'imm': (13, 32)},
  'B':   {'rs1': (5, 9), 'rs2': (9, 13), 'imm': (13, 32)},
  'S':   {'rs1': (5, 9), 'rs2': (9, 13), 'imm': (13, 32)},
  'J':   {'rd': (5, 9), 'imm': (9, 32)},
  'SYS': {} # ecall requires no additional slicing
}
