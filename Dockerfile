# Use Debian
FROM debian:12-slim

# Prevent apt from prompting for timezone or keyboard layouts
ENV DEBIAN_FRONTEND=noninteractive

# 1. Update package list
# 2. Install standard C++ build tools (Make, CMake, GCC)
# 3. Install the pre-built RISC-V cross-compiler
# 4. Clean up apt cache to keep the image lightweight
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    gcc-riscv64-unknown-elf \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Mount the code in the Dockerfile as a volume.
CMD ["/bin/bash"]
