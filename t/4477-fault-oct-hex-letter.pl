# kind: fault
# perl warns: Illegal hexadecimal digit 'g' ignored, and gives 1.
use v5.42;
say oct("0x1g");
