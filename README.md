# MSc thesis

The work in this repository is part of my MSc thesis that can be found [here](https://openarchive.usn.no/usn-xmlui/handle/11250/3169529).

# RV32IToREBEL (R2R)

A lightweight translator to translate and simulate binary RISCV RV32I assembly to ternary REBEL6 assembly. The RV32I assembly code is generated using the GCC Toolchain. Some GCC features and syntax is therefor supported, but far from everything. No optimization has been used when compiling C code to RV32I assembly when using the GCC Toolchain to generate assembly files.

# References

The Lexer, Parser, and Token classes under code/Parsers was copied from [GIT](https://github.com/AZHenley/riscv-parser), a [RISC-V parser created by Austin Henley](https://austinhenley.com/blog/parsingriscv.html), and then adapted to our needs.

# REBEL-6 Ternary Virtual Machine (Python Prototype)

A software-defined, balanced-ternary Virtual Machine and custom Assembler built to emulate the REBEL-6 architecture.

## Features
* **Custom Assembler:** Parses legacy RISC-V pseudo-assembly (`.tas`), handles ABI register normalization, dynamically allocates physical ternary bus widths, and emits 32-trit machine code.
* **Data-Driven Decoder:** Utilizes a strict hardware wiring schematic (`isa.py`) to blindly slice opcodes, enforcing true RISC architecture without software-level conditional loops.
* **Balanced Ternary ALU:** Performs base-10 math under the hood while routing states back into physical `-`, `0`, and `+` ternary strings.
* **32-Bit Legacy Compatibility:** Built-in overflow limits to seamlessly emulate standard 32-bit two's-complement binary on an infinitely sized Python integer backend.
* **Full RV32I Core Support:** Supports mathematical operations, bitwise logic, bit-shifting, RAM memory addressing (Load/Store), and subroutine jumps.

## Architecture
* `isa.py`: The core schematic. Contains the standard ABI mappings, the Hardware Control ROM, and Instruction Format slicing coordinates.
* `assembler.py`: The compiler. Converts human-readable text into 32-trit physical wire states.
* `vm.py`: The CPU core. Manages the Fetch-Decode-Execute cycle, the Program Counter, and the RAM/ROM memory arrays.
* `instructions.py`: The Arithmetic Logic Unit (ALU) and Memory Controller. Houses the mathematical logic for every opcode.

## Usage

Run the Virtual Machine from the command line by pointing it to a `.tas` file.

```bash
python3 Python-Tools/Assembler/vm.py code/custom_test.tas --compat -vv
```
## Flags  
- --compat or -c: Enables 32-bit Legacy Compatibility Mode (forces integer overflow/underflow).
- -v or -vv: Adjusts logging verbosity. -v outputs the Program Counter trace, -vv outputs real-time ALU math and RAM memory operations.

---

## Containerized Development Environment

To eliminate the need for manual GCC toolchain installations and environment variable configurations, this project now uses a Dockerized build environment. 

### Prerequisites
* Docker installed on your host machine.

### Build Instructions

**1. Build the Docker image:**
Run this command from the root of the repository to install the required RISC-V cross-compilers and C++ build tools:
```bash
docker build -t rebel6-dev .
```
**2. Start the interactive container:**
This will spin up the container and mount your local directory to `/app` inside the container. This allows you to edit files on your host machine using your preferred IDE while compiling in the container.
```bash
docker run -it --rm -v $(pwd):/app rebel6-dev
```
**3. Compile the Translator:**
Once inside the container's terminal, navigate tot he code directory and build the executable using CMake:
```bash
cd code
cmake .
make
```
The RV32IToREBEL executable will be generated inside the `code/` directory. Because of the volume mount, this binary will also be immediately available on your host machine.

---

# Bare Metal/Manual Setup (Legacy)

## GCC Toolchain setup

The setup and installation of the [GCC Toolchain](https://pages.github.com/) has been tested using Windows Subsystem for Linux (WSL) as OS, targeting the Newlib (bare-metal) cross-compiler to avoid interference from an OS when generating RV32I assembly. Although the GIT page for the toolchain contains a walkthrough of how to set up and install the toolchain, we none the less describe the setup that worked for us.

As the walkthrough dictates, certain prerequisites need to be installed.

```
$ sudo apt-get install autoconf automake autotools-dev curl python3 python3-pip libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev libexpat-dev ninja-build git cmake libglib2.0-dev
```

A handful of environments are created to make it easier to run the installation commands and to give a better overview. These can be added to the .bashrc file.

```
// Base directory for RISCV tools.
export RISCV_TOOL_BASE=/riscv
// Toolchain directory
export RISCV_TOOLCHAIN=${RISCV_TOOL_BASE}/toolchain
// Directory for all installed toolchain-related binaries and programs
export RISCV_TOOLCHAIN_INSTALL=${RISCV_TOOLCHAIN}/installed
```

The PATH variable need to be updated before initiating installation. Add the following to the same file as you added the above lines.

```
export PATH="${RISCV_TOOLCHAIN_INSTALL}/bin:$PATH"
```

Once configured, the only thing remaining is to setup and install the toolchain itself, targeting the RV32I architecture.
Do note that this may take a while.

```
sudo mkdir -p $RISCV_TOOLCHAIN_INSTALL
cd $RISCV_TOOLCHAIN
git clone https://github.com/riscv/riscv-gnu-toolchain
cd riscv-gnu-toolchain
sudo mkdir build
cd build
../configure --prefix=$RISCV_TOOLCHAIN_INSTALL --with-arch=rv32i --with-abi=ilp32
make -j$(nproc) // This can take a while
```

## Building the translator

The translator is built with cmake and make using the following commands.

```
BUILD_DIR=<Target directory for build files and the executable>
sudo mkdir ${BUILD_DIR}
cd ${BUILD_DIR}
cmake <Path to the translator's local repository>/code
make
```

## Generating assembly files using the GCC Toolchain

The translator only supports single-file assembly code. This comes from single C-file programs since the GCC Compiler generates one assembly file per C file.
To generate an assembly file from a C file, run `riscv32-unknown-elf-gcc -S <C-coded file>.c -o <RV32I Assembly file>.s`

## Running the translator

The command `./RV32IToREBEL <RV32I Assembly file>.s` is used to run the translator, using the generated RV32I assembly file as input.
