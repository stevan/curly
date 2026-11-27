# kind: refused
# perl exits 0, and warns: Possible precedence issue with control flow operator (T506).
use v5.42;
exit 0 || 3;
