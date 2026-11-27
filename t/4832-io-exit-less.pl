# kind: refused
# perl exits 2, and warns (T506).
use v5.42;
exit 2 < 3;
