import sys
import re

# Constants for special memory addresses
P_REG = 0      # Pointer register (memory address)
DATA_REG_A = 1   # Data register A
DATA_REG_X = 2   # Data register X
PROGRAM_START = 3  # Program start address

# Constants for instruction opcodes
OPCODES = {
    "loada": 0x0,         # Load the next word into the A register
    "a2x": 0x1,           # Move A to X
    "x2a": 0x2,           # Move X to A
    "a2p": 0x3,           # Move A to pointer register (address register)
    "read": 0x4,          # Read word from address in pointer register to A
    "write": 0x5,         # Write word in A to address in pointer register
    "add": 0x6,           # Add A and X, store result in A
    "lshift": 0x7,        # Left shift A
    "rshift": 0x8,        # Right shift A
    "and": 0x9,           # Binary AND: A = A & X
    "or": 0xa,            # Binary OR: A = A | X
    "not": 0xb,           # Binary NOT: Invert all bits of A
    "jump": 0xc,          # Jump to address in pointer register
    "jumpz": 0xd,         # Jump to address in pointer register if A == 0
    "output": 0xe,        # Output character
    "halt": 0xf           # Halt execution
}

# Inverse map for debug output
OPCODE_NAMES = {v: k for k, v in OPCODES.items()}

def assemble(filename):
    # Initialize memory array
    memory = [0] * 1000000

    # Dictionary to store label addresses
    labels = {}

    # List to track locations needing patching with label addresses
    patches = []  # (memory_address, label_name)

    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error opening file: {e}")
        sys.exit(1)

    # Current memory address for code generation
    current_addr = 0

    # Process each line
    for line_num, line in enumerate(lines, 1):
        # Remove comments and whitespace
        line = re.sub(r';.*$', '', line).strip()
        if not line:
            continue

        # Handle labels
        if ':' in line:
            parts = line.split(':', 1)
            label = parts[0].strip()
            labels[label] = current_addr

            # If there's content after the label on the same line, process it
            line = parts[1].strip()
            if not line:
                continue

        # Process instructions and data directives
        if line.startswith('.data'):
            # Handle data directive
            data_content = line[5:].strip()

            # Handle string data
            if data_content.startswith('"'):
                end_quote = data_content.rfind('"')
                if end_quote > 0:
                    string_content = data_content[1:end_quote]

                    # Store each character's ASCII value
                    for char in string_content:
                        memory[current_addr] = ord(char)
                        current_addr += 1

                    # Process additional values after the string
                    remaining = data_content[end_quote + 1:].strip()
                    if remaining:
                        if remaining.startswith(','):
                            remaining = remaining[1:].strip()
                        values = [v.strip() for v in remaining.split(',')]
                        for val in values:
                            try:
                                memory[current_addr] = int(val)
                            except ValueError:
                                patches.append((current_addr, val))
                            current_addr += 1
            else:
                # Handle numeric data
                values = [v.strip() for v in data_content.split(',')]
                for val in values:
                    try:
                        memory[current_addr] = int(val)
                    except ValueError:
                        patches.append((current_addr, val))
                    current_addr += 1
        elif line.startswith('loada'):
            # Handle loada instruction
            memory[current_addr] = OPCODES["loada"]
            current_addr += 1

            # Process operand
            parts = line.split(maxsplit=1)
            if len(parts) > 1:
                operand = parts[1].strip()
                try:
                    memory[current_addr] = int(operand)
                except ValueError:
                    patches.append((current_addr, operand))
                current_addr += 1
            else:
                print(f"Warning: loada without operand at line {line_num}")
                current_addr += 1  # Skip the operand location
        elif any(line.startswith(op) for op in OPCODES.keys()):
            # Handle other instructions
            parts = line.split(maxsplit=1)
            opcode = parts[0].strip()
            if opcode in OPCODES:
                memory[current_addr] = OPCODES[opcode]
                current_addr += 1
            else:
                print(f"Warning: Unrecognized instruction '{opcode}' at line {line_num}")
        else:
            print(f"Warning: Unrecognized line format at line {line_num}: {line}")

    # Apply patches - resolve label references
    for addr, label in patches:
        if label in labels:
            memory[addr] = labels[label]
        else:
            print(f"Error: Undefined label '{label}' referenced at address {addr}")
            sys.exit(1)

    return memory, current_addr  # Return the memory and end address

def disassemble(memory, start_addr=0, end_addr=None):
    """
    Disassemble the program in memory in a traditional format.
    """
    if end_addr is None:
        # Try to determine end by finding the last non-zero value
        for i in range(len(memory) - 1, 0, -1):
            if memory[i] != 0:
                end_addr = i + 1
                break
        if end_addr is None:
            end_addr = 100  # Default to showing 100 words

    # Special handling for first 3 addresses (registers)
    if start_addr == 0:
        for i in range(3):
            print(f"{i:08x} {memory[i]:08x}          {['P_REG', 'DATA_REG_A', 'DATA_REG_X'][i]}")
        pc = PROGRAM_START
    else:
        pc = start_addr

    # Disassemble the program
    while pc < end_addr:
        value = memory[pc]
        addr_str = f"{pc:08x}"

        # Handle instructions
        if value in OPCODE_NAMES:
            mnemonic = OPCODE_NAMES[value]

            # Handle loada which takes an operand
            if value == OPCODES["loada"] and pc + 1 < end_addr:
                operand = memory[pc + 1]
                print(f"{addr_str} {value:08x} {operand:08x} {mnemonic} {operand}")
                pc += 2  # Skip operand
                continue
            else:
                print(f"{addr_str} {value:08x}          {mnemonic}")
        else:
            # Try to interpret as ASCII if in printable range
            if 32 <= value <= 126:  # Printable ASCII range
                data_str = f"'{chr(value)}'"
            else:
                data_str = f"{value}"
            print(f"{addr_str} {value:08x}          {data_str}")

        pc += 1

def execute_vm(memory, debug=False):
    """
    Execute the program stored in memory.
    """
    pc = PROGRAM_START  # Program Counter starts at address 3
    halted = False
    instruction_count = 0
    output_buffer = ""

    if debug:
        print("\nDebug trace:")

    try:
        while not halted and instruction_count < 10000:  # Prevent infinite loops
            # Fetch
            instruction = memory[pc]
            original_pc = pc  # Store for debug output
            pc += 1
            instruction_count += 1

            # Get instruction name for debug
            inst_name = OPCODE_NAMES.get(instruction, f"UNKNOWN(0x{instruction:02x})")

            # Execute
            if instruction == OPCODES["loada"]:
                # Load the next word into the A register
                memory[DATA_REG_A] = memory[pc]
                pc += 1
            elif instruction == OPCODES["a2x"]:
                # Move data from register A to X
                memory[DATA_REG_X] = memory[DATA_REG_A]
            elif instruction == OPCODES["x2a"]:
                # Move data from register X to A
                memory[DATA_REG_A] = memory[DATA_REG_X]
            elif instruction == OPCODES["a2p"]:
                # Move A to pointer register (address register)
                memory[P_REG] = memory[DATA_REG_A]
            elif instruction == OPCODES["read"]:
                # Read word from memory at pointer register into data register A
                addr = memory[P_REG]
                memory[DATA_REG_A] = memory[addr]
            elif instruction == OPCODES["write"]:
                # Write word from data register A to memory at pointer register
                addr = memory[P_REG]
                memory[addr] = memory[DATA_REG_A]
            elif instruction == OPCODES["add"]:
                # Add A and X, store result in A
                memory[DATA_REG_A] = (memory[DATA_REG_A] + memory[DATA_REG_X]) & 0xFFFFFFFF
            elif instruction == OPCODES["lshift"]:
                # Left shift A by 1 bit
                memory[DATA_REG_A] = (memory[DATA_REG_A] << 1) & 0xFFFFFFFF
            elif instruction == OPCODES["rshift"]:
                # Right shift A by 1 bit
                memory[DATA_REG_A] = (memory[DATA_REG_A] >> 1) & 0xFFFFFFFF
            elif instruction == OPCODES["and"]:
                # Binary AND: A = A & X
                memory[DATA_REG_A] = (memory[DATA_REG_A] & memory[DATA_REG_X]) & 0xFFFFFFFF
            elif instruction == OPCODES["or"]:
                # Binary OR: A = A | X
                memory[DATA_REG_A] = (memory[DATA_REG_A] | memory[DATA_REG_X]) & 0xFFFFFFFF
            elif instruction == OPCODES["not"]:
                # Binary NOT: Invert all bits of A
                memory[DATA_REG_A] = (~memory[DATA_REG_A]) & 0xFFFFFFFF
            elif instruction == OPCODES["jump"]:
                # Jump to address in pointer register
                new_pc = memory[P_REG]
                pc = new_pc
            elif instruction == OPCODES["jumpz"]:
                # Jump to address in pointer register if A == 0
                if memory[DATA_REG_A] == 0:
                    new_pc = memory[P_REG]
                    pc = new_pc
            elif instruction == OPCODES["output"]:
                # Print the lower 8 bits as ASCII - no newline
                char = chr(memory[DATA_REG_A] & 0xFF)
                output_buffer += char
            elif instruction == OPCODES["halt"]:
                # Halt execution
                halted = True
            else:
                print(f"\nProgram terminated: Unknown instruction: 0x{instruction:02x} at address {original_pc}")
                break

            if debug:
                # Print compact debug info with fixed width fields for alignment
                print(f"0x{original_pc:08x} {inst_name:<14} p=0x{memory[P_REG]:08x} a=0x{memory[DATA_REG_A]:08x} x=0x{memory[DATA_REG_X]:08x}")

        if instruction_count >= 10000:
            print("\nExecution terminated: Maximum instruction count reached (possible infinite loop)")
    except Exception as e:
        print(f"\nProgram terminated with error: {str(e)}")

    if debug:
        print("\nEnd of debug trace")

    # Print the final output buffer
    print("\nProgram Output:")
    print(output_buffer)

    print("\nSummary:")
    print(f"Total instructions executed: {instruction_count}")
    print(f"Final register values: P_REG=0x{memory[P_REG]:08x}, DATA_REG_A=0x{memory[DATA_REG_A]:08x}, DATA_REG_X=0x{memory[DATA_REG_X]:08x}")

def format_binary(value, bit_width=8):
    """
    Format a number as a binary string with the specified bit width.
    """
    mask = (1 << bit_width) - 1
    value = value & mask
    return format(value, f'0{bit_width}b')

def format_memory_binary(memory, end_addr, bit_width=8):
    """
    Format memory in binary format with specified pattern.
    """
    parts = []
    
    # Format registers
    parts.append(format_binary(memory[P_REG], bit_width))
    parts.append(format_binary(memory[DATA_REG_A], bit_width))
    parts.append(format_binary(memory[DATA_REG_X], bit_width))
    
    # Format memory starting at PROGRAM_START
    first_mem = format_binary(memory[PROGRAM_START], bit_width)
    parts.append(f"p{first_mem}")
    
    for addr in range(PROGRAM_START + 1, end_addr):
        bin_val = format_binary(memory[addr], bit_width)
        parts.append(f" {bin_val}")
    
    # Join with hyphens
    return "-".join(parts)

# Parse command line arguments
if len(sys.argv) < 2:
    print("Usage: python vm_assembler.py <assembly_file> [--disassemble] [--debug] [--bits N]")
    sys.exit(1)

filename = sys.argv[1]
disassemble_flag = "--disassemble" in sys.argv
debug_flag = "--debug" in sys.argv

# Get bit width if specified
bit_width = 8  # Default
for i, arg in enumerate(sys.argv):
    if arg == "--bits" and i + 1 < len(sys.argv):
        try:
            bit_width = int(sys.argv[i + 1])
        except ValueError:
            print(f"Warning: Invalid bit width '{sys.argv[i + 1]}', using default (8)")

# Run assembler
memory, end_addr = assemble(filename)

# Print the binary memory representation before execution
binary_output = format_memory_binary(memory, end_addr, bit_width)
print(binary_output)

# Continue with the rest of the program
if disassemble_flag:
    disassemble(memory, 0, end_addr)

# Execute the VM
execute_vm(memory, debug_flag)
