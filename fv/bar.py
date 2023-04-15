#!/usr/bin/python3
import os
from mmap import mmap, PROT_READ, PROT_WRITE, PAGESIZE
from struct import pack, unpack
from threading import Timer

class Bar(object):
    """ Create a Bar instance that ``mmap()`` s a PCIe device BAR.

    :param str filename: sysfs filename for the corresponding resourceX file.

    """
    def __init__(self, filename: str):
        self.__map = None
        self.__stat = os.stat(filename)
        fd = os.open(filename, os.O_RDWR)
        self.__map = mmap(fd, 0, prot=PROT_READ | PROT_WRITE)

        self.__isr_mask = 0 
        self.__isr_status = 0
        self.__isr = {}
        self.__isr_enabled = 0

        self.__size = 4

    def field_get(self, x, field, size = -1):
        if size == -1:
            size = self.__size
        bits = size*8
        return int(f"{x:0={bits}b}"[(bits - field.stop):(bits - field.start)], base = 2)

    def field_set(self, x, field, v, size = -1):
        if size == -1:
            size = self.__size
        bits = size*8
        xb = f"{x:0={bits}b}"
        r = field.stop - field.start
        vb = f"{v:0={r}b}"
        rb = xb[:bits - field.stop] + vb + xb[bits - field.start:]
        return int(rb, base = 2)

    def field_clear(self, x, field, size = -1):
        if size == -1:
            size = self.__size
        bits = size*8
        xb = f"{x:0={bits}b}"
        r = field.stop - field.start
        vb = f"{0:0={r}b}"
        rb = xb[:bits - field.stop] + vb + xb[bits - field.start:]
        return int(rb, base = 2)

    def reg_get(self, reg: int, size = -1):
        if size == -1:
            size = self.__size

        value = self.read(reg, size);
        if size == 1:
            return unpack('<B', value)[0]
        if size == 2:
            return unpack('<H', value)[0]
        if size == 4:
            return unpack('<L', value)[0]
        if size == 8:
            return unpack('<Q', value)[0]

    def reg_set(self, reg: int, value:int, size = -1):
        if size == -1:
            size = 4

        if size == 1:
            x = pack('<B', value)
        if size == 2:
            x = pack('<H', value)
        if size == 4:
            x = pack('<L', value)
        if size == 8:
            x = pack('<Q', value)
        return self.write(reg, x)

    def reg_size(self, size = 4):
        self.__size = size

    def isr_init (self, mask, status):
        self.__isr_mask = mask
        self.__isr_status = status
        self.__isr_enabled = 0

    def isr_register (self, isr, mask):
        self.__isr[mask] = isr
        x = self.reg_get(self.__mask_reg)
        x = x | mask
        self.reg_set(self.__mask_reg, x)
        if self__isr_enabled == 0:
            self.__isr_enabled = 1
            self.__isr_handler()

    def isr_unregister (self, isr):
        for s, isr in self.__isr:
            if isr == isr:
               del self.__isr[s]

        if len(self.__isr) == 0:
            self__isr_enabled = 0

    def __isr_handler(self):
        if self.__isr_enabled == 0:
            return

        mask = self.reg_get(self.__isr_mask)
        self.reg_set(self.__isr_mask, 0)
        status = self.reg_get(self.__isr_status)
        for s, isr in self.__isr:
            if s & status:
                isr(status)
        self.reg_set(self.__mask_reg, mask)
        self.__isr_timer = Timer(0.05, self.__isr_handler)
        self.__isr.timer.start()

    def __del__(self):
        if self.__map is not None:
            self.__map.close()

    def __check_offset(self, offset: int):
        """ Check if the given offset is properly DW-aligned and the access
            falls within the BAR size.

        """
        if offset & 0x3:
            raise ValueError("unaligned access to offset 0x%x" % (offset))
        if offset + 3 > self.size:
            raise ValueError("offset (0x%x) exceeds BAR size (0x%x)" %
                             (offset, self.size))

    def read(self, offset: int, size = 4):
        """ Read a 32 bit / double word value from offset.

        :param int offset: BAR byte offset to read from.
        :returns: Double word read from the given BAR offset.
        :rtype: double word / 32 bit unsigned long / int

        """
        self.__map.seek(offset)
        return self.__map.read(size)

    def readb(self, offset: int):
        """ Read a 32 bit / double word value from offset.

        :param int offset: BAR byte offset to read from.
        :returns: Byte read from the given BAR offset.
        :rtype: Byte

        """
        self.__map.seek(offset)
        return self.__map.read_byte()

    def write(self, offset: int, data):
        """ Write a 32 bit / double word value to offset.

        :param int offset: BAR byte offset to write to.
        :param int data: double word to write to the given BAR offset.
        """
        self.__map.seek(offset)
        # write to map. no ret. check: ValueError/TypeError is raised on error
        return self.__map.write(data)

    def writeb(self, offset: int, data:int):
        """ Write a 32 bit / double word value to offset.

        :param int offset: BAR byte offset to write to.
        :param int data: double word to write to the given BAR offset.
        """
        # self.__check_offset(offset)
        self.__map.seek(offset)
        # write to map. no ret. check: ValueError/TypeError is raised on error
        return self.__map.write_byte(data)

    @property
    def size(self):
        """
        Get the size of the BAR.

        :returns: BAR size in bytes.
        :rtype: int
        """
        return self.__stat.st_size

