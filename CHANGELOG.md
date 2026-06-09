# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [v0.1.0] - Phase 1 Completion 
### Added
* **Data-Driven ISA Schema:** Created `isa.py` to decouple instruction formats, opcodes, and control ROM routing from the core execution logic.
* **Virtual Machine Core (`vm.py`):** Fully implemented Fetch-Decode-Execute pipeline.
* **RAM Module:** Added read/write memory dictionary to the VM for `lw` and `sw` instructions.
* **Full RV32I Instruction Set:** Implemented mathematical arithmetic, bitwise logic, shifts, loads, stores, branches, and jumps (including native `.t` ternary variants).
* **Dynamic Bus Width Allocation:** Assembler now calculates register widths and grants the remaining 32-trit bus to the immediate value.
* **CLI Arguments:** Added `argparse` support for `--compat` (32-bit overflow enforcement) and `-v` / `-vv` (verbosity levels).
* **Assembler Directives:** Parser now safely ignores `.text`, `.data`, `.align`, and `.globl` compiler directives.

### Fixed
* **Infinite Loop Bug:** Fixed an issue where the assembler truncated jump offsets by capping instructions at 32 trits. Replaced with dynamic width calculation and explicit `Hardware Overflow` errors.
* **Zero-Padding Alignment Failure:** Fixed a data alignment bug where register `x0` generated a 1-trit string instead of a padded 4-trit string.
* **Hexadecimal Parsing (`0x` trap):** Upgraded `normalize_arg` to safely parse standard decimal, hex strings, and ABI names while enforcing 32-bit bounds, rendering the old `parse_immediate` function obsolete. 

### Changed
* Refactored `vm.py`'s Decoder to slice based on `INSTRUCTION_FORMATS` coordinates instead of using hardcoded Python `if/elif` loops.
* Unified the legacy binary (`addi`) and native ternary (`addi.t`) execution paths to share mathematical logic.

### Added
- `Dockerfile` to create a reproducible, containerized development environment based on Debian 12.
- Pre-compiled `gcc-riscv64-unknown-elf` toolchain integration via Docker, bypassing the need for manual source builds.
- Added `.gitignore` to prevent tracking CMake and Make build artifacts.

### Fixed
- Added missing `#include <algorithm>` directives in multiple `.cpp` files (`directive.cpp`, `instruction.cpp`, `registry.cpp`, etc.) to resolve compilation errors under modern GCC 12+.

### Changed
- Updated `README.md` to prioritize the new Docker-based build process while retaining legacy bare-metal instructions.
