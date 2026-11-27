# kind: fault
# perl warns: Illegal hexadecimal digit '_' ignored (T473).
use v5.42;
say hex("_ff");
say hex("ff_");
