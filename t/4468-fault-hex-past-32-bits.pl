# kind: fault
# perl warns: Hexadecimal number > 0xffffffff non-portable (T473).
use v5.42;
say hex("ffffffff");
say hex("100000000");
