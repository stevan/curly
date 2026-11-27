# check: ok
# kind: same
# The knobs are given to perl as they are to the program (D220).
use v5.42;
say exists $ENV{CURLY_GC_STRESS} ? "knob" : "none";
