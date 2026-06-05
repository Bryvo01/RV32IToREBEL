# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- `Dockerfile` to create a reproducible, containerized development environment based on Debian 12.
- Pre-compiled `gcc-riscv64-unknown-elf` toolchain integration via Docker, bypassing the need for manual source builds.
- Added `.gitignore` to prevent tracking CMake and Make build artifacts.

### Fixed
- Added missing `#include <algorithm>` directives in multiple `.cpp` files (`directive.cpp`, `instruction.cpp`, `registry.cpp`, etc.) to resolve compilation errors under modern GCC 12+.

### Changed
- Updated `README.md` to prioritize the new Docker-based build process while retaining legacy bare-metal instructions.
