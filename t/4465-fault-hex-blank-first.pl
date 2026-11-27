# kind: fault
# perl warns: Illegal hexadecimal digit ' ' ignored, and gives 0 (T473).
use v5.42;
say hex(" ff");
