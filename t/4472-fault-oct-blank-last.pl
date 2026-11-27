# kind: fault
# perl gives 493 in silence (T473): a stop it makes in silence is a fault here (D203).
use v5.42;
say oct(" 755");
say oct("755 ");
