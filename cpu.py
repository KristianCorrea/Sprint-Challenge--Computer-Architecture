"""CPU functionality."""

import sys

LDI = 0b10000010  # LDI R0,8
PRN = 0b01000111  # PRN R0
HLT = 0b00000001
MUL = 0b10100010  # MUL R0,R1
PUSH = 0b01000101  # PUSH R0
POP = 0b01000110  # POP R2
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.sp = 7
        self.reg[7] = 0xf4
        self.fl = 0b00000000

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print("usage: comp.py filename")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for instruction in f:
                    try:
                        instruction = instruction.strip()
                        instruction = instruction.split('#', 1)[0]
                        instruction = int(instruction, 2)
                        # print(instruction)
                        self.ram[address] = instruction
                        address += 1
                    except ValueError:
                        pass
        except FileNotFoundError:
            print(f"Couldn't find file {sys.argv[1]}")
            sys.exit(1)


    def ram_read(self, address):
        return self.ram[address]
    
    def ram_write(self, value, address):
        self.ram[address] = value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            else:
                self.fl = 0b00000001
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
    
    def JMP(self):
        address = self.ram_read(self.pc + 1)
        self.pc = self.reg[address]

    def AND(self, a, b):
        return a & b

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            inst = self.ram_read(self.pc)
            if inst == HLT: #HLT
                ## HALT
                running = False
            elif inst == PRN:
                ## PRN print value in giver register
                reg = self.ram_read(self.pc + 1)
                print(self.reg[reg])
                self.pc += 2
            elif inst == LDI:
                ## LDI set register to value
                reg = self.pc + 1
                val = self.pc + 2
                self.reg[self.ram_read(reg)] = self.ram_read(val)
                self.pc += 3
            elif inst == MUL:
                ## MULT regA and regB together, store esults in regA
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                self.alu('MUL', reg_a, reg_b)
                self.pc += 3
            elif inst == PUSH:
                self.reg[self.sp] -= 1

                reg_num = self.ram_read(self.pc + 1)
                value = self.reg[reg_num]
                # print(self.reg[self.sp])
                push_to = self.reg[self.sp]
                # print(push_to)
                self.ram[push_to] = value

                self.pc += 2
            elif inst == POP:
                address_pop_from = self.reg[self.sp]
                value = self.ram[address_pop_from]

                reg_num = self.ram[self.pc + 1]
                self.reg[reg_num] = value

                self.reg[self.sp] += 1

                self.pc += 2
            elif inst == CALL:
                # Where RET will return to
                # we are going to add to the stack so decrement the stack pointer
                address = self.pc + 2
                self.reg[7] -= 1
                self.ram[self.reg[7]] = address
                # get address to call
                reg_num = self.ram[self.pc + 1]
                # assign the value in the register to the program counter
                self.pc = self.reg[reg_num]
            elif inst == RET:
                # get the return address
                address = self.ram[self.reg[7]]
                # increment the stack pointer since a value was "popped"
                self.reg[7] += 1
                # # set pc to return address
                self.pc = address
            elif inst == CMP:
                self.alu("CMP",self.ram_read(self.pc + 1),self.ram_read(self.pc + 2) )
                self.pc += 3
            elif inst == JMP:
                self.JMP()
            elif inst == JEQ:
                # masking with 1 to check the other value
                if self.AND(self.fl, 0b00000001) == 1:
                    self.JMP()
                else:
                    self.pc += 2
            elif inst == JNE:
                # masking with 1 to check the other value
                if self.AND(self.fl, 0b00000001) == 0:
                    self.JMP()
                else:
                    self.pc += 2
            