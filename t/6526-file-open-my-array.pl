# kind: refused
# perl dies: Can't use string ("0") as a symbol ref.
use v5.42;
open(my @fh, '<', 'in.txt');
