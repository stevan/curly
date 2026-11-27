# kind: fault
# perl warns: Illegal octal digit '8' ignored, and gives 7 (T473).
use v5.42;
say oct("789");
