# kind: fault
# perl warns: Illegal hexadecimal digit '_' ignored, and gives 15 (T473).
use v5.42;
say hex("f_f");
say hex("f__f");
