# kind: refused
# perl prints '\Uab' as it is: no refusal there; this one is the line call.
use v5.42;
say __LINE__();
