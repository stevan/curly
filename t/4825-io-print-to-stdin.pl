# kind: refused
# perl prints nothing, and warns: Filehandle STDIN opened only for input.
use v5.42;
print STDIN "x";
