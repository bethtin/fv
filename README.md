# fv: Simple Python Module to access PCIe resources

fv provides a quick way to perform FPGA verification based on the PCI interface.

1. Variable length register read/write.
2. Variable length Memory read/write.
3. Interrupt routins.

The fv is forked from the PyCIe.

All the python scripts using fv must run as root.*

## Example

#python
import fv

# Bind to PCI device at "0000:01:00.0"
pci = fv.Pci("0000:01:00.0")

# Access BAR 0
bar = pci.bar[1]

# set register default size
bar.reg_size(4)

# write 0xdeadbeef to BAR0, offset 0x1000, length 4 register
bar.reg_set(0x1000, 0xdeadbeef)

# write 0xde to BAR0, offset 0x2000, length 1 register
bar.reg_set(0x1000, 0xde, 1)

# read BAR 0, offset 0x1004, length 4 register
ret = bar.reg_get(0x1004)
