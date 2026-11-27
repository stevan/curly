# kind: fault
# perl warns: Illegal binary digit '2' ignored, and gives 2 (T473).
use v5.42;
say oct("0b101");
say oct("0b102");
