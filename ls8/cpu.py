"""CPU functionality."""

import sys

LDI = 0b10000010
HLT = 0b00000001
PRN = 0b01000111
ADD = 0b10100000
SUB = 0b10100001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
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
        self.ram = [0] * 256
        self.register = [0] * 8
        self.pc = 0
        self.flag = 0
        self.running = True
        self.sp = 7
        self.register[self.sp] = 0xF4
        self.branch_table = {
            LDI: self.LDI,
            HLT: self.HLT,
            PRN: self.PRN,
            ADD: self.ADD,
            SUB: self.SUB,
            MUL: self.MUL,
            PUSH: self.PUSH,
            POP: self.POP,
            CALL: self.CALL,
            RET: self.RET,
            CMP: self.CMP,
            JMP: self.JMP,
            JEQ: self.JEQ,
            JNE: self.JNE
        }

    def load(self):
        """Load a program into memory."""

        program = [0] * 256

        filename = sys.argv[1]

        with open(f'examples/{filename}') as f:
            address = 0

            for line in f:
                line = line.split("#")
                line = line[0].strip()

                if line == "":
                    continue
                
                value = int(line, 2)
                self.ram_write(address, value)
                address += 1

    def ram_read(self, MAR): # Memory Address Register - contains address being written or read
        return self.ram[MAR]

    def ram_write(self, MAR, MDR): #Memory Data Register - data that was read or the data to write
        self.ram[MAR] = MDR

    def LDI(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        
        self.register[operand_a] = operand_b
        self.pc += 3

    def HLT(self):
        self.running = False
        self.pc += 1

    def PRN(self):
        operand_a = self.ram_read(self.pc + 1)
        print(self.register[operand_a])
        self.pc += 2

    def ADD(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu('ADD', operand_a, operand_b)
        self.pc += 3

    def SUB(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu('SUB', operand_a, operand_b)
        self.pc += 3

    def MUL(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu('MUL', operand_a, operand_b)
        self.pc += 3

    def CMP(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu('CMP', operand_a, operand_b)
        self.pc += 3

    def PUSH(self):
        # decrement SP
        self.register[self.sp] -= 1
        # get value from register
        reg_num = self.ram_read(self.pc + 1)
        value = self.register[reg_num]
        # store value in register
        self.ram_write(self.register[self.sp], value)

        self.pc += 2

    def POP(self):
        # get value from register
        reg_num = self.ram_read(self.pc + 1)
        value = self.ram_read(self.register[self.sp])
        # remove that value
        self.register[reg_num] = value
        # increment SP
        self.register[self.sp] += 1

        self.pc += 2

    def CALL(self):
        rtn_addr = self.pc + 2 # address we're going to RET

        # push on to stack
        self.register[self.sp] -= 1
        self.ram_write(self.register[self.sp], rtn_addr)
        # get address to call
        reg_num = self.ram_read(self.pc + 1)
        sub_addr = self.register[reg_num]
        # call address
        self.pc = sub_addr

    def RET(self):
        self.pc = self.ram_read(self.register[self.sp])
        self.register[self.sp] += 1

    def JMP(self):
        # get address to call
        reg_num = self.ram_read(self.pc + 1)
        sub_addr = self.register[reg_num]
        # set pc to address
        self.pc = sub_addr

    def JEQ(self):
        # if flag is true(1), jump to address
        if self.flag == 1:
            self.JMP()
        else:
            self.pc += 2

    def JNE(self):
        # if flag is false(0), jump to address
        if self.flag == 0:
            self.JMP()
        else:
            self.pc += 2

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        elif op == "SUB":
            self.register[reg_a] -+ self.register[reg_b]
        elif op == 'MUL':
            self.register[reg_a] *= self.register[reg_b]
        elif op == 'CMP':
            if self.register[reg_a] == self.register[reg_b]:
                self.flag = 1
            elif self.register[reg_a] < self.register[reg_b]:
                self.flag = 0
            elif self.register[reg_a] > self.register[reg_b]:
                self.flag = 0
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

    def run(self):
        """Run the CPU."""
        while self.running:
            # read memory address stored in register PC and store as ir
            ir = self.ram_read(self.pc)
            # print(ir)
            self.branch_table[ir]()