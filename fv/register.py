from struct import pack, unpack
from threading import Timer

class Register(object):
    def __init__(self, bar):
       self.__size = 4
       self.__bar = bar

    # field = slice(1, 2)
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

        value = self.__bar.read(reg, size);
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
        return self.__bar.write(reg, value)

    def register_size(size):
        self.__size = size
