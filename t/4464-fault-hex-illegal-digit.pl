# kind: fault
# perl warns: Illegal hexadecimal digit 'g' ignored (T473).
use v5.42;
say hex("ff");
say hex("fg");
