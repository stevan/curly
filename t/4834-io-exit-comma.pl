# kind: refused
# perl exits 1, and warns: Useless use of a constant (2) in void context.
use v5.42;
exit 1, 2;
